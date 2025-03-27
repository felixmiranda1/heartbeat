from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from reports.models import Report, ReportMeasurement, MeasurementType, ReportBlock, CustomOptionCategory
from accounts.models import Patient, Appointment
import uuid
from decimal import Decimal
from reports.forms import PatientForm, AppointmentForm, ReportMeasurementForm, ReportBlockFormSet, modelformset_factory

def create_report(request):
    if request.method == 'POST':
        patient_form = PatientForm(request.POST)
        appointment_form = AppointmentForm(request.POST)
        measurement_form = ReportMeasurementForm(request.POST)

        if patient_form.is_valid() and appointment_form.is_valid() and measurement_form.is_valid():
            # ✅ Get the measurements filled out by the doctor in the manual form
            manual_values = measurement_form.cleaned_data

            # ✅ Calculate derived values based on the filled measurements
            derived_values = calculate_derived_measurements_from_form(manual_values)

            # ✅ Check if a patient with the same birth date and similar name already exists
            birth_date = patient_form.cleaned_data.get('birth_date')
            name = patient_form.cleaned_data.get('name').strip().lower()

            existing_patient = Patient.objects.filter(birth_date=birth_date).filter(name__iexact=name).first()

            if existing_patient:
                patient = existing_patient
            else:
                patient = patient_form.save(commit=False)
                patient.id = uuid.uuid4()
                patient.created_at = timezone.now()
                patient.updated_at = timezone.now()
                patient.save()

            # ✅ Create and save the Appointment
            appointment = appointment_form.save(commit=False)
            appointment.id = uuid.uuid4()
            appointment.patient = patient
            appointment.created_at = timezone.now()
            appointment.updated_at = timezone.now()
            appointment.save()

            # ✅ Create and save the Report
            report = Report.objects.create(
                id=uuid.uuid4(),
                appointment=appointment,
                patient=patient,
                status='draft',
                created_at=timezone.now(),
                updated_at=timezone.now()
            )

            # ✅ Add the ReportBlocks and save the created ones
            categories = CustomOptionCategory.objects.all().order_by('order_index')
            created_blocks = []
            for category in categories:
                block = ReportBlock.objects.create(
                    id=uuid.uuid4(),
                    report=report,
                    title=category.name,
                    order_index=category.order_index,
                    created_at=timezone.now(),
                    updated_at=timezone.now()
                )
                created_blocks.append(block)

            # ✅ Update the contents of the descriptive blocks based on the formset
            ReportBlockFormSet = modelformset_factory(ReportBlock, fields=('content',), extra=0)
            formset = ReportBlockFormSet(request.POST, queryset=ReportBlock.objects.filter(id__in=[b.id for b in created_blocks]))
            if formset.is_valid():
                for form, category in zip(formset.forms, categories):
                    instance = form.save(commit=False)
                    instance.report = report
                    instance.title = category.name
                    instance.order_index = category.order_index
                    instance.updated_at = timezone.now()
                    if not instance.created_at:
                        instance.created_at = timezone.now()
                    instance.save()
            else:
                for form in formset:
                    print("⛔ Errors in form:", form.errors)
                print("General formset errors:", formset.non_form_errors())
                
            # ✅ Save the manual measurements linked to the Report
            measurement_form.report = report
            measurement_form.save()

            # ✅ Save the calculated measures directly to the database
            for measurement_type_id, value in derived_values.items():
                if value is None:
                    continue 
                measurement_type = MeasurementType.objects.get(id=measurement_type_id)

                ReportMeasurement.objects.update_or_create(
                    report=report,
                    measurement_type=measurement_type,
                    defaults={
                        'value': value,
                        'updated_at': timezone.now()
                    }
                )

            messages.success(request, "Measurements saved successfully.")
            return redirect('reports:create_report')

        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        # Handle GET: initialize blank forms and context
        patient_form = PatientForm()
        appointment_form = AppointmentForm(initial={'date': timezone.now()})
        measurement_form = ReportMeasurementForm()
        categories = CustomOptionCategory.objects.all().order_by('order_index')

        # Create a formset with one form for each category
        ReportBlockFormSet = modelformset_factory(ReportBlock, fields=('content',), extra=len(categories))
        formset = ReportBlockFormSet(queryset=ReportBlock.objects.none())

        # Set the title (category name) for each block of the form
        for form, category in zip(formset.forms, categories):
            form.instance.title = category.name
            form.instance.order_index = category.order_index

        # Combine the forms with the category objects
        combined_blocks = list(zip(formset.forms, categories))

        # Group the options by category ID (for safe lookup in the template)
        custom_options = CustomOption.objects.select_related('category').all().order_by('category__name')
        grouped_options = {}
        for option in custom_options:
            grouped_options.setdefault(option.category.id, []).append(option)

        context = {
            'patient_form': patient_form,
            'appointment_form': appointment_form,
            'measurement_form': measurement_form,
            'formset': formset,
            'combined_blocks': combined_blocks,
            'grouped_options': grouped_options,
            'section': 'new_report'
        }
        return render(request, 'reports/report.html', context)

