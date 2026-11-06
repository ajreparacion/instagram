#!/usr/bin/env python3
"""Busca fotos REALES con licencia libre en Wikimedia Commons para los reels (modo "humano").

Lo lanza .github/workflows/imagenes.yml (en GitHub Actions sí hay acceso a Commons; desde la nube
de los agentes no). Lee equipo/busqueda_imagenes.json:
    {"tema": ["consulta 1", "consulta 2", ...], ...}
y escribe para cada tema:
  - equipo/imagenes_candidatas/<tema>.json: candidatos numerados con URL lista para guion.json
    (miniatura de 1080 px de ancho de upload.wikimedia.org), licencia, autor y crédito ya redactado.
  - /tmp/imagenes/<tema>.jpg: hoja de contactos numerada (se sube a la release "pruebas") para que
    Calidad, Creador y Remasterizador vean las fotos antes de elegir.
Solo acepta dominio público, CC0 y CC BY (nunca BY-SA, NC, ND ni «uso legítimo»).
Creado por Calidad el 6/11/2026 (petición 2 de equipo/mejoras.md), con autorización total del usuario.
"""
import io, json, os, re, sys, time, html, urllib.parse, urllib.request

from PIL import Image, ImageDraw, ImageFont

API = "https://commons.wikimedia.org/w/api.php"
UA = "ExpedientesImposibles-buscador/1.0 (https://github.com/ajreparacion/instagram; reels con fuentes)"
ENTRADA = "equipo/busqueda_imagenes.json"
SALIDA = "equipo/imagenes_candidatas"
HOJAS = "/tmp/imagenes"
ACEPTADAS = re.compile(r"^(public domain|pd\b|pd-|cc0|cc[ -]by[ -]?\d|cc[ -]by$|no restrictions)", re.I)
# Sin CC BY-SA: un reel con zoom/recorte es obra derivada y la cláusula «compartir igual» no se puede cumplir en Instagram.
VETADAS = re.compile(r"(nc|nd|sa|fair use|non-free)", re.I)


def get(url, binario=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for intento in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                datos = r.read()
            return datos if binario else json.loads(datos)
        except Exception as e:
            print("  reintento", intento + 1, url[:100], e)
            time.sleep(2 + 3 * intento)
    return None


def limpio(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def buscar(consulta, n=25):
    q = {"action": "query", "format": "json", "generator": "search", "gsrnamespace": "6",
         "gsrsearch": consulta + " filetype:bitmap", "gsrlimit": str(n), "prop": "imageinfo",
         "iiprop": "url|extmetadata|size|mime", "iiurlwidth": "1080"}
    d = get(API + "?" + urllib.parse.urlencode(q))
    paginas = ((d or {}).get("query") or {}).get("pages") or {}
    out = []
    for p in sorted(paginas.values(), key=lambda x: x.get("index", 99)):
        ii = (p.get("imageinfo") or [{}])[0]
        md = ii.get("extmetadata") or {}
        lic = limpio((md.get("LicenseShortName") or {}).get("value"))
        if not lic or VETADAS.search(lic) or not ACEPTADAS.search(lic):
            continue
        if ii.get("mime") not in ("image/jpeg", "image/png", "image/tiff", "image/webp"):
            continue
        if min(ii.get("width", 0), ii.get("height", 0)) < 500:
            continue
        autor = limpio((md.get("Artist") or {}).get("value"))[:80] or "Autor desconocido"
        out.append({
            "titulo": p.get("title"),
            "url": ii.get("thumburl") or ii.get("url"),
            "url_original": ii.get("url"),
            "pagina": ii.get("descriptionurl"),
            "licencia": lic,
            "autor": autor,
            "credito": f"{autor} · {lic} · Wikimedia Commons",
            "descripcion": limpio((md.get("ImageDescription") or {}).get("value"))[:300],
            "fecha": limpio((md.get("DateTimeOriginal") or {}).get("value"))[:40],
            "ancho": ii.get("width"), "alto": ii.get("height"),
            "consulta": consulta,
        })
    return out


def hoja(tema, cands):
    cols, tw, th = 5, 300, 300
    filas = (len(cands) + cols - 1) // cols or 1
    lienzo = Image.new("RGB", (cols * tw, filas * th), (20, 20, 20))
    d = ImageDraw.Draw(lienzo)
    try:
        f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 34)
    except Exception:
        f = ImageFont.load_default()
    for i, c in enumerate(cands):
        url = c["url"].replace("/1080px-", "/330px-") if "/1080px-" in c["url"] else c["url"]
        datos = get(url, binario=True)
        x, y = (i % cols) * tw, (i // cols) * th
        if datos:
            try:
                im = Image.open(io.BytesIO(datos)).convert("RGB")
                im.thumbnail((tw - 6, th - 6))
                lienzo.paste(im, (x + (tw - im.width) // 2, y + (th - im.height) // 2))
            except Exception as e:
                print("  miniatura ilegible", c["titulo"], e)
        d.rectangle([x, y, x + 62, y + 44], fill=(0, 0, 0))
        d.text((x + 6, y + 4), str(c["n"]), font=f, fill=(255, 212, 0))
    os.makedirs(HOJAS, exist_ok=True)
    lienzo.save(os.path.join(HOJAS, "imagenes_" + tema + ".jpg"), quality=82)


def main():
    temas = json.load(open(ENTRADA, encoding="utf-8"))
    os.makedirs(SALIDA, exist_ok=True)
    solo = sys.argv[1:]
    for tema, consultas in temas.items():
        if tema.startswith("_") or (solo and tema not in solo):
            continue
        print("==", tema)
        vistos, cands = set(), []
        for q in consultas:
            for c in buscar(q):
                if c["titulo"] in vistos:
                    continue
                vistos.add(c["titulo"]); cands.append(c)
            time.sleep(0.5)
        cands = cands[:40]
        for i, c in enumerate(cands, 1):
            c["n"] = i
        json.dump({"tema": tema, "fecha": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   "hoja": f"release pruebas: imagenes_{tema}.jpg", "candidatas": cands},
                  open(os.path.join(SALIDA, tema + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        hoja(tema, cands)
        print("  ", len(cands), "candidatas")


if __name__ == "__main__":
    main()
