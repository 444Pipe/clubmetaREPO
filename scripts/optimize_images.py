"""Convert heavy PNG/JPEG images to WebP and shrink the favicon.

Run once from the project root:
    python scripts/optimize_images.py
"""
from PIL import Image
from pathlib import Path

IMG_DIR = Path(__file__).resolve().parent.parent / "static" / "img"

# (source, webp_quality)
TO_WEBP = [
    ("carru2.png", 82),
    ("carru3.png", 82),
    ("carru4.png", 82),
    ("carru5.png", 82),
    ("logo.png",   90),  # also refresh logo.webp at higher quality
    ("fondo.jpg",  82),
    ("porque.jpg", 82),
    ("fondin.jpeg",82),
]

def to_webp(src_name, quality):
    src = IMG_DIR / src_name
    if not src.exists():
        print(f"SKIP (missing): {src_name}")
        return
    dst = src.with_suffix(".webp")
    img = Image.open(src)
    save_kwargs = {"quality": quality, "method": 6}
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        save_kwargs["lossless"] = False
    else:
        img = img.convert("RGB")
    img.save(dst, "WEBP", **save_kwargs)
    s_kb = src.stat().st_size / 1024
    d_kb = dst.stat().st_size / 1024
    pct = (1 - d_kb / s_kb) * 100 if s_kb else 0
    print(f"{src_name:>20} {s_kb:7.0f} KB -> {dst.name:>20} {d_kb:7.0f} KB  (-{pct:.0f}%)")

def shrink_favicon():
    src = IMG_DIR / "faviconlogo.png"
    if not src.exists():
        return
    img = Image.open(src)
    img.thumbnail((64, 64), Image.LANCZOS)
    img.save(src, "PNG", optimize=True)
    print(f"favicon shrunk to {src.stat().st_size/1024:.0f} KB ({img.size[0]}x{img.size[1]})")

if __name__ == "__main__":
    for name, q in TO_WEBP:
        to_webp(name, q)
    shrink_favicon()
