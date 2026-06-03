"""
Template tags para servir imagenes a traves de Cloudinary en modo "upload".

Las imagenes se subieron una vez con `manage.py upload_static_to_cloudinary`
y se sirven desde Cloudinary CDN. public_id = ruta relativa sin extension.
URL: https://res.cloudinary.com/{cloud}/image/upload/{transforms}/{public_id}

Uso:

    {% load cdn_tags %}
    <img src="{% cdn_static 'img/fondin.webp' %}" alt="...">

    # Con transformaciones extra (ej. recorte centrado a 800x600)
    <img src="{% cdn_static 'img/fondin.webp' transforms='c_fill,w_800,h_600' %}" alt="...">

Si CLOUDINARY_ENABLED=false (default en dev) o no hay CLOUDINARY_CLOUD_NAME,
el tag cae a la URL estatica clasica.
"""
import os
from django import template
from django.conf import settings
from django.templatetags.static import static
from urllib.parse import quote

register = template.Library()


def _strip_static_prefix(path: str) -> str:
    """Quita un prefijo '/static/' inicial si lo hay."""
    static_url = getattr(settings, "STATIC_URL", "/static/")
    if static_url and path.startswith(static_url):
        return path[len(static_url):]
    if path.startswith("/static/"):
        return path[len("/static/"):]
    return path.lstrip("/")


def _public_id_from_path(path: str) -> str:
    """De 'img/yotas1.jpeg' -> 'img/yotas1' (sin extension).
    public_id se url-encoded por componente para tolerar espacios."""
    no_ext = os.path.splitext(path)[0]
    # URL-encode preservando los slashes que separan carpetas
    parts = [quote(seg, safe="") for seg in no_ext.split("/")]
    return "/".join(parts)


def _cloudinary_upload_url(public_id: str, transforms: str) -> str:
    cloud = getattr(settings, "CLOUDINARY_CLOUD_NAME", "")
    default_transforms = getattr(settings, "CLOUDINARY_DEFAULT_TRANSFORMS", "f_auto,q_auto")
    chain = transforms or default_transforms
    return f"https://res.cloudinary.com/{cloud}/image/upload/{chain}/{public_id}"


@register.simple_tag
def cdn_static(path, transforms: str = ""):
    """Devuelve URL de Cloudinary (image/upload mode) para una imagen estatica
    ya subida, o la URL estatica clasica si Cloudinary esta desactivado.

    `path` es la ruta relativa desde static/ (ej: 'img/yotas1.jpeg').
    """
    cloud = getattr(settings, "CLOUDINARY_CLOUD_NAME", "")
    enabled = getattr(settings, "CLOUDINARY_ENABLED", False)
    if not (enabled and cloud):
        return static(path)
    public_id = _public_id_from_path(_strip_static_prefix(path))
    return _cloudinary_upload_url(public_id, transforms)


@register.simple_tag
def cdn_url(url, transforms: str = ""):
    """Compatibilidad. Para URLs ya resueltas que apunten a /static/img/.
    Si Cloudinary esta deshabilitado devuelve la URL tal cual.
    """
    cloud = getattr(settings, "CLOUDINARY_CLOUD_NAME", "")
    enabled = getattr(settings, "CLOUDINARY_ENABLED", False)
    if not (enabled and cloud) or not url:
        return url
    # Solo transformamos URLs que apunten al static local
    rel = _strip_static_prefix(url)
    if rel == url and not url.startswith("img/"):
        # URL absoluta a otro host: la dejamos como esta
        return url
    public_id = _public_id_from_path(rel)
    return _cloudinary_upload_url(public_id, transforms)
