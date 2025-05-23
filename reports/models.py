from django.db import models
import uuid
from accounts.models import User  # Assumindo que você tem o accounts registrado no INSTALLED_APPS

# Report (Laudo)
class Report(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment = models.ForeignKey('accounts.Appointment', on_delete=models.CASCADE)
    patient = models.ForeignKey('accounts.Patient', on_delete=models.CASCADE)
    pdf_path = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('draft', 'Draft'), ('finalized', 'Finalized')], default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'heartbeat"."report'
        managed = False

    def __str__(self):
        return f"Report for {self.patient.name} - {self.status}"

class MeasurementType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)

    UNIT_CHOICES = [
        ('mm', 'mm'),
        ('cm', 'cm'),
        ('ml', 'ml'),
        ('ml/m²', 'ml/m²'),
        ('mm/m²', 'mm/m²'),
        ('mm/m', 'mm/m'),
        ('g', 'g'),
        ('g/m²', 'g/m²'),
        ('g/m', 'g/m'),
        ('%', '%'),
        ('L/min', 'L/min'),
        ('-', '-')
    ]

    unit = models.CharField(max_length=20, choices=UNIT_CHOICES)
    is_calculated = models.BooleanField(default=False)
    reference_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reference_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'heartbeat"."measurement_type'
        managed = False

    def __str__(self):
        return self.name

# Report Measurement (Medições numéricas + derivadas)
class ReportMeasurement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey('Report', on_delete=models.CASCADE)
    measurement_type = models.ForeignKey(MeasurementType, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'heartbeat"."report_measurement'
        managed = False

    def __str__(self):
        return f"{self.measurement_type.name}: {self.value} {self.measurement_type.unit}"

# Descriptive Report Block (Bloco descritivo do laudo)
class ReportBlock(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    order_index = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'heartbeat"."report_block'
        managed = False

    def __str__(self):
        return f"{self.title}"


# Custom Option Category (categorias de atalhos personalizados)
class CustomOptionCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    order_index = models.IntegerField(default=0)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'heartbeat"."custom_option_category'
        managed = False

    def __str__(self):
        return self.name


# Custom Option (atalhos)
class CustomOption(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_ref = models.ForeignKey('CustomOptionClass', on_delete=models.CASCADE, null=True, blank=True)
    shortcut_key = models.CharField(max_length=5)
    alpha_numeric_code = models.CharField(max_length=10, null=True, blank=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'heartbeat"."custom_option'
        managed = False

    def __str__(self):
        return f"{self.shortcut_key}: {self.text}  [{self.class_ref.name if self.class_ref else 'Sem Classe'}]"


# Sync Log (controle de sincronização offline/online)
class SyncLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    entity = models.CharField(max_length=50)
    entity_id = models.UUIDField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('success', 'Success'), ('error', 'Error')])
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'heartbeat"."sync_log'
        managed = False

    def __str__(self):
        return f"{self.action} on {self.entity} - {self.status}"


# FavoriteShortcut (atalhos favoritados por usuário)
class FavoriteShortcut(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shortcut = models.ForeignKey(CustomOption, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'heartbeat"."favorite_shortcut'
        unique_together = ('user', 'shortcut')
        managed = False

    def __str__(self):
        return f"{self.user} → {self.shortcut.shortcut_key}"


# Classe de atalhos reutilizáveis
class CustomOptionClass(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'heartbeat"."custom_option_class'
        managed = False

    def __str__(self):
        return self.name


# Associação entre classes de atalhos e categorias visuais
class OptionClassCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_ref = models.ForeignKey(CustomOptionClass, on_delete=models.CASCADE)
    category = models.ForeignKey(CustomOptionCategory, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'heartbeat"."option_class_category'
        unique_together = ('class_ref', 'category')
        managed = False

    def __str__(self):
        return f"{self.class_ref.name} ↔ {self.category.name}"