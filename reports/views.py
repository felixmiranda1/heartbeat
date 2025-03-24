from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from reports.models import Report, ReportMeasurement, MeasurementType
from accounts.models import Patient, Appointment
import uuid
from decimal import Decimal
from reports.forms import PatientForm, AppointmentForm, ReportMeasurementForm


def create_report(request):
    if request.method == 'POST':
        patient_form = PatientForm(request.POST)
        appointment_form = AppointmentForm(request.POST)
        measurement_form = ReportMeasurementForm(request.POST)

        if patient_form.is_valid() and appointment_form.is_valid() and measurement_form.is_valid():
            # ✅ Obtém as medidas preenchidas pelo Dr. no form manual
            manual_values = measurement_form.cleaned_data

            # ✅ Calcula os valores derivados com base nas medidas preenchidas
            derived_values = calculate_derived_measurements_from_form(manual_values)

            # ✅ Cria e salva o Patient
            patient = patient_form.save(commit=False)
            patient.id = uuid.uuid4()
            patient.created_at = timezone.now()
            patient.updated_at = timezone.now()
            patient.save()

            # ✅ Cria e salva o Appointment
            appointment = appointment_form.save(commit=False)
            appointment.id = uuid.uuid4()
            appointment.patient = patient
            appointment.created_at = timezone.now()
            appointment.updated_at = timezone.now()
            appointment.save()

            # ✅ Cria e salva o Report
            report = Report.objects.create(
                id=uuid.uuid4(),
                appointment=appointment,
                patient=patient,
                status='draft',
                created_at=timezone.now(),
                updated_at=timezone.now()
            )

            # ✅ Salva as medições manuais vinculadas ao Report
            measurement_form.report = report
            measurement_form.save()

            # ✅ Salva diretamente as medidas calculadas no banco
            for measurement_type_id, value in derived_values.items():
                measurement_type = MeasurementType.objects.get(id=measurement_type_id)

                ReportMeasurement.objects.update_or_create(
                    report=report,
                    measurement_type=measurement_type,
                    defaults={
                        'value': value,
                        'updated_at': timezone.now()
                    }
                )

            messages.success(request, "Medições salvas com sucesso.")
            return redirect('reports:create_report')

        else:
            messages.error(request, "Por favor, corrija os erros no formulário.")

        # Se houver erro nos forms, renderiza novamente o report.html com os forms preenchidos e erros
        context = {
            'patient_form': patient_form,
            'appointment_form': appointment_form,
            'measurement_form': measurement_form,
            'section': 'new_report'
        }
        return render(request, 'reports/report.html', context)

    elif request.method == 'GET':
        # Primeiro acesso, exibe os formulários em branco
        patient_form = PatientForm()
        appointment_form = AppointmentForm(initial={'date': timezone.now()})
        measurement_form = ReportMeasurementForm()

        context = {
            'patient_form': patient_form,
            'appointment_form': appointment_form,
            'measurement_form': measurement_form,
            'section': 'new_report'
        }
        return render(request, 'reports/report.html', context)

def calculate_derived_measurements_from_form(manual_values):
    """
    Calcula os valores derivados a partir dos dados preenchidos no formulário de medições manuais.
    manual_values: dict vindo do measurement_form.cleaned_data
    Retorna: dicionário {measurement_type_id: valor_calculado}
    """

    # Pegando valores manuais preenchidos no formulário
    aorta_raiz = float(manual_values.get('measurement_fc2afb5f-6110-4714-8b0d-4455696bbb10', 0))
    atrio_esquerdo = float(manual_values.get('measurement_ea1bd53d-a826-4815-972e-a2801a1b99e0', 0))
    dvd = float(manual_values.get('measurement_7051b7b6-841b-4e98-a539-3601578dcfe1', 0))
    diastole_final_ve = float(manual_values.get('measurement_7afa3a2b-d414-4fa0-8d82-b941f3f7db36', 0))
    sistole_final_ve = float(manual_values.get('measurement_c5326b50-bf6c-46f7-bbec-15748bee04c4', 0))
    septo = float(manual_values.get('measurement_690b176b-8163-4ce4-82d7-8df8e9df6050', 0))
    parede_posterior = float(manual_values.get('measurement_846611f4-8e53-4487-83cd-1ca680a2bd48', 0))

    derived_values = {}

    # Volume do Átrio Esquerdo / SC
    derived_values['d8a8dbd0-c50c-42ff-b81b-e8cd2a32157f'] = atrio_esquerdo * 0.6 if atrio_esquerdo else None

    # VE(d) / Superfície Corporal
    derived_values['726c5c78-1404-464b-8372-6a40128782b6'] = diastole_final_ve * 0.9 if diastole_final_ve else None

    # VE(d) / Altura
    derived_values['bc89d090-a6fb-4f59-a89c-1cc8fc56aba2'] = diastole_final_ve / 1.7 if diastole_final_ve else None

    # Volume Diastólico Final
    derived_values['6db01c09-ea55-428d-a9d3-fb4c812e3b7f'] = diastole_final_ve * 1.2 if diastole_final_ve else None

    # Volume Sistólico Final
    derived_values['3cb036a2-bc21-4124-b607-dc9b1b6245e0'] = sistole_final_ve * 1.2 if sistole_final_ve else None

    # Fração de Ejeção (Teicholz)
    derived_values['9c28deef-78d5-47aa-9fd2-218fbccb1eeb'] = (
        ((diastole_final_ve - sistole_final_ve) / diastole_final_ve * 100)
        if diastole_final_ve > 0 else None
    )

    # Fração de Ejeção (Simpson)
    derived_values['facaa610-84b8-47a3-9db2-13065b31fa94'] = (
        ((diastole_final_ve - sistole_final_ve) / diastole_final_ve * 100)
        if diastole_final_ve > 0 else None
    )

    # Percentual de Encurtamento Cavitário
    derived_values['96f07bcc-8336-434a-8e1c-12d57e9b822a'] = (
        ((diastole_final_ve - sistole_final_ve) / diastole_final_ve * 100)
        if diastole_final_ve > 0 else None
    )

    # Massa Ventricular Esquerda
    derived_values['70d430a4-23a9-4690-8523-31a693bc4ec5'] = (
        0.8 * (diastole_final_ve + septo + parede_posterior)**3
        if diastole_final_ve and septo and parede_posterior else None
    )

    # Massa do VE / Superfície Corporal
    derived_values['f391f7ed-f21c-4d79-a51a-766262958d57'] = (
        0.8 * (diastole_final_ve + septo + parede_posterior)**3 / 1.7
        if diastole_final_ve and septo and parede_posterior else None
    )

    # Massa do VE / Altura
    derived_values['fb0db8fa-9976-4b31-ae04-23277d07d67c'] = (
        0.8 * (diastole_final_ve + septo + parede_posterior)**3 / 1.7
        if diastole_final_ve and septo and parede_posterior else None
    )

    # Espessura Relativa das Paredes do VE
    derived_values['84540bfa-2749-4e9c-bec1-f7689616caac'] = (
        (2 * parede_posterior) / diastole_final_ve
        if parede_posterior and diastole_final_ve else None
    )

    # Relação ERP e Massa VE
    massa_ve = (
        0.8 * (diastole_final_ve + septo + parede_posterior)**3
        if diastole_final_ve and septo and parede_posterior else None
    )
    derived_values['c1e484a6-4441-4126-98e3-0b00dd90236b'] = (
        ((2 * parede_posterior) / diastole_final_ve) / massa_ve
        if parede_posterior and diastole_final_ve and massa_ve else None
    )
    return derived_values
