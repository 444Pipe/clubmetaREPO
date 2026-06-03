# Imágenes vía Cloudinary (upload mode)

Las imágenes del sitio están subidas a Cloudinary y se sirven desde su
CDN con `f_auto` (formato moderno por navegador: WebP/AVIF/etc.) y
`q_auto` (calidad automática). Esto reduce significativamente el peso
de las imágenes y el tiempo de carga.

**Cloud name**: `dxfgqsp8y`

## Configuración en producción

```bash
CLOUDINARY_CLOUD_NAME=dxfgqsp8y
CLOUDINARY_ENABLED=true
```

En desarrollo local, basta con dejar `CLOUDINARY_ENABLED` sin definir
(o `false`) y las imágenes se sirven desde `/static/img/` como antes.

> Las credenciales `CLOUDINARY_API_KEY` y `CLOUDINARY_API_SECRET` solo
> se necesitan para SUBIR imágenes (ver "Subir nuevas imágenes" abajo),
> no para servirlas. La app puede correr sin ellas en producción.

## Cómo funciona

El template tag `{% cdn_static %}` genera URLs con el formato:

```
https://res.cloudinary.com/dxfgqsp8y/image/upload/{transforms}/{public_id}
```

Donde `public_id` es la ruta relativa desde `static/` sin extensión
(ej. `img/yotas1` para el archivo `static/img/yotas1.jpeg`).

## Uso en templates

```django
{% load cdn_tags %}

<!-- Tag por defecto: aplica f_auto + q_auto -->
<img src="{% cdn_static 'img/fondin.webp' %}" alt="...">

<!-- Con transformaciones explícitas -->
<img src="{% cdn_static 'img/yotas1.jpeg' transforms='c_fill,w_900,h_600,f_auto,q_auto' %}"
     alt="..." loading="lazy" decoding="async">

<!-- Para una URL ya construida desde el static/ -->
<img src="{% cdn_url '/static/img/algo.png' %}" alt="...">
```

### Transformaciones comunes

| Transformación        | Para qué                                          |
| --------------------- | ------------------------------------------------- |
| `f_auto,q_auto`       | Default. Formato moderno + calidad automática.    |
| `c_fill,w_900,h_600`  | Recorta y rellena a 900×600 manteniendo proporción|
| `c_fit,w_1200`        | Reduce a 1200 de ancho sin recortar               |
| `dpr_auto`            | Sirve resolución adecuada a la pantalla del user  |

## Subir nuevas imágenes

Cuando agregues una imagen nueva a `static/img/`:

```bash
# Configurar credenciales SOLO via env vars (NUNCA en archivos commiteados):
export CLOUDINARY_CLOUD_NAME=dxfgqsp8y
export CLOUDINARY_API_KEY=tu-api-key
export CLOUDINARY_API_SECRET=tu-api-secret

# Subir todo lo que falte (idempotente: salta lo que ya existe):
python manage.py upload_static_to_cloudinary

# O subir solo lo de una carpeta concreta:
python manage.py upload_static_to_cloudinary --root=static/img/nueva_carpeta

# O subir desde una lista (una ruta relativa por línea):
python manage.py upload_static_to_cloudinary --list rutas.txt

# Forzar re-subida (sobreescribe):
python manage.py upload_static_to_cloudinary --overwrite

# Dry-run para ver qué se subiría sin hacerlo:
python manage.py upload_static_to_cloudinary --dry-run
```

## Templates ya migrados

- [`index.html`](templates/index.html) — hero background + carrusel "Por qué elegir"
- [`espacios.html`](templates/espacios.html) — carruseles de cards de salones + modal de detalle
- [`instalaciones.html`](templates/instalaciones.html) — 3 carruseles (jardines, áreas sociales, áreas deportivas)

## Pendientes (puedes extender cuando quieras)

Estos templates aún usan `{% static 'img/...' %}` directo. Para migrarlos
basta con agregar `{% load cdn_tags %}` y reemplazar `static` por
`cdn_static`:

- `templates/deportes/*.html` (tenis, fútbol, natación, gimnasio) — ya
  subidas a Cloudinary, solo falta actualizar los tags.
- `templates/gastronomia/nuestro_menu.html` — imágenes del menú ya
  subidas.
- `templates/mision.html`, `templates/vision.html`

## Desactivar Cloudinary

Si necesitas volver a servir desde el origen (debugging, etc.), pon
`CLOUDINARY_ENABLED=false` en las env vars y redeploy. Los templates
seguirán funcionando con la URL estática original.

## Seguridad

- **NUNCA** commitear `CLOUDINARY_API_KEY` ni `CLOUDINARY_API_SECRET`.
  Pasarlas SOLO por env vars en el hosting.
- Si las credenciales se exponen accidentalmente, ir a Cloudinary →
  Settings → Access Keys → "Generate New" para rotar el secret.
