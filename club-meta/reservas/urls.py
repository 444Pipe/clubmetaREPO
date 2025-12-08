from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from . import views

app_name = 'reservas'

urlpatterns = [
    path('', views.index, name='index'),
    path('espacios/', views.espacios, name='espacios'),
    path('register/', views.register, name='register'),
    path('check-availability/', views.check_availability, name='check_availability'),
    path('get-bloqueos-salon/', views.get_bloqueos_salon, name='get_bloqueos_salon'),
    # Simple static pages: preguntas frecuentes and politicas
    path('preguntas-frecuentes/', TemplateView.as_view(template_name='preguntas_frecuentes.html'), name='preguntas_frecuentes'),
    path('politicas/', TemplateView.as_view(template_name='politicas.html'), name='politicas'),
    # Panel de reservas personalizado (evita conflicto con /admin de Django)
    path('panel/', views.admin, name='panel'),
    path('reportes/', views.reportes_dashboard, name='reportes'),
    path('borrar_reservas/', views.borrar_reservas, name='borrar_reservas'),
    path('export_csv/', views.export_reservas_csv, name='export_csv'),
    # Auth
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
]
