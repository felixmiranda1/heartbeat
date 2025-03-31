from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import HttpResponse
from decimal import Decimal
import uuid
from xhtml2pdf import pisa
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import render_to_string
from reports.models import (
    Report, ReportMeasurement, MeasurementType,
    ReportBlock, CustomOptionCategory, CustomOption
)
from accounts.models import Patient, Appointment
from reports.forms import (
    PatientForm, AppointmentForm, ReportMeasurementForm,
    ReportBlockFormSet, modelformset_factory
)

# ------------------------------------------------------------------------------
# 🚀 Report Creation View
# ------------------------------------------------------------------------------

def create_report(request):
    """Handle creation of a new echocardiographic report."""
    if request.method == 'POST':
        patient_form = PatientForm(request.POST)
        appointment_form = AppointmentForm(request.POST)
        measurement_form = ReportMeasurementForm(request.POST)

        if patient_form.is_valid() and appointment_form.is_valid() and measurement_form.is_valid():
            manual_values = measurement_form.cleaned_data
            patient_values = patient_form.cleaned_data
            derived_values = calculate_derived_measurements(manual_values, patient_values)
                        # Try to reuse existing patient
            birth_date = patient_form.cleaned_data.get('birth_date')
            name = patient_form.cleaned_data.get('name').strip().lower()
            patient = Patient.objects.filter(birth_date=birth_date, name__iexact=name).first()

            if not patient:
                patient = patient_form.save(commit=False)
                patient.id = uuid.uuid4()
                patient.created_at = timezone.now()
                patient.updated_at = timezone.now()
                patient.save()

            appointment = appointment_form.save(commit=False)
            appointment.id = uuid.uuid4()
            appointment.patient = patient
            appointment.created_at = timezone.now()
            appointment.updated_at = timezone.now()
            appointment.save()

            report = Report.objects.create(
                id=uuid.uuid4(),
                appointment=appointment,
                patient=patient,
                status='draft',
                created_at=timezone.now(),
                updated_at=timezone.now()
            )

            # Create descriptive blocks for this report
            categories = CustomOptionCategory.objects.all().order_by('order_index')

            # Fill in descriptive blocks using formset
            ReportBlockFormSet = modelformset_factory(ReportBlock, fields=('content',), extra=0)
            formset = ReportBlockFormSet(request.POST, queryset=ReportBlock.objects.none())

            if formset.is_valid():
                for form, category in zip(formset.forms, categories):
                    instance = form.save(commit=False)
                    instance.report = report
                    instance.title = category.name
                    instance.order_index = category.order_index
                    instance.updated_at = timezone.now()
                    if not instance.created_at:
                        instance.created_at = timezone.now()
                    if instance.id:
                        instance.save()
            else:
                print("⛔ Formset errors:", formset.errors, formset.non_form_errors())

            # Save measurements
            measurement_form.report = report
            measurement_form.save()

            for measurement_type_id, value in derived_values.items():
                if value is None:
                    continue
                measurement_type = MeasurementType.objects.get(id=measurement_type_id)
                ReportMeasurement.objects.update_or_create(
                    report=report,
                    measurement_type=measurement_type,
                    defaults={'value': value, 'updated_at': timezone.now()}
                )
        # After the report is saved, generate the PDF
        #generate_report_pdf(request, report.id)
            
        messages.success(request, "Measurements saved successfully.")
        return generate_report_pdf(request, report.id)  # This will return PDF directly

        messages.error(request, "Please correct the errors in the form.")

    else:
        patient_form = PatientForm()
        appointment_form = AppointmentForm(initial={'date': timezone.now()})
        measurement_form = ReportMeasurementForm()
        categories = CustomOptionCategory.objects.all().order_by('order_index')

        ReportBlockFormSet = modelformset_factory(ReportBlock, fields=('content',), extra=len(categories))
        formset = ReportBlockFormSet(queryset=ReportBlock.objects.none())

        for form, category in zip(formset.forms, categories):
            form.instance.title = category.name
            form.instance.order_index = category.order_index

        combined_blocks = list(zip(formset.forms, categories))
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

# ------------------------------------------------------------------------------
# 🧠 Calculations
# ------------------------------------------------------------------------------

