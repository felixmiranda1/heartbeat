from django.urls import path
from reports import views


app_name = 'reports'

urlpatterns = [
    path('create/', views.create_report, name='create_report'),
    path('hx/paciente/', views.hx_paciente, name='patient_data'),
    path('hx/numerico/', views.hx_numerico, name='numeric_report'),
    path('hx/descritivo/', views.hx_descritivo, name='descriptive_report')
]
