"""
URL configuration for clubelmeta project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('reservas.urls')),
    # Páginas estáticas sencillas: preguntas frecuentes y políticas
    path('preguntas-frecuentes/', TemplateView.as_view(template_name='preguntas_frecuentes.html'), name='preguntas_frecuentes'),
    path('politicas/', TemplateView.as_view(template_name='politicas.html'), name='politicas'),
    # Información institucional: Visión / Misión / Instalaciones
    path('bienvenidos/vision/', TemplateView.as_view(template_name='vision.html'), name='vision'),
    path('bienvenidos/mision/', TemplateView.as_view(template_name='mision.html'), name='mision'),
    path('bienvenidos/instalaciones/', TemplateView.as_view(template_name='instalaciones.html'), name='instalaciones'),
    # Comunicados y administración
    path('estatutos/', TemplateView.as_view(template_name='estatutos.html'), name='estatutos'),
    path('comunicados/', TemplateView.as_view(template_name='comunicados.html'), name='comunicados'),
    path('junta-directiva/', TemplateView.as_view(template_name='junta_directiva.html'), name='junta_directiva'),
    path('actividades/', TemplateView.as_view(template_name='actividades.html'), name='actividades'),
    path('administracion/', TemplateView.as_view(template_name='administracion.html'), name='administracion'),
    # Deportes y subpáginas
    path('deportes/', TemplateView.as_view(template_name='deportes.html'), name='deportes'),
    path('deportes/tenis/', TemplateView.as_view(template_name='deportes/tenis.html'), name='deportes_tenis'),
    path('deportes/natacion/', TemplateView.as_view(template_name='deportes/natacion.html'), name='deportes_natacion'),
    path('deportes/futbol/', TemplateView.as_view(template_name='deportes/futbol.html'), name='deportes_futbol'),
    path('deportes/gimnasio/', TemplateView.as_view(template_name='deportes/gimnasio.html'), name='deportes_gimnasio'),
    # Gastronomía and subpages
    path('gastronomia/', TemplateView.as_view(template_name='gastronomia.html'), name='gastronomia'),
    # Redirect 'Salones de eventos' to the reservas 'espacios' page
    path('gastronomia/salones-eventos/', RedirectView.as_view(pattern_name='reservas:espacios', permanent=False), name='gastronomia_salones'),
]

# Servir archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
