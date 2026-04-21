from PIL import Image
import os

src = "static/img/logo.png"
dst = "static/img/logo.webp"

img = Image.open(src)
img.save(dst, "WEBP", quality=85, method=6)

png_size = os.path.getsize(src) / 1024
webp_size = os.path.getsize(dst) / 1024
print(f"PNG:  {png_size:.0f} KB")
print(f"WebP: {webp_size:.0f} KB")
print(f"Reduction: {(1 - webp_size/png_size)*100:.0f}%")