def calculate_derived_measurements_from_form(manual_values):
    """
    Calculates derived values from the data filled in the manual measurement form.
    manual_values: dict from measurement_form.cleaned_data
    Returns: dictionary {measurement_type_id: calculated_value}
    """

    # Getting manual values filled in the form
    aorta_raiz = float(manual_values.get('measurement_fc2afb5f-6110-4714-8b0d-4455696bbb10') or 0)
    atrio_esquerdo = float(manual_values.get('measurement_ea1bd53d-a826-4815-972e-a2801a1b99e0') or 0)
    dvd = float(manual_values.get('measurement_7051b7b6-841b-4e98-a539-3601578dcfe1') or 0)
    diastole_final_ve = float(manual_values.get('measurement_7afa3a2b-d414-4fa0-8d82-b941f3f7db36') or 0)
    sistole_final_ve = float(manual_values.get('measurement_c5326b50-bf6c-46f7-bbec-15748bee04c4') or 0)
    septo = float(manual_values.get('measurement_690b176b-8163-4ce4-82d7-8df8e9df6050') or 0)
    parede_posterior = float(manual_values.get('measurement_846611f4-8e53-4487-83cd-1ca680a2bd48') or 0)

    derived_values = {}

    # Left Atrium Volume / BSA
    derived_values['d8a8dbd0-c50c-42ff-b81b-e8cd2a32157f'] = atrio_esquerdo * 0.6 if atrio_esquerdo else None

    # LVEDV / BSA
    derived_values['726c5c78-1404-464b-8372-6a40128782b6'] = diastole_final_ve * 0.9 if diastole_final_ve else None

    # LVEDV / Height
    derived_values['bc89d090-a6fb-4f59-a89c-1cc8fc56aba2'] = diastole_final_ve / 1.7 if diastole_final_ve else None

    # End-Diastolic Volume
    derived_values['6db01c09-ea55-428d-a9d3-fb4c812e3b7f'] = diastole_final_ve * 1.2 if diastole_final_ve else None

    # End-Systolic Volume
    derived_values['3cb036a2-bc21-4124-b607-dc9b1b6245e0'] = sistole_final_ve * 1.2 if sistole_final_ve else None

    # Ejection Fraction (Teicholz)
    derived_values['9c28deef-78d5-47aa-9fd2-218fbccb1eeb'] = (
        ((diastole_final_ve - sistole_final_ve) / diastole_final_ve * 100)
        if diastole_final_ve > 0 else None
    )

    # Ejection Fraction (Simpson)
    derived_values['facaa610-84b8-47a3-9db2-13065b31fa94'] = (
        ((diastole_final_ve - sistole_final_ve) / diastole_final_ve * 100)
        if diastole_final_ve > 0 else None
    )

    # Percent Shortening
    derived_values['96f07bcc-8336-434a-8e1c-12d57e9b822a'] = (
        ((diastole_final_ve - sistole_final_ve) / diastole_final_ve * 100)
        if diastole_final_ve > 0 else None
    )

    # Left Ventricular Mass
    derived_values['70d430a4-23a9-4690-8523-31a693bc4ec5'] = (
        0.8 * (diastole_final_ve + septo + parede_posterior)**3
        if diastole_final_ve and septo and parede_posterior else None
    )

    # LV Mass / BSA
    derived_values['f391f7ed-f21c-4d79-a51a-766262958d57'] = (
        0.8 * (diastole_final_ve + septo + parede_posterior)**3 / 1.7
        if diastole_final_ve and septo and parede_posterior else None
    )

    # LV Mass / Height
    derived_values['fb0db8fa-9976-4b31-ae04-23277d07d67c'] = (
        0.8 * (diastole_final_ve + septo + parede_posterior)**3 / 1.7
        if diastole_final_ve and septo and parede_posterior else None
    )

    # Relative Wall Thickness
    derived_values['84540bfa-2749-4e9c-bec1-f7689616caac'] = (
        (2 * parede_posterior) / diastole_final_ve
        if parede_posterior and diastole_final_ve else None
    )

    # RWT and LV Mass Ratio
    massa_ve = (
        0.8 * (diastole_final_ve + septo + parede_posterior)**3
        if diastole_final_ve and septo and parede_posterior else None
    )
    derived_values['c1e484a6-4441-4126-98e3-0b00dd90236b'] = (
        ((2 * parede_posterior) / diastole_final_ve) / massa_ve
        if parede_posterior and diastole_final_ve and massa_ve else None
    )
    return derived_values

from reports.models import ReportBlock, CustomOption
from reports.forms import ReportBlockFormSet

def edit_descriptive_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    # 🔽 Step 1: Load the block categories
    categories = CustomOptionCategory.objects.all().order_by('name')

    # 🔽 Step 2: Load the options (grouped by category name)
    custom_options = CustomOption.objects.select_related('category').all().order_by('category__name')
    grouped_options = {}
    for option in custom_options:
        grouped_options.setdefault(option.category.name, []).append(option)

    if request.method == 'POST':
        formset = ReportBlockFormSet(request.POST, queryset=ReportBlock.objects.filter(report=report).order_by('order_index'))

        if formset.is_valid():
            instances = formset.save(commit=False)

            for instance in instances:
                instance.report = report
                instance.updated_at = timezone.now()
                if not instance.created_at:
                    instance.created_at = timezone.now()
                instance.save()

            messages.success(request, "Descriptive report updated successfully.")
            return redirect('reports:edit_descriptive_report', report_id=report.id)
        else:
            messages.error(request, "Please correct the errors in the descriptive report fields.")
    else:
        all_blocks = []
 
        for index, category in enumerate(categories):
            # Check if a block with this title already exists
            block, created = ReportBlock.objects.get_or_create(
                report=report,
                title=category.name,
                defaults={
                    'order_index': index,
                    'created_at': timezone.now(),
                    'updated_at': timezone.now()
                }
            )
            all_blocks.append(block)
 
        formset = ReportBlockFormSet(queryset=ReportBlock.objects.filter(report=report).order_by('order_index'))

    context = {
        'report': report,
        'formset': formset,
        'grouped_options': grouped_options,
        'section': 'edit_descriptive_report'
    }
    return render(request, 'reports/report.html', context)