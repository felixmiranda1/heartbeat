from django.db import models
import uuid

# Usuário do sistema
class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    cpf = models.CharField(max_length=11, unique=True)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'heartbeat"."user'
        managed = False

    def __str__(self):
        return self.name


# Paciente
class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    birth_date = models.DateField()
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    social_name = models.CharField(max_length=255, null=True, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    cpf = models.CharField(max_length=11, null=True, blank=True)
    contact = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'heartbeat"."patient'
        managed = False

    def __str__(self):
        return self.name


# Agendamento / Atendimento
class Appointment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateTimeField()
    professional = models.CharField(max_length=255, null=True, blank=True)
    procedure = models.CharField(max_length=255, null=True, blank=True)
    health_insurance = models.CharField(max_length=255, null=True, blank=True)
    insurance_plan = models.CharField(max_length=255, null=True, blank=True)
    external_guide_number = models.CharField(max_length=50, null=True, blank=True)
    registration_number = models.CharField(max_length=50, null=True, blank=True)
    requester = models.CharField(max_length=255, null=True, blank=True)
    observations = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'heartbeat"."appointment'
        managed = False

    def __str__(self):
        return f"{self.patient.name} - {self.procedure} - {self.date}"