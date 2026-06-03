# Imágenes vía Cloudinary (fetch mode)

Para acelerar la carga de imágenes en producción se sirven a través
de **Cloudinary** en modo *fetch*: Cloudinary descarga la imagen desde
`SITE_BASE_URL` la primera vez que se pide, la cachea en su CDN y la
sirve optimizada (`f_auto` = formato moderno como WebP/AVIF según el
navegador, `q_auto` = calidad ajustada automáticamente).

No hace falta subir imágenes manualmente ni configurar API keys.

## Configuración

Variables de entorno (en producción, ej. en Railway/Render/etc.):

```bash
CLOUDINARY_CLOUD_NAME=dxfgqsp8y         # tu cloud name
CLOUDINARY_ENABLED=true                  # activa el fetch via Cloudinary
SITE_BASE_URL=https://www.clubelmeta.co  # URL pública del sitio (sin / al final)
```

En desarrollo local (`CLOUDINARY_ENABLED=false` o no definida) las
imágenes se siguen sirviendo desde `/static/img/` normalmente.

> **Importante:** en el panel de Cloudinary asegúrate de tener habilitada
> la opción **Settings → Security → Allowed fetch domains** incluyendo
> `clubelmeta.co` (o dejarlo vacío para permitir todo).

## Uso en templates

```django
{% load cdn_tags %}

<!-- Imagen simple con f_auto + q_auto por defecto -->
<img src="{% cdn_static 'img/fondin.webp' %}" alt="...">

<!-- Con transformaciones explícitas (recorte + tamaño objetivo) -->
<img src="{% cdn_static 'img/yotas1.jpeg' transforms='c_fill,w_900,h_600,f_auto,q_auto' %}" alt="...">

<!-- Para URLs ya resueltas (ej. media/ desde BD) -->
<img src="{% cdn_url img.imagen.url transforms='c_fit,w_1200,f_auto,q_auto' %}" alt="...">
```

### Transformaciones comunes

| Transformación        | Para qué                                          |
| --------------------- | ------------------------------------------------- |
| `f_auto,q_auto`       | Default. Formato moderno + calidad automática.    |
| `c_fill,w_900,h_600`  | Recorta y rellena a 900×600 manteniendo proporción|
| `c_fit,w_1200`        | Reduce a 1200 de ancho sin recortar               |
| `e_blur:200`          | Blur (útil para placeholders)                     |
| `dpr_auto`            | Sirve resolución adecuada a la pantalla del user  |

## Templates ya migrados

- `index.html` — hero background + carrusel "Por qué elegir"
- `espacios.html` — carruseles de cards de salón + modal de detalle
- `instalaciones.html` — 3 carruseles (jardines, áreas sociales, áreas deportivas)

## Pendientes (puedes extender cuando quieras)

Los siguientes templates aún usan `{% static 'img/...' %}` directo y
pueden migrarse con la misma técnica si quieres acelerarlos también:

- `templates/deportes/*.html` (tenis, fútbol, natación, gimnasio)
- `templates/gastronomia/*.html` (menú, salones de eventos)
- `templates/mision.html` y `templates/vision.html`
- `templates/comunicados.html` (cuando las imágenes vienen de la BD,
  usar `{% cdn_url img.imagen.url %}` en lugar de `{% cdn_static %}`)

## Cómo extender a otra imagen

1. Asegúrate de tener `{% load cdn_tags %}` arriba del template.
2. Reemplaza:
   ```django
   <img src="{% static 'img/algo.jpg' %}" alt="...">
   ```
   por:
   ```django
   <img src="{% cdn_static 'img/algo.jpg' transforms='c_fill,w_900,h_600,f_auto,q_auto' %}" alt="..." loading="lazy" decoding="async">
   ```
3. Listo. En dev seguirá sirviendo desde `/static/`, en producción
   pasará por Cloudinary.

## Desactivar Cloudinary en producción

Si necesitas volver a servir desde el origen (debugging, problema con
Cloudinary, costos, etc.), basta con poner `CLOUDINARY_ENABLED=false`
en las env vars y redeploy. Los templates seguirán funcionando con la
URL estática original.