def calculate_derived_measurements(manual_values, patient_values):
    """Calculate derived measurement values from form input."""

    altura_cm = float(patient_values.get('height') or 0)
    peso_kg = float(patient_values.get('weight') or 0)
    altura_m = altura_cm / 100 if altura_cm > 3 else altura_cm  # Evita erro se já estiver em metros

    aorta_raiz = float(manual_values.get('measurement_fc2afb5f-6110-4714-8b0d-4455696bbb10') or 0)
    atrio_esquerdo = float(manual_values.get('measurement_ea1bd53d-a826-4815-972e-a2801a1b99e0') or 0)
    dvd = float(manual_values.get('measurement_7051b7b6-841b-4e98-a539-3601578dcfe1') or 0)
    diastole_final_ve = float(manual_values.get('measurement_7afa3a2b-d414-4fa0-8d82-b941f3f7db36') or 0)
    sistole_final_ve = float(manual_values.get('measurement_c5326b50-bf6c-46f7-bbec-15748bee04c4') or 0)
    septo = float(manual_values.get('measurement_690b176b-8163-4ce4-82d7-8df8e9df6050') or 0)
    parede_posterior = float(manual_values.get('measurement_846611f4-8e53-4487-83cd-1ca680a2bd48') or 0)

    derived_values = {}

    # Superfície Corporal (Du Bois & Du Bois)
    sc = (
        0.007184 * (peso_kg ** 0.425) * (altura_cm ** 0.725)
        if altura_cm and peso_kg else None
    )

    # Volume do AE / SC
    derived_values['d8a8dbd0-c50c-42ff-b81b-e8cd2a32157f'] = (
        atrio_esquerdo / sc if atrio_esquerdo and sc else None
    )

    # VE(d) / SC
    derived_values['726c5c78-1404-464b-8372-6a40128782b6'] = (
        diastole_final_ve / sc if diastole_final_ve and sc else None
    )

    # VE(d) / altura
    derived_values['bc89d090-a6fb-4f59-a89c-1cc8fc56aba2'] = (
        diastole_final_ve / altura_m if diastole_final_ve and altura_m else None
    )

    # Volume Diastólico Final (Simpson)
    derived_values['6db01c09-ea55-428d-a9d3-fb4c812e3b7f'] = diastole_final_ve if diastole_final_ve else None

    # Volume Sistólico Final (Simpson)
    derived_values['3cb036a2-bc21-4124-b607-dc9b1b6245e0'] = sistole_final_ve if sistole_final_ve else None

    # Fração de Ejeção (Simpson)
    derived_values['facaa610-84b8-47a3-9db2-13065b31fa94'] = (
        ((diastole_final_ve - sistole_final_ve) / diastole_final_ve * 100)
        if diastole_final_ve > 0 else None
    )

    # Fração de Ejeção (Teichholz)
    derived_values['9c28deef-78d5-47aa-9fd2-218fbccb1eeb'] = (
        ((diastole_final_ve - sistole_final_ve) / diastole_final_ve * 100)
        if diastole_final_ve > 0 else None
    )

    # Encurtamento da Cavidade (%)
    derived_values['96f07bcc-8336-434a-8e1c-12d57e9b822a'] = (
        ((diastole_final_ve - sistole_final_ve) / diastole_final_ve * 100)
        if diastole_final_ve > 0 else None
    )

    # Massa Ventricular Esquerda (g)
    mve = (
        0.8 * 1.04 * ((septo + diastole_final_ve + parede_posterior) ** 3 - diastole_final_ve ** 3) + 0.6
        if diastole_final_ve and septo and parede_posterior else None
    )
    derived_values['70d430a4-23a9-4690-8523-31a693bc4ec5'] = mve

    # MVE / SC
    derived_values['f391f7ed-f21c-4d79-a51a-766262958d57'] = (
        mve / sc if mve and sc else None
    )

    # MVE / altura
    derived_values['fb0db8fa-9976-4b31-ae04-23277d07d67c'] = (
        mve / altura_m if mve and altura_m else None
    )

    # Espessura Relativa das Paredes (ERP)
    erp = (
        (2 * parede_posterior) / diastole_final_ve
        if parede_posterior and diastole_final_ve else None
    )
    derived_values['84540bfa-2749-4e9c-bec1-f7689616caac'] = erp

    # Relação ERP / MVE indexada
    derived_values['c1e484a6-4441-4126-98e3-0b00dd90236b'] = (
        erp / (mve / sc) if erp and mve and sc else None
    )
    return derived_values

