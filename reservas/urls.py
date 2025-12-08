from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'reservas'

urlpatterns = [
    path('', views.index, name='index'),
    path('espacios/', views.espacios, name='espacios'),
    path('register/', views.register, name='register'),
    path('check-availability/', views.check_availability, name='check_availability'),
    path('get-bloqueos-salon/', views.get_bloqueos_salon, name='get_bloqueos_salon'),
    path('preguntas-frecuentes/', views.preguntas_frecuentes, name='preguntas_frecuentes'),
    path('politicas/', views.politicas, name='politicas'),
    path('validate-socio-code/', views.validate_socio_code, name='validate_socio_code'),
    # Calendario
    path('calendario/', views.calendario, name='calendario'),
    path('get-calendar-events/', views.get_calendar_events, name='get_calendar_events'),
    # Panel de reservas personalizado (evita conflicto con /admin de Django)
    path('panel/', views.admin, name='panel'),
    path('reportes/', views.reportes_dashboard, name='reportes'),
    path('borrar_reservas/', views.borrar_reservas, name='borrar_reservas'),
    path('borrar_reserva/<int:reserva_id>/', views.borrar_reserva_individual, name='borrar_reserva_individual'),
    path('export_csv/', views.export_reservas_csv, name='export_csv'),
    # Auth
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
]
