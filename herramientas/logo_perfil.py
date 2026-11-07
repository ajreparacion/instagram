"""Genera la foto de perfil de Instagram de Neogest Lab desde el logo oficial."""
import urllib.request, io
from PIL import Image, ImageFilter
URL = "https://media.base44.com/images/public/6ae5244d4e2b32702f0a3cd6/c25965060_neogest-lab-logo.webp"
im = Image.open(io.BytesIO(urllib.request.urlopen(URL).read())).convert("RGB")
k = 1100 / 1408; L, T, S = round(567*k), round(192*k), round(335*k)  # recorte del símbolo NL (marca-kit)
cx, cy = L + S/2, T + S/2; side = round(S/0.72)
x0 = max(0, min(round(cx-side/2), im.width-side)); y0 = max(0, min(round(cy-side/2), im.height-side))
c = im.crop((x0, y0, x0+side, y0+side)).resize((1080, 1080), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 60, 2))
c.save("equipo/perfil_kit/perfil_neogest_lab_1080.jpg", quality=95)
im.save("equipo/perfil_kit/logo_neogest_lab_oficial.png")
print("ok", im.size)
