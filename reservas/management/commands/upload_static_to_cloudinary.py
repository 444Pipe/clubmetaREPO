"""Sube las imagenes de static/img/ a Cloudinary con public_id = ruta
relativa sin extension. Idempotente: por defecto salta si ya existe.

Uso:
    # Configurar credenciales SOLO via env vars (NUNCA hardcodear):
    export CLOUDINARY_CLOUD_NAME=dxfgqsp8y
    export CLOUDINARY_API_KEY=xxx
    export CLOUDINARY_API_SECRET=yyy
    python manage.py upload_static_to_cloudinary

    # Opciones:
    #   --overwrite : re-sube las imagenes aunque ya existan
    #   --root=path : carpeta a procesar (default: static/img)
    #   --dry-run   : muestra que subiria sin subir
"""
import os
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif"}


class Command(BaseCommand):
    help = "Sube las imagenes de static/img/ a Cloudinary."

    def add_arguments(self, parser):
        parser.add_argument("--root", default="static/img",
                            help="Carpeta raiz a procesar (default: static/img)")
        parser.add_argument("--overwrite", action="store_true",
                            help="Re-subir aunque ya exista en Cloudinary.")
        parser.add_argument("--dry-run", action="store_true",
                            help="Solo muestra que se subiria, sin tocar Cloudinary.")
        parser.add_argument("--limit", type=int, default=0,
                            help="Subir como maximo N archivos (0 = sin limite).")
        parser.add_argument("--list", default="",
                            help="Archivo con rutas a subir (una por linea, ej. 'img/yotas1.jpeg'). "
                                 "Si se especifica, --root se ignora.")

    def handle(self, *args, **opts):
        cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME") or getattr(settings, "CLOUDINARY_CLOUD_NAME", "")
        api_key = os.environ.get("CLOUDINARY_API_KEY", "")
        api_secret = os.environ.get("CLOUDINARY_API_SECRET", "")
        if not (cloud_name and api_key and api_secret):
            raise CommandError(
                "Faltan credenciales. Configura las env vars CLOUDINARY_CLOUD_NAME, "
                "CLOUDINARY_API_KEY y CLOUDINARY_API_SECRET antes de correr el comando."
            )

        try:
            import cloudinary
            import cloudinary.uploader
            import cloudinary.api
            import cloudinary.exceptions
        except ImportError as e:
            raise CommandError(f"La libreria `cloudinary` no esta disponible: {e}")

        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True,
        )

        overwrite = opts["overwrite"]
        dry_run = opts["dry_run"]
        limit = opts["limit"]
        list_path = opts["list"]

        files = []
        if list_path:
            # Modo lista: cada linea es una ruta relativa desde static/
            list_file = Path(list_path).resolve()
            if not list_file.is_file():
                raise CommandError(f"No existe la lista {list_file}")
            static_root = Path("static").resolve()
            for line in list_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                full = static_root / line
                if full.is_file() and full.suffix.lower() in IMAGE_EXTS:
                    files.append(full)
                else:
                    self.stderr.write(self.style.WARNING(f"skip (no existe en disco): {line}"))
            self.stdout.write(self.style.SUCCESS(
                f"Cloud: {cloud_name} | Lista: {list_file.name} | overwrite={overwrite} | dry_run={dry_run}"
            ))
        else:
            root = Path(opts["root"]).resolve()
            if not root.is_dir():
                raise CommandError(f"No existe la carpeta {root}")
            base_dir = Path(settings.BASE_DIR).resolve()
            try:
                rel_root = root.relative_to(base_dir).as_posix()
            except ValueError:
                rel_root = root.name
            self.stdout.write(self.style.SUCCESS(
                f"Cloud: {cloud_name} | Carpeta: {rel_root} | overwrite={overwrite} | dry_run={dry_run}"
            ))
            for p in sorted(root.rglob("*")):
                if not p.is_file():
                    continue
                if p.suffix.lower() not in IMAGE_EXTS:
                    continue
                files.append(p)

        self.stdout.write(f"Encontrados {len(files)} archivos imagen para procesar.")

        uploaded = 0
        skipped = 0
        failed = 0
        total = len(files) if not limit else min(len(files), limit)

        for i, fpath in enumerate(files):
            if limit and uploaded + skipped + failed >= limit:
                break
            # public_id = ruta relativa desde static/, sin extension
            # ej: 'static/img/yotas1.jpeg' -> 'img/yotas1'
            try:
                rel_from_static = fpath.relative_to(Path("static").resolve()).as_posix()
            except ValueError:
                rel_from_static = fpath.relative_to(root.parent).as_posix()
            public_id = os.path.splitext(rel_from_static)[0]

            prefix = f"[{i+1}/{total}]"

            if not overwrite:
                # Chequea si ya existe; si si, salta
                try:
                    cloudinary.api.resource(public_id)
                    skipped += 1
                    self.stdout.write(f"{prefix} skip (existe): {public_id}")
                    continue
                except cloudinary.exceptions.NotFound:
                    pass
                except Exception as e:
                    self.stderr.write(self.style.WARNING(f"{prefix} chequeo existencia fallo para {public_id}: {e}"))
                    # continuamos al upload

            if dry_run:
                self.stdout.write(f"{prefix} (dry) subiria: {public_id} <- {fpath}")
                uploaded += 1
                continue

            try:
                cloudinary.uploader.upload(
                    str(fpath),
                    public_id=public_id,
                    overwrite=overwrite,
                    resource_type="image",
                    use_filename=False,
                    unique_filename=False,
                )
                uploaded += 1
                self.stdout.write(self.style.SUCCESS(f"{prefix} OK: {public_id}"))
            except Exception as e:
                failed += 1
                self.stderr.write(self.style.ERROR(f"{prefix} FAIL {public_id}: {e}"))

        self.stdout.write(self.style.SUCCESS(
            f"\nResumen: uploaded={uploaded} skipped={skipped} failed={failed}"
        ))
