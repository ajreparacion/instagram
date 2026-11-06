#!/usr/bin/env python3
"""Generador de reels de misterio / falso documental.
Uso: python3 hacer_reel.py guion.json salida.mp4
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
def wrap_fit(text, path, maxw=W - SAFE_L - SAFE_R - 40, maxlines=3, smax=118, smin=44):
    probe = ImageDraw.Draw(Image.new("L", (4, 4)))
    for size in range(smax, smin - 1, -4):
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


def make_music(scenes, n, seed, gs, hook_end):
    rng = random.Random(seed * 7919 + 13)
    total = n / SR
    bpm = rng.uniform(70, 90); beat = 60.0 / bpm
    cut0 = gs - CORTE_GIRO if (gs and gs >= 3.0) else None
    if gs and gs >= 3.0:  # que el giro caiga en un pulso
        b2 = gs / max(1, round(gs / beat))
        if 70 <= 60 / b2 <= 90: beat = b2
    key = rng.randrange(12); base = 38 + key
    prog = rng.choice(PROGS); add9 = rng.random() < 0.5
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
    if cut0:
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
    w = np.full(n, 0.15)
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
    kick *= 1.1
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
    cutg = np.ones(n)
    if cut0:
        i0, i1 = int(cut0 * SR), int(gs * SR); r0 = int(0.006 * SR)
        cutg[i0:i0 + r0] = np.linspace(1, 0, r0); cutg[i0 + r0:i1] = 0.0
    return L, R, cutg, dict(bpm=60 / beat, key=key, prog=PROGS.index(prog), box=box, cut=cut0, riser=tr0)

def make_audio(scenes, total, seed, musica=True):
    rg = np.random.default_rng(seed)
    n = int(total * SR); t = np.arange(n) / SR
    gs = next((s.start / FPS for s in scenes if s.style == "giro"), None)
    hook_end = scenes[0].nframes / FPS
    cutg = np.ones(n)
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
    gfx = 10 ** ((-21 - lufs(fx)) / 20)
    st = fx * gfx
    lm = None
    if musica:
        mus = np.stack([mL * cutg, mR * cutg], 1)
        lm0 = lufs(mus)
        mus *= 10 ** ((-24 - lm0) / 20)
        st = st + mus
    fade = np.minimum(1, np.minimum(t / 0.3, (total - t) / 0.9))
    st *= fade[:, None]
    a = np.abs(st); th = 0.7   # limitador suave (sin clipping)
    st = np.where(a > th, np.sign(st) * (th + (1 - th) * np.tanh((a - th) / (1 - th))), st)
    pk = np.abs(st).max()
    if pk > 0.89: st *= 0.89 / pk
    return (st * 32767).astype(np.int16)


# ---------------------------------------------------------------- principal
def main():
    if len(sys.argv) < 3:
        print("Uso: python3 hacer_reel.py guion.json salida.mp4"); sys.exit(1)
    t0 = time.time()
    g = json.load(open(sys.argv[1], encoding="utf-8")); out = sys.argv[2]
    seed = int(g.get("semilla", 1)); title = g.get("titulo", "")
    musica = bool(g.get("musica", True))
    esc = g["escenas"]
    bounds = [0]
    for i, e in enumerate(esc):
        d = float(e.get("duracion", 3.0))
        voz = (e.get("voz") or "").strip()
        if voz:  # duracion minima para que el narrador termine
            need = len(voz.split()) / 2.6 + 0.6
            if i + 1 < len(esc) and esc[i + 1].get("estilo") == "giro":
                need += 0.5  # deja libre el segundo de silencio antes del giro
            d = max(d, need)
        bounds.append(bounds[-1] + int(math.ceil(d * FPS - 1e-6)))
    scenes = [Scene(i, e, seed, title, bounds[i + 1] - bounds[i], bounds[i]) for i, e in enumerate(esc)]
    total_f = bounds[-1]
    loc = [{"inicio": round(bounds[i] / FPS, 3), "duracion": round((bounds[i + 1] - bounds[i]) / FPS, 3), "texto": e["voz"].strip()}
           for i, e in enumerate(esc) if (e.get("voz") or "").strip()]
    with open(os.path.splitext(out)[0] + ".locucion.json", "w", encoding="utf-8") as fh:
        json.dump(loc, fh, ensure_ascii=False, indent=1)
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
    print("OK %s (%d frames, %.1fs, render %.1fs)" % (out, total_f, total_f / FPS, time.time() - t0))

if __name__ == "__main__":
    main()
