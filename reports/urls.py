from django.urls import path
from reports import views

app_name = 'reports'

urlpatterns = [
    path('create/', views.create_report, name='create_report'),
]