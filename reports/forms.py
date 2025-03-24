from django import forms
from accounts.models import Patient, Appointment
from reports.models import MeasurementType, ReportMeasurement, ReportBlock

from django.forms import modelformset_factory


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'birth_date', 'gender', 'cpf']  # Adicione outros se quiser
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()

        name = cleaned_data.get("name")
        birth_date = cleaned_data.get("birth_date")
        gender = cleaned_data.get("gender")

        # Validação extra se algum campo obrigatório não estiver preenchido
        if not name or not birth_date or not gender:
            raise forms.ValidationError("Nome, Data de Nascimento e Gênero do paciente são obrigatórios.")

        return cleaned_data

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['date']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if not date:
            raise forms.ValidationError("A data do exame é obrigatória.")
        return date

class ReportMeasurementForm(forms.Form):
    def __init__(self, *args, **kwargs):
        # Expect a report instance to associate the measurements
        self.report = kwargs.pop('report', None)
        super().__init__(*args, **kwargs)

        # Query all manual measurements (not calculated)
        manual_measurements = MeasurementType.objects.filter(is_calculated=False).order_by('name')

        # Dynamically create a field for each measurement type
        for measurement in manual_measurements:
            field_name = f"measurement_{measurement.id}"
            self.fields[field_name] = forms.DecimalField(
                label=f"{measurement.name} ({measurement.unit})",
                required=False,
                min_value=None,
                max_value=None,
                initial=self.get_existing_value(measurement),
                widget=forms.NumberInput(attrs={'step': 0.01}),
                help_text=f"Ref: {measurement.reference_min} - {measurement.reference_max}"
            )

    def get_existing_value(self, measurement_type):
        """Check if there is an existing ReportMeasurement for this report and type."""
        if not self.report:
            return None
        try:
            report_measurement = ReportMeasurement.objects.get(
                report=self.report,
                measurement_type=measurement_type
            )
            return report_measurement.value
        except ReportMeasurement.DoesNotExist:
            return None

    def save(self):
        if not self.report:
            raise ValueError("Report instance is required to save measurements.")

        for field_name, value in self.cleaned_data.items():
            if value is None:
                continue
            # Extract the measurement_type_id from the field_name
            measurement_type_id = field_name.replace("measurement_", "")
            measurement_type = MeasurementType.objects.get(id=measurement_type_id)

            # Update or create the ReportMeasurement record
            ReportMeasurement.objects.update_or_create(
                report=self.report,
                measurement_type=measurement_type,
                defaults={'value': value}
            )

ReportBlockFormSet = modelformset_factory(
    ReportBlock,
    fields=('content',),
    extra=0,
    widgets={
        'content': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
    }
)