"""
Template tag que devuelve un SVG inline representando esquemáticamente cada
tipo de montaje (auditorio, banquete, escuela, mesa en U, etc).

Reemplaza las imágenes estáticas: el ícono se genera dinámicamente a partir
del código del tipo de configuración (ConfiguracionSalon.TIPO_CONFIGURACION_CHOICES).
"""
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


# Paleta: navy primario, dorado acento, fondo translúcido
NAVY = "#1e3a8a"
NAVY_DARK = "#0c2a5e"
GOLD = "#d97706"
INK = "#475569"


def _svg(content, viewbox="0 0 64 64"):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}" '
        f'aria-hidden="true" focusable="false" class="montaje-svg">'
        f'{content}</svg>'
    )


def _auditorio():
    """Filas de sillas frente a una tarima/pantalla."""
    seats = []
    rows = [(24, [16, 22, 28, 34, 40, 46, 52]),
            (32, [16, 22, 28, 34, 40, 46, 52]),
            (40, [16, 22, 28, 34, 40, 46, 52]),
            (48, [16, 22, 28, 34, 40, 46, 52])]
    for cy, xs in rows:
        for cx in xs:
            seats.append(f'<circle cx="{cx}" cy="{cy}" r="2" fill="{NAVY}"/>')
    stage = f'<rect x="14" y="12" width="40" height="4" rx="2" fill="{GOLD}"/>'
    return _svg(stage + "".join(seats))


def _escuela():
    """Filas de mesas rectangulares con sillas detrás."""
    parts = []
    parts.append(f'<rect x="14" y="10" width="40" height="3" rx="1.5" fill="{GOLD}"/>')
    for i, y in enumerate([22, 36, 50]):
        # Mesas (rectángulo largo)
        parts.append(f'<rect x="14" y="{y-2}" width="36" height="5" rx="1.5" fill="{NAVY}" opacity="0.85"/>')
        # Sillas detrás (círculos)
        for cx in [20, 28, 36, 44]:
            parts.append(f'<circle cx="{cx}" cy="{y+8}" r="1.8" fill="{NAVY}"/>')
    return _svg("".join(parts))


def _banquete():
    """Mesas redondas con sillas alrededor (vista de planta)."""
    tables = [(20, 20), (44, 20), (20, 44), (44, 44)]
    parts = []
    for cx, cy in tables:
        # Mesa redonda
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="6" fill="{NAVY}" opacity="0.85"/>')
        # 8 sillas alrededor (puntos en círculo)
        for k in range(8):
            import math
            ang = (k / 8.0) * 6.2832
            sx = cx + 10 * math.cos(ang)
            sy = cy + 10 * math.sin(ang)
            parts.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="1.6" fill="{GOLD}"/>')
    return _svg("".join(parts))


def _mesa_u():
    """Mesa en forma de U con sillas en el exterior."""
    parts = []
    # U: tres rectángulos formando la U
    parts.append(f'<path d="M14 14 L14 50 L24 50 L24 24 L40 24 L40 50 L50 50 L50 14 Z" '
                 f'fill="{NAVY}" opacity="0.85"/>')
    # Sillas en el exterior (puntos)
    for cx, cy in [(10, 18), (10, 26), (10, 34), (10, 42), (10, 50),
                   (54, 18), (54, 26), (54, 34), (54, 42), (54, 50),
                   (18, 10), (26, 10), (34, 10), (42, 10), (50, 10)]:
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="1.8" fill="{GOLD}"/>')
    return _svg("".join(parts))


def _imperial():
    """Mesa rectangular larga (imperial) con sillas alrededor."""
    parts = []
    parts.append(f'<rect x="16" y="20" width="32" height="24" rx="2" fill="{NAVY}" opacity="0.88"/>')
    # Sillas a lo largo
    for cx in [20, 28, 36, 44]:
        parts.append(f'<circle cx="{cx}" cy="14" r="1.8" fill="{GOLD}"/>')
        parts.append(f'<circle cx="{cx}" cy="50" r="1.8" fill="{GOLD}"/>')
    for cy in [26, 34, 42]:
        parts.append(f'<circle cx="12" cy="{cy}" r="1.8" fill="{GOLD}"/>')
        parts.append(f'<circle cx="52" cy="{cy}" r="1.8" fill="{GOLD}"/>')
    return _svg("".join(parts))


