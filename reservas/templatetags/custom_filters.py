from django import template

register = template.Library()

@register.filter(name='format_price')
def format_price(value):
    """
    Formatea un número como precio colombiano con separadores de miles (puntos)
    Ejemplo: 1200000 -> $1.200.000 COP
    """
    try:
        value = int(value)
        # Convertir a string y agregar puntos manualmente
        value_str = str(value)
        # Invertir el string para trabajar de derecha a izquierda
        reversed_str = value_str[::-1]
        # Agregar puntos cada 3 dígitos
        groups = [reversed_str[i:i+3] for i in range(0, len(reversed_str), 3)]
        # Unir con puntos y volver a invertir
        formatted = '.'.join(groups)[::-1]
        return f"${formatted} COP"
    except (ValueError, TypeError):
        return value