# ------------------------------------------------------------------------------
# ✏️ Edit Existing Descriptive Report
# ------------------------------------------------------------------------------

def edit_descriptive_report(request, report_id):
    """Edit the descriptive block section of an existing report."""
    report = get_object_or_404(Report, id=report_id)

    # Load the block categories
    categories = CustomOptionCategory.objects.all().order_by('name')

    # Load the options (grouped by category name)
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

# ------------------------------------------------------------------------------
# ⚡ HTMX Views (Partial Responses)
# ------------------------------------------------------------------------------

def hx_paciente(request):
    """HTMX partial: patient and appointment data."""
    patient_form = PatientForm()
    appointment_form = AppointmentForm(initial={'date': timezone.now()})
    html = render_to_string('reports/partials/paciente.html', {
        'patient_form': patient_form,
        'appointment_form': appointment_form
    }, request=request)
    return HttpResponse(html)

def hx_numerico(request):
    """HTMX partial: numeric report."""
    measurement_form = ReportMeasurementForm()
    html = render_to_string('reports/partials/numerico.html', {
        'measurement_form': measurement_form
    }, request=request)
    return HttpResponse(html)

def hx_descritivo(request):
    """HTMX partial: descriptive report and shortcuts."""
    categories = CustomOptionCategory.objects.all().order_by('order_index')
    ReportBlockFormSet = modelformset_factory(ReportBlock, fields=('content',), extra=len(categories))
    formset = ReportBlockFormSet(queryset=ReportBlock.objects.none())

    for form, category in zip(formset.forms, categories):
        form.instance.title = category.name
        form.instance.order_index = category.order_index

    combined_blocks = list(zip(formset.forms, categories))
    custom_options = CustomOption.objects.select_related('category').all().order_by('category__name')
    grouped_options = {}
    for option in custom_options:
        grouped_options.setdefault(option.category.id, []).append(option)

    html = render_to_string('reports/partials/descritivo.html', {
        'formset': formset,
        'combined_blocks': combined_blocks,
        'grouped_options': grouped_options
    }, request=request)
    return HttpResponse(html)

# ------------------------------------------------------------------------------
# ✏️ Generate PDF
# ------------------------------------------------------------------------------
def generate_report_pdf(request, report_id):
    """Generate PDF for the finalized report."""
    
    # Buscar o relatório no banco de dados
    report = get_object_or_404(Report, id=report_id)
    patient = report.patient
    appointment = report.appointment
    measurements = ReportMeasurement.objects.filter(report=report_id)
    report_blocks = ReportBlock.objects.filter(report=report_id).exclude(content__exact='')

    # Dividir as medições
    structural_measurements = measurements[:7]  # Primeiros 7 para Parâmetros Estruturais
    ventricular_functions = measurements[7:]    # Restantes para Funções Ventriculares

    # Preencher o contexto com os dados do paciente, medições e blocos descritivos
    context = {
        "patient_name": patient.name,
        "patient_birth_date": patient.birth_date.strftime("%d/%m/%Y"),
        "patient_cpf": patient.cpf,
        "report_date": report.created_at.strftime("%d/%m/%Y"),
        "appointment_procedure": appointment.procedure,
        "appointment_health_insurance": appointment.health_insurance,
        "appointment_date": appointment.date.strftime("%d/%m/%Y"),
        "appointment_requester": appointment.requester,

        # Passando as medições divididas para o template
        "structural_measurements": structural_measurements,
        "ventricular_functions": ventricular_functions,
        
        # Blocos descritivos (que são preenchidos dinamicamente com os campos do formulário)
        "report_blocks": report_blocks,
        
        # Outros dados adicionais
        "parametros_descritivos": {},
        "final_observations": "Exame realizado com Doppler Espectral e Mapeamento de Fluxo em Cores."
    }

    # Gerar o conteúdo HTML a partir do template
    html_content = render_to_string("pdf/pdf_report_template.html", context)

    # Criar o buffer PDF
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_buffer)

    if pisa_status.err:
        return HttpResponse("Erro ao gerar o PDF", status=500)

    # Retornar o PDF como resposta HTTP
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "inline; filename=Laudo_Ecocardiografico.pdf"
    pdf_buffer.seek(0)
    response.write(pdf_buffer.read())

    return response

