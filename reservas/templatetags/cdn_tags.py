"""
Template tags para servir imagenes estaticas a traves de Cloudinary en
modo "fetch". En produccion Cloudinary descarga la imagen desde SITE_BASE_URL,
la cachea y la sirve por CDN con f_auto / q_auto (formato moderno + calidad
automatica), mejorando significativamente el tiempo de carga.

Uso:

    {% load cdn_tags %}
    <img src="{% cdn_static 'img/fondin.jpeg' %}" alt="...">

    # Con transformaciones extra (ej. recorte centrado a 800x600)
    <img src="{% cdn_static 'img/fondin.jpeg' transforms='c_fill,w_800,h_600' %}" alt="...">

Si CLOUDINARY_ENABLED=false (default en dev) o no hay CLOUDINARY_CLOUD_NAME,
el tag se comporta como {% static %} clasico.
"""
from django import template
from django.conf import settings
from django.templatetags.static import static
from urllib.parse import quote

register = template.Library()


def _build_cloudinary_url(absolute_url: str, transforms: str = "") -> str:
    cloud = getattr(settings, "CLOUDINARY_CLOUD_NAME", "")
    default_transforms = getattr(settings, "CLOUDINARY_DEFAULT_TRANSFORMS", "f_auto,q_auto")
    chain = transforms or default_transforms
    # Encode la URL completa (Cloudinary la espera URL-encoded en fetch mode)
    encoded = quote(absolute_url, safe="")
    return f"https://res.cloudinary.com/{cloud}/image/fetch/{chain}/{encoded}"


@register.simple_tag(takes_context=True)
def cdn_static(context, path, transforms: str = ""):
    """Devuelve una URL de Cloudinary fetch para `path` (path relativo dentro
    de STATIC), o la URL estatica clasica si Cloudinary esta desactivado.
    """
    # Resolver primero la ruta estatica
    static_path = static(path)
    cloud = getattr(settings, "CLOUDINARY_CLOUD_NAME", "")
    enabled = getattr(settings, "CLOUDINARY_ENABLED", False)
    if not (enabled and cloud):
        return static_path
    # Construir URL absoluta para Cloudinary
    if static_path.startswith("http://") or static_path.startswith("https://"):
        absolute = static_path
    else:
        request = context.get("request")
        if request is not None:
            try:
                absolute = request.build_absolute_uri(static_path)
            except Exception:
                base = getattr(settings, "SITE_BASE_URL", "")
                absolute = base + static_path
        else:
            base = getattr(settings, "SITE_BASE_URL", "")
            absolute = base + static_path
    return _build_cloudinary_url(absolute, transforms)


@register.simple_tag(takes_context=True)
def cdn_url(context, url, transforms: str = ""):
    """Variante para URLs ya construidas (ej. media/usuario, imagenes desde
    la BD con `.url`). Si Cloudinary esta desactivado devuelve la URL tal cual.
    """
    cloud = getattr(settings, "CLOUDINARY_CLOUD_NAME", "")
    enabled = getattr(settings, "CLOUDINARY_ENABLED", False)
    if not (enabled and cloud):
        return url
    if not url:
        return url
    if url.startswith("http://") or url.startswith("https://"):
        absolute = url
    else:
        request = context.get("request")
        if request is not None:
            try:
                absolute = request.build_absolute_uri(url)
            except Exception:
                base = getattr(settings, "SITE_BASE_URL", "")
                absolute = base + url
        else:
            base = getattr(settings, "SITE_BASE_URL", "")
            absolute = base + url
    return _build_cloudinary_url(absolute, transforms)