def _mesa_12():
    """Una única mesa redonda grande para 12 personas."""
    parts = [f'<circle cx="32" cy="32" r="14" fill="{NAVY}" opacity="0.88"/>']
    import math
    for k in range(12):
        ang = (k / 12.0) * 6.2832
        sx = 32 + 20 * math.cos(ang)
        sy = 32 + 20 * math.sin(ang)
        parts.append(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="2" fill="{GOLD}"/>')
    return _svg("".join(parts))


def _empresarial():
    """Mesa de juntas: rectangular con sillas en los lados largos."""
    parts = []
    parts.append(f'<rect x="14" y="24" width="36" height="16" rx="3" fill="{NAVY}" opacity="0.88"/>')
    for cx in [18, 24, 30, 36, 42, 48]:
        parts.append(f'<circle cx="{cx}" cy="18" r="2" fill="{GOLD}"/>')
        parts.append(f'<circle cx="{cx}" cy="46" r="2" fill="{GOLD}"/>')
    # Sillas cabeza
    parts.append(f'<circle cx="10" cy="32" r="2" fill="{GOLD}"/>')
    parts.append(f'<circle cx="54" cy="32" r="2" fill="{GOLD}"/>')
    return _svg("".join(parts))


def _sofa():
    """Salas de estar con sofás dispuestos en lounge."""
    parts = []
    # Sofás como rectángulos redondeados con cojines
    parts.append(f'<rect x="14" y="20" width="20" height="8" rx="2" fill="{NAVY}" opacity="0.85"/>')
    parts.append(f'<rect x="36" y="20" width="14" height="8" rx="2" fill="{NAVY}" opacity="0.85"/>')
    parts.append(f'<rect x="14" y="38" width="14" height="8" rx="2" fill="{NAVY}" opacity="0.85"/>')
    parts.append(f'<rect x="30" y="38" width="20" height="8" rx="2" fill="{NAVY}" opacity="0.85"/>')
    # Mesa de centro
    parts.append(f'<circle cx="32" cy="32" r="4" fill="{GOLD}"/>')
    return _svg("".join(parts))


def _cortesia():
    """Etiqueta / regalo de cortesía."""
    parts = []
    parts.append(f'<rect x="14" y="22" width="36" height="28" rx="3" fill="{NAVY}" opacity="0.88"/>')
    # Lazo
    parts.append(f'<path d="M20 22 L32 14 L44 22" fill="none" stroke="{GOLD}" stroke-width="3" stroke-linecap="round"/>')
    parts.append(f'<circle cx="32" cy="14" r="3" fill="{GOLD}"/>')
    # Cinta vertical
    parts.append(f'<rect x="30" y="22" width="4" height="28" fill="{GOLD}"/>')
    return _svg("".join(parts))


def _generic():
    """Fallback: grid de 4 celdas."""
    parts = []
    for x in (18, 36):
        for y in (18, 36):
            parts.append(f'<rect x="{x}" y="{y}" width="10" height="10" rx="2" fill="{NAVY}" opacity="0.85"/>')
    return _svg("".join(parts))


# Mapeo desde TIPO_CONFIGURACION_CHOICES (código) a renderer
_RENDERERS = {
    'AUDITORIO': _auditorio,
    'ESCUELA': _escuela,
    'BANQUETE': _banquete,
    'MESA_U': _mesa_u,
    'IMPERIAL': _imperial,
    'MESA_12': _mesa_12,
    'EMPRESARIAL': _empresarial,
    'SOFA': _sofa,
    'CORTESIA': _cortesia,
}

# También permitimos resolver por etiqueta legible (display) por si el contexto
# solo trae el nombre humano del tipo (ej. "Mesa en U", "Auditorio")
_LABEL_TO_CODE = {
    'mesa en u': 'MESA_U',
    'u': 'MESA_U',
    'auditorio': 'AUDITORIO',
    'escuela': 'ESCUELA',
    'banquete': 'BANQUETE',
    'sofá': 'SOFA',
    'sofa': 'SOFA',
    'cortesía': 'CORTESIA',
    'cortesia': 'CORTESIA',
    'mesa de 12': 'MESA_12',
    'mesa 12': 'MESA_12',
    'imperial': 'IMPERIAL',
    'empresarial': 'EMPRESARIAL',
}


@register.simple_tag
def montaje_icon(tipo):
    """Devuelve un SVG inline para el tipo de montaje dado.

    `tipo` puede ser el código (ej. 'AUDITORIO') o la etiqueta legible
    (ej. 'Auditorio', 'Mesa en U').
    """
    if not tipo:
        return mark_safe(_generic())
    key = str(tipo).strip()
    # Primero intentar por código directo (mayúsculas)
    renderer = _RENDERERS.get(key.upper())
    if renderer is None:
        # Si no, intentar por etiqueta humana
        code = _LABEL_TO_CODE.get(key.lower())
        renderer = _RENDERERS.get(code) if code else None
    if renderer is None:
        return mark_safe(_generic())
    return mark_safe(renderer())