from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.http import HttpResponse

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def calcular_derive_htmx(request):
    if request.method == 'POST':
        altura_cm = float(request.POST.get('height') or 0)
        peso_kg = float(request.POST.get('weight') or 0)
        print("🔍 Dados recebidos via HTMX:")
        for key, value in request.POST.items():
            print(f"{key}: {value}")
        manual_values = {
        'measurement_7afa3a2b-d414-4fa0-8d82-b941f3f7db36': float(request.POST.get('diastole_final_ve') or 0),
        'measurement_c5326b50-bf6c-46f7-bbec-15748bee04c4': float(request.POST.get('sistole_final_ve') or 0),
        'measurement_690b176b-8163-4ce4-82d7-8df8e9df6050': float(request.POST.get('septo') or 0),
        'measurement_846611f4-8e53-4487-83cd-1ca680a2bd48': float(request.POST.get('parede_posterior') or 0),
        'measurement_ea1bd53d-a826-4815-972e-a2801a1b99e0': float(request.POST.get('atrio_esquerdo') or 0),
         }

        patient_values = {
            'height': float(request.POST.get('height') or 0),
            'weight': float(request.POST.get('weight') or 0),
        }

        derived = calculate_derived_measurements(manual_values, patient_values)

        # Renderizar diretamente o HTML a ser inserido na div resultado-derivado
        html = f"""
        <div id="resultado-derivado" class="col-span-12 lg:col-span-4 bg-blue-100 p-6 rounded-xl border border-blue-400 shadow-md">
        <h2 class="text-lg font-bold mb-4">🧮 Cálculos Derivados</h2>
        <div class="space-y-4 text-sm divide-y divide-blue-200">
            {"".join([
            f'''
            <div class="flex justify-between items-center pt-1">
                <span class="flex items-center gap-2 text-gray-700">{emoji} {label}</span>
                <span class="text-blue-700 font-semibold">
                {f"{derived[key]:.2f} {unit}" if derived.get(key) is not None else "--"}
                </span>
            </div>
            ''' for key, label, emoji, unit in [
                ("d8a8dbd0-c50c-42ff-b81b-e8cd2a32157f", "Volume do AE / SC", "🫀", "mL/m²"),
                ("726c5c78-1404-464b-8372-6a40128782b6", "VE(d) / SC", "📐", "mm/m²"),
                ("bc89d090-a6fb-4f59-a89c-1cc8fc56aba2", "VE(d) / Altura", "📏", ""),
                ("6db01c09-ea55-428d-a9d3-fb4c812e3b7f", "Volume Diastólico Final", "🫁", "mL"),
                ("3cb036a2-bc21-4124-b607-dc9b1b6245e0", "Volume Sistólico Final", "🫁", "mL"),
                ("facaa610-84b8-47a3-9db2-13065b31fa94", "Fração de Ejeção (Simpson)", "🔃", "%"),
                ("9c28deef-78d5-47aa-9fd2-218fbccb1eeb", "Fração de Ejeção (Teicholz)", "🫀", "%"),
                ("96f07bcc-8336-434a-8e1c-12d57e9b822a", "Encurtamento Cavidade", "📉", "%"),
                ("70d430a4-23a9-4690-8523-31a693bc4ec5", "Massa Ventricular Esquerda", "⚖️", "g"),
                ("f391f7ed-f21c-4d79-a51a-766262958d57", "MVE / SC", "📐", "g/m²"),
                ("fb0db8fa-9976-4b31-ae04-23277d07d67c", "MVE / Altura", "📏", "g/m"),
                ("84540bfa-2749-4e9c-bec1-f7689616caac", "Espessura Relativa das Paredes", "🧱", ""),
                ("c1e484a6-4441-4126-98e3-0b00dd90236b", "ERP / MVE indexada", "📊", ""),
            ]
            ])}
        </div>
        </div>

        """

        return HttpResponse(html)
    else:
        return HttpResponse("Método não suportado", status=405)