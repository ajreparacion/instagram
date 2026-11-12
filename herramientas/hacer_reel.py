#!/usr/bin/env python3
"""Generador de reels de misterio / falso documental.
Uso: python3 hacer_reel.py guion.json salida.mp4 [--solo-locucion] [--tiempos tiempos.json] [--ensayo]
Modo "humano": fotos y CLIPS DE VIDEO reales ("imagenes": [{"video": url|ruta, "inicio": s, ...}]) con subtitulos palabra a palabra.
Solo Pillow + numpy + ffmpeg (subprocess). Fuentes: DejaVu del sistema; si hay
fuentes opcionales en ./fonts (Oswald*.ttf, SpecialElite*.ttf) se usan."""
import sys, os, re, json, math, random, shutil, subprocess, tempfile, wave, time, glob, hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
DJV = "/usr/share/fonts/truetype/dejavu/"
SAFE_L, SAFE_R, SAFE_T, SAFE_B = 70, 70, 150, 350
TEXT_CY = 1000

def find_font(cands):
    for c in cands:
        for p in ([c] if os.path.isabs(c) else glob.glob(os.path.join(HERE, "fonts", c))):
            if os.path.exists(p):
                return p
    return DJV + "DejaVuSansCondensed-Bold.ttf"

FONT_PATHS = {
    "gancho":    find_font(["Oswald*.ttf", DJV + "DejaVuSansCondensed-Bold.ttf"]),
    "archivo":   find_font([DJV + "DejaVuSansMono-Bold.ttf"]),
    "evidencia": find_font([DJV + "DejaVuSansCondensed-Bold.ttf"]),
    "giro":      find_font(["Oswald*.ttf", DJV + "DejaVuSansCondensed-Bold.ttf"]),
    "cierre":    find_font([DJV + "DejaVuSans-Bold.ttf"]),
}
_fc = {}
def font(path, size):
    k = (path, size)
    if k not in _fc:
        f = ImageFont.truetype(path, size)
        if "wght" in path.lower() or "oswald" in path.lower():
            try: f.set_variation_by_axes([700])
            except Exception: pass
        _fc[k] = f
    return _fc[k]
MONO = DJV + "DejaVuSansMono-Bold.ttf"

PAL = {  # tinte fondo, acento
    "gancho":    ((26, 12, 14), (200, 40, 40)),
    "archivo":   ((16, 20, 14), (210, 170, 70)),
    "evidencia": ((10, 18, 24), (70, 190, 210)),
    "giro":      ((24, 8, 26), (240, 50, 150)),
    "cierre":    ((10, 14, 12), (90, 220, 120)),
}
LABEL = {"gancho": "▶ INCIDENTE", "archivo": "ARCHIVO DESCLASIFICADO",
         "evidencia": "EVIDENCIA", "giro": "⚠ ANOMALÍA DETECTADA",
         "cierre": "FIN DE LA GRABACIÓN"}
CPS = {"gancho": 48, "archivo": 26, "evidencia": 30, "giro": 55, "cierre": 30}

# ---------------------------------------------------------------- fondo
def make_bg(style, rng):
    tint, acc = PAL[style]
    sw, sh = 135, 240
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
    cx = sw * (0.5 + rng.uniform(-0.1, 0.1)); cy = sh * (0.38 + rng.uniform(-0.05, 0.05))
    r = np.sqrt(((xx - cx) / sw) ** 2 + ((yy - cy) / sh) ** 2)
    glow = np.clip(1.15 - r * 2.0, 0.0, 1.0) ** 1.5
    vign = np.clip(1.0 - (r * 1.15) ** 2.2, 0.12, 1.0)
    base = np.array(tint, np.float32)[None, None, :]
    a = base * (0.55 + 1.3 * glow[..., None]) * vign[..., None]
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    d = ImageDraw.Draw(img, "RGBA")
    if style == "archivo":  # mapa de cuadricula
        step = rng.choice([60, 90, 120])
        ox, oy = rng.randrange(step), rng.randrange(step)
        for x in range(ox, W, step):
            d.line([(x, 0), (x, H)], fill=acc + (22,), width=2 if x // step % 4 == 0 else 1)
        for y in range(oy, H, step):
            d.line([(0, y), (W, y)], fill=acc + (22,), width=2 if y // step % 4 == 0 else 1)
    return img

# ---------------------------------------------------------------- visuales
def make_params(style, rng, visual):
    P = {"ph": rng.uniform(0, 6.28), "n": rng.randint(3, 7), "sp": rng.uniform(0.6, 1.4)}
    P["pts"] = [(rng.randint(180, 900), rng.randint(330, 720)) for _ in range(rng.randint(3, 5))]
    P["eyes"] = [(rng.randint(160, 920), rng.randint(330, 700), rng.randint(40, 90)) for _ in range(rng.randint(5, 9))]
    P["sides"] = rng.choice([3, 4, 5, 6, 8])
    P["bars"] = [rng.uniform(0, 6.28) for _ in range(34)]
    P["big_eye"] = rng.random() < 0.5
    P["coord"] = "N %d°%02d' W %d°%02d'" % (rng.randint(20, 60), rng.randint(0, 59), rng.randint(1, 9), rng.randint(0, 59))
    return P

def eye(d, cx, cy, r, t, col, ph):
    for k in range(4, 0, -1):
        rr = r * (k / 4) * (1 + 0.04 * math.sin(t * 3 + ph + k))
        d.ellipse([cx - rr, cy - rr * 0.62, cx + rr, cy + rr * 0.62], outline=col + (110,), width=3)
    p = r * 0.34 * (1 + 0.15 * math.sin(t * 5 + ph))
    ox = r * 0.18 * math.sin(t * 1.3 + ph)
    d.ellipse([cx - p + ox, cy - p, cx + p + ox, cy + p], fill=(0, 0, 0, 230), outline=col + (200,), width=3)
    d.ellipse([cx + ox - p * .4, cy - p * .6, cx + ox - p * .1, cy - p * .3], fill=(255, 255, 255, 150))

def draw_visual(style, d, t, P):
    acc = PAL[style][1]
    ph, sp = P["ph"], P["sp"]
    cx, cy = 540, 520
    if style == "gancho":
        if P["big_eye"]:
            eye(d, cx, cy, 300 + 12 * math.sin(t * 4), t, acc, ph)
        else:
            for (x, y, r) in P["eyes"][:5]:
                eye(d, x, y, r * 1.3, t, acc, x)
        for k in range(3):  # anillos de alerta
            rr = ((t * 200 * sp + k * 150) % 450) + 30
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=acc + (int(90 * (1 - rr / 480)),), width=3)
    elif style == "archivo":
        pts = P["pts"]
        for a, b in zip(pts, pts[1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy) or 1
            for s in range(0, int(L), 28):
                e = min(s + 14, L)
                d.line([(a[0] + dx * s / L, a[1] + dy * s / L), (a[0] + dx * e / L, a[1] + dy * e / L)], fill=acc + (150,), width=3)
        for i, (x, y) in enumerate(pts):
            rr = 18 + ((t * 70 + i * 25) % 70)
            d.ellipse([x - rr, y - rr, x + rr, y + rr], outline=acc + (int(200 * (1 - (rr - 18) / 70)),), width=3)
            d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=acc + (230,))
        px = cx + 340 * math.sin(t * 0.9 * sp + ph); py = cy + 180 * math.sin(t * 1.4 * sp)
        d.line([(px - 70, py), (px + 70, py)], fill=(255, 80, 70, 220), width=3)
        d.line([(px, py - 70), (px, py + 70)], fill=(255, 80, 70, 220), width=3)
        d.text((pts[0][0] + 30, pts[0][1] + 24), P["coord"], font=font(MONO, 30), fill=acc + (230,))
    elif style == "evidencia":
        sway = 18 * math.sin(t * 1.1 + ph)
        x0 = cx + sway
        d.ellipse([x0 - 60, 300, x0 + 60, 420], fill=(4, 6, 8, 255), outline=acc + (180,), width=3)
        d.polygon([(x0 - 200, 760), (x0 - 160, 480), (x0 - 60, 430), (x0 + 60, 430), (x0 + 160, 480), (x0 + 200, 760)],
                  fill=(4, 6, 8, 255), outline=acc + (180,))
        bw = 150 + 8 * math.sin(t * 6)
        L = 40
        bx0, by0, bx1, by1 = x0 - 250, 270, x0 + 250, 770
        for (ax, ay, sx, sy) in [(bx0, by0, 1, 1), (bx1, by0, -1, 1), (bx0, by1, 1, -1), (bx1, by1, -1, -1)]:
            d.line([(ax, ay), (ax + sx * L, ay)], fill=acc + (255,), width=5)
            d.line([(ax, ay), (ax, ay + sy * L)], fill=acc + (255,), width=5)
        for i, b in enumerate(P["bars"]):  # onda
            h = 12 + 55 * abs(math.sin(t * 5 + b + i * 0.4))
            x = 120 + i * 26
            d.rectangle([x, 1300 - h / 2, x + 14, 1300 + h / 2], fill=acc + (170,))
    elif style == "giro":
        n = P["sides"]
        for k in range(9):
            r = 50 + k * 26 + 8 * math.sin(t * 6 + k)
            a0 = t * (0.8 + k * 0.15) * (1 if k % 2 else -1) + ph
            poly = [(cx + r * math.cos(a0 + 6.2832 * j / n), cy + r * math.sin(a0 + 6.2832 * j / n)) for j in range(n)]
            col = acc if k % 2 else (250, 230, 60)
            d.polygon(poly, outline=col + (170,))
            d.line(poly + [poly[0]], fill=col + (170,), width=4)
        for (x, y, r) in P["eyes"][:P["n"]]:
            eye(d, x, y, r * 0.7, t * 2, (250, 230, 60), x)
    else:  # cierre
        for k in range(6):
            rr = ((t * 110 * sp + k * 70) % 440) + 20
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=acc + (int(170 * (1 - rr / 460)),), width=4)
        d.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill=acc + (220,))
        # flecha hacia abajo (hacia los comentarios)
        ay = 1320 + 14 * math.sin(t * 5)
        d.polygon([(cx - 50, ay - 30), (cx + 50, ay - 30), (cx, ay + 25)], fill=acc + (200,))

def _cifra_parts(txt):
    m = re.search(r"\d[\d.,]*", txt)
    if not m: return None
    digs = m.group(0).rstrip(".,")
    try: val = int(re.sub(r"[.,]", "", digs))
    except ValueError: return None
    sep = "." if "." in digs else ("," if "," in digs else "")
    return txt[:m.start()], val, txt[m.start() + len(digs):], sep

def draw_prueba(sc, d, t):
    """Recurso que PRUEBA el dato, dibujado por codigo: contador animado ("cifra"), linea de tiempo ("fechas")
    o lista numerada que aparece punto a punto ("lista", p. ej. recapitulacion final). True si dibujo algo."""
    acc = PAL[sc.style][1]
    if sc.cifra:
        parts = _cifra_parts(sc.cifra)
        k = min(1.0, max(0.0, (t - 0.15) / 1.3)); k = 1 - (1 - k) ** 3
        if parts:
            pre, val, post, sep = parts
            cur = int(round(val * k))
            txt_n = "{:,}".format(cur).replace(",", sep) if sep else str(cur)
            txt = pre + txt_n + post
        else:
            txt = sc.cifra
        path = FONT_PATHS["gancho"]; probe = ImageDraw.Draw(Image.new("L", (4, 4)))
        size = 230
        while size > 90 and probe.textlength(sc.cifra, font=font(path, size)) > 900: size -= 8
        f = font(path, size)
        d.text((540, 560), txt, font=f, anchor="mm", fill=(255, 255, 255, 255), stroke_width=8, stroke_fill=acc + (255,))
        if sc.unidad:
            d.text((540, 560 + size // 2 + 50), sc.unidad.upper()[:28], font=font(MONO, 50), anchor="mm",
                   fill=acc + (255,), stroke_width=4, stroke_fill=(0, 0, 0, 255))
        w = int(780 * k)  # barra de progreso del contador
        d.rectangle([150, 400, 930, 412], outline=acc + (120,), width=2)
        d.rectangle([150, 400, 150 + w, 412], fill=acc + (230,))
        return True
    if sc.fechas:
        n = len(sc.fechas); x0, x1, y = 170, 910, 650
        prog = min(1.0, max(0.0, (t - 0.1) / max(0.6, sc.dur * 0.55)))
        xe = x0 + (x1 - x0) * prog
        d.line([(x0, y), (x1, y)], fill=acc + (70,), width=6)
        d.line([(x0, y), (xe, y)], fill=acc + (255,), width=8)
        fa = font(FONT_PATHS["gancho"], 64 if n <= 3 else 54); ft = font(DJV + "DejaVuSansCondensed-Bold.ttf", 34)
        xs = [x0 + (x1 - x0) * (i / (n - 1) if n > 1 else 0.5) for i in range(n)]
        for i, fe in enumerate(sc.fechas):
            x = xs[i]; on = xe >= x - 1
            last = on and (i == n - 1 or xe < xs[i + 1] - 1)
            r = 24 if last else 15
            d.ellipse([x - r, y - r, x + r, y + r], fill=(acc + (255,)) if on else (40, 40, 40, 255),
                      outline=(255, 255, 255, 230 if on else 90), width=4)
            up = i % 2 == 0
            col = (255, 255, 255, 255) if on else (150, 150, 150, 110)
            d.text((x, y - 50 if up else y + 50), str(fe.get("anio"))[:10], font=fa, anchor="md" if up else "ma",
                   fill=col, stroke_width=5, stroke_fill=(0, 0, 0, 255))
            tx = str(fe.get("texto", "")).strip()[:20]
            if tx:
                d.text((x, y - 125 if up else y + 125), tx, font=ft, anchor="md" if up else "ma",
                       fill=(acc + (255,)) if on else (130, 130, 130, 100), stroke_width=3, stroke_fill=(0, 0, 0, 255))
        return True
    if sc.lista:
        n = len(sc.lista); ft = font(DJV + "DejaVuSansCondensed-Bold.ttf", 44); fn = font(FONT_PATHS["gancho"], 66)
        probe = ImageDraw.Draw(Image.new("L", (4, 4)))
        step = max(0.35, min(0.9, sc.dur * 0.5 / n))
        y = 505
        for i, it in enumerate(sc.lista):
            k = min(1.0, max(0.0, (t - 0.15 - i * step) / 0.2))
            words, lines, cur = it.split(), [], ""
            for wd in words:
                t2 = (cur + " " + wd).strip()
                if probe.textlength(t2, font=ft) <= 740: cur = t2
                else: lines.append(cur); cur = wd
            lines.append(cur); lines = lines[:2]
            hgt = 52 * len(lines)
            if k > 0:
                off = int((1 - k) * 60)
                d.rounded_rectangle([90 - off, y - 10, 990 - off, y + hgt + 10], 14, fill=(0, 0, 0, int(150 * k)),
                                    outline=acc + (int(200 * k),), width=3)
                d.text((150 - off, y + hgt // 2), str(i + 1), font=fn, anchor="mm", fill=acc + (int(255 * k),),
                       stroke_width=4, stroke_fill=(0, 0, 0, 255))
                for j, ln in enumerate(lines):
                    d.text((215 - off, y + 4 + 52 * j), ln, font=ft, fill=(255, 255, 255, int(255 * k)),
                           stroke_width=3, stroke_fill=(0, 0, 0, 255))
            y += hgt + 26
        return True
    return False

# ---------------------------------------------------------------- texto
def wrap_fit(text, path, maxw=W - SAFE_L - SAFE_R - 40, maxlines=3, smax=118, smin=44, estricto=0):
    """Ajusta `text` a maxlines líneas bajando la letra de smax a smin. Si aun así no cabe: con estricto=N (12/11/2026,
    petición de Calidad: el mensaje se recortaba sin avisar) sigue bajando hasta N px y, si tampoco cabe, FALLA con un
    mensaje claro; sin estricto se recorta como siempre (los modos antiguos no cambian) pero se avisa por la salida."""
    probe = ImageDraw.Draw(Image.new("L", (4, 4)))
    piso = min(smin, int(estricto)) if estricto else smin
    for size in range(smax, piso - 1, -4):
        f = font(path, size)
        words, lines, cur = text.split(), [], ""
        for w in words:
            t2 = (cur + " " + w).strip()
            if probe.textlength(t2, font=f) <= maxw: cur = t2
            else:
                if cur: lines.append(cur)
                cur = w
        lines.append(cur)
        if len(lines) <= maxlines and all(probe.textlength(l, font=f) <= maxw for l in lines):
            return f, size, lines
    if estricto:
        raise ValueError("el texto no cabe en %d líneas ni con letra de %d px (%d caracteres): acórtalo. Texto: %r" % (maxlines, piso, len(text), text[:90]))
    print("AVISO: texto recortado a %d líneas (no cabe con letra de %d px): %r" % (maxlines, smin, text[:70]))
    f = font(path, smin)
    return f, smin, lines[:maxlines]

class TextBlock:
    def __init__(self, text, style, cy=TEXT_CY):
        if style in ("gancho", "giro"): text = text.upper()
        self.style = style
        self.f, self.size, self.lines = wrap_fit(text, FONT_PATHS[style])
        self.lh = int(self.size * 1.2)
        self.total = len(self.lines) * self.lh
        self.top = int(cy - self.total / 2)
        self.nchars = sum(len(l) for l in self.lines)
        self.cache = {}
        probe = ImageDraw.Draw(Image.new("L", (4, 4)))
        # x de cada linea COMPLETA (centrada por su caja real de tinta); el texto parcial
        # se dibuja desde esa misma x, asi crece hacia la derecha sin saltos.
        bbs = [probe.textbbox((0, 0), l, font=self.f) for l in self.lines]
        self.xs = [int(round((W - (b[2] - b[0])) / 2 - b[0])) for b in bbs]
        self.xl = min(x + b[0] for x, b in zip(self.xs, bbs)) - 28
        self.xr = max(x + b[2] for x, b in zip(self.xs, bbs)) + 28
    def get(self, n):
        n = min(n, self.nchars)
        if n in self.cache: return self.cache[n]
        pad = 30
        y0 = self.top - 90; hh = self.total + 90 + pad
        im = Image.new("RGBA", (W, hh), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle([self.xl, 80, self.xr, hh - 10], 18, fill=(0, 0, 0, 150))
        acc = PAL[self.style][1]
        d.text((W // 2, 14), LABEL[self.style], anchor="ma", font=font(MONO, 34), fill=acc + (255,), stroke_width=3, stroke_fill=(0, 0, 0, 255))
        left = n
        for l, x, i in zip(self.lines, self.xs, range(len(self.lines))):
            part = l[:max(0, left)]; left -= len(l)
            if part:
                d.text((x, 90 + i * self.lh), part, font=self.f, fill=(255, 255, 255, 255), stroke_width=max(6, self.size // 14), stroke_fill=(0, 0, 0, 255))
            if left <= 0: break
        self.cache[n] = (im, y0)
        return self.cache[n]


# ---------------------------------------------------------------- modo "humano"
# "modo": "humano" en guion.json (INSTRUCCIONES_EQUIPO.md, orden del usuario del 6/11/2026: humanizar al
# maximo). Implementado por el Remasterizador el 6/11. Sin HUD (REC, CAM 02, etiquetas), sin sello
# CLASIFICADO, sin ojos/siluetas/radar, sin glitch ni lineas de escaneo. Cada escena: fotos reales
# ("imagenes": url + credito + mov) con movimiento de camara leve, o un fondo neutro si no hay fotos o
# fallan; subtitulos estilo creador PALABRA A PALABRA (grupos de 2-4 palabras, la actual en amarillo)
# tomados de "subtitulos" (si existe; para poner cifras con digitos) o de la propia "voz"; en el gancho,
# el texto entero desde el primer fotograma; "texto" en las demas escenas = rotulo corto fijo arriba.
# Musica discreta (-31 LUFS antes de la voz), sin lecho de tension, sin golpes ni subidas.
# Con "modo" ausente o distinto, todo se comporta exactamente como antes.
MASTER_DATOS = [False]   # modo datos sin ninguna voz: make_audio masteriza a -14 LUFS (ver make_audio)
MODO = {"humano": False, "dibujo": False, "app": False, "sketch": False, "datos": False}

def _sk():
    """Modulo sketch.py (serie «El Jambo que sabe y las IAs»), enchufado a este modulo."""
    import sketch
    sketch.bind(sys.modules[__name__])
    return sketch

def _dt():
    """Modulo datos.py (reels explicativos con datos verificados y graficos animados), enchufado a este modulo."""
    import datos
    datos.bind(sys.modules[__name__])
    return datos
SEMILLA = {"v": 1}

def modo_suave():
    """Modos sin HUD ni tension (humano y dibujo): musica discreta, sin bombo ni golpes."""
    return MODO["humano"] or MODO["dibujo"] or MODO["app"] or MODO["sketch"] or MODO["datos"]

def modo_alegre():
    """Musica mayor y viva (dibujo y app)."""
    return MODO["dibujo"] or MODO["app"] or MODO["sketch"]
AMARILLO = (255, 212, 0)
WPS_HUMANO = 2.6          # palabras por segundo de la voz (misma cifra que usa main() para la duracion minima)
CACHE_IMG = os.path.expanduser("~/.cache/expedientes/imagenes")
FUENTE_SUB = DJV + "DejaVuSans-Bold.ttf"

ULTIMAS_FOTOS = {"fotos": None}   # fotos de la ultima escena con foto real (respaldo si una descarga falla)

def url_miniatura_commons(url, ancho=1280):
    """Para un original de upload.wikimedia.org/wikipedia/commons/a/ab/Nombre.ext devuelve la miniatura de 1280 px
    (mucho mas ligera; los originales de Commons pueden pasar de 40 MB y fallar o tardar). None si no aplica."""
    m = re.match(r"^(https?://upload\.wikimedia\.org/wikipedia/commons)/([0-9a-f])/([0-9a-f]{2})/([^/?#]+)$", url)
    if not m: return None
    base, a, ab, nombre = m.groups()
    sufijo = ".png" if nombre.lower().endswith((".svg", ".tif", ".tiff", ".pdf", ".webp", ".gif")) else ""
    return f"{base}/thumb/{a}/{ab}/{nombre}/{ancho}px-{nombre}{sufijo}"

def descargar_imagen(url):
    """Descarga (con cache) una foto de dominio publico / licencia libre. None si falla: no se cae el render.
    Reintenta 3 veces (1 s, 3 s) y, si el original de Commons falla o pesa mas de 40 MB, prueba su miniatura
    de 1280 px (peticion de Calidad, 6/11/2026: dos escenas salieron en negro por una descarga fallida)."""
    if not url: return None
    os.makedirs(CACHE_IMG, exist_ok=True)
    dst = os.path.join(CACHE_IMG, hashlib.md5(url.encode()).hexdigest() + ".img")
    if not os.path.exists(dst) or os.path.getsize(dst) < 1000:
        import urllib.request
        candidatas = [url] + ([url_miniatura_commons(url)] if url_miniatura_commons(url) else [])
        ok = False
        for cand in candidatas:
            for intento, espera in enumerate((0, 1, 3)):
                if espera: time.sleep(espera)
                try:
                    req = urllib.request.Request(cand, headers={"User-Agent": "ExpedientesImposibles-render/1.0 (reel de dominio publico; contacto: github.com/ajreparacion/instagram)"})
                    with urllib.request.urlopen(req, timeout=25) as r, open(dst + ".part", "wb") as fh:
                        datos = r.read(40 * 1024 * 1024 + 1)
                        if len(datos) > 40 * 1024 * 1024:
                            raise ValueError("mas de 40 MB")
                        fh.write(datos)
                    os.replace(dst + ".part", dst); ok = True; break
                except Exception as e:
                    print("imagen no descargada (intento %d):" % (intento + 1), cand[:90], "->", str(e)[:120])
            if ok: break
        if not ok: return None
    try:
        im = Image.open(dst); im.load()
        return im.convert("RGB")
    except Exception as e:
        print("imagen ilegible:", url[:90], "->", str(e)[:120])
        try: os.remove(dst)
        except OSError: pass
        return None

def preparar_foto(im, zoom_max=1.10):
    """Devuelve una imagen algo mayor que el lienzo (para zoom/paneo) que llena 1080x1920 sin bandas.
    Las fotos muy apaisadas van sobre si mismas desenfocadas y oscurecidas (como en los reels de creadores)."""
    tw, th = int(W * zoom_max) + 2, int(H * zoom_max) + 2
    w, h = im.size
    if w / h < 0.62 * 1.25:   # bastante vertical o cuadrada: llenar y recortar
        s = max(tw / w, th / h)
        im2 = im.resize((max(tw, int(w * s + 1)), max(th, int(h * s + 1))), Image.LANCZOS)
        x0 = (im2.width - tw) // 2; y0 = (im2.height - th) // 2
        return im2.crop((x0, y0, x0 + tw, y0 + th))
    bg = im.resize((tw, th), Image.BILINEAR).filter(ImageFilter.GaussianBlur(28))
    bg = Image.eval(bg, lambda v: int(v * 0.45))
    fw = tw; fh = int(h * fw / w)
    fg = im.resize((fw, fh), Image.LANCZOS)
    bg.paste(fg, (0, (th - fh) // 2))
    return bg

CACHE_VID = os.path.expanduser("~/.cache/expedientes/videos")

def descargar_video(src):
    """Ruta local de un clip de video (6/11/2026, humanizar: video REAL en vez de fondos generados).
    src: URL http(s) de un video de dominio publico / licencia libre (Commons .webm/.ogv/.mp4, NASA, Pexels...),
    o una ruta local (absoluta o relativa al guion; publicar_gh.py deja ahi los reels propios del usuario).
    Con cache en ~/.cache/expedientes/videos/. None si falla: la escena sigue con sus fotos o el fondo neutro."""
    src = (src or "").strip()
    if not src: return None
    if not re.match(r"https?://", src):
        p = src if os.path.isabs(src) else os.path.join(GUION_DIR[0], src)
        return p if os.path.exists(p) and os.path.getsize(p) > 1000 else None
    os.makedirs(CACHE_VID, exist_ok=True)
    dst = os.path.join(CACHE_VID, hashlib.md5(src.encode()).hexdigest() + ".vid")
    if not os.path.exists(dst) or os.path.getsize(dst) < 1000:
        try:
            import urllib.request
            req = urllib.request.Request(src, headers={"User-Agent": "ExpedientesImposibles-render/1.0 (reel de dominio publico)"})
            with urllib.request.urlopen(req, timeout=60) as r, open(dst + ".part", "wb") as fh:
                shutil.copyfileobj(r, fh, 1 << 20)
            if os.path.getsize(dst + ".part") > 200 * 1024 * 1024:
                os.remove(dst + ".part"); print("video demasiado grande (>200 MB):", src[:90]); return None
            os.replace(dst + ".part", dst)
        except Exception as e:
            print("video no descargado:", src[:90], "->", str(e)[:120])
            return None
    return dst

def sonda_video(path):
    """(ancho, alto, duracion) con ffprobe; None si no es un video legible."""
    try:
        r = subprocess.run([shutil.which("ffprobe") or "ffprobe", "-v", "error", "-select_streams", "v:0",
                            "-show_entries", "stream=width,height:format=duration", "-of", "json", path],
                           capture_output=True, text=True, timeout=60)
        j = json.loads(r.stdout or "{}")
        st = (j.get("streams") or [{}])[0]
        return int(st["width"]), int(st["height"]), float((j.get("format") or {}).get("duration") or 0)
    except Exception as e:
        print("video ilegible:", path[-60:], "->", str(e)[:100])
        return None

class Clip:
    """Fotogramas de un clip de video ya encajados en el lienzo (algo mayor, como las fotos, para el zoom/paneo).
    Se extraen con ffmpeg a JPEG en una carpeta temporal; frame(i) devuelve el fotograma i (el ultimo si se acaba)."""
    def __init__(self, path, inicio, dur, zoom_max=1.10, velocidad=1.0, bucle=True, app=False):
        # velocidad > 1 acelera el clip (modo app: el tramo dura lo que su voz); bucle=False congela el ultimo
        # fotograma si el video se acaba; app=True encaja sin desenfoque (vertical a pantalla completa, apaisado a
        # APP_VID_W de ancho para enmarcarlo sobre papel).
        self.ok = False
        info = sonda_video(path)
        if not info or info[0] < 16 or info[1] < 16: return
        w, h, total = info
        tw, th = int(W * zoom_max) + 2, int(H * zoom_max) + 2
        if tw % 2: tw += 1
        if th % 2: th += 1
        self.size = (tw, th)
        inicio = max(0.0, float(inicio or 0))
        if total > 0.5 and inicio >= total - 0.3: inicio = 0.0
        need = dur + 0.25
        vert = w / h < 0.62 * 1.25
        if app:
            encaje = ("scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d" % (W, H, W, H)) if vert else ("scale=%d:-2" % APP_VID_W)
        else:
            encaje = ("scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d" % (tw, th, tw, th)) if vert else (
                "split[a][b];[a]scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,gblur=sigma=28,"
                "eq=brightness=-0.28[bg];[b]scale=%d:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2" % (tw, th, tw, th, tw))
        vel = max(0.25, float(velocidad or 1.0))
        ritmo = ("setpts=PTS/%.4f," % vel) if abs(vel - 1.0) > 0.001 else ""
        self.dir = tempfile.mkdtemp(prefix="clip_")
        CLIP_DIRS.append(self.dir)   # se borran al terminar (atexit)
        cmd = [FFMPEG, "-y", "-loglevel", "error"]
        if bucle and total > 0.5 and total - inicio < need * vel:   # clip corto: se repite en bucle para llenar la escena
            cmd += ["-stream_loop", "-1"]
        if app and abs(vel - 1.0) > 0.001:
            # 10/11/2026: con velocidad != 1, -ss/-t DESPUES de -i se medían tras el setpts (en tiempo ya acelerado):
            # el tramo salía desplazado (inicio*vel) o vacío si inicio > duración/vel. Antes de -i miden vídeo original.
            cmd += ["-ss", "%.3f" % inicio, "-t", "%.3f" % (need * vel), "-i", path, "-an"]
        else:
            cmd += ["-i", path, "-ss", "%.3f" % inicio, "-t", "%.3f" % (need * vel), "-an"]
        cmd += ["-filter_complex", "[0:v]" + encaje + "," + ritmo + "fps=%d,format=yuv420p[v]" % FPS, "-map", "[v]",
                "-q:v", "3", os.path.join(self.dir, "f%05d.jpg")]
        try:
            subprocess.run(cmd, check=True, timeout=600, capture_output=True)
        except Exception as e:
            print("clip no extraido:", path[-60:], "->", str(getattr(e, 'stderr', b'') or e)[-160:])
            return
        self.files = sorted(glob.glob(os.path.join(self.dir, "f*.jpg")))
        self.n = len(self.files)
        self.ok = self.n >= 2
        self.last = (None, None)
        if app and self.ok:
            self.size = Image.open(self.files[0]).size
    def frame(self, i):
        i = max(0, min(i, self.n - 1))
        if self.last[0] != i:
            im = Image.open(self.files[i]).convert("RGB")
            if im.size != self.size: im = im.resize(self.size, Image.BILINEAR)
            self.last = (i, im)
        return self.last[1]

GUION_DIR = [os.getcwd()]   # carpeta del guion (rutas relativas de "video")
CLIP_DIRS = []
import atexit
atexit.register(lambda: [shutil.rmtree(d, ignore_errors=True) for d in CLIP_DIRS])

def fondo_neutro(style, rng):
    """Fondo neutro (degradado oscuro con un foco suave) cuando una escena no lleva fotos."""
    tint = {"gancho": (24, 18, 18), "archivo": (20, 20, 18), "evidencia": (16, 19, 22),
            "giro": (26, 16, 18), "cierre": (18, 20, 18)}[style]
    sw, sh = 135, 240
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
    cx = sw * (0.5 + rng.uniform(-0.15, 0.15)); cy = sh * (0.45 + rng.uniform(-0.08, 0.08))
    r = np.sqrt(((xx - cx) / sw) ** 2 + ((yy - cy) / sh) ** 2)
    glow = np.clip(1.0 - r * 1.6, 0.0, 1.0) ** 1.3
    grad = 1.0 - 0.35 * (yy / sh)
    a = np.array(tint, np.float32)[None, None, :] * (0.7 + 1.1 * glow[..., None]) * grad[..., None]
    tw, th = int(W * 1.10) + 2, int(H * 1.10) + 2
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).resize((tw, th), Image.BICUBIC)

def trocear_subtitulos(texto, maxw=4):
    """Grupos de 2-4 palabras; corta en los signos de puntuacion para respetar las pausas de la voz."""
    palabras = texto.split()
    grupos, cur = [], []
    for w in palabras:
        cur.append(w)
        if len(cur) >= maxw or w[-1] in ".,;:!?…" or (len(cur) >= 2 and w.endswith(("—", "-"))):
            grupos.append(cur); cur = []
    if cur: grupos.append(cur)
    # un grupo de 1 palabra se une al anterior si cabe
    out = []
    for g in grupos:
        if len(g) == 1 and out and len(out[-1]) < maxw: out[-1] = out[-1] + g
        else: out.append(g)
    return out

ROJO_ENFASIS = (255, 82, 58)

def parsear_enfasis(texto):
    """'*palabra*' o '*varias palabras*' en la voz = ENFASIS (6/11/2026, peticion del usuario: falta enfasis).
    Devuelve (texto limpio para la voz, indices de las palabras enfatizadas en ese texto limpio)."""
    texto = (texto or "").strip()
    if "*" not in texto: return texto, []
    idx, out, k, dentro = [], [], 0, False
    for tok in texto.split():
        t = tok
        abre = t.startswith("*"); cierra = t.rstrip(".,;:!?…\"»)").endswith("*") or t.endswith("*")
        t = t.replace("*", "")
        if not t: continue
        if abre: dentro = True
        if dentro: idx.append(k)
        if cierra: dentro = False
        out.append(t); k += 1
    return " ".join(out), idx

class Subtitulos:
    """Subtitulos palabra a palabra: grupo actual en grande, centrado, la palabra activa en amarillo,
    las palabras con enfasis en rojo. Con 'tiempos' (inicio real de cada palabra, en s desde el principio de
    la escena) van clavados a la voz; si no, al ritmo wps estimado."""
    def __init__(self, texto, wps, delay, dur, entero=False, enfasis=(), tiempos=None, estilo=None):
        # estilo (modo dibujo): {"fill", "stroke", "activo", "enfasis", "cy", "smax", "smin"}; sin el, igual que siempre
        self.estilo = estilo or {}
        self.grupos = trocear_subtitulos(texto)
        self.n = sum(len(g) for g in self.grupos)
        self.wps, self.delay, self.dur, self.entero = wps, delay, dur, entero
        self.enfasis = set(int(i) for i in (enfasis or []))
        self.tiempos = list(tiempos) if (tiempos and len(tiempos) == self.n) else None
        self.cache = {}
        self.probe = ImageDraw.Draw(Image.new("L", (4, 4)))
        self.starts = []   # indice de la primera palabra de cada grupo
        k = 0
        for g in self.grupos: self.starts.append(k); k += len(g)
    def estado(self, t):
        """(indice de grupo, palabras visibles del grupo, palabra activa global)"""
        if self.n == 0: return None
        if self.entero:
            k = self.n
        elif self.tiempos is not None:   # tiempos reales de la voz (alineados): la palabra entra 60 ms antes de oirse
            k = sum(1 for ti in self.tiempos if ti - 0.06 <= t)
            k = max(0, min(k, self.n))
        else:
            k = int(max(0.0, t - self.delay) * self.wps) + (1 if t > self.delay else 0)
            k = max(0, min(k, self.n))
        if k == 0: return None
        gi = max(i for i, s in enumerate(self.starts) if s < k)
        return gi, k - self.starts[gi], k
    def capa(self, t):
        e = self.estado(t)
        if e is None: return None
        gi, vis, k = e
        key = (gi, vis, k) if not self.entero else ("all",)
        if key in self.cache: return self.cache[key]
        if self.entero:
            texto = " ".join(" ".join(g) for g in self.grupos)
            f, size, lines = wrap_fit(texto, FUENTE_SUB, maxw=W - SAFE_L - SAFE_R - 40, maxlines=3,
                                      smax=self.estilo.get("smax_entero", 104), smin=56)
            if self.estilo.get("gancho_2_lineas"):   # plantilla app: 2 lineas si caben a >= 56 px; si no, 3 mas pequenas para no tocar el movil
                f2, s2, l2 = wrap_fit(texto, FUENTE_SUB, maxw=W - SAFE_L - SAFE_R - 40, maxlines=2,
                                      smax=self.estilo.get("smax_entero", 104), smin=56)
                if " ".join(l2).split() == texto.split():
                    f, size, lines = f2, s2, l2
                else:
                    f, size, lines = wrap_fit(texto, FUENTE_SUB, maxw=W - SAFE_L - SAFE_R - 40, maxlines=3,
                                              smax=min(66, self.estilo.get("smax_entero", 104)), smin=48)
            activo = -1
        else:
            texto = " ".join(self.grupos[gi])
            f, size, lines = wrap_fit(texto, FUENTE_SUB, maxw=W - SAFE_L - SAFE_R - 40, maxlines=2,
                                      smax=self.estilo.get("smax", 112), smin=self.estilo.get("smin", 64))
            activo = vis - 1
            if self.estilo.get("bottom_max") and len(lines) > 1 and size > 58:   # plantilla app: 2 lineas mas pequenas para no pisar el pie
                f, size, lines = wrap_fit(texto, FUENTE_SUB, maxw=W - SAFE_L - SAFE_R - 40, maxlines=2, smax=58, smin=46)
        lh = int(size * 1.18); total = len(lines) * lh
        im = Image.new("RGBA", (W, total + 60), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        stroke = max(5, size // 12)
        c_fill = self.estilo.get("fill", (255, 255, 255)); c_stroke = self.estilo.get("stroke", (0, 0, 0))
        c_act = self.estilo.get("activo", AMARILLO); c_enf = self.estilo.get("enfasis", ROJO_ENFASIS)
        if self.estilo: stroke = max(3, size // int(self.estilo.get("grosor", 18)))
        space = self.probe.textlength(" ", font=f)
        idx = 0
        base_global = 0 if self.entero else self.starts[gi]
        for i, l in enumerate(lines):
            ws = l.split()
            widths = [self.probe.textlength(w, font=f) for w in ws]
            x = (W - (sum(widths) + space * (len(ws) - 1))) / 2
            for j, w in enumerate(ws):
                if not self.entero and idx > activo: break
                sw = stroke
                if (base_global + idx) in self.enfasis:
                    col = c_enf                   # palabra con enfasis: en rojo (tambien cuando es la activa)
                    if self.estilo.get("marca"):  # ...o, con "marca", tinta sobre un resaltado de rotulador cian
                        d.rounded_rectangle([x - 10, 30 + i * lh + size * 0.06, x + widths[j] + 10, 30 + i * lh + size * 1.1],
                                            10, fill=CIAN + (235,))
                        sw = 0
                else:
                    col = c_act if (not self.entero and idx == activo) else c_fill
                d.text((x, 30 + i * lh), w, font=f, fill=col + (255,), stroke_width=sw, stroke_fill=c_stroke + (255,))
                x += widths[j] + space; idx += 1
        cy_ef = self.estilo.get("cy", TEXT_CY)
        if self.estilo.get("bottom_max"): cy_ef = min(cy_ef, self.estilo["bottom_max"] - total / 2)   # el texto nunca baja de esa y
        self.cache[key] = (im, int(cy_ef - total / 2) - 30)
        return self.cache[key]

def rotulo_humano(texto):
    """Rotulo corto fijo arriba (p. ej. «1936 · Tasmania»), dentro de la zona segura."""
    f = font(DJV + "DejaVuSansCondensed-Bold.ttf", 46)
    probe = ImageDraw.Draw(Image.new("L", (4, 4)))
    texto = texto.strip()[:48]
    tw = probe.textlength(texto, font=f)
    im = Image.new("RGBA", (W, 110), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    x0 = int((W - tw) / 2) - 26
    d.rounded_rectangle([x0, 14, x0 + tw + 52, 96], 16, fill=(0, 0, 0, 140))
    d.text((W / 2, 55), texto, font=f, anchor="mm", fill=(255, 255, 255, 255))
    return im

def preparar_humano(sc, spec, rng):
    """Carga fotos, prepara subtitulos y movimiento de camara para una escena en modo humano."""
    sc.fotos = []
    # 1) fotos y rutas de video validas (un "video" por entrada tiene prioridad sobre su "url")
    entradas = []
    for im_spec in (spec.get("imagenes") or [])[:3]:
        if not isinstance(im_spec, dict): continue
        credito = str(im_spec.get("credito") or "").strip()
        mov = str(im_spec.get("mov") or rng.choice(["zoom_in", "zoom_out", "pan_izq", "pan_der"])).strip()
        vid = descargar_video(str(im_spec.get("video") or "")) if im_spec.get("video") else None
        if vid:
            entradas.append(("video", vid, float(im_spec.get("inicio") or 0), credito, mov)); continue
        im = descargar_imagen(str(im_spec.get("url") or "").strip())
        if im is None: continue
        entradas.append(("foto", im, 0.0, credito, mov))
    # 2) cada entrada ocupa el mismo tramo de la escena; los clips se extraen solo para ese tramo
    seg = sc.dur / max(1, len(entradas))
    for tipo, obj, inicio, credito, mov in entradas:
        if tipo == "video":
            clip = Clip(obj, inicio, seg)
            if not clip.ok: continue
            sc.fotos.append((clip, credito, mov if mov in ("zoom_in", "zoom_out", "fijo") else "fijo"))
        else:
            sc.fotos.append((preparar_foto(obj), credito, mov))
    if sc.fotos and any(not isinstance(f[0], Clip) for f in sc.fotos):
        ULTIMAS_FOTOS["fotos"] = [f for f in sc.fotos if not isinstance(f[0], Clip)]
    if not sc.fotos:
        if ULTIMAS_FOTOS["fotos"]:   # antes que un fondo neutro, se repite la foto real de la escena anterior
            prev = ULTIMAS_FOTOS["fotos"][-1]
            print("escena sin foto: se reutiliza la de la escena anterior")
            sc.fotos = [(prev[0], prev[1], rng.choice([m for m in ("zoom_in", "zoom_out", "pan_izq", "pan_der") if m != prev[2]]))]
        else:
            sc.fotos = [(fondo_neutro(sc.style, rng), "", rng.choice(["pan_izq", "pan_der", "zoom_in"]))]
    voz, enf_voz = parsear_enfasis(spec.get("voz") or "")
    sub, enf_sub = parsear_enfasis(spec.get("subtitulos") or "")
    texto, enf_txt = parsear_enfasis(spec.get("texto") or "")
    if sc.style == "gancho":
        base, enf = (texto, enf_txt) if texto else ((sub, enf_sub) if sub else (voz, enf_voz))
        sc.sub = Subtitulos(base, WPS_HUMANO, 0.0, sc.dur, entero=True, enfasis=enf)
        sc.rotulo = None
    else:
        base, enf = (sub, enf_sub) if sub else ((voz, enf_voz) if voz else (texto, enf_txt))
        dv = float(spec.get("_voz_dur") or 0)
        tiempos = spec.get("_voz_palabras")   # inicio real de cada palabra (alineacion con la voz), si existe
        if tiempos and len(tiempos) == len(base.split()):
            tiempos = [float(x) + 0.12 for x in tiempos]   # la voz se mezcla con 120 ms de retardo
        else:
            tiempos = None
        if dv > 0.2:   # duracion real de la voz (voz primero): los subtitulos van al ritmo real de la frase
            wps = len(base.split()) / max(0.3, dv - 0.1)
            retardo = 0.12   # la voz entra a los 120 ms en todas las escenas (publicar_gh.py adelay)
        else:
            wps = max(WPS_HUMANO, len(base.split()) / max(0.3, sc.dur * 0.8))
            retardo = 0.35 if sc.style == "giro" else 0.12
        sc.sub = Subtitulos(base, wps, retardo, sc.dur, enfasis=enf, tiempos=tiempos)
        sc.rotulo = rotulo_humano(texto) if (texto and base != texto) else None

def render_frame_humano(fi, sc, noise, rg):
    lf = fi - sc.start; t = lf / FPS
    nf = len(sc.fotos); seg = sc.dur / nf
    k = min(nf - 1, int(t / seg)); tk = t - k * seg
    foto, credito, mov = sc.fotos[k]
    if isinstance(foto, Clip):   # clip de video real: fotograma del tramo (el clip corre a la misma velocidad)
        foto = foto.frame(lf - int(k * seg * FPS))
    p = min(1.0, tk / max(0.5, seg))
    fw, fh = foto.size
    if mov == "zoom_in":   z = 1.0 + 0.09 * p
    elif mov == "zoom_out": z = 1.09 - 0.09 * p
    else: z = 1.045
    cw, ch = int(W * z), int(H * z)
    cw, ch = min(cw, fw), min(ch, fh)
    cx = (fw - cw) // 2; cy = (fh - ch) // 2
    if mov == "pan_izq": cx = int((fw - cw) * (1 - p))
    elif mov == "pan_der": cx = int((fw - cw) * p)
    img = foto.crop((cx, cy, cx + cw, cy + ch))
    if (cw, ch) != (W, H): img = img.resize((W, H), Image.BILINEAR)
    capa = sc.sub.capa(t)
    if capa:
        timg, ty = capa
        img.paste(timg, (0, ty), timg)
    if sc.rotulo is not None:
        img.paste(sc.rotulo, (0, 470), sc.rotulo)
    if credito:
        d = ImageDraw.Draw(img, "RGBA")
        d.text((W - SAFE_R, 1500), credito[:70], font=font(DJV + "DejaVuSans.ttf", 24), anchor="ra",
               fill=(235, 235, 235, 230), stroke_width=2, stroke_fill=(0, 0, 0, 200))
    a = np.asarray(img, dtype=np.int16).copy()
    a += noise[fi % 8] // 4            # grano leve
    if lf < 3: a += int(12 * (3 - lf))  # parpadeo minimo en el corte
    np.clip(a, 0, 255, out=a)
    return a.astype(np.uint8)

# ---------------------------------------------------------------- modo "dibujo"
# "modo": "dibujo" en guion.json (DIRECTIVA VIGENTE de INSTRUCCIONES_EQUIPO.md, 6/11/2026: IA facil con dibujos
# animados). Implementado por Mejora de produccion el 7/11/2026. Todo dibujado por codigo en CPU: papel claro con
# textura, trazo negro grueso con temblor de dibujo a mano (line boil cada 4 fotogramas), un unico acento cian.
# Personajes fijos: "bit" (robot redondo blanco, cara-pantalla cian, parpadea y mueve la boca al hablar) y "paco"
# (muneco de palo que se agobia). Por escena: "dibujo": {"personajes", "accion", "objeto", "pantalla", "invitados",
# "pizarra", "flecha", "antes_despues"} + "texto" (rotulo arriba), "cifra", "lista", "sello" y subtitulos palabra a
# palabra de la propia "voz" (palabra activa y enfasis *asi* en cian: un unico acento).
PAPEL = (248, 244, 232)
TINTA = (28, 26, 24)
CIAN = (0, 184, 217)
CIAN_CLARO = (190, 236, 244)
# 7/11 (Mejora, 2.ª sesion): letra redondeada Poppins (OFL, en ./fonts) para rotulos, pizarra, lista y paneles;
# si falta la fuente, DejaVu como antes. Los subtitulos siguen con FUENTE_SUB (legibilidad).
F_DIB = find_font(["Poppins-Bold.ttf", DJV + "DejaVuSans-Bold.ttf"])
F_DIB_C = find_font(["Poppins-Bold.ttf", DJV + "DejaVuSansCondensed-Bold.ttf"])
F_DIB_MONO = DJV + "DejaVuSansMono-Bold.ttf"
SUB_CY_DIB = 1030          # centro de la banda de subtitulos (entre el objeto y los personajes)
SUELO_DIB = 1500           # linea de suelo de los personajes
OBJ_CY_DIB = 690           # centro del area del objeto / pizarra
DIB_PREV = {"pers": set()} # personajes de la escena anterior (para la animacion de entrada)
_papel = {}

def papel_img(seed):
    """Fondo de papel claro con textura suave (fija por semilla)."""
    if seed not in _papel:
        rg = np.random.default_rng(seed + 777)
        low = Image.fromarray(np.clip(128 + rg.normal(0, 40, (H // 16, W // 16)), 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR)
        low = (np.asarray(low, dtype=np.float32) - 128) / 128 * 5.0
        fino = rg.normal(0, 2.2, (H, W)).astype(np.float32)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        vig = 1 - 0.06 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        base = np.array(PAPEL, np.float32)[None, None, :] * vig[:, :, None]
        a = base + (low + fino)[:, :, None] * np.array([1.0, 0.9, 0.7], np.float32)
        _papel[seed] = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return _papel[seed]

def _wob(rng, amp): return rng.uniform(-amp, amp)

def trazo(d, pts, rng, w=9, col=TINTA, amp=2.2, cerrado=False):
    """Polilinea a mano alzada: puntos con temblor, trazo grueso con puntas redondas."""
    p = [(x + _wob(rng, amp), y + _wob(rng, amp)) for x, y in pts]
    if cerrado: p.append(p[0])
    if len(p) >= 2: d.line(p, fill=col, width=w, joint="curve")
    r = w / 2
    for x, y in (p if len(p) <= 12 else [p[0], p[-1]]):
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)

def puntos_elipse(cx, cy, rx, ry, n=36, a0=0.0, a1=2 * math.pi):
    return [(cx + rx * math.cos(a0 + (a1 - a0) * i / n), cy + ry * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]

def circulo(d, cx, cy, r, rng, w=9, relleno=None, col=TINTA, amp=2.0, ry=None):
    ry = ry or r
    pts = puntos_elipse(cx, cy, r, ry, 40)
    if relleno is not None: d.polygon(pts, fill=relleno)
    trazo(d, pts[:-1], rng, w, col, amp, cerrado=True)

def rect_mano(d, x0, y0, x1, y1, rng, w=9, relleno=None, col=TINTA, amp=2.0, radio=0):
    if radio > 0:
        pts = []
        for (cx, cy, a0) in [(x1 - radio, y0 + radio, -math.pi / 2), (x1 - radio, y1 - radio, 0),
                             (x0 + radio, y1 - radio, math.pi / 2), (x0 + radio, y0 + radio, math.pi)]:
            pts += puntos_elipse(cx, cy, radio, radio, 6, a0, a0 + math.pi / 2)
    else:
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    if relleno is not None: d.polygon(pts, fill=relleno)
    trazo(d, pts, rng, w, col, amp, cerrado=True)

def texto_mano(d, x, y, txt, f, rng, col=TINTA, anchor="la", amp=1.5):
    """Texto con un ligero baile vertical por caracter (aire de rotulado a mano)."""
    probe = d
    if anchor.startswith("m"):
        x = x - probe.textlength(txt, font=f) / 2
    elif anchor.startswith("r"):
        x = x - probe.textlength(txt, font=f)
    va = anchor[1] if len(anchor) > 1 else "a"
    for ch in txt:
        d.text((x, y + _wob(rng, amp)), ch, font=f, fill=col, anchor="l" + va)
        x += probe.textlength(ch, font=f)

def flecha_mano(d, p0, p1, rng, w=9, col=CIAN, prog=1.0):
    """Flecha dibujandose de p0 a p1 (prog 0-1)."""
    if prog <= 0.02: return
    x0, y0 = p0; x1, y1 = p1
    xe, ye = x0 + (x1 - x0) * prog, y0 + (y1 - y0) * prog
    ang = math.atan2(y1 - y0, x1 - x0)
    # ligera curva: punto medio desplazado
    mx, my = (x0 + xe) / 2 - 30 * math.sin(ang), (y0 + ye) / 2 + 30 * math.cos(ang)
    trazo(d, [(x0, y0), (mx, my), (xe, ye)], rng, w, col, 2.0)
    if prog > 0.85:
        L = 34
        for s in (-1, 1):
            a = ang + math.pi + s * 0.5
            trazo(d, [(xe, ye), (xe + L * math.cos(a), ye + L * math.sin(a))], rng, w, col, 1.5)

def estrella(d, cx, cy, r, rng, col=CIAN, w=6):
    for k in range(4):
        a = k * math.pi / 4
        trazo(d, [(cx - r * math.cos(a), cy - r * math.sin(a)), (cx + r * math.cos(a), cy + r * math.sin(a))], rng, w, col, 1.2)

def check_mano(d, cx, cy, s, rng, col=CIAN, w=10, prog=1.0):
    pts = [(cx - s, cy), (cx - s * 0.3, cy + s * 0.7), (cx + s, cy - s * 0.8)]
    if prog < 1.0:
        n = max(2, int(1 + 2 * prog))
        pts = pts[:n] if n >= 3 else [pts[0], (pts[0][0] + (pts[1][0] - pts[0][0]) * min(1, prog * 2), pts[0][1] + (pts[1][1] - pts[0][1]) * min(1, prog * 2))]
    trazo(d, pts, rng, w, col, 1.5)

def cruz_mano(d, cx, cy, s, rng, col=ROJO_ENFASIS, w=10, prog=1.0):
    trazo(d, [(cx - s, cy - s), (cx - s + 2 * s * min(1, prog * 2), cy - s + 2 * s * min(1, prog * 2))], rng, w, col, 1.5)
    if prog > 0.5:
        q = min(1, (prog - 0.5) * 2)
        trazo(d, [(cx + s, cy - s), (cx + s - 2 * s * q, cy - s + 2 * s * q)], rng, w, col, 1.5)

def ease_out(k): k = min(1.0, max(0.0, k)); return 1 - (1 - k) ** 3

# ---- personajes
def dibujar_bit(d, cx, base, t, rng, accion, habla, entrada=1.0, s=1.0):
    """Bit: robot redondo blanco con cara-pantalla cian. base = y del suelo."""
    hv = float(habla); habla = hv > 0.08     # hv: apertura de la boca 0-1 (envolvente real de la voz)
    resp = math.sin(t * 2.2)
    cy = base - 150 * s + 3 * resp - 4 * hv * s   # al hablar se yergue un poco
    r = 92 * s
    if accion == "celebra": cy -= 22 * abs(math.sin(t * 6.5))
    # ruedas / pies
    for sx in (-1, 1):
        circulo(d, cx + sx * 44 * s, base - 14 * s, 18 * s, rng, 7, relleno=(255, 255, 255))
    # brazos (antes del cuerpo para que queden detras)
    if accion in ("explica", "senala"):
        ang_r = -1.05 + 0.12 * math.sin(t * 3.0) - 0.25 * hv   # brazo derecho senalando arriba (al objeto); gesticula con la voz
        ang_l = 0.55 - 0.35 * hv
    elif accion == "celebra":
        ang_r = -1.25 + 0.3 * math.sin(t * 7); ang_l = -1.25 - 0.3 * math.sin(t * 7)
    elif accion == "sorprendido":
        ang_r = -0.35; ang_l = -0.35
    elif accion == "piensa":
        ang_r = -0.9; ang_l = 0.6
    else:
        ang_r = 0.55 + 0.05 * resp; ang_l = 0.55 + 0.05 * resp
    L = 78 * s
    for sx, ang in ((1, ang_r), (-1, ang_l)):
        x0, y0 = cx + sx * r * 0.85, cy + 10 * s
        x1, y1 = x0 + sx * L * math.cos(ang), y0 + L * math.sin(ang)
        trazo(d, [(x0, y0), (x1, y1)], rng, 9, TINTA, 2.0)
        circulo(d, x1, y1, 13 * s, rng, 7, relleno=(255, 255, 255))
    # antena
    trazo(d, [(cx, cy - r + 4), (cx + 6 * s, cy - r - 36 * s)], rng, 8, TINTA, 1.5)
    circulo(d, cx + 7 * s, cy - r - 46 * s, 11 * s, rng, 6, relleno=CIAN)
    # cuerpo
    circulo(d, cx, cy, r, rng, 10, relleno=(255, 255, 255), ry=r * (1 + 0.015 * resp))
    # pantalla-cara
    fx0, fy0, fx1, fy1 = cx - 62 * s, cy - 52 * s, cx + 62 * s, cy + 40 * s
    rect_mano(d, fx0, fy0, fx1, fy1, rng, 7, relleno=CIAN, radio=18 * s, amp=1.2)
    # ojos (parpadeo cada ~3,3 s)
    parp = ((t + 0.9) % 3.3) < 0.13
    ey = cy - 14 * s
    for sx in (-1, 1):
        ex = cx + sx * 26 * s
        if accion == "sorprendido":
            circulo(d, ex, ey, 13 * s, rng, 4, relleno=(255, 255, 255), col=(255, 255, 255), amp=0.8)
            circulo(d, ex, ey, 5 * s, rng, 3, relleno=TINTA, col=TINTA, amp=0.5)
        elif parp:
            d.line([(ex - 11 * s, ey), (ex + 11 * s, ey)], fill=(255, 255, 255), width=int(5 * s))
        elif accion == "celebra":   # ojos felices ^ ^
            trazo(d, [(ex - 11 * s, ey + 5 * s), (ex, ey - 7 * s), (ex + 11 * s, ey + 5 * s)], rng, 6, (255, 255, 255), 0.8)
        else:
            d.ellipse([ex - 10 * s, ey - 10 * s, ex + 10 * s, ey + 10 * s], fill=(255, 255, 255))
            d.ellipse([ex - 4 * s, ey - 4 * s, ex + 4 * s, ey + 4 * s], fill=TINTA)
    # boca
    my = cy + 18 * s
    if habla:   # boca abierta segun la envolvente real de la voz (labios sincronizados)
        ab = 3 + 19 * hv; aw = 12 + 6 * hv
        d.ellipse([cx - aw * s, my - ab * s / 2, cx + aw * s, my + ab * s / 2 + 2], fill=(255, 255, 255))
        if ab > 12: d.ellipse([cx - (aw - 5) * s, my + 2 * s, cx + (aw - 5) * s, my + ab * s / 2], fill=(0, 120, 150))
    elif accion == "sorprendido":
        d.ellipse([cx - 10 * s, my - 10 * s, cx + 10 * s, my + 10 * s], fill=(255, 255, 255))
    else:
        trazo(d, [(cx - 16 * s, my - 2), (cx, my + 8 * s), (cx + 16 * s, my - 2)], rng, 6, (255, 255, 255), 0.8)
    if habla:  # rayitas de voz junto a la boca
        for i in range(2):
            x = cx + 90 * s + i * 14 * s; a = (0.3 + 0.7 * hv) * (0.7 + 0.3 * abs(math.sin(t * 9 + i)))
            trazo(d, [(x, cy + 8 * s - 12 * a * s), (x, cy + 8 * s + 12 * a * s)], rng, 5, CIAN, 1.0)
    if accion == "celebra":
        for i in range(5):
            r2 = random.Random(31 * i + 7)
            ex = cx + (r2.uniform(130, 200) * r2.choice([-1, 1])) * s; ey = base - 180 * s - ((t * 70 + i * 60) % 170)
            estrella(d, ex, ey, 10 + r2.uniform(0, 6), rng, CIAN, 5)

def dibujar_paco(d, cx, base, t, rng, accion, habla, s=1.0):
    """Paco: muneco de palo que se agobia con la tecnologia."""
    hv = float(habla); habla = hv > 0.08     # hv: apertura de la boca 0-1 (envolvente real de la voz)
    bob = 2.5 * math.sin(t * 2.0) - 3 * hv
    salto = 24 * abs(math.sin(t * 6.5)) if accion == "celebra" else 0
    tiembla = 2.0 * math.sin(t * 30) if accion == "agobiado" else 0
    hy = base - 300 * s + bob - salto + tiembla * 0.3   # centro de la cabeza
    cx = cx + tiembla
    r = 44 * s
    cuello = hy + r; cad = base - 120 * s - salto; hombros = cuello + 22 * s
    # piernas
    for sx in (-1, 1):
        abre = 36 * s + (10 * s * abs(math.sin(t * 6.5)) if accion == "celebra" else 0)
        trazo(d, [(cx, cad), (cx + sx * abre, base - salto)], rng, 10, TINTA, 2.0)
        trazo(d, [(cx + sx * abre, base - salto), (cx + sx * (abre + 22 * s), base - salto)], rng, 9, TINTA, 1.5)
    # tronco
    trazo(d, [(cx, cuello), (cx, cad)], rng, 10, TINTA, 2.0)
    # brazos
    L = 95 * s
    def brazo(sx, a1, a2=None, L1=None, Lt=None):
        L = Lt or 95 * s
        L1 = L1 or L * 0.55
        x0, y0 = cx, hombros
        x1, y1 = x0 + sx * L1 * math.cos(a1), y0 + L1 * math.sin(a1)
        pts = [(x0, y0), (x1, y1)]
        if a2 is not None:
            pts.append((x1 + sx * (L - L1) * math.cos(a2), y1 + (L - L1) * math.sin(a2)))
        trazo(d, pts, rng, 10, TINTA, 2.0)
        circulo(d, pts[-1][0], pts[-1][1], 9 * s, rng, 6, relleno=(255, 255, 255))
    if accion == "agobiado":       # manos a los lados de la cabeza
        for sx in (-1, 1):
            brazo(sx, -0.54, -1.77, L1=70 * s, Lt=131 * s)
    elif accion == "celebra":
        w = 0.35 * math.sin(t * 7)
        brazo(1, -1.2 + w, -1.7 + w); brazo(-1, -1.2 - w, -1.7 - w)
    elif accion == "sorprendido":
        brazo(1, -0.6, -1.4); brazo(-1, -0.6, -1.4)
    elif accion == "piensa":
        brazo(1, -0.5, -2.0); brazo(-1, 1.1)
    elif accion in ("senala",):
        brazo(1, -0.75 + 0.08 * math.sin(t * 3), -0.75); brazo(-1, 1.1)
    elif habla:                     # Paco habla (sin Bit): gesticula con la mano al ritmo de la voz
        brazo(1, -0.1 - 0.6 * hv, -1.3 - 0.3 * hv); brazo(-1, 1.1 + 0.05 * bob)
    else:                           # escucha: brazos relajados, ligero balanceo
        brazo(1, 1.15 + 0.05 * bob); brazo(-1, 1.15 - 0.05 * bob)
    # cabeza
    circulo(d, cx, hy, r, rng, 10, relleno=(255, 255, 255))
    ey = hy - 8 * s
    parp = ((t + 1.7) % 3.7) < 0.13
    for sx in (-1, 1):
        ex = cx + sx * 15 * s
        if accion == "sorprendido":
            circulo(d, ex, ey, 8 * s, rng, 4, relleno=(255, 255, 255), amp=0.6)
            d.ellipse([ex - 3 * s, ey - 3 * s, ex + 3 * s, ey + 3 * s], fill=TINTA)
        elif parp:
            d.line([(ex - 6 * s, ey), (ex + 6 * s, ey)], fill=TINTA, width=int(4 * s))
        elif accion == "celebra":
            trazo(d, [(ex - 7 * s, ey + 3 * s), (ex, ey - 5 * s), (ex + 7 * s, ey + 3 * s)], rng, 5, TINTA, 0.6)
        else:
            d.ellipse([ex - 5 * s, ey - 5 * s, ex + 5 * s, ey + 5 * s], fill=TINTA)
    if accion == "agobiado":   # cejas de agobio
        for sx in (-1, 1):
            trazo(d, [(cx + sx * 24 * s, ey - 20 * s), (cx + sx * 7 * s, ey - 14 * s)], rng, 5, TINTA, 0.8)
    my = hy + 16 * s
    if habla:   # boca abierta segun la envolvente real de la voz
        ab = 2 + 13 * hv; aw = 9 + 4 * hv
        d.ellipse([cx - aw * s, my - ab * s / 2, cx + aw * s, my + ab * s / 2 + 2], fill=TINTA)
    elif accion == "agobiado":
        trazo(d, [(cx - 14 * s, my + 2), (cx - 7 * s, my - 4), (cx, my + 2), (cx + 7 * s, my - 4), (cx + 14 * s, my + 2)], rng, 5, TINTA, 0.8)
    elif accion == "sorprendido":
        circulo(d, cx, my + 2, 7 * s, rng, 4, relleno=TINTA, amp=0.5)
    elif accion in ("celebra",):
        trazo(d, [(cx - 16 * s, my - 4), (cx, my + 10 * s), (cx + 16 * s, my - 4)], rng, 6, TINTA, 0.8)
    else:
        trazo(d, [(cx - 11 * s, my), (cx, my + 5 * s), (cx + 11 * s, my)], rng, 5, TINTA, 0.8)
    # extras por accion
    if accion == "agobiado":
        for i, sx in enumerate((-1, 1)):   # gotas de sudor
            gy = hy - 10 * s + ((t * 60 + i * 25) % 40)
            gx = cx + sx * (r + 16 * s)
            d.polygon([(gx, gy - 14 * s), (gx - 7 * s, gy + 2), (gx + 7 * s, gy + 2)], fill=CIAN)
            d.ellipse([gx - 7 * s, gy - 4 * s, gx + 7 * s, gy + 9 * s], fill=CIAN)
        for k in range(3):                  # rayitas de nervios
            a = -2.2 + k * 0.5
            trazo(d, [(cx + (r + 14 * s) * math.cos(a), hy + (r + 14 * s) * math.sin(a)),
                      (cx + (r + 34 * s) * math.cos(a), hy + (r + 34 * s) * math.sin(a))], rng, 5, TINTA, 1.0)
    elif accion == "sorprendido":
        f = font(F_DIB, int(74 * s))
        texto_mano(d, cx + r + 30 * s, hy - 60 * s - 6 * abs(math.sin(t * 5)), "!", f, rng, CIAN, "ma", 1.0)
    elif accion == "piensa":
        for i, (dx, dy, rr) in enumerate([(30, -70, 7), (52, -100, 11), (90, -150, 34)]):
            circulo(d, cx + dx * s, hy + dy * s + 2 * math.sin(t * 2 + i), rr * s, rng, 6, relleno=(255, 255, 255), amp=1.0)
        f = font(F_DIB, int(44 * s))
        d.text((cx + 90 * s, hy - 150 * s), "?", font=f, fill=CIAN, anchor="mm")
    elif accion == "celebra":
        for i in range(5):
            r2 = random.Random(17 * i + 3)
            ex = cx + (r2.uniform(90, 170) * r2.choice([-1, 1])) * s; ey = base - 200 * s - ((t * 70 + i * 50) % 170)
            estrella(d, ex, ey, 9 + r2.uniform(0, 6), rng, CIAN, 5)

def dibujar_invitado(d, cx, cy, t, rng, nombre, s=1.0):
    """Personaje generico inventado para ChatGPT / Claude / Gemini: blob redondeado con etiqueta de texto (sin logos)."""
    bob = 4 * math.sin(t * 2.4 + len(nombre))
    cy = cy + bob
    w, h = 118 * s, 96 * s
    rect_mano(d, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, rng, 8, relleno=(255, 255, 255), radio=30 * s)
    # orejitas / antenas pequenas segun el nombre (para distinguirlos sin logos)
    k = sum(ord(c) for c in nombre) % 3
    if k == 0:
        trazo(d, [(cx, cy - h / 2), (cx, cy - h / 2 - 22 * s)], rng, 6, TINTA, 1.2); circulo(d, cx, cy - h / 2 - 28 * s, 7 * s, rng, 5, relleno=CIAN)
    elif k == 1:
        for sx in (-1, 1): trazo(d, [(cx + sx * 30 * s, cy - h / 2), (cx + sx * 44 * s, cy - h / 2 - 22 * s)], rng, 6, TINTA, 1.2)
    else:
        for sx in (-1, 1): circulo(d, cx + sx * 40 * s, cy - h / 2 - 4 * s, 12 * s, rng, 6, relleno=(255, 255, 255))
    parp = ((t + 2.3) % 4.1) < 0.12
    for sx in (-1, 1):
        ex = cx + sx * 24 * s; ey = cy - 10 * s
        if parp: d.line([(ex - 7 * s, ey), (ex + 7 * s, ey)], fill=TINTA, width=4)
        else: d.ellipse([ex - 6 * s, ey - 6 * s, ex + 6 * s, ey + 6 * s], fill=TINTA)
    trazo(d, [(cx - 14 * s, cy + 16 * s), (cx, cy + 24 * s), (cx + 14 * s, cy + 16 * s)], rng, 5, TINTA, 0.8)
    f = font(F_DIB_C, int(34 * s))
    tw = d.textlength(nombre, font=f)
    rect_mano(d, cx - tw / 2 - 16, cy + h / 2 + 10, cx + tw / 2 + 16, cy + h / 2 + 58 * s, rng, 5, relleno=CIAN, radio=12, amp=1.0)
    d.text((cx, cy + h / 2 + 34 * s), nombre, font=f, fill=(255, 255, 255), anchor="mm")

# ---- objetos y pantalla
def _wrap(probe, txt, f, maxw, maxlines):
    lines, cur = [], ""
    for wd in str(txt).split():
        t2 = (cur + " " + wd).strip()
        if probe.textlength(t2, font=f) <= maxw: cur = t2
        else:
            if cur: lines.append(cur)
            cur = wd
    if cur: lines.append(cur)
    return lines[:maxlines]

def texto_tecleado(d, lineas, x, y, maxw, t, rng, f, t0=0.55, cps=30, maxlines=4, col=TINTA, lh=None):
    """Lineas de texto que aparecen letra a letra (como tecleadas) con cursor parpadeante."""
    probe = d
    todas = []
    for ln in lineas:
        todas += _wrap(probe, ln, f, maxw, 3) or [""]
    todas = todas[:maxlines]
    n_tot = sum(len(l) for l in todas)
    n = int(max(0.0, t - t0) * cps)
    lh = lh or int(f.size * 1.35)
    fin = n >= n_tot
    cur_x, cur_y = x, y
    for i, ln in enumerate(todas):
        part = ln[:max(0, n)]; n -= len(ln)
        if part: d.text((x, y + i * lh), part, font=f, fill=col)
        cur_x = x + probe.textlength(part, font=f); cur_y = y + i * lh
        if n < 0: break
    if (not fin or int(t * 2.5) % 2 == 0) and t >= t0 - 0.3:
        d.rectangle([cur_x + 3, cur_y + 2, cur_x + 7, cur_y + f.size + 2], fill=CIAN)
    return fin

def dibujar_objeto(d, obj, pantalla, t, rng, cx=540, cy=OBJ_CY_DIB):
    """Dibuja el objeto de la escena (movil, portatil, chat, ...) con la "pantalla" tecleada dentro si la hay."""
    if obj == "movil":
        w, h = 360, 500; cy = cy - 30
        rect_mano(d, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, rng, 10, relleno=(255, 255, 255), radio=46)
        rect_mano(d, cx - w / 2 + 22, cy - h / 2 + 60, cx + w / 2 - 22, cy + h / 2 - 60, rng, 5, relleno=CIAN_CLARO, radio=10, amp=1.2)
        trazo(d, [(cx - 30, cy - h / 2 + 32), (cx + 30, cy - h / 2 + 32)], rng, 6, TINTA, 1.0)
        circulo(d, cx, cy + h / 2 - 30, 11, rng, 5, relleno=(255, 255, 255))
        if pantalla:
            texto_tecleado(d, pantalla, cx - w / 2 + 38, cy - h / 2 + 80, w - 76, t, rng, font(F_DIB_MONO, 28), maxlines=7)
    elif obj == "portatil":
        w, h = 660, 420
        rect_mano(d, cx - w / 2, cy - h / 2 - 40, cx + w / 2, cy + h / 2 - 60, rng, 10, relleno=(255, 255, 255), radio=18)
        rect_mano(d, cx - w / 2 + 24, cy - h / 2 - 16, cx + w / 2 - 24, cy + h / 2 - 84, rng, 5, relleno=CIAN_CLARO, radio=8, amp=1.2)
        trazo(d, [(cx - w / 2 - 40, cy + h / 2 - 60), (cx + w / 2 + 40, cy + h / 2 - 60), (cx + w / 2 + 20, cy + h / 2 - 20), (cx - w / 2 - 20, cy + h / 2 - 20)], rng, 9, TINTA, 2.0, cerrado=True)
        trazo(d, [(cx - 60, cy + h / 2 - 48), (cx + 60, cy + h / 2 - 48)], rng, 5, TINTA, 1.0)
        if pantalla:
            texto_tecleado(d, pantalla, cx - w / 2 + 44, cy - h / 2 + 8, w - 90, t, rng, font(F_DIB_MONO, 32), maxlines=5)
    elif obj == "chat":
        w, h = 700, 400; cx = cx - 40
        x0, y0, x1, y1 = cx - w / 2, cy - h / 2 - 30, cx + w / 2, cy + h / 2 - 50
        rect_mano(d, x0, y0, x1, y1, rng, 10, relleno=(255, 255, 255), radio=38)
        # rabito del bocadillo hacia abajo-izquierda (hacia Paco)
        d.polygon([(x0 + 150, y1 - 6), (x0 + 110, y1 + 70), (x0 + 240, y1 - 6)], fill=(255, 255, 255))
        trazo(d, [(x0 + 150, y1 - 2), (x0 + 110, y1 + 70), (x0 + 240, y1 - 2)], rng, 10, TINTA, 2.0)
        # cabecera del chat
        trazo(d, [(x0 + 36, y0 + 64), (x1 - 36, y0 + 64)], rng, 5, CIAN, 1.0)
        circulo(d, x0 + 58, y0 + 36, 12, rng, 5, relleno=CIAN)
        if pantalla:
            texto_tecleado(d, pantalla, x0 + 40, y0 + 90, w - 80, t, rng, font(F_DIB_MONO, 34), maxlines=5)
        else:   # chat sin "pantalla": puntos suspensivos animados (esta "escribiendo")
            for i in range(3):
                a = 0.5 + 0.5 * math.sin(t * 5.0 - i * 1.1)
                circulo(d, cx - 60 + i * 60, cy - 10 - 10 * a, 13 + 4 * a, rng, 4, relleno=CIAN if a > 0.6 else CIAN_CLARO, col=TINTA, amp=0.8)
    else:
        # icono arriba + tarjeta de texto debajo si hay pantalla
        icy = cy - 150 if pantalla else cy
        if obj == "correo":
            w, h = 360, 240
            rect_mano(d, cx - w / 2, icy - h / 2, cx + w / 2, icy + h / 2, rng, 10, relleno=(255, 255, 255), radio=14)
            trazo(d, [(cx - w / 2, icy - h / 2), (cx, icy + 20), (cx + w / 2, icy - h / 2)], rng, 9, TINTA, 2.0)
            circulo(d, cx + w / 2 - 10, icy - h / 2 + 10, 26, rng, 6, relleno=CIAN)
            d.text((cx + w / 2 - 10, icy - h / 2 + 10), "1", font=font(F_DIB, 34), fill=(255, 255, 255), anchor="mm")
        elif obj == "calendario":
            w, h = 340, 300
            rect_mano(d, cx - w / 2, icy - h / 2, cx + w / 2, icy + h / 2, rng, 10, relleno=(255, 255, 255), radio=16)
            d.rectangle([cx - w / 2 + 6, icy - h / 2 + 6, cx + w / 2 - 6, icy - h / 2 + 64], fill=CIAN)
            for sx in (-1, 1): trazo(d, [(cx + sx * 90, icy - h / 2 - 30), (cx + sx * 90, icy - h / 2 + 30)], rng, 9, TINTA, 1.2)
            for i in range(12):
                gx = cx - 110 + (i % 4) * 73; gy = icy - 40 + (i // 4) * 70
                d.ellipse([gx - 9, gy - 9, gx + 9, gy + 9], fill=(190, 190, 190))
            sel = int(t * 1.5) % 12
            circulo(d, cx - 110 + (sel % 4) * 73, icy - 40 + (sel // 4) * 70, 24, rng, 6, col=CIAN, amp=1.0)
        elif obj == "lista":
            w, h = 320, 380
            rect_mano(d, cx - w / 2, icy - h / 2, cx + w / 2, icy + h / 2, rng, 10, relleno=(255, 255, 255), radio=12)
            for i in range(3):
                ly = icy - h / 2 + 70 + i * 105
                rect_mano(d, cx - w / 2 + 34, ly - 24, cx - w / 2 + 82, ly + 24, rng, 6, relleno=(255, 255, 255), radio=8, amp=1.0)
                trazo(d, [(cx - w / 2 + 110, ly), (cx + w / 2 - 40, ly)], rng, 6, (170, 170, 170), 1.0)
                if t > 0.8 + i * 0.7:
                    check_mano(d, cx - w / 2 + 58, ly, 16, rng, CIAN, 8, min(1.0, (t - 0.8 - i * 0.7) / 0.3))
        elif obj == "reloj":
            circulo(d, cx, icy, 150, rng, 10, relleno=(255, 255, 255))
            for k in range(12):
                a = k * math.pi / 6
                trazo(d, [(cx + 125 * math.cos(a), icy + 125 * math.sin(a)), (cx + 140 * math.cos(a), icy + 140 * math.sin(a))], rng, 6, TINTA, 0.8)
            am = -math.pi / 2 + t * 2.4; ah = -math.pi / 2 + t * 0.2
            trazo(d, [(cx, icy), (cx + 70 * math.cos(ah), icy + 70 * math.sin(ah))], rng, 9, TINTA, 1.0)
            trazo(d, [(cx, icy), (cx + 110 * math.cos(am), icy + 110 * math.sin(am))], rng, 7, CIAN, 1.0)
            circulo(d, cx, icy, 10, rng, 5, relleno=TINTA)
        elif obj == "bombilla":
            on = t > 0.7
            circulo(d, cx, icy - 30, 110, rng, 10, relleno=(255, 240, 150) if on else (255, 255, 255))
            rect_mano(d, cx - 46, icy + 70, cx + 46, icy + 130, rng, 8, relleno=(255, 255, 255), radio=10)
            trazo(d, [(cx - 30, icy + 100), (cx + 30, icy + 100)], rng, 5, TINTA, 0.8)
            trazo(d, [(cx - 25, icy + 20), (cx - 10, icy + 70), (cx + 10, icy + 70), (cx + 25, icy + 20)], rng, 6, TINTA, 1.0)
            if on:
                k = min(1.0, (t - 0.7) / 0.3)
                for j in range(8):
                    a = j * math.pi / 4 + 0.2 * math.sin(t * 3)
                    r0, r1 = 135, 135 + 45 * k
                    trazo(d, [(cx + r0 * math.cos(a), icy - 30 + r0 * math.sin(a)), (cx + r1 * math.cos(a), icy - 30 + r1 * math.sin(a))], rng, 7, CIAN, 1.2)
        elif obj == "carpeta":
            w, h = 400, 280
            rect_mano(d, cx - w / 2, icy - h / 2 + 30, cx + w / 2, icy + h / 2, rng, 10, relleno=CIAN_CLARO, radio=14)
            trazo(d, [(cx - w / 2, icy - h / 2 + 30), (cx - w / 2, icy - h / 2), (cx - w / 2 + 150, icy - h / 2), (cx - w / 2 + 180, icy - h / 2 + 30)], rng, 10, TINTA, 2.0)
            # papel que entra en la carpeta
            k = ease_out((t - 0.4) / 0.8)
            py = icy - h / 2 - 50 + 60 * k   # entra desde mas abajo: no pisa el rotulo de arriba (Estratega 7/11)
            rect_mano(d, cx - 90, py, cx + 90, py + 180, rng, 7, relleno=(255, 255, 255), radio=6, amp=1.2)
            for j in range(3): trazo(d, [(cx - 60, py + 40 + j * 36), (cx + 50, py + 40 + j * 36)], rng, 5, (170, 170, 170), 0.8)
            d.polygon([(cx - w / 2 + 6, icy - h / 2 + 90), (cx + w / 2 - 6, icy - h / 2 + 90), (cx + w / 2 - 6, icy + h / 2 - 6), (cx - w / 2 + 6, icy + h / 2 - 6)], fill=CIAN_CLARO)
            trazo(d, [(cx - w / 2, icy - h / 2 + 90), (cx + w / 2, icy - h / 2 + 90), (cx + w / 2, icy + h / 2), (cx - w / 2, icy + h / 2)], rng, 10, TINTA, 2.0, cerrado=True)
        if pantalla:
            w, h = 740, 250
            y0 = cy + 90
            rect_mano(d, cx - w / 2, y0 - h / 2, cx + w / 2, y0 + h / 2, rng, 8, relleno=(255, 255, 255), radio=20)
            texto_tecleado(d, pantalla, cx - w / 2 + 40, y0 - h / 2 + 36, w - 80, t, rng, font(F_DIB_MONO, 34), maxlines=4)

def dibujar_pizarra(d, lineas, t, rng, numerada=False, cx=540, cy=OBJ_CY_DIB):
    """Pizarra: texto o lista de pasos que se dibuja trazo a trazo (barrido por linea)."""
    f = font(F_DIB_C, 46 if numerada else 52)
    probe = d
    todas = []
    for ln in lineas:
        ws = _wrap(probe, ln, f, 640 if numerada else 680, 2) or [""]
        todas.append(ws)
    nl = sum(len(x) for x in todas)
    lh = 66; gap = 26
    h = max(260, nl * lh + (len(todas) - 1) * gap + 90)
    w = 800
    y0 = cy - h / 2 + 10
    rect_mano(d, cx - w / 2, y0, cx + w / 2, y0 + h, rng, 10, relleno=(255, 255, 255), radio=20)
    # pinzas / marco superior
    for sx in (-1, 1): circulo(d, cx + sx * 300, y0 + 2, 12, rng, 6, relleno=CIAN)
    y = y0 + 48
    paso = max(0.45, min(1.1, 0.55 * (len(todas) and 3.0 / len(todas))))
    for i, ws in enumerate(todas):
        k0 = (t - 0.35 - i * paso)
        if k0 <= 0: break
        if numerada:
            kk = ease_out(k0 / 0.25)
            circulo(d, cx - w / 2 + 62, y + 30, 26 * kk, rng, 6, relleno=CIAN)
            if kk > 0.6:
                d.text((cx - w / 2 + 62, y + 30), str(i + 1), font=font(F_DIB, 34), fill=(255, 255, 255), anchor="mm")
        x = cx - w / 2 + (112 if numerada else 50)
        for j, ln in enumerate(ws):
            prog = min(1.0, max(0.0, (k0 - j * 0.3) / 0.35))
            if prog <= 0: break
            tw = probe.textlength(ln, font=f)
            d.text((x, y + j * lh), ln, font=f, fill=TINTA)
            cut = int((tw + 20) * prog)
            if cut < tw + 20:   # la parte aun no dibujada se tapa con el blanco de la pizarra
                d.rectangle([x + cut, y + j * lh - 4, x + tw + 24, y + j * lh + lh], fill=(255, 255, 255))
            if prog < 1.0:   # punta del rotulador
                d.ellipse([x + cut - 8, y + j * lh + lh - 14, x + cut + 8, y + j * lh + lh + 2], fill=CIAN)
        y += len(ws) * lh + gap

def dibujar_cifra(d, sc, t, rng, cx=540, cy=OBJ_CY_DIB):
    parts = _cifra_parts(sc.cifra)
    k = ease_out((t - 0.15) / 1.3)
    if parts:
        pre, val, post, sep = parts
        cur = int(round(val * k))
        txt = pre + ("{:,}".format(cur).replace(",", sep) if sep else str(cur)) + post
    else:
        txt = sc.cifra
    size = 230
    while size > 90 and d.textlength(sc.cifra, font=font(F_DIB, size)) > 880: size -= 8
    f = font(F_DIB, size)
    d.text((cx + 6, cy - 20 + 6), txt, font=f, anchor="mm", fill=CIAN_CLARO)
    d.text((cx, cy - 20), txt, font=f, anchor="mm", fill=CIAN, stroke_width=6, stroke_fill=TINTA)
    if sc.unidad:
        texto_mano(d, cx, cy + size // 2 + 40, sc.unidad.upper()[:28], font(F_DIB_C, 54), rng, TINTA, "mm")
    trazo(d, [(cx - 300, cy + size // 2 + 100), (cx + 300, cy + size // 2 + 100)], rng, 8, CIAN, 2.0)

def dibujar_antes_despues(d, ad, t, rng, cx=540, cy=OBJ_CY_DIB):
    """Dos tarjetas: ANTES (tachado en rojo) -> DESPUES (check cian)."""
    antes = str(ad.get("antes", ""))[:40]; despues = str(ad.get("despues", ""))[:40]
    w, h = 400, 300; gap = 60
    f = font(F_DIB_C, 46); fe = font(F_DIB, 34)
    for i, (lab, txt, x0) in enumerate((("ANTES", antes, cx - w - gap / 2), ("DESPUÉS", despues, cx + gap / 2))):
        k = ease_out((t - 0.1 - i * 0.9) / 0.35)
        if k <= 0: continue
        y0 = cy - h / 2 + (1 - k) * 40
        rect_mano(d, x0, y0, x0 + w, y0 + h, rng, 9, relleno=(255, 255, 255), radio=18)
        d.rectangle([x0 + 6, y0 + 6, x0 + w - 6, y0 + 62], fill=CIAN if i else (200, 200, 200))
        d.text((x0 + w / 2, y0 + 34), lab, font=fe, fill=(255, 255, 255) if i else TINTA, anchor="mm")
        ls = _wrap(d, txt, f, w - 50, 3)
        for j, ln in enumerate(ls):
            d.text((x0 + w / 2, y0 + 110 + j * 56), ln, font=f, fill=TINTA, anchor="mm")
        if i == 0 and t > 0.9:
            cruz_mano(d, x0 + w / 2, y0 + h / 2 + 20, 70, rng, ROJO_ENFASIS, 12, min(1.0, (t - 0.9) / 0.4))
        if i == 1 and t > 1.9:
            check_mano(d, x0 + w - 70, y0 + h - 60, 32, rng, CIAN, 12, min(1.0, (t - 1.9) / 0.35))
    if t > 0.8:
        flecha_mano(d, (cx - 110, cy + h / 2 + 50), (cx + 110, cy + h / 2 + 50), rng, 9, CIAN, min(1.0, (t - 0.8) / 0.3))

_sello_dib = {}
def sello_dibujo_img(txt):
    """Sello doodle: contorno y texto cian (rojo si es FALSO/NO), rotado, sobre el objeto."""
    if txt not in _sello_dib:
        col = ROJO_ENFASIS if (txt.startswith("FALS") or txt in ("NO", "MAL", "BULO", "MITO")) else CIAN
        size = 150
        probe = ImageDraw.Draw(Image.new("L", (4, 4)))
        while size > 70 and probe.textlength(txt, font=font(F_DIB, size)) > 620: size -= 6
        f = font(F_DIB, size); tw = int(probe.textlength(txt, font=f))
        bw, bh = tw + 100, int(size * 1.25) + 50
        im = Image.new("RGBA", (bw + 24, bh + 24), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        rng = random.Random(len(txt))
        rect_mano(d, 12, 12, bw + 12, bh + 12, rng, 12, relleno=PAPEL + (235,), col=col + (255,), radio=18, amp=2.5)
        d.text(((bw + 24) // 2, (bh + 24) // 2), txt, font=f, fill=col + (255,), anchor="mm")
        _sello_dib[txt] = im.rotate(-7, expand=True, resample=Image.BICUBIC)
    return _sello_dib[txt]

def rotulo_dibujo(texto, grande=False):
    """Rotulo corto arriba con subrayado de rotulador cian (gancho: mas grande)."""
    texto = texto.strip()
    f, size, lines = wrap_fit(texto.upper(), F_DIB_C, maxw=W - 160, maxlines=2, smax=(104 if grande else 70), smin=44)
    lh = int(size * 1.15)
    im = Image.new("RGBA", (W, lh * len(lines) + 60), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    rng = random.Random(len(texto))
    probe = d
    for i, ln in enumerate(lines):
        tw = probe.textlength(ln, font=f); x0 = (W - tw) / 2; y = 20 + i * lh
        # marcador cian detras (ligeramente inclinado)
        d.polygon([(x0 - 14, y + size * 0.45), (x0 + tw + 14, y + size * 0.40), (x0 + tw + 10, y + size * 1.02), (x0 - 18, y + size * 1.06)], fill=CIAN + (110,))
        d.text((x0, y), ln, font=f, fill=TINTA + (255,))
    return im

def hablando(sub, t):
    """True si la voz esta diciendo algo en t (para mover la boca)."""
    if sub is None or sub.n == 0: return False
    if sub.tiempos is not None:
        return any(ti - 0.05 <= t <= ti + 0.42 for ti in sub.tiempos)
    return sub.delay < t < sub.delay + sub.n / max(0.5, sub.wps) + 0.15

def boca(sc, t):
    """Apertura de la boca (0-1) sincronizada con la voz REAL: envolvente de la locucion (tiempos_voz.json "env",
    FPS valores por segundo, la escribe publicar_gh.py) si la hay; si no, alterna mientras suena una palabra."""
    env = getattr(sc, "env", None)
    if env:
        i = int((t - 0.12) * FPS)   # la voz entra en la mezcla 120 ms despues del inicio de la escena
        return float(env[i]) if 0 <= i < len(env) else 0.0
    if not hablando(sc.sub, t): return 0.0
    return 0.45 + 0.55 * abs(math.sin(t * 17.0))

def capa_escala(capa, z, px, py):
    """Escala una capa RGBA alrededor del punto (px, py) (rebote de entrada de los objetos)."""
    z = max(0.05, z)
    nw, nh = max(1, int(W * z)), max(1, int(H * z))
    r = capa.resize((nw, nh), Image.BILINEAR)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.paste(r, (int(px - px * z), int(py - py * z)), r)
    return out

def ease_out_back(k, c1=1.70158):
    k = min(1.0, max(0.0, k)); c3 = c1 + 1
    return 1 + c3 * (k - 1) ** 3 + c1 * (k - 1) ** 2

def preparar_dibujo(sc, spec, rng):
    """Prepara una escena en modo dibujo: subtitulos, rotulo, personajes, objeto y recursos."""
    sc.estilo_d = str(spec.get("estilo") or "paso").strip().lower()
    dib = spec.get("dibujo") or {}
    if not isinstance(dib, dict): dib = {}
    pers = [str(p).strip().lower() for p in (dib.get("personajes") or [])]
    sc.pers = [p for p in pers if p in ("bit", "paco")]
    if not sc.pers and not dib and sc.estilo_d in ("gancho", "cierre"):
        sc.pers = ["bit", "paco"]
    sc.accion = str(dib.get("accion") or ("agobiado" if sc.estilo_d == "problema" else ("celebra" if sc.estilo_d in ("resultado", "cierre") else "explica"))).strip().lower()
    sc.objeto = str(dib.get("objeto") or "nada").strip().lower()
    sc.pantalla = [str(x) for x in (dib.get("pantalla") or [])][:4] if isinstance(dib.get("pantalla"), list) else ([str(dib["pantalla"])] if dib.get("pantalla") else [])
    if sc.pantalla and sc.objeto == "nada": sc.objeto = "chat"
    nombres = {"chatgpt": "ChatGPT", "claude": "Claude", "gemini": "Gemini", "copilot": "Copilot", "gmail": "Gmail"}
    sc.invitados = [nombres.get(str(x).strip().lower(), str(x).strip()[:14]) for x in (dib.get("invitados") or []) if str(x).strip()][:2]
    piz = dib.get("pizarra") or spec.get("pizarra")
    sc.pizarra = ([str(x) for x in piz] if isinstance(piz, list) else ([str(piz)] if piz else []))[:4]
    sc.flecha = dib.get("flecha") or spec.get("flecha")
    ad = dib.get("antes_despues") or spec.get("antes_despues")
    sc.antes_despues = ad if isinstance(ad, dict) else None
    sc.entran = [p for p in sc.pers if p not in DIB_PREV["pers"]]
    DIB_PREV["pers"] = set(sc.pers)
    # subtitulos (misma logica que el modo humano: voz real si hay tiempos)
    voz, enf_voz = parsear_enfasis(spec.get("voz") or "")
    sub, enf_sub = parsear_enfasis(spec.get("subtitulos") or "")
    texto, enf_txt = parsear_enfasis(spec.get("texto") or "")
    base, enf = (sub, enf_sub) if sub else ((voz, enf_voz) if voz else ("", []))
    dv = float(spec.get("_voz_dur") or 0)
    tiempos = spec.get("_voz_palabras")
    if tiempos and len(tiempos) == len(base.split()):
        tiempos = [float(x) + 0.12 for x in tiempos]
    else:
        tiempos = None
    if dv > 0.2:
        wps = len(base.split()) / max(0.3, dv - 0.1); retardo = 0.12
    else:
        wps = max(WPS_HUMANO, len(base.split()) / max(0.3, sc.dur * 0.8)); retardo = 0.12
    sc.con_objeto = bool(sc.objeto != "nada" or sc.cifra or sc.lista or sc.pizarra or sc.antes_despues)
    estilo_sub = dict(fill=TINTA, stroke=PAPEL, activo=CIAN, enfasis=TINTA, marca=True,   # enfasis: resaltado cian (un solo acento)
                      cy=(SUB_CY_DIB if sc.con_objeto else 760), smax=(80 if sc.con_objeto else 100), smin=54)
    sc.sub = Subtitulos(base, wps, retardo, sc.dur, enfasis=enf, tiempos=tiempos, estilo=estilo_sub) if base else None
    sc.rotulo = rotulo_dibujo(texto, grande=(sc.estilo_d == "gancho")) if texto else None
    sc.habla_bit = "bit" in sc.pers
    env = spec.get("_voz_env")
    sc.env = [min(1.0, max(0.0, float(x))) for x in env] if isinstance(env, list) and env else None
    sc.rebote = bool(sc.con_objeto and not (sc.pizarra or sc.lista))   # objeto/cifra/antes-despues entran con rebote; pizarra/lista se dibujan
    # efectos de sonido sutiles de la escena (los mezcla make_audio): (tipo, t relativo, duracion)
    sc.sfx = []
    if sc.idx > 0 or sc.entran: sc.sfx.append(("whoosh", 0.0, 0.22))
    if sc.rebote: sc.sfx.append(("pop", 0.3, 0.09))
    piz = sc.lista or sc.pizarra
    if piz:
        paso = max(0.45, min(1.1, 0.55 * (3.0 / len(piz))))
        for i in range(len(piz)): sc.sfx.append(("lapiz", 0.35 + i * paso, 0.45))
    if sc.pantalla and sc.objeto != "nada":
        sc.sfx.append(("teclas", 0.55, min(sc.dur - 0.8, sum(len(x) for x in sc.pantalla) / 30.0)))
    if sc.cifra: sc.sfx.append(("ding", 1.3, 0.5))
    # camara: segmentos de ~3 s con encuadre distinto (corte dentro de escenas largas)
    rc = random.Random(sc.idx * 13 + 5)
    sc.cam = [(rc.choice([1.02, 1.04, 1.06]), rc.uniform(-14, 14), rc.uniform(-10, 10), rc.choice([1, -1])) for _ in range(int(sc.dur / 3.0) + 2)]

def render_frame_dibujo(fi, sc, noise, rg, seed):
    lf = fi - sc.start; t = lf / FPS
    img = papel_img(seed).copy()
    d = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(seed * 31 + sc.idx * 101 + fi // 4)   # temblor del trazo: cambia cada 4 fotogramas
    # ---- area del objeto / pizarra (se "dibuja" con un barrido en los primeros 0,5 s)
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dc = ImageDraw.Draw(capa, "RGBA")
    ocy = OBJ_CY_DIB + (40 if (sc.rotulo is not None and sc.rotulo.height > 170) else 0)   # rotulo de 2 lineas: objeto mas abajo
    if sc.antes_despues:
        dibujar_antes_despues(dc, sc.antes_despues, t, rng, cy=ocy)
    elif sc.cifra:
        dibujar_cifra(dc, sc, t, rng, cy=ocy)
    elif sc.lista:
        dibujar_pizarra(dc, sc.lista, t, rng, numerada=True, cy=ocy)
    elif sc.pizarra:
        dibujar_pizarra(dc, sc.pizarra, t, rng, numerada=False, cy=ocy)
    elif sc.objeto != "nada":
        dibujar_objeto(dc, sc.objeto, sc.pantalla, t, rng, cy=ocy)
    for i, inv in enumerate(sc.invitados):
        dibujar_invitado(dc, 950 - i * 170, 480, t, rng, inv, 0.8)
    if sc.flecha and t > 0.4:
        prog = min(1.0, (t - 0.4) / 0.4)
        xr = {"movil": 705, "portatil": 870, "chat": 850, "nada": 600}.get(sc.objeto, 760)
        x0 = min(1010, xr + 240)
        flecha_mano(dc, (x0, 540), (xr + 45, 620), rng, 10, CIAN, prog)
        if isinstance(sc.flecha, str) and prog >= 1.0:
            texto_mano(dc, x0, 500, sc.flecha[:18], font(F_DIB_C, 40), rng, CIAN, "mm")
    if sc.rebote:   # objeto, cifra o antes/despues: entra con rebote (0,45 s) y despues flota (nada queda quieto)
        if t < 0.45:
            capa = capa_escala(capa, ease_out_back(t / 0.45), 540, ocy)
        img.paste(capa, (0, int(4 * math.sin(t * 1.9 + sc.idx))), capa)
    else:
        if t < 0.5:   # pizarra / lista: aparece dibujandose (barrido de arriba abajo)
            a = np.asarray(capa.getchannel("A"), dtype=np.uint8).copy()
            corte = 300 + int(1000 * ease_out(t / 0.5))
            a[corte:, :] = 0
            capa.putalpha(Image.fromarray(a))
        img.paste(capa, (0, 0), capa)
    # ---- rotulo
    if sc.rotulo is not None:
        k = ease_out(t / 0.3)
        ro = sc.rotulo
        if k < 1.0:
            ro = ro.crop((0, 0, max(1, int(W * k)), ro.height))
        img.paste(ro, (0, 170), ro)
    # ---- personajes
    hv = boca(sc, t)   # apertura de la boca 0-1 (voz real)
    esc = 1.0 if sc.con_objeto else 1.3
    if len(sc.pers) == 2:
        pos = {"paco": 300, "bit": 740} if sc.con_objeto else {"paco": 280, "bit": 770}
    else:
        pos = {p: 540 for p in sc.pers}
    for p in sc.pers:
        x = pos[p]
        if p in sc.entran:
            k = ease_out(t / 0.45)
            x += (1 - k) * (-520 if p == "paco" else 520)
        if p == "bit":
            dibujar_bit(d, x, SUELO_DIB, t, rng, sc.accion if sc.accion in ("explica", "senala", "celebra", "sorprendido", "piensa") else "explica",
                        hv if sc.habla_bit else 0.0, s=esc)
        else:
            acc_p = sc.accion
            if "bit" in sc.pers and acc_p in ("explica", "senala"): acc_p = "escucha"
            dibujar_paco(d, x, SUELO_DIB, t, rng, acc_p, 0.0 if sc.habla_bit else hv, s=esc)
    # suelo
    trazo(d, [(120, SUELO_DIB + 6), (960, SUELO_DIB + 2)], rng, 7, TINTA, 1.5)
    # ---- subtitulos
    if sc.sub is not None:
        cp = sc.sub.capa(t)
        if cp:
            timg, ty = cp
            img.paste(timg, (0, ty), timg)
    # ---- sello
    if sc.sello and t >= sc.sello_t:
        st = sello_dibujo_img(sc.sello); k = min(1.0, (t - sc.sello_t) / 0.13)
        if k < 1.0:
            z = 2.0 - 1.0 * k
            st = st.resize((int(st.width * z), int(st.height * z)))
        if sc.con_objeto:
            st = st.resize((int(st.width * 0.72), int(st.height * 0.72)))
            img.paste(st, (700 - st.width // 2, 440 - st.height // 2), st)
        else:
            img.paste(st, (540 - st.width // 2, 640 - st.height // 2), st)
    # ---- camara leve (zoom/paneo por segmentos de ~3 s)
    seg = min(len(sc.cam) - 1, int(t / 3.0)); z0, dx, dy, sg = sc.cam[seg]
    ts = t - seg * 3.0
    z = z0 + 0.012 * sg * ts / 3.0
    if sc.idx > 0: z *= 1 + 0.045 * (1 - ease_out(t / 0.3))   # «punch-in» en cada corte (entra un 4,5 % mas cerca y se asienta)
    cw, ch = int(W / z), int(H / z)
    cx = int((W - cw) / 2 + dx * ts / 3.0); cy = int((H - ch) / 2 + dy * ts / 3.0)
    cx = max(0, min(W - cw, cx)); cy = max(0, min(H - ch, cy))
    img = img.crop((cx, cy, cx + cw, cy + ch)).resize((W, H), Image.BILINEAR)
    a = np.asarray(img, dtype=np.int16).copy()
    a += noise[fi % 8] // 6
    if lf < 2: a -= 10   # micro parpadeo en el corte
    np.clip(a, 0, 255, out=a)
    return a.astype(np.uint8)


# ---------------------------------------------------------------- modo "app"
# "modo": "app" (7/11/2026, SERIE APPS NEOGEST LAB, orden del usuario): reutiliza un VIDEO PROPIO de demostracion
# ("video": URL o ruta; p. ej. media_url de la entidad Publicacion de la app Base44 «Centro de Contenido Apps») con
# LOCUCION durante todo el reel. Escenas: "gancho" (texto grande + voz, ~2 s), "tramo" (trozo del video
# "clip": {"inicio", "fin"} con la voz narrando lo que se ve; el trozo se acelera hasta x1,75 para durar lo que la
# voz: sin huecos) y "cierre" (papel, palabra clave, Bit). Bit opcional ("bit": true) en gancho y cierre. Pie
# «By Neogest Lab» siempre. Audio original bajado ("volumen_original"; 0 = quitado) + ducking en publicar_gh.py; si
# el video no trae sonido, musica discreta (la del modo dibujo). Subtitulos palabra a palabra de la propia "voz".
# Video vertical: a pantalla completa. Apaisado: enmarcado a mano sobre papel (estilo dibujo).
APP = {"path": None, "w": 0, "h": 0, "dur": 0.0, "vertical": True, "audio": False, "volumen": 0.5, "primer_inicio": 0.0, "plantilla": False}
# "plantilla": true (guion app, 7/11/2026 tarde): el video es una grabacion de pantalla de herramientas/grabar_pantalla.py
# (movil/portatil sobre fondo plano suave, 1080x1920). Entonces: gancho y rotulo ARRIBA en tinta oscura (sin banda negra
# ni Ken Burns que corten el marco), subtitulos oscuros bajo el dispositivo con el unico acento cian, Bit mas abajo.
PLANT_HOOK_CY = 185       # gancho en la franja libre sobre el dispositivo (plantilla)
PLANT_ROTULO_Y = 120      # rotulo corto (plantilla)
SUB_CY_PLANT = 1502       # subtitulos bajo el dispositivo (plantilla)
MAX_VEL_APP = 1.75
APP_VID_W = 1000          # ancho del video apaisado enmarcado sobre papel
APP_VID_CY = 800          # centro vertical del video apaisado
SUB_CY_APP_V = 1330       # subtitulos sobre video vertical (por encima de la interfaz de Instagram)
SUB_CY_APP_H = 1250       # subtitulos bajo el video apaisado

def video_tiene_audio(path):
    try:
        r = subprocess.run([shutil.which("ffprobe") or "ffprobe", "-v", "error", "-select_streams", "a:0",
                            "-show_entries", "stream=codec_type", "-of", "csv=p=0", path],
                           capture_output=True, text=True, timeout=60)
        return "audio" in (r.stdout or "")
    except Exception:
        return False

def cargar_video_app(src):
    """Descarga (con cache) y sondea el video propio del guion. Si falla, el render se detiene a proposito."""
    path = descargar_video(src)
    if not path: sys.exit("modo app: no se puede descargar o leer el video %r" % (src or "")[:140])
    info = sonda_video(path)
    if not info or info[2] <= 0.3: sys.exit("modo app: video ilegible o vacio: %s" % path)
    w, h, dur = info
    APP.update(path=path, w=w, h=h, dur=dur, vertical=(w / h < 0.62 * 1.25), audio=video_tiene_audio(path))
    print("video app: %dx%d, %.1fs, %s, %s" % (w, h, dur, "vertical" if APP["vertical"] else "apaisado",
                                              "con audio" if APP["audio"] else "sin audio"))
    return APP

def fotograma_video(path, t):
    """Un fotograma (RGB) del video en el segundo t; None si falla."""
    try:
        r = subprocess.run([FFMPEG, "-v", "error", "-ss", "%.3f" % max(0.0, t), "-i", path, "-frames:v", "1",
                            "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True, timeout=120)
        import io
        return Image.open(io.BytesIO(r.stdout)).convert("RGB") if r.stdout else None
    except Exception as e:
        print("fotograma no extraido:", str(e)[:100]); return None

def audio_tramo(path, inicio, dur, vel, nsamp):
    """Audio original de un tramo (estereo, SR), acelerado como el video. Ceros si no hay pista."""
    out = np.zeros((max(0, nsamp), 2))
    if not APP["audio"] or nsamp <= 0: return out
    af = ("atempo=%.4f" % vel) if abs(vel - 1.0) > 0.01 else "anull"
    r = subprocess.run([FFMPEG, "-v", "error", "-ss", "%.3f" % inicio, "-t", "%.3f" % (dur * vel + 0.3), "-i", path,
                        "-vn", "-af", af, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True)
    a = np.frombuffer(r.stdout, "<f4").reshape(-1, 2).astype(np.float64) if r.stdout else np.zeros((0, 2))
    k = min(len(a), nsamp); out[:k] = a[:k]
    e = int(0.02 * SR)
    if k > 2 * e:
        out[:e] *= np.linspace(0, 1, e)[:, None]; out[k - e:k] *= np.linspace(1, 0, e)[:, None]
    return out

_app_cache = {}
def banda_oscura():
    """Degradado oscuro translucido tras el texto grande del gancho (video vertical)."""
    if "banda" not in _app_cache:
        yy = np.arange(H, dtype=np.float32)
        a = np.clip(1 - np.abs(yy - 740) / 420, 0, 1) ** 0.8 * 165
        arr = np.zeros((H, W, 4), np.uint8); arr[..., 3] = a.astype(np.uint8)[:, None]
        _app_cache["banda"] = Image.fromarray(arr, "RGBA")
    return _app_cache["banda"]

def pie_neogest(d, vertical):
    """Pie «By Neogest Lab» (firma de la marca) dentro de la zona segura, abajo a la derecha."""
    f = font(DJV + "DejaVuSans-Bold.ttf", 30); fs = font(DJV + "DejaVuSans-Bold.ttf", 22)
    txt = "By Neogest Lab"
    tw = d.textlength(txt, font=f); y = 1548; x1 = W - SAFE_R
    x0 = x1 - tw
    if vertical:
        d.text((x0, y), txt, font=f, fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0, 220))
    else:
        d.text((x0, y), txt, font=f, fill=TINTA + (255,))
    bx = x0 - 52
    d.rounded_rectangle([bx, y - 2, bx + 40, y + 38], 9, fill=CIAN + (255,))
    d.text((bx + 20, y + 18), "NL", font=fs, fill=(255, 255, 255, 255), anchor="mm")

def enmarcar_apaisado(fr, seed, rng):
    """Video apaisado sobre papel con marco dibujado a mano y sombra."""
    img = papel_img(seed).copy(); d = ImageDraw.Draw(img, "RGBA")
    fw, fh = fr.size
    x0 = (W - fw) // 2; y0 = APP_VID_CY - fh // 2
    d.rounded_rectangle([x0 + 10, y0 + 14, x0 + fw + 10, y0 + fh + 14], 12, fill=TINTA + (70,))
    img.paste(fr, (x0, y0))
    rect_mano(d, x0 - 6, y0 - 6, x0 + fw + 6, y0 + fh + 6, rng, 10, radio=14, amp=2.0)
    return img

def preparar_app(sc, spec, rng):
    """Prepara una escena en modo app: tramo de video (acelerado a la voz), gancho, cierre, subtitulos y Bit."""
    sc.estilo_a = str(spec.get("estilo") or "tramo").strip().lower()
    if sc.estilo_a not in ("gancho", "tramo", "cierre"): sc.estilo_a = "tramo"
    sc.bit = bool(spec.get("bit", sc.estilo_a == "cierre"))
    sc.accion_bit = str(spec.get("accion") or ("celebra" if sc.estilo_a == "cierre" else "sorprendido")).strip().lower()
    clip = spec.get("clip") if isinstance(spec.get("clip"), dict) else {}
    ini = clip.get("inicio", spec.get("inicio")); fin = clip.get("fin", spec.get("fin"))
    sc.clip = None; sc.still = None; sc.vel = 1.0; sc.ini = None
    vert = APP["vertical"]
    if sc.estilo_a != "cierre":
        if ini is None and sc.estilo_a == "gancho":   # gancho sin tramo: fotograma fijo del primer tramo
            st = fotograma_video(APP["path"], APP["primer_inicio"])
            if st is not None:
                if vert: sc.still = st.resize((W, H), Image.LANCZOS) if APP["plantilla"] else preparar_foto(st, 1.10)
                else: sc.still = st.resize((APP_VID_W, max(2, int(st.height * APP_VID_W / st.width))), Image.LANCZOS)
        if sc.still is None:
            ini = max(0.0, min(float(ini if ini is not None else APP["primer_inicio"]), max(0.0, APP["dur"] - 0.5)))
            largo = (min(float(fin), APP["dur"]) - ini) if fin is not None else sc.dur
            vel = float(clip.get("velocidad") or spec.get("velocidad") or 0)
            if vel <= 0: vel = min(MAX_VEL_APP, max(1.0, largo / max(0.3, sc.dur)))
            sc.vel = min(2.0, max(0.5, vel))
            sc.clip = Clip(APP["path"], ini, sc.dur, zoom_max=1.0, velocidad=sc.vel, bucle=False, app=True)
            if not sc.clip.ok: sys.exit("modo app: no se pudo extraer el tramo %.1f-%s del video" % (ini, fin))
            sc.ini = ini
            if fin is not None and largo / sc.vel > sc.dur + 1.5:
                print("aviso: el tramo %.1f-%.1f (x%.2f) dura mas que su voz; se corta en %.1f s" % (ini, float(fin), sc.vel, sc.dur))
    # subtitulos (misma logica que el modo dibujo: voz real si hay tiempos)
    voz, enf_voz = parsear_enfasis(spec.get("voz") or "")
    texto, enf_txt = parsear_enfasis(spec.get("texto") or "")
    dv = float(spec.get("_voz_dur") or 0)
    tiempos = spec.get("_voz_palabras")
    if tiempos and len(tiempos) == len(voz.split()):
        tiempos = [float(x) + 0.12 for x in tiempos]
    else:
        tiempos = None
    if dv > 0.2:
        wps = len(voz.split()) / max(0.3, dv - 0.1)
    else:
        wps = max(WPS_HUMANO, len(voz.split()) / max(0.3, sc.dur * 0.8))
    sobre_video = vert and sc.estilo_a != "cierre"
    plant = bool(APP["plantilla"]) and vert and sc.estilo_a != "cierre"
    if plant:
        est = dict(fill=TINTA, stroke=(255, 255, 255), activo=CIAN, enfasis=TINTA, marca=True, grosor=14, cy=SUB_CY_PLANT, smax=74, smin=50, bottom_max=1540)
    elif sobre_video:
        est = dict(fill=(255, 255, 255), stroke=(0, 0, 0), activo=CIAN, enfasis=TINTA, marca=True, grosor=11, cy=SUB_CY_APP_V, smax=96, smin=56)
    else:
        est = dict(fill=TINTA, stroke=PAPEL, activo=CIAN, enfasis=TINTA, marca=True, cy=(1330 if sc.estilo_a == "cierre" else SUB_CY_APP_H), smax=88, smin=54)
    sc.sub = None; sc.grande = None; sc.rotulo = None
    if sc.estilo_a == "gancho":
        base, enf = (texto, enf_txt) if texto else (voz, enf_voz)
        est_g = dict(est, cy=(PLANT_HOOK_CY if plant else (720 if vert else 290)), smax_entero=(80 if plant else (112 if vert else 90)), gancho_2_lineas=plant)
        sc.grande = Subtitulos(base, wps, 0.0, sc.dur, entero=True, enfasis=enf, estilo=est_g) if base else None
    else:
        sc.sub = Subtitulos(voz, wps, 0.12, sc.dur, enfasis=enf_voz, tiempos=tiempos, estilo=est) if voz else None
        env = spec.get("_voz_env")
        sc.env = [min(1.0, max(0.0, float(x))) for x in env] if isinstance(env, list) and env else None
        if texto:
            sc.rotulo = rotulo_humano(texto) if (sobre_video and not plant) else rotulo_dibujo(texto, grande=(sc.estilo_a == "cierre"))

def render_frame_app(fi, sc, noise, rg, seed):
    lf = fi - sc.start; t = lf / FPS
    rng = random.Random(seed * 31 + sc.idx * 101 + fi // 4)
    vert = APP["vertical"]
    sobre_video = vert and sc.estilo_a != "cierre" and (sc.clip is not None or sc.still is not None)
    plant = bool(APP["plantilla"]) and sobre_video
    if sc.clip is not None:
        fr = sc.clip.frame(lf)
        if vert:
            img = fr.crop((0, 0, W, H)).copy() if fr.size != (W, H) else fr.copy()
        else:
            img = enmarcar_apaisado(fr, seed, rng)
    elif sc.still is not None and plant:
        img = sc.still.copy()
    elif sc.still is not None:
        if vert:   # zoom lento (Ken Burns) sobre el fotograma fijo
            fw, fh = sc.still.size; z = 1.0 + 0.06 * min(1.0, t / 3.0)
            cw, ch = min(fw, int(W * 1.10 / z)), min(fh, int(H * 1.10 / z))
            cx = (fw - cw) // 2; cy = (fh - ch) // 2
            img = sc.still.crop((cx, cy, cx + cw, cy + ch)).resize((W, H), Image.BILINEAR)
        else:
            img = enmarcar_apaisado(sc.still, seed, rng)
    elif APP["plantilla"] and APP.get("fondo"):
        img = Image.new("RGB", (W, H), APP["fondo"])   # cierre en plantilla: el mismo fondo plano de la grabacion
    else:
        img = papel_img(seed).copy()
    d = ImageDraw.Draw(img, "RGBA")
    # ---- gancho: texto grande (entra con un pequeno "pop")
    if sc.grande is not None:
        if sobre_video and not plant:
            img.paste(banda_oscura(), (0, 0), banda_oscura())
        cp = sc.grande.capa(t)
        if cp:
            timg, ty = cp
            k = ease_out(t / 0.22); z = 0.82 + 0.18 * k
            if z < 0.999:
                tw2, th2 = int(timg.width * z), int(timg.height * z)
                timg2 = timg.resize((tw2, th2), Image.BILINEAR)
                img.paste(timg2, ((W - tw2) // 2, ty + (timg.height - th2) // 2), timg2)
            else:
                img.paste(timg, (0, ty), timg)
    # ---- rotulo (tramo / cierre)
    if sc.rotulo is not None:
        k = ease_out(t / 0.3); ro = sc.rotulo
        if k < 1.0: ro = ro.crop((0, 0, max(1, int(W * k)), ro.height))
        img.paste(ro, (0, PLANT_ROTULO_Y if plant else (170 if not sobre_video else 200)), ro)
    # ---- Bit (gancho: abajo a la derecha sobre un circulo de papel; cierre: en el centro celebrando)
    if sc.bit and sc.estilo_a in ("gancho", "cierre"):
        habla = boca(sc, t) if sc.sub is not None else ((0.45 + 0.55 * abs(math.sin(t * 17.0))) if t < max(0.6, sc.dur - 0.4) else 0.0)   # apertura 0-1 (voz real)
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dc = ImageDraw.Draw(capa, "RGBA")
        if sc.estilo_a == "cierre":
            k = ease_out(t / 0.45)
            cx = 540; base = 1140
            dibujar_bit(dc, cx, base - int((1 - k) * 60), t, rng, sc.accion_bit if sc.accion_bit in ("celebra", "explica", "sorprendido", "senala") else "celebra", habla, s=1.0)
            trazo(dc, [(300, base + 6), (780, base + 2)], rng, 7, TINTA, 1.5)
        else:
            k = ease_out(t / 0.45); s = 0.62
            cx = 880 + int((1 - k) * 420); base = (1400 if vert else 1465)
            if plant: s = 0.42; cx = 910 + int((1 - k) * 420); base = 1640
            circulo(dc, cx, base - 130 * s, 190 * s, rng, 7, relleno=PAPEL, amp=2.5)
            dibujar_bit(dc, cx, base, t, rng, sc.accion_bit if sc.accion_bit in ("celebra", "explica", "sorprendido", "senala") else "sorprendido", habla, s=s)
        img.paste(capa, (0, 0), capa)
    # ---- subtitulos palabra a palabra
    if sc.sub is not None:
        cp = sc.sub.capa(t)
        if cp:
            timg, ty = cp
            img.paste(timg, (0, ty), timg)
    pie_neogest(d, sobre_video and not plant)
    a = np.asarray(img, dtype=np.int16).copy()
    a += noise[fi % 8] // 8
    if lf < 3: a += int(10 * (3 - lf))   # parpadeo minimo en el corte
    np.clip(a, 0, 255, out=a)
    return a.astype(np.uint8)


# ---------------------------------------------------------------- escena
class Scene:
    def __init__(self, idx, sc, seed, title, nframes, start_frame):
        self.idx, self.style = idx, sc.get("estilo", "evidencia")
        if self.style not in PAL: self.style = "evidencia"
        rng = random.Random(seed * 1000 + idx * 7 + int(hashlib.md5(sc.get("visual", "").encode()).hexdigest()[:4], 16))
        self.rng = rng
        self.bg = make_bg(self.style, rng)
        self.P = make_params(self.style, rng, sc.get("visual", ""))
        # con lista o linea de tiempo el texto baja un poco para dejar sitio a la prueba (sigue dentro de y 500-1450)
        cy = 1150 if (sc.get("lista") or sc.get("fechas")) else (1060 if sc.get("cifra") else TEXT_CY)
        self.tb = TextBlock(sc.get("texto", ""), self.style, cy)
        self.nframes, self.start = nframes, start_frame
        self.dur = nframes / FPS
        cps = min(CPS[self.style], max(14, self.tb.nchars / max(0.4, self.dur * 0.6)))
        self.cps = max(cps, self.tb.nchars / max(0.3, self.dur * 0.75))
        if self.style == "gancho":  # estandar: el gancho se lee entero sin sonido en < 2 s
            self.cps = max(self.cps, self.tb.nchars / 0.45)  # sin retardo: entero a los 0,45 s
        self.exp = "%04d-%s" % (rng.randint(100, 9999), rng.choice("ABCDEFKX"))
        self.delay = 0.35 if self.style == "giro" else (0.0 if self.style == "gancho" else 0.12)
        # recursos que PRUEBAN el dato (sustituyen al dibujo decorativo): cifra, fechas o lista
        self.cifra = str(sc.get("cifra") or "").strip()
        self.unidad = str(sc.get("unidad") or "").strip()
        self.fechas = [f for f in (sc.get("fechas") or []) if isinstance(f, dict) and str(f.get("anio", "")).strip()][:4]
        self.lista = [str(x).strip() for x in (sc.get("lista") or []) if str(x).strip()][:3]
        # sello de veredicto opcional ("sello": "FALSO" | "REAL" ...): cae de golpe sobre la escena
        self.sello = str(sc.get("sello") or "").strip().upper()[:12]
        self.sello_t = float(sc.get("sello_t", 0.5 if self.style == "giro" else 0.25))
        self.sello_t = min(max(self.sello_t, 0.0), max(0.0, self.dur - 0.6))
        if MODO["humano"]:
            preparar_humano(self, sc, rng)
        elif MODO["dibujo"]:
            preparar_dibujo(self, sc, rng)
        elif MODO["sketch"]:
            _sk().preparar(self, sc, rng)
        elif MODO["datos"]:
            _dt().preparar(self, sc, rng)
        elif MODO["app"]:
            preparar_app(self, sc, rng)

def hud(d, scene, t_abs, date_s, title):
    f = font(MONO, 44); fs = font(MONO, 32)
    ts = 3 * 3600 + 17 * 60 + 42 + int(t_abs)
    tm = "%02d:%02d:%02d" % ((ts // 3600) % 24, (ts // 60) % 60, ts % 60)
    dot_on = int(t_abs * 2) % 2 == 0
    x = SAFE_L + 10
    d.text((x, 165), "REC", font=f, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))
    if dot_on: d.text((x + 100, 165), "●", font=f, fill=(235, 30, 30), stroke_width=4, stroke_fill=(0, 0, 0))
    d.text((x + 160, 165), tm, font=f, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))
    d.text((x, 222), date_s + "  CAM 02", font=fs, fill=(230, 230, 230), stroke_width=3, stroke_fill=(0, 0, 0))
    d.text((W - SAFE_R - 10 - 190, 1500), "SP ▶ LP", font=fs, fill=(230, 230, 230), stroke_width=3, stroke_fill=(0, 0, 0))
    if scene.style == "archivo":
        acc = PAL["archivo"][1]
        L = 60; x0, y0, x1, y1 = SAFE_L, 285, W - SAFE_R, 1560
        for (ax, ay, sx, sy) in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)]:
            d.line([(ax, ay), (ax + sx * L, ay)], fill=acc, width=6)
            d.line([(ax, ay), (ax, ay + sy * L)], fill=acc, width=6)
        d.text((x0 + 18, y0 + 14), "EXPEDIENTE N.º " + scene.exp, font=font(MONO, 34), fill=acc, stroke_width=3, stroke_fill=(0, 0, 0))
    if scene.style in ("archivo", "evidencia") and title:
        d.text((150, 1512), (title if len(title) <= 28 else title[:27].rstrip() + "\u2026").upper(), font=font(MONO, 26), fill=(190, 190, 190), stroke_width=2, stroke_fill=(0, 0, 0))

_stamp = {}
def stamp_img():
    if "s" not in _stamp:
        im = Image.new("RGBA", (620, 170), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([6, 6, 614, 164], 12, outline=(220, 40, 40, 235), width=9)
        f = font(DJV + "DejaVuSansCondensed-Bold.ttf", 84)
        d.text((310, 88), "CLASIFICADO", font=f, fill=(220, 40, 40, 235), anchor="mm")
        _stamp["s"] = im.rotate(8, expand=True, resample=Image.BICUBIC)
    return _stamp["s"]

_veredicto = {}
def veredicto_img(txt):
    """Sello grande de veredicto (¿REAL O FALSO?): rojo si es FALSO, verde si es REAL/VERDADERO/CIERTO."""
    if txt not in _veredicto:
        if txt.startswith("FALS") or txt in ("MITO", "BULO", "MENTIRA"): col = (232, 38, 38)
        elif txt in ("REAL", "VERDAD", "VERDADERO", "CIERTO", "CONFIRMADO"): col = (60, 215, 105)
        else: col = (240, 190, 60)
        path = DJV + "DejaVuSansCondensed-Bold.ttf"; probe = ImageDraw.Draw(Image.new("L", (4, 4)))
        size = 168
        while size > 80 and probe.textlength(txt, font=font(path, size)) > 640: size -= 6
        f = font(path, size); tw = int(probe.textlength(txt, font=f))
        bw, bh = tw + 110, int(size * 1.25) + 60
        im = Image.new("RGBA", (bw + 20, bh + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([10, 10, bw + 10, bh + 10], 22, fill=(0, 0, 0, 170), outline=col + (255,), width=14)
        d.rounded_rectangle([30, 30, bw - 10, bh - 10], 14, outline=col + (200,), width=5)
        d.text(((bw + 20) // 2, (bh + 20) // 2), txt, font=f, fill=col + (255,), anchor="mm",
               stroke_width=4, stroke_fill=(0, 0, 0, 255))
        _veredicto[txt] = im.rotate(-7, expand=True, resample=Image.BICUBIC)
    return _veredicto[txt]

def build_noise(seed):
    rg = np.random.default_rng(seed)
    out = []
    for _ in range(8):
        n = rg.normal(0, 9, (H // 2, W // 2)).astype(np.int16)
        out.append(np.repeat(np.repeat(n, 2, 0), 2, 1)[:, :, None])
    return out

def render_frame(fi, scenes, noise, date_s, title, rg):
    sc = next(s for s in scenes if fi < s.start + s.nframes)
    if MODO["humano"]:
        return render_frame_humano(fi, sc, noise, rg)
    if MODO["dibujo"]:
        return render_frame_dibujo(fi, sc, noise, rg, SEMILLA["v"])
    if MODO["sketch"]:
        return _sk().render_frame(fi, sc, noise, rg, SEMILLA["v"])
    if MODO["datos"]:
        return _dt().render_frame(fi, sc, noise, rg, SEMILLA["v"])
    if MODO["app"]:
        return render_frame_app(fi, sc, noise, rg, SEMILLA["v"])
    lf = fi - sc.start; t = lf / FPS; ta = fi / FPS
    img = sc.bg.copy()
    d = ImageDraw.Draw(img, "RGBA")
    if not draw_prueba(sc, d, t):
        draw_visual(sc.style, d, t, sc.P)
    glitch = sc.style == "giro" and lf < 14
    n = int(max(0, t - sc.delay) * sc.cps) + (1 if t > sc.delay else 0)
    timg, ty = sc.tb.get(n)
    jx = jy = 0
    if glitch: jx, jy = rg.randint(-14, 14), rg.randint(-6, 6)
    img.paste(timg, (jx, ty + jy), timg)
    hud(d, sc, ta, date_s, title)
    if sc.style == "archivo" and t > 0.8:
        st = stamp_img(); k = min(1.0, (t - 0.8) / 0.12)
        if k < 1.0:
            sz = (int(st.width * (1.8 - 0.8 * k)), int(st.height * (1.8 - 0.8 * k)))
            st = st.resize(sz)
        img.paste(st, (540 - st.width // 2, 1360 - st.height // 2), st)
    impacto = 0
    if sc.sello and t >= sc.sello_t:
        st = veredicto_img(sc.sello); k = min(1.0, (t - sc.sello_t) / 0.13)
        if k < 1.0:
            z = 2.3 - 1.3 * k
            st = st.resize((int(st.width * z), int(st.height * z)))
            al = st.getchannel("A").point(lambda v: int(v * (0.35 + 0.65 * k))); st.putalpha(al)
        else:
            impacto = int((t - sc.sello_t - 0.13) * FPS)
        sx, sy = (rg.randint(-12, 12), rg.randint(-8, 8)) if 0 <= impacto < 4 and k >= 1.0 else (0, 0)
        img.paste(st, (540 - st.width // 2 + sx, 490 - st.height // 2 + sy), st)
    a = np.asarray(img, dtype=np.int16).copy()
    if glitch:
        for _ in range(rg.randint(4, 8)):
            y = rg.randrange(0, H - 120); h = rg.randint(20, 160)
            a[y:y + h] = np.roll(a[y:y + h], rg.randint(-70, 70), axis=1)
        a[:, :, 0] = np.roll(a[:, :, 0], 14, axis=1); a[:, :, 2] = np.roll(a[:, :, 2], -14, axis=1)
        if lf % 5 == 0: a[:, :, :] = 255 - a[:, :, :]
        a = np.roll(a, (rg.randint(-10, 10), rg.randint(-18, 18)), axis=(0, 1))
    rows = np.arange(H)
    vec = np.where(rows % 4 == 0, -14, 0).astype(np.int16)
    band = int((ta * 190) % (H + 400)) - 200
    vec += (24 * np.exp(-((rows - band) / 60.0) ** 2)).astype(np.int16)
    flick = int(rg.randint(-5, 5)) + (int(90 * (1 - lf / 5)) if lf < 5 else 0)
    if sc.style == "giro" and lf < 5: flick += 40
    if sc.sello and t >= sc.sello_t + 0.13 and impacto < 3: flick += 55 - 15 * impacto  # destello del golpe
    vec += flick
    a += noise[fi % 8]
    a += vec[:, None, None]
    np.clip(a, 0, 255, out=a)
    return a.astype(np.uint8)

# ---------------------------------------------------------------- audio
FFMPEG = shutil.which("ffmpeg") or "/usr/local/bin/ffmpeg"

def midi_hz(m):
    return 440.0 * 2.0 ** ((m - 69) / 12.0)

def lowpass_sweep(x, a0, a1):
    n = len(x); out = np.empty(n); y = 0.0
    al = np.linspace(a0, a1, n)
    for i in range(n):
        y += al[i] * (x[i] - y); out[i] = y
    return out

def lp_fft(x, fc, order=2):
    """Paso bajo de fase cero por FFT (rapido, sin bucles)."""
    n = len(x)
    f = np.fft.rfftfreq(n, 1.0 / SR)
    return np.fft.irfft(np.fft.rfft(x) / np.sqrt(1.0 + (f / fc) ** (2 * order)), n)

def adsr(n, hold, A, D, S, R):
    hold = max(hold, A + D + 1)
    return np.interp(np.arange(n), [0, A, A + D, hold, hold + R], [0, 1, S, S, 0]).astype(np.float32)

def comb(x, D, g):
    y = x.copy()
    for s in range(D, len(x), D):
        e = min(s + D, len(x)); y[s:e] += g * y[s - D:e - D]
    return y

def allpass(x, D, g):
    y = -g * x
    for s in range(D, len(x), D):
        e = min(s + D, len(x)); y[s:e] += x[s - D:e - D] + g * y[s - D:e - D]
    return y

def reverb(x, right=False, g=0.86):
    """Reverb tipo Schroeder: 6 peines con amortiguacion + 2 pasa-todo."""
    dl = [1116, 1188, 1277, 1356, 1422, 1491]
    if right: dl = [d + 23 for d in dl]
    xin = lp_fft(x, 3200, 1)
    y = sum(comb(xin, d, g) for d in dl) * (1 - g) / len(dl) * 2.2
    for d, gg in ((556, 0.5), (441, 0.5)):
        y = allpass(y, d + (11 if right else 0), gg)
    return y

def add_at(buf, sig, t0):
    i0 = int(round(t0 * SR))
    if i0 >= len(buf): return
    i1 = min(len(buf), i0 + len(sig))
    if i0 < 0:
        sig = sig[-i0:]; i0 = 0
    buf[i0:i1] += sig[:i1 - i0]

def lufs(st):
    """LUFS integrados (ffmpeg ebur128) de un array estereo float."""
    f = tempfile.NamedTemporaryFile(suffix=".f32", delete=False)
    try:
        f.write(st.astype("<f4").tobytes()); f.close()
        r = subprocess.run([FFMPEG, "-nostats", "-hide_banner", "-f", "f32le", "-ar", str(SR), "-ac", "2",
                            "-i", f.name, "-af", "ebur128=framelog=quiet", "-f", "null", "-"],
                           capture_output=True, text=True)
        m = re.findall(r"\bI:\s+(-?\d+\.?\d*)\s+LUFS", r.stderr)
        return float(m[-1]) if m else -70.0
    finally:
        os.remove(f.name)

PROGS_MAYOR = [  # modo dibujo: progresiones mayores, alegres (I-V-vi-IV, I-IV-V-IV, I-vi-IV-V)
    [(0, "M"), (7, "M"), (9, "m"), (5, "M")],
    [(0, "M"), (5, "M"), (7, "M"), (5, "M")],
    [(0, "M"), (9, "m"), (5, "M"), (7, "M")],
]
PROGS = [  # (semitonos de la raiz, calidad) en tonalidad menor
    [(0, "m"), (8, "M"), (3, "M"), (10, "M")],   # i  VI III VII
    [(0, "m"), (5, "m"), (8, "M"), (7, "M")],    # i  iv VI  V
    [(0, "m"), (7, "m"), (8, "M"), (5, "m")],    # i  v  VI  iv
    [(0, "m"), (3, "M"), (5, "m"), (8, "M")],    # i  III iv VI
    [(0, "m"), (10, "M"), (8, "M"), (7, "m")],   # i  VII VI v
]

def saw_voice(f, n, ph0):
    t = np.arange(n, dtype=np.float32) / SR
    ph = 2 * np.pi * f * t + 0.6 * np.sin(2 * np.pi * 0.23 * t + ph0)
    out = np.zeros(n, np.float32)
    for k in range(1, 9):
        if k * f > 5000: break
        out += np.sin(k * ph + k * ph0) / k
    return out

# Silencio de musica justo antes del giro (s). Antes 1,0 s: en el 002 real dejaba la mezcla a -53 LUFS
# casi un segundo. Las guias de retencion piden 0,3-0,5 s de pausa antes de una revelacion.
CORTE_GIRO = 0.5


def ajustar_rejilla(cortes, beat0, lo=94.0, hi=124.0):
    """Cortes AL GOLPE (modo dibujo/app): elige el tempo (lo-hi bpm, paso 0,1) y el desfase de la rejilla de pulsos
    para que cada corte de escena caiga lo mas cerca posible de un pulso (minimo error cuadratico medio).
    Devuelve (beat_s, fase_s, info) con el error medio/maximo en ms antes (beat0, fase 0) y despues."""
    c = np.asarray([x for x in cortes if x > 0.2], dtype=np.float64)
    def dist(b, fase):
        return np.abs(((c[None, :] - fase[:, None] + b / 2) % b) - b / 2)
    f0 = np.zeros(1)
    d0 = dist(beat0, f0)[0] if len(c) else np.zeros(1)
    info = {"antes_ms": round(float(d0.mean()) * 1000, 1), "antes_max_ms": round(float(d0.max()) * 1000, 1)}
    if len(c) < 2:
        info.update(despues_ms=info["antes_ms"], despues_max_ms=info["antes_max_ms"])
        return beat0, 0.0, info
    mejor = (1e9, beat0, 0.0)
    for bpm in np.arange(lo, hi + 1e-6, 0.1):
        b = 60.0 / bpm
        fases = np.arange(0.0, b, 0.004)
        d = dist(b, fases)
        e = np.sqrt((d ** 2).mean(axis=1))
        i = int(np.argmin(e))
        if e[i] < mejor[0] - 1e-9: mejor = (float(e[i]), b, float(fases[i]))
    _, b, fase = mejor
    d1 = dist(b, np.asarray([fase]))[0]
    info.update(despues_ms=round(float(d1.mean()) * 1000, 1), despues_max_ms=round(float(d1.max()) * 1000, 1))
    return b, fase, info

def _golpe(tipo, rg, v=1.0):
    """Percusion sintetica de los modos dibujo/app (clap, hat, caja)."""
    if tipo == "clap":
        m = int(0.22 * SR); t = np.arange(m) / SR
        x = lp_fft(rg.standard_normal(m), 6500, 2) - lp_fft(rg.standard_normal(m), 1100, 2)
        env = np.exp(-t * 24)
        for d, a in ((0.011, 0.75), (0.022, 0.55)):
            env = env + a * np.exp(-np.maximum(t - d, 0) * 24) * (t > d)
        return (x * env * 1.05 + 0.35 * np.sin(2 * np.pi * 185 * t) * np.exp(-t * 28)) * v
    if tipo == "hat":
        m = int(0.07 * SR); t = np.arange(m) / SR
        x = rg.standard_normal(m); x = x - lp_fft(x, 7500, 2)
        return x * np.exp(-t * 75) * 0.55 * v
    m = int(0.16 * SR); t = np.arange(m) / SR   # caja (relleno)
    x = lp_fft(rg.standard_normal(m), 5200, 2) - lp_fft(rg.standard_normal(m), 900, 2)
    return (x * np.exp(-t * 32) * 0.9 + 0.5 * np.sin(2 * np.pi * 210 * t) * np.exp(-t * 38)) * v

INFO_MUSICA = {}


def make_music(scenes, n, seed, gs, hook_end):
    rng = random.Random(seed * 7919 + 13)
    total = n / SR
    try:   # 10/11/2026 (orden del dueno): pistas reales SIN DERECHOS de musica/ (con ficha de licencia en musica/pistas.json)
        import pistas as _pi
        ficha = _pi.elegir("reel%s" % seed) if _pi.hay_pistas() else None
        if ficha:
            mL, mR, info_p = _pi.segmento(ficha, n, SR, [s.start / FPS for s in scenes[1:]], total)
            INFO_MUSICA.clear(); INFO_MUSICA.update(info_p, atribucion=ficha.get("atribucion", ""), url=ficha.get("url", ""))
            return mL, mR, np.ones(n), info_p
    except Exception as e:
        print("pistas no disponibles (%s): se sigue con la musica generada" % e)
    bpm = rng.uniform(70, 90); beat = 60.0 / bpm
    if modo_alegre(): bpm = rng.uniform(98, 110); beat = 60.0 / bpm   # dibujo/app: mas vivo
    fase = 0.0; rejilla = None
    if modo_alegre():   # tempo y fase de la rejilla elegidos para que los cortes caigan en un pulso
        beat, fase, rejilla = ajustar_rejilla([s.start / FPS for s in scenes[1:]], beat)
        try:   # 10/11/2026 (queja «parece de ascensor»): pista con bombo, bajo 808, palmas, hats y melodia que ENGANCHA
            import musica_viral as _mv   # herramientas/musica_viral.py (numpy, sin licencias); si falla, cae al colchon antiguo
            estilo_mv = ("dembow", "phonk", "house")[rng.randrange(3)]
            cortes_mv = [0.0] + [s.start / FPS for s in scenes[1:]]
            mL, mR, info_mv = _mv.generar(n, SR, beat, fase, cortes_mv, seed, estilo=estilo_mv, total=total)
            info_mv.update(cortes_al_golpe=rejilla, motor="musica_viral")
            return mL, mR, np.ones(n), info_mv
        except Exception as e:
            print("musica_viral no disponible (%s): se usa la musica antigua" % e)
    cut0 = gs - CORTE_GIRO if (gs and gs >= 3.0) else None
    if gs and gs >= 3.0:  # que el giro caiga en un pulso
        b2 = gs / max(1, round(gs / beat))
        if 70 <= 60 / b2 <= 90: beat = b2
    key = rng.randrange(12); base = 38 + key
    prog = rng.choice(PROGS_MAYOR if modo_alegre() else PROGS); add9 = rng.random() < 0.5
    box = rng.random() < 0.5
    tr1 = cut0
    tr0 = max(hook_end + 0.5, tr1 - 3.2) if cut0 else None
    if cut0 and tr1 - tr0 < 1.2: tr0 = None
    # ---- segmentos de acordes
    segs = []
    def run(ts, te, att0):
        t, i = ts, 0
        while t < te - 0.05:
            segs.append((t, min(t + 8 * beat, te), i % 4, att0 if i == 0 else 1.4)); t += 8 * beat; i += 1
    if cut0:
        run(0.0, cut0, 1.4); run(gs, total, 0.05)
    else:
        run(0.0, total, 1.4)
    def tones(ci):
        off, q = prog[ci]
        return [off, off + (3 if q == "m" else 4), off + 7], q
    def fold(m, lo, hi):
        while m >= hi: m -= 12
        while m < lo: m += 12
        return m
    # ---- kicks (entran tras el gancho; callan en el corte)
    kicks = []
    def kick_run(ts, te):
        k = int(math.ceil(ts / beat - 1e-6))
        while k * beat < te - 0.02:
            kicks.append((k * beat, 1.0 if k % 4 == 0 else 0.72)); k += 1
    acentos = set()
    if modo_alegre():
        # dibujo/app: bombo en los tiempos 1 y 3 de cada compas (mas fuerte donde cae un corte de escena); la caja, el
        # hi-hat y los rellenos se anaden despues de desplazar la rejilla por `fase`. Suena desde el segundo 0.
        tr0 = None
        acentos = {int(round((s.start / FPS - fase) / beat)) for s in scenes[1:]}
        k = 0
        while k * beat < total - fase - 0.02:
            if k % 4 in (0, 2) or k in acentos:
                kicks.append((k * beat, (1.0 if k % 4 == 0 else 0.85) * (1.3 if k in acentos else 1.0)))
            k += 1
    elif modo_suave():
        tr0 = None            # modo humano: sin subida de tension ni bombo, solo colchon y arpegio
    elif cut0:
        kick_run(hook_end, cut0); kick_run(gs, total); kicks.append((gs, 1.5))
    else:
        kick_run(hook_end, total)
    duck = np.ones(n)
    kt = np.arange(int(0.3 * SR)) / SR
    kd = 1 - 0.3 * np.exp(-kt / 0.1)
    for tk, v in kicks:
        i0 = int(tk * SR)
        if i0 < n:
            i1 = min(n, i0 + len(kd)); duck[i0:i1] = np.minimum(duck[i0:i1], kd[:i1 - i0])
    # ---- PAD
    padL = np.zeros(n); padR = np.zeros(n); bass = np.zeros(n)
    for (t0, t1, ci, att) in segs:
        iv, q = tones(ci)
        notes = [fold(base + 12 + x, 50, 68) for x in iv] + [fold(base + 12 + iv[0], 50, 68) + 12]
        if add9 and q == "m": notes.append(fold(base + 12 + iv[0] + 14, 50, 74))
        hold = int((t1 - t0) * SR); R = int(2.0 * SR)
        m = min(hold + R, n - int(t0 * SR))
        if m <= 0: continue
        env = adsr(m, hold, int(att * SR), int(0.8 * SR), 0.75, R)
        for j, nt in enumerate(notes):
            f = midi_hz(nt); amp = 0.5 if j == 3 else (0.3 if j == 4 else 1.0)
            c0 = saw_voice(f, m, j); cm = saw_voice(f * 2 ** (-7 / 1200), m, j + 1); cp = saw_voice(f * 2 ** (7 / 1200), m, j + 2)
            add_at(padL, (cm + 0.7 * c0) * env * amp, t0); add_at(padR, (cp + 0.7 * c0) * env * amp, t0)
        fb = midi_hz(fold(base + iv[0], 31, 43)); tt = np.arange(m) / SR
        add_at(bass, np.sin(2 * np.pi * fb * tt) * adsr(m, hold, int(0.05 * SR), int(0.3 * SR), 0.8, int(0.5 * SR)), t0)
    tt = np.arange(n) / SR
    bass *= np.clip((tt - hook_end) / 1.0, 0, 1) * 0.55
    # filtro: oscuro en el gancho, abre hacia el giro
    w = np.full(n, 0.55 if modo_alegre() else 0.15)   # dibujo/app: colchon mas brillante
    if tr0: w[int(tr0 * SR):int(tr1 * SR)] = np.linspace(0.15, 1.0, int(tr1 * SR) - int(tr0 * SR))
    if cut0: w[int(gs * SR):] = 0.7
    padL = (lp_fft(padL, 850) * (1 - w) + lp_fft(padL, 2600) * w) * duck
    padR = (lp_fft(padR, 850) * (1 - w) + lp_fft(padR, 2600) * w) * duck
    padL *= 0.55; padR *= 0.55
    # ---- ARPEGIO caja de musica / pluck
    arpL = np.zeros(n); arpR = np.zeros(n)
    partials = [(1, 1.0, 0.9), (2.0, 0.4, 0.45), (4.2, 0.14, 0.2), (6.9, 0.05, 0.1)] if box else \
               [(k, 1.0 / k, 0.55 / k ** 0.6) for k in range(1, 6)]
    lo, hi = (67, 91) if box else (60, 84)
    pat_rng = {}
    ts = math.ceil(0.5 / (beat / 2)) * beat / 2; step_i = 0; idx_state = {}
    while ts < total - 0.4:
        in_riser = bool(tr0) and tr0 <= ts < tr1
        step = beat / 4 if in_riser else beat / 2
        if cut0 and cut0 <= ts < gs: ts = gs; continue
        seg = next((s for s in segs if s[0] <= ts < s[1]), None)
        if seg:
            ci = seg[2]; iv, q = tones(ci)
            pcs = {(base + x) % 12 for x in iv}
            pool = [m for m in range(lo, hi) if m % 12 in pcs]
            r2 = pat_rng.setdefault(ci, random.Random(seed * 31 + ci))
            k = idx_state.get(ci, len(pool) // 2)
            k = max(0, min(len(pool) - 1, k + r2.choice([-2, -1, 1, 2, 1, -1])))
            idx_state[ci] = k
            on_beat = abs((ts / beat) - round(ts / beat)) < 1e-3
            if on_beat or rng.random() > 0.2:
                vel = (0.55 + 0.35 * on_beat) * (0.75 if ts < hook_end else 1.0) * (1.2 if (gs and ts >= gs) else 1.0)
                if in_riser: vel *= 1 + 0.8 * (ts - tr0) / (tr1 - tr0)
                f = midi_hz(pool[k]); m = int(2.2 * SR); tn = np.arange(m, dtype=np.float32) / SR
                sig = np.zeros(m, np.float32)
                for (rat, a, tau) in partials:
                    if f * rat < 9000:
                        sig += a * np.sin(2 * np.pi * f * rat * tn) * np.exp(-tn / tau)
                sig *= np.minimum(1, tn / 0.003) * vel
                pan = 0.35 if step_i % 2 == 0 else 0.65
                add_at(arpL, sig * (1 - pan) * 1.4, ts); add_at(arpR, sig * pan * 1.4, ts)
        ts += step; step_i += 1
    arpL *= 0.22; arpR *= 0.22
    echo = comb((arpL + arpR) * 0.5, int(0.75 * beat * SR), 0.45) - (arpL + arpR) * 0.5
    arpL += 0.6 * echo; arpR += 0.6 * np.roll(echo, int(0.013 * SR))
    # ---- KICK
    m = int(0.5 * SR); tk_ = np.arange(m) / SR
    kw = np.sin(2 * np.pi * np.cumsum(46 + 95 * np.exp(-tk_ * 30)) / SR) * np.exp(-tk_ * 6.5) * np.minimum(1, tk_ / 0.002)
    kw += 0.12 * np.random.default_rng(seed).standard_normal(m) * np.exp(-tk_ * 400)
    kick = np.zeros(n)
    for tkk, v in kicks: add_at(kick, kw * v, tkk)
    kick *= 0.62 if modo_alegre() else 1.1
    # ---- SUBIDA DE TENSION
    riser = np.zeros(n)
    if tr0:
        m = int((tr1 - tr0) * SR); pr = np.arange(m) / m; tr_ = np.arange(m) / SR
        nz = np.random.default_rng(seed + 5).standard_normal(m)
        n1, n2, n3 = lp_fft(nz, 500, 2), lp_fft(nz, 2200, 2), lp_fft(nz, 8000, 2)
        w1 = (1 - pr) ** 1.5; w3 = pr ** 2; w2 = np.clip(1 - w1 - w3, 0, 1)
        r = (n1 * 3.0 * w1 + n2 * 1.6 * w2 + n3 * 1.0 * w3) * pr ** 2.2 * 0.5
        f0 = midi_hz(base + 24); fr = f0 * 2 ** (2.0 * pr ** 1.3)
        ph = 2 * np.pi * np.cumsum(fr) / SR
        r += (np.sin(ph) + 0.5 * np.sin(ph * 1.0595)) * pr ** 1.8 * 0.35 * (0.85 + 0.15 * np.sin(2 * np.pi * 6 * tr_))
        add_at(riser, r, tr0)
    # ---- mezcla del bus de musica
    dryL = padL + arpL + kick + bass + riser * 0.9
    dryR = padR + arpR + kick + bass + riser * 0.9
    sendL = padL * 0.5 + arpL * 0.9 + riser * 0.4
    sendR = padR * 0.5 + arpR * 0.9 + riser * 0.4
    L = dryL + 0.9 * reverb(sendL); R = dryR + 0.9 * reverb(sendR, True)
    if modo_alegre():
        sh = int(round(fase * SR))   # toda la musica (colchon, arpegio, bombo) se desplaza a la rejilla de los cortes
        if sh > 0:
            L = np.concatenate([np.zeros(sh), L])[:n]; R = np.concatenate([np.zeros(sh), R])[:n]
        rg = np.random.default_rng(seed + 77)
        bl = np.zeros(n); br = np.zeros(n)
        nb = int((total - fase) / beat) + 1
        for k in range(nb):
            tb = fase + k * beat
            comp, pos = k // 4, k % 4
            relleno = (comp % 4 == 3 and pos == 3)          # cada 4 compases, relleno de cajas antes del siguiente
            if pos in (1, 3) and not relleno:
                add_at(bl, _golpe("clap", rg, 0.8 + (0.35 if k in acentos else 0.0)), tb)
                add_at(br, _golpe("clap", rg, 0.8 + (0.35 if k in acentos else 0.0)), tb)
            if relleno:
                for j in range(4):
                    v = 0.5 + 0.18 * j
                    add_at(bl, _golpe("caja", rg, v), tb + j * beat / 4); add_at(br, _golpe("caja", rg, v), tb + j * beat / 4)
            for j, (dt, v) in enumerate(((0.0, 0.32), (0.5, 0.62))):      # hi-hat a corcheas, el contratiempo mas fuerte
                if relleno and j == 1: continue
                add_at(bl, _golpe("hat", rg, v), tb + dt * beat); add_at(br, _golpe("hat", rg, v * 0.85), tb + dt * beat + 0.004)
            if pos == 2:                                    # sincopa suave antes del tiempo 4 (da balanceo)
                add_at(bl, _golpe("hat", rg, 0.9), tb + 0.75 * beat)
        L = L + 0.42 * bl; R = R + 0.42 * br
    cutg = np.ones(n)
    if cut0:
        i0, i1 = int(cut0 * SR), int(gs * SR); r0 = int(0.006 * SR)
        cutg[i0:i0 + r0] = np.linspace(1, 0, r0); cutg[i0 + r0:i1] = 0.0
    return L, R, cutg, dict(bpm=round(60 / beat, 2), fase_ms=round(fase * 1000), cortes_al_golpe=rejilla, key=key, prog=(PROGS_MAYOR if modo_alegre() else PROGS).index(prog), box=box, cut=cut0, riser=tr0)

def sfx_dibujo(tipo, dur, rg):
    """Efectos de sonido del modo dibujo, generados por codigo y discretos (amplitud < 0,16; la voz los hunde en la
    mezcla): whoosh (entrada / corte), pop (el objeto aterriza tras el rebote), lapiz (trazo que se dibuja en la
    pizarra), teclas (texto que se teclea en la pantalla) y ding (la cifra llega a su valor)."""
    dur = max(0.03, float(dur)); m = int(dur * SR); tt = np.arange(m) / SR
    if tipo == "whoosh":
        x = rg.standard_normal(m)
        x = lp_fft(x, 3200, 2) - lp_fft(x, 500, 2)
        env = np.sin(np.pi * np.minimum(1.0, tt / dur)) ** 2 * np.linspace(0.4, 1.0, m)
        return x * env * 0.30
    if tipo == "pop":
        f = 420 - 220 * tt / dur
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 40) * 0.32
    if tipo == "lapiz":
        x = rg.standard_normal(m)
        x = lp_fft(x, 6000, 2) - lp_fft(x, 1500, 2)
        mod = 0.55 + 0.45 * np.abs(np.sin(2 * np.pi * 11 * tt + rg.uniform(0, 3)))
        env = np.minimum(1.0, tt / 0.03) * np.minimum(1.0, (dur - tt) / 0.06)
        return x * mod * env * 0.10
    if tipo == "teclas":
        out = np.zeros(m); k = 0.0
        while k < dur - 0.02:
            i0 = int(k * SR); mm = min(int(0.018 * SR), m - i0)
            if mm <= 0: break
            t2 = np.arange(mm) / SR
            click = (lp_fft(rg.standard_normal(mm), 4500, 2) if mm > 8 else np.zeros(mm)) * np.exp(-t2 * 260)
            out[i0:i0 + mm] += click * rg.uniform(0.5, 1.0)
            k += rg.uniform(0.07, 0.12)
        return out * 0.22
    if tipo in ("tick", "sting", "boing", "thud", "papeles"):   # efectos del modo sketch (sketch.py)
        return _sk().sfx(tipo, dur, rg, lp_fft)
    if tipo.startswith("dt_"):   # efectos del modo datos (datos.py)
        return _dt().sfx(tipo, dur, rg, lp_fft)
    if tipo == "ding":
        return (np.sin(2 * np.pi * 1318.5 * tt) + 0.35 * np.sin(2 * np.pi * 2637 * tt)) * np.exp(-tt * 6.5) * 0.17
    return None

def make_audio(scenes, total, seed, musica=True):
    rg = np.random.default_rng(seed)
    n = int(total * SR); t = np.arange(n) / SR
    gs = next((s.start / FPS for s in scenes if s.style == "giro"), None)
    hook_end = scenes[0].nframes / FPS
    cutg = np.ones(n)
    orig = None
    if MODO["app"]:   # audio original del video propio, por tramos (acelerado como el video), bajo la voz
        orig = np.zeros((n, 2))
        if APP["audio"] and APP["volumen"] > 0:
            for s in scenes:
                if getattr(s, "clip", None) is None or getattr(s, "ini", None) is None: continue
                i0 = int(s.start / FPS * SR); k = min(int(s.nframes / FPS * SR), n - i0)
                if k > 0: orig[i0:i0 + k] += audio_tramo(APP["path"], s.ini, s.nframes / FPS, s.vel, k)
        lo = lufs(orig) if np.abs(orig).max() > 1e-4 else -99.0
        if musica is None:   # sin "musica" en el guion: musica solo si el video no trae sonido util
            musica = lo < -45.0
            print("audio original: %.1f LUFS -> %s" % (lo, "musica discreta" if musica else "sin musica (el video ya suena)"))
        if lo > -60:
            orig *= 10 ** ((-24.0 - lo) / 20) * APP["volumen"]   # -24 LUFS x volumen_original (0,5 = -30 LUFS)
        else:
            orig = None
    musica = bool(musica)
    if musica:
        mL, mR, cutg, info = make_music(scenes, n, seed, gs, hook_end)
        print("musica:", info)
    elif gs and gs >= 3.0:
        i0, i1 = int((gs - CORTE_GIRO) * SR), int(gs * SR); cutg[i0:i1] = 0.0
    # ---- efectos: lecho (drone + rumor) y golpes
    drone = (0.5 * np.sin(2 * np.pi * 55 * t + 0.8 * np.sin(2 * np.pi * 0.13 * t))
             + 0.35 * np.sin(2 * np.pi * 55.8 * t)
             + 0.25 * np.sin(2 * np.pi * 82.4 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t))
             + 0.10 * np.sin(2 * np.pi * 110.9 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.21 * t)))
    drone *= 0.55
    bL = drone + 0.016 * np.diff(rg.standard_normal(n + 1)) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.4 * t))
    bR = drone + 0.016 * np.diff(rg.standard_normal(n + 1)) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.37 * t))
    rum = lp_fft(rg.standard_normal(n), 28, 1) * 0.9 * 0.5
    bL = bL + rum; bR = bR + rum
    fcut = np.maximum(cutg, 0.04)
    bL *= fcut; bR *= fcut
    hL = np.zeros(n); hR = np.zeros(n)
    for s in scenes:
        g = s.style == "giro"
        dur = 0.9 if g else 0.55
        m = int(dur * SR); tt = np.arange(m) / SR
        x = rg.standard_normal(m)
        w = lowpass_sweep(x, 0.02, 0.35) if not g else lowpass_sweep(x, 0.01, 0.5)
        env = np.sin(np.pi * np.minimum(1, (tt / dur) ** 0.7)) ** 2
        amp = 1.5 if g else 0.75
        sig = w * env * amp * 1.6
        f = 40 + 110 * np.exp(-tt * 12)
        th = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * (5 if g else 7)) * (1.0 if g else 0.6)
        sig = sig + th
        if g:
            sig += 0.12 * (np.sin(2 * np.pi * 740 * tt) + np.sin(2 * np.pi * 783 * tt) * 0.9 + np.sin(2 * np.pi * 1109 * tt) * 0.5) * np.exp(-tt * 3.5)
        i0 = int(s.start / FPS * SR); i1 = min(n, i0 + m)
        hL[i0:i1] += sig[:i1 - i0]; hR[i0:i1] += sig[:i1 - i0] * 0.92
        if getattr(s, "sello", ""):  # golpe seco del sello (cuando termina de caer)
            m2 = int(0.45 * SR); t2 = np.arange(m2) / SR
            f2 = 38 + 120 * np.exp(-t2 * 22)
            thud = np.sin(2 * np.pi * np.cumsum(f2) / SR) * np.exp(-t2 * 9) * 0.9
            thud += lowpass_sweep(rg.standard_normal(m2), 0.25, 0.04) * np.exp(-t2 * 28) * 1.1
            j0 = int((s.start / FPS + s.sello_t + 0.13) * SR); j1 = min(n, j0 + m2)
            if j0 < n:
                hL[j0:j1] += thud[:j1 - j0]; hR[j0:j1] += thud[:j1 - j0]
    fx = np.stack([bL + hL, bR + hR], 1)
    if modo_suave():
        st = np.zeros_like(fx)            # modo humano/dibujo: sin lecho de tension ni golpes
        if modo_alegre():                 # dibujo/app: un "pop" suave en cada corte de escena
            m = int(0.09 * SR); tp = np.arange(m) / SR
            pop = np.sin(2 * np.pi * np.cumsum(620 - 300 * tp / 0.09) / SR) * np.exp(-tp * 45) * 0.45
            for s in scenes[1:]:
                if getattr(s, "serio", False): continue   # sketch: el mensaje final va serio, sin efectos
                i0 = int(s.start / FPS * SR); i1 = min(n, i0 + m)
                st[i0:i1, 0] += pop[:i1 - i0]; st[i0:i1, 1] += pop[:i1 - i0]
        if MODO["app"]:      # 7/11 (queja del dueno: «mas efectos sonoros»): whoosh en cada corte, pop de entrada y ding en el cierre
            for k, s in enumerate(scenes):
                for tipo, t_rel, dur, amp in ([("whoosh", -0.12, 0.34, 1.0)] if k else [("pop", 0.0, 0.09, 1.0)]) + \
                                             ([("ding", 0.25, 0.5, 1.0)] if k == len(scenes) - 1 else []):
                    sig = sfx_dibujo(tipo, dur, rg)
                    if sig is None: continue
                    i0 = max(0, int((s.start / FPS + t_rel) * SR)); i1 = min(n, i0 + len(sig))
                    if i0 < n and i1 > i0:
                        st[i0:i1, 0] += amp * sig[:i1 - i0]; st[i0:i1, 1] += amp * sig[:i1 - i0] * 0.95
        if MODO["dibujo"] or MODO["sketch"] or MODO["datos"]:   # efectos sutiles por evento (whoosh en el corte, pop del rebote, lapiz, teclas, ding)
            for s in scenes:
                for tipo, t_rel, dur in getattr(s, "sfx", []):
                    sig = sfx_dibujo(tipo, dur, rg)
                    if sig is None: continue
                    i0 = int((s.start / FPS + t_rel) * SR); i1 = min(n, i0 + len(sig))
                    if i0 < n and i1 > i0:
                        st[i0:i1, 0] += sig[:i1 - i0]; st[i0:i1, 1] += sig[:i1 - i0] * 0.95
    else:
        gfx = 10 ** ((-21 - lufs(fx)) / 20)
        st = fx * gfx
    lm = None
    if orig is not None:
        st = st + orig
    if musica:
        mus = np.stack([mL * cutg, mR * cutg], 1)
        if MODO["sketch"]:   # sketch: sin musica de chiste en el mensaje serio (fundido de 0,35 s)
            duck = np.ones(n)
            for s in scenes:
                if getattr(s, "serio", False):
                    i0 = int(s.start / FPS * SR); k = int(0.35 * SR)
                    duck[max(0, i0 - k):i0] = np.linspace(1, 0, min(k, i0))
                    duck[i0:] = 0.0
                    break
            mus *= duck[:, None]
        lm0 = lufs(mus)
        mus *= 10 ** (((-31 if MODO["humano"] else (-18 if (modo_alegre() or MODO["datos"]) else -24)) - lm0) / 20)   # humano/dibujo/app: musica discreta
        if modo_suave() and hook_end < total - 2.0:
            # el gancho va a pelo (solo la voz): la musica entra en fundido de 0,8 s cuando termina la primera escena
            mus *= np.clip((t - hook_end + 0.2) / 0.8, 0.5 if (modo_alegre() or MODO["datos"]) else 0.0, 1.0)[:, None]   # dibujo/app: ya suena en el gancho (a media fuerza)
        st = st + mus
    fade = np.minimum(1, np.minimum(t / 0.3, (total - t) / 0.9))
    st *= fade[:, None]
    if MASTER_DATOS[0]:
        # datos SIN voz (12/11/2026): no pasa por la mezcla de voz de publicar_gh.py, que es la que masteriza; aquí se deja
        # ya a -14 LUFS con techo de -1,9 dBFS (margen para el pico verdadero ≤ -1 dBTP que exige control_datos.py).
        techo = 10 ** (-1.9 / 20)
        for _ in range(3):
            l0 = lufs(st)
            if l0 is None or not np.isfinite(l0): break
            st = st * 10 ** ((-14.0 - l0) / 20)
            a = np.abs(st); th = techo * 0.75
            st = np.where(a > th, np.sign(st) * (th + (techo - th) * np.tanh((a - th) / (techo - th))), st)
        return (np.clip(st, -techo, techo) * 32767).astype(np.int16)
    a = np.abs(st); th = 0.7   # limitador suave (sin clipping)
    st = np.where(a > th, np.sign(st) * (th + (1 - th) * np.tanh((a - th) / (1 - th))), st)
    pk = np.abs(st).max()
    if pk > 0.89: st *= 0.89 / pk
    return (st * 32767).astype(np.int16)


# ---------------------------------------------------------------- principal
def main():
    if len(sys.argv) < 3:
        print("Uso: python3 hacer_reel.py guion.json salida.mp4 [--solo-locucion] [--tiempos tiempos.json] [--ensayo]"); sys.exit(1)
    t0 = time.time()
    g = json.load(open(sys.argv[1], encoding="utf-8")); out = sys.argv[2]
    GUION_DIR[0] = os.path.dirname(os.path.abspath(sys.argv[1]))
    # Voz primero (publicar_gh.py, 6/11/2026): con --solo-locucion solo se escribe <salida>.locucion.json (sin
    # fotogramas) para generar la voz antes; con --tiempos se recibe la duracion REAL de la voz de cada escena
    # ({"0": 3.21, "2": 4.8, ...}, indice de escena -> segundos) y entonces la escena se alarga para que la voz
    # quepa sin acelerarla y los subtitulos van al ritmo real de esa frase (no al estimado de 2,6 palabras/s).
    solo_loc = "--solo-locucion" in sys.argv
    tiempos = {}
    palabras_voz = {}   # indice de escena -> [inicio de cada palabra] (alineacion real; opcional)
    env_voz = {}        # indice de escena -> envolvente de la voz (FPS valores/s, 0-1) para la boca (opcional)
    if "--tiempos" in sys.argv:
        try:
            for k, v in json.load(open(sys.argv[sys.argv.index("--tiempos") + 1], encoding="utf-8")).items():
                if isinstance(v, dict):   # {"dur": s, "palabras": [[ini, fin], ...], "env": [0.0-1.0, ...]}
                    tiempos[int(k)] = float(v.get("dur") or 0)
                    if v.get("palabras"):
                        palabras_voz[int(k)] = [float(x[0]) if isinstance(x, (list, tuple)) else float(x) for x in v["palabras"]]
                    if isinstance(v.get("env"), list) and v["env"]:
                        env_voz[int(k)] = v["env"]
                else:
                    tiempos[int(k)] = float(v)
        except Exception as e:
            print("tiempos de voz no leidos (se usa la estimacion):", str(e)[:120])
    seed = int(g.get("semilla", 1)); title = g.get("titulo", "")
    musica = bool(g.get("musica", True))
    if g.get("modo") == "sketch":
        musica = False   # sketch: nunca musica cocida (orden del dueno 10/11: la cancion la pone Instagram al publicar, audio_ig)
    modo = (g.get("modo") or "").strip().lower()
    # datos (12/11/2026, orden del dueño: «música y voz si lo consideran»): la música la decide el equipo con "musica" en el
    # guion (por defecto sí). Si se publica con canción de Instagram, publicar_gh.py ya pasa "musica": false (guion_sin_musica).
    if modo not in ("", "humano", "dibujo", "app", "sketch", "datos"):   # guardia: un modo desconocido nunca se renderiza con otro estilo
        sys.exit("modo desconocido en guion.json: %r (este generador conoce: humano, dibujo, app, sketch, datos)" % modo)
    MODO["humano"] = modo == "humano"
    MODO["dibujo"] = modo == "dibujo"
    MODO["app"] = modo == "app"
    MODO["sketch"] = modo == "sketch"
    MODO["datos"] = modo == "datos"
    if MODO["app"]:
        cargar_video_app(str(g.get("video") or ""))
        APP["plantilla"] = bool(g.get("plantilla")) and APP["vertical"]
        if APP["plantilla"]:
            f0 = fotograma_video(APP["path"], 0.0)
            if f0 is not None: APP["fondo"] = f0.getpixel((4, 4))
        APP["volumen"] = max(0.0, min(1.5, float(g.get("volumen_original", 0.5))))
        if "musica" not in g: musica = None   # automatico: segun si el video trae sonido
        for e in g["escenas"]:
            c = e.get("clip") if isinstance(e.get("clip"), dict) else {}
            ini = c.get("inicio", e.get("inicio"))
            if ini is not None and (e.get("estilo") or "tramo") != "cierre":
                APP["primer_inicio"] = max(0.0, float(ini)); break
    SEMILLA["v"] = int(g.get("semilla", 1))
    DIB_PREV["pers"] = set()
    esc = g["escenas"]
    MASTER_DATOS[0] = modo == "datos" and not any(str(e.get("voz") or "").strip() for e in esc)
    if MODO["datos"]:   # puerta dura de la ficha de datos (salvo --ensayo) y contexto de cada escena
        _dt().iniciar(g, "--ensayo" in sys.argv)
    if MODO["sketch"]:   # contexto de la serie para cada escena (gancho fijo, contador, mensaje serio y su fuente)
        DIB_PREV["pers"] = set()
        gancho = str(esc[0].get("texto") or g.get("portada_texto") or "")
        if str(esc[0].get("estilo") or "").strip().lower() == "texto":
            gancho = ""   # 12/11/2026: reel que arranca con escena «texto» (sin voz): la frase gigante ya es el gancho, sin «POV» arriba
        cont = g.get("contador") if isinstance(g.get("contador"), dict) else {}
        valor = int(cont.get("valor") or 0)
        mf = g.get("mensaje_final") if isinstance(g.get("mensaje_final"), dict) else {}
        msg = next((str(e.get("texto") or "") for e in esc if e.get("estilo") == "mensaje"), "")
        base = int(cont.get("inicio") or 0)   # veces acumuladas en episodios anteriores: el contador sube +1 en cada escena "delega"
        k = base
        for i, e in enumerate(esc):
            ini = k
            if e.get("estilo") == "delega" or e.get("contar"): k += 1
            e["_ctx"] = {"gancho": gancho, "contador": cont if cont.get("texto") else None, "cont_ini": ini, "cont_fin": k,
                         "mensaje": msg, "fuente": str(mf.get("fuente") or ""),
                         "gancho_corto": str(g.get("gancho_corto") or ""), "fondo": g.get("fondo", "auto"),
                         "primer_plano": g.get("primer_plano", True) is not False}
    bounds = [0]
    for i, e in enumerate(esc):
        d = float(e.get("duracion", 1.8 if MODO["sketch"] else 3.0))
        if MODO["app"] and "duracion" not in e:   # app: sin "duracion", el tramo dura lo que su clip (o 1,8 s el gancho)
            c = e.get("clip") if isinstance(e.get("clip"), dict) else {}
            ini, fin = c.get("inicio", e.get("inicio")), c.get("fin", e.get("fin"))
            d = 1.8 if (e.get("estilo") == "gancho") else (max(0.5, float(fin) - float(ini)) if (ini is not None and fin is not None) else 3.0)
            if e.get("estilo") != "gancho" and ini is not None and fin is not None:
                e["_largo_clip"] = max(0.5, float(fin) - float(ini))
        voz = parsear_enfasis(e.get("voz") or "")[0]
        if voz:  # duracion minima para que el narrador termine
            if i in tiempos and tiempos[i] > 0.2:
                need = tiempos[i] + 0.45   # voz real + 120 ms de retardo de mezcla + respiro
                e["_voz_dur"] = tiempos[i]
                if i in palabras_voz: e["_voz_palabras"] = palabras_voz[i]
                if i in env_voz: e["_voz_env"] = env_voz[i]
            else:
                need = len(voz.split()) / 2.6 + 0.6
            if i + 1 < len(esc) and esc[i + 1].get("estilo") == "giro":
                need += 0.5  # deja libre el segundo de silencio antes del giro
            if MODO["app"] and "duracion" not in e and e.get("estilo") != "gancho" and "_largo_clip" in e:
                # 10/11/2026 (petición de Calidad): sin "duracion", la escena dura lo que la voz real (+0,5 s) y el
                # clip se acelera hasta x1,75; nunca más corta que clip/1,75 (si no, el tramo se cortaría).
                d = max(need, e["_largo_clip"] / MAX_VEL_APP)
            else:
                d = max(d, need)
        if MODO["datos"]:   # los graficos necesitan tiempo para animarse y leerse
            d = max(d, {"gancho": 2.2, "cierre": 3.0, "giro": 2.4}.get(e.get("estilo"), 3.2))
        if MODO["sketch"]:   # el mensaje serio se lee entero y el fotograma final se puede guardar
            d = max(d, {"mensaje": 3.2, "cierre": 2.2, "gancho": 1.8}.get(e.get("estilo"), 1.8))
        bounds.append(bounds[-1] + int(math.ceil(d * FPS - 1e-6)))
    loc = []
    for i, e in enumerate(esc):
        if not (e.get("voz") or "").strip(): continue
        limpio, enf = parsear_enfasis(e["voz"])   # la voz recibe el texto sin asteriscos; el enfasis va aparte
        loc.append({"escena": i, "estilo": e.get("estilo", "evidencia"), "hablante": e.get("hablante"), "inicio": round(bounds[i] / FPS, 3),
                    "duracion": round((bounds[i + 1] - bounds[i]) / FPS, 3), "texto": limpio, "enfasis": enf})
    with open(os.path.splitext(out)[0] + ".locucion.json", "w", encoding="utf-8") as fh:
        json.dump(loc, fh, ensure_ascii=False, indent=1)
    if solo_loc:
        print("locucion %d frases, %.1fs" % (len(loc), bounds[-1] / FPS)); return
    scenes = [Scene(i, e, seed, title, bounds[i + 1] - bounds[i], bounds[i]) for i, e in enumerate(esc)]
    total_f = bounds[-1]
    if MODO["datos"]:
        _dt().fijar_total(scenes, total_f)
    rr = random.Random(seed)
    date_s = "%02d/%02d/%d" % (rr.randint(1, 28), rr.randint(1, 12), rr.randint(1994, 2007))
    noise = build_noise(seed); rg = random.Random(seed + 99)
    tmp = tempfile.mkdtemp()
    wav = os.path.join(tmp, "a.wav")
    ta = time.time()
    pcm = make_audio(scenes, total_f / FPS, seed, musica)
    print("audio %.1fs" % (time.time() - ta))
    with wave.open(wav, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    # portada
    cov = {"texto": g.get("portada_texto") or title, "estilo": "gancho", "duracion": 3}
    if MODO["dibujo"]:
        cov["dibujo"] = {"personajes": ["paco", "bit"], "accion": "sorprendido", "objeto": "nada"}
        DIB_PREV["pers"] = {"paco", "bit"}
    if MODO["app"]:
        cov["bit"] = True
    if MODO["sketch"]:
        DIB_PREV["pers"] = set()
        cov.update({"texto": str(esc[0].get("texto") or cov["texto"]), "hablante": "jambo", "dibujo": {"personajes": ["jambo"], "accion": "presume"},
                    "_ctx": dict(esc[0].get("_ctx") or {}, cont_ini=0, cont_fin=0)})
    if MODO["datos"]:   # portada = fotograma del gancho
        cov.update({"texto": str(g.get("gancho_corto") or esc[0].get("texto") or cov["texto"]), "grafico": "texto", "_ctx": dict(esc[0].get("_ctx") or {})})
    cs = Scene(0, cov, seed, title, 90, 0)
    cimg = render_frame(60, [cs], noise, date_s, title, random.Random(1))
    Image.fromarray(cimg).save(os.path.splitext(out)[0] + "_portada.jpg", quality=90)
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
           "-r", str(FPS), "-i", "-", "-i", wav, "-map", "0:v", "-map", "1:a",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-maxrate", "5M", "-bufsize", "10M", "-pix_fmt", "yuv420p", "-r", str(FPS),
           "-ar", "44100", "-c:a", "aac", "-b:a", "160k",
           "-frames:v", str(total_f), "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(total_f):
        p.stdin.write(render_frame(fi, scenes, noise, date_s, title, rg).tobytes())
    p.stdin.close()
    if p.wait() != 0: sys.exit("ffmpeg fallo")
    if INFO_MUSICA:
        with open(os.path.splitext(out)[0] + ".musica.json", "w", encoding="utf-8") as fh:
            json.dump(INFO_MUSICA, fh, ensure_ascii=False)
    if MODO["app"] or MODO["datos"]:   # control de ritmo (12/11/2026, petición de Calidad por 406): avisa de tramos quietos > 3 s
        try:
            r = subprocess.run([FFMPEG, "-hide_banner", "-i", out, "-vf", "freezedetect=n=-55dB:d=3", "-an", "-f", "null", "-"],
                               capture_output=True, text=True, timeout=300)
            ini = re.findall(r"freeze_start: ([0-9.]+)", r.stderr); dur = re.findall(r"freeze_duration: ([0-9.]+)", r.stderr)
            for a, d in zip(ini, dur):
                print("AVISO RITMO: imagen quieta %.1f s desde %.1f s (B5: máx. 3 s sin cambio); acorta el clip o añade movimiento/corte" % (float(d), float(a)))
        except Exception as ex:
            print("control de ritmo no disponible:", str(ex)[:80])
    print("OK %s (%d frames, %.1fs, render %.1fs)" % (out, total_f, total_f / FPS, time.time() - t0))

if __name__ == "__main__":
    main()
