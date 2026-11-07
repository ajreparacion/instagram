#!/usr/bin/env python3
"""Modo "dibujo" de hacer_reel.py (6/11/2026, nueva estrategia del usuario: IA facil con DIBUJOS ANIMADOS).
Todo dibujado por codigo en CPU (Pillow + numpy): papel claro con textura, trazo negro grueso con temblor de mano,
un unico acento cian. Personajes fijos: «Bit» (robotito redondo blanco con pantalla-cara cian) y «Paco» (muneco de
palo que se agobia con la tecnologia). Elementos por escena: personajes/accion, pizarra, pantalla (movil/portatil
con texto tecleado), flecha, antes_despues, cifra, lista, sello, objeto (icono), invitados (ChatGPT/Claude/Gemini
como personajes genericos con su nombre en texto, nunca su logo).
Lo usa hacer_reel.py (que rellena HR con su propio modulo para compartir fuentes, Subtitulos y audio). Los demas
modos de hacer_reel.py no pasan por aqui."""
import math, random, hashlib, os, glob, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HR = None   # lo rellena hacer_reel.py (sys.modules[__name__]) para evitar la importacion circular

W, H, FPS = 1080, 1920, 30
PAPEL = (248, 244, 234)
TINTA = (30, 28, 26)
CIAN = (0, 184, 217)
CIAN_OSCURO = (0, 120, 145)
CIAN_CLARO = (205, 240, 247)
ROJO = (226, 60, 60)
BLANCO = (255, 255, 255)
SOMBRA = (226, 222, 211)
GRIS = (150, 146, 140)

HERE = os.path.dirname(os.path.abspath(__file__))
DJV = "/usr/share/fonts/truetype/dejavu/"

def _buscar(nombres, defecto):
    for n in nombres:
        for p in glob.glob(os.path.join(HERE, "fonts", n)) + glob.glob("/usr/share/fonts/truetype/*/" + n):
            if os.path.exists(p): return p
    return defecto

F_LETRA = _buscar(["Poppins-Bold.ttf"], DJV + "DejaVuSans-Bold.ttf")   # letra «rotulada» (con temblor por glifo)
F_MONO = DJV + "DejaVuSansMono-Bold.ttf" if os.path.exists(DJV + "DejaVuSansMono-Bold.ttf") else F_LETRA
_fc = {}
def fuente(path, tam):
    k = (path, int(tam))
    if k not in _fc: _fc[k] = ImageFont.truetype(path, int(tam))
    return _fc[k]
_probe = ImageDraw.Draw(Image.new("L", (4, 4)))

ACCIONES = ("explica", "senala", "encoge", "sorpresa", "celebra", "piensa", "agobiado", "entrar", "saluda", "escucha")
OBJETOS = ("movil", "portatil", "correo", "calendario", "lista", "reloj", "bombilla", "chat", "carpeta")
INVITADOS = {"chatgpt": "ChatGPT", "claude": "Claude", "gemini": "Gemini", "copilot": "Copilot", "siri": "Siri", "alexa": "Alexa"}

# ---------------------------------------------------------------- papel
_papel = {}
def papel(seed):
    """Fondo de papel claro con textura suave (ruido de dos escalas + vineta leve). Se calcula una vez."""
    if "im" not in _papel:
        rg = np.random.default_rng(seed)
        low = rg.normal(0, 1, (26, 15)).astype(np.float32)
        low = np.asarray(Image.fromarray(low).resize((W, H), Image.BICUBIC), dtype=np.float32)
        fino = rg.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
        fino = np.repeat(np.repeat(fino, 2, 0), 2, 1)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r2 = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2
        vig = 1.0 - 0.06 * r2
        base = np.array(PAPEL, np.float32)[None, None, :] * vig[:, :, None]
        a = base + low[:, :, None] * 4.5 + fino[:, :, None] * 2.2
        # fibras horizontales muy leves
        fib = rg.normal(0, 1, (H, 1)).astype(np.float32)
        a += fib[:, :, None] * 0.8
        _papel["im"] = np.clip(a, 0, 255).astype(np.uint8)
    return _papel["im"]

# ---------------------------------------------------------------- trazo a mano
def _remuestrear(pts, paso=9.0):
    out = [pts[0]]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        if L < 1e-6: continue
        n = max(1, int(L / paso))
        for i in range(1, n + 1):
            f = i / n; out.append((x0 + (x1 - x0) * f, y0 + (y1 - y0) * f))
    return out

def trazo(d, pts, grosor=9, color=TINTA, k=1.0, temblor=1.6, fase=0.0, fill=None, cerrado=False):
    """Polilinea dibujada a mano: temblor suave a lo largo del trazo (dos senos), extremos redondeados.
    k = fraccion dibujada (efecto pizarra). fill (con cerrado) rellena cuando el contorno esta completo."""
    if k <= 0 or len(pts) < 2: return
    pts = list(pts)
    if cerrado and pts[0] != pts[-1]: pts.append(pts[0])
    p = _remuestrear(pts)
    n = len(p)
    if temblor > 0:
        a1, a2 = fase, fase * 1.7 + 2.1
        q = []
        for i, (x, y) in enumerate(p):
            x0, y0 = p[max(0, i - 1)]; x1, y1 = p[min(n - 1, i + 1)]
            dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy) or 1.0
            nx, ny = -dy / L, dx / L
            s = i * 9.0
            off = temblor * (math.sin(s / 43.0 + a1) + 0.5 * math.sin(s / 14.0 + a2))
            q.append((x + nx * off, y + ny * off))
        p = q
    if fill is not None and k >= 1.0 and n >= 3:
        d.polygon(p, fill=fill)
    m = max(2, int(round(n * min(1.0, k))))
    seg = p[:m]
    d.line(seg, fill=color, width=int(max(1, grosor)), joint="curve")
    r = grosor / 2.0
    for (x, y) in (seg[0], seg[-1]):
        d.ellipse([x - r, y - r, x + r, y + r], fill=color)

class Lienzo:
    """Envuelve ImageDraw con la fase del temblor: cambia cada 3 fotogramas (la linea «hierve» como en un doodle)."""
    def __init__(self, img, fi):
        self.img = img; self.d = ImageDraw.Draw(img); self.fi = fi; self.i = 0
        self.base = (fi // 3) * 1.37
    def trazo(self, pts, grosor=9, color=TINTA, k=1.0, temblor=1.6, fill=None, cerrado=False):
        self.i += 1
        trazo(self.d, pts, grosor, color, k, temblor, self.base + self.i * 0.83, fill, cerrado)
    def punto(self, x, y, r, color=TINTA):
        self.d.ellipse([x - r, y - r, x + r, y + r], fill=color)

def circ(cx, cy, r, n=44, a0=-100):
    return [(cx + r * math.cos(math.radians(a0 + 360.0 * i / n)), cy + r * math.sin(math.radians(a0 + 360.0 * i / n))) for i in range(n + 1)]

def arco(cx, cy, rx, ry, a0, a1, n=18):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]

def rrect(x0, y0, x1, y1, r, n=6):
    r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
    pts = []
    pts += arco(x0 + r, y0 + r, r, r, 180, 270, n)
    pts += arco(x1 - r, y0 + r, r, r, 270, 360, n)
    pts += arco(x1 - r, y1 - r, r, r, 0, 90, n)
    pts += arco(x0 + r, y1 - r, r, r, 90, 180, n)
    pts.append(pts[0])
    return pts

def kparte(k, i, n):
    """Progreso del trazo i (de n) cuando el conjunto va por k: se dibujan uno tras otro."""
    return max(0.0, min(1.0, k * n - i))

def ease_out(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def pop(k):
    """Escala de aparicion con un pequeno rebote (0 → 1)."""
    if k <= 0: return 0.0
    if k >= 1: return 1.0
    return ease_out(k) * (1 + 0.16 * math.sin(math.pi * k) * (1 - k) ** 0.5)

# ---------------------------------------------------------------- letras «rotuladas»
_glifos = {}
def glifos(texto, tam, col):
    """Glifos sueltos con un giro y un desplazamiento pequenos y deterministas: letra rotulada a mano."""
    key = (texto, int(tam), col)
    if key in _glifos: return _glifos[key]
    f = fuente(F_LETRA, tam)
    rng = random.Random(int(hashlib.md5(texto.encode("utf-8")).hexdigest()[:6], 16) + int(tam))
    out, x = [], 0.0
    asc, desc = f.getmetrics()
    gh = asc + desc + 12
    for ch in texto:
        w = f.getlength(ch)
        if ch.strip():
            bb = f.getbbox(ch)
            gw = int(bb[2] - bb[0]) + 14
            im = Image.new("RGBA", (gw, int(gh)), (0, 0, 0, 0)); dd = ImageDraw.Draw(im)
            dd.text((7 - bb[0], 6), ch, font=f, fill=col + (255,))
            im = im.rotate(rng.uniform(-3.5, 3.5), resample=Image.BICUBIC)
            out.append((im, x + bb[0] - 7, rng.uniform(-1, 1) * tam * 0.035 - 6))
        x += w
    _glifos[key] = (out, x)
    return _glifos[key]

def letras(img, x, y, texto, tam, col=TINTA, n=None, centrado=False):
    """Pega las n primeras letras de `texto` (todas si n es None) con la parte superior en y. Devuelve el ancho."""
    gl, ancho = glifos(texto, tam, col)
    if centrado: x -= ancho / 2
    for i, (im, gx, gy) in enumerate(gl):
        if n is not None and i >= n: break
        img.paste(im, (int(x + gx), int(y + gy)), im)
    return ancho

def ancho_letras(texto, tam):
    return fuente(F_LETRA, tam).getlength(texto)

def envolver(texto, tam, maxw, maxlines=4):
    f = fuente(F_LETRA, tam)
    lines, cur = [], ""
    for w in texto.split():
        t2 = (cur + " " + w).strip()
        if f.getlength(t2) <= maxw or not cur: cur = t2
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines[:maxlines]

def ajustar(texto, maxw, smax, smin=30, maxlines=3):
    for tam in range(int(smax), int(smin) - 1, -4):
        ls = envolver(texto, tam, maxw, maxlines + 1)
        if len(ls) <= maxlines and all(ancho_letras(l, tam) <= maxw for l in ls):
            return tam, ls
    return smin, envolver(texto, smin, maxw, maxlines)

# ---------------------------------------------------------------- personajes
def parpadeo(t, fase):
    b = (t * 1.0 + fase) % 3.3
    return 0.1 if b < 0.12 else 1.0

def bit(L, cx, cy, esc, t, accion, hablando, k=1.0, mira=1):
    """«Bit»: robotito redondo blanco con pantalla-cara cian. (cx, cy) = suelo bajo los pies."""
    if k <= 0: return
    R = 150 * esc * pop(k)
    if R < 4: return
    g = max(4, int(9 * esc))
    resp = 1 + 0.012 * math.sin(2 * math.pi * 0.5 * t)
    salto = 0.0
    if accion == "sorpresa": salto = 34 * esc * max(0.0, math.sin(min(1.0, t / 0.4) * math.pi))
    if accion == "celebra": salto = 24 * esc * abs(math.sin(2 * math.pi * 1.5 * t))
    if accion == "entrar": salto = 10 * esc * abs(math.sin(2 * math.pi * 3 * t)) * (1 if t < 0.8 else 0)
    yc = cy - R * 1.08 * resp - salto
    tilt = 0.0
    if accion == "encoge": tilt = 8 * esc * math.sin(2 * math.pi * 0.6 * t)
    if accion == "piensa": tilt = -6 * esc
    # sombra y ruedas
    L.d.ellipse([cx - R * 0.78, cy - 9 * esc, cx + R * 0.78, cy + 9 * esc], fill=SOMBRA)
    for s in (-1, 1):
        L.trazo(arco(cx + s * R * 0.42, cy - 14 * esc - salto, R * 0.2, R * 0.16, 180, 360), g, TINTA, 1.0, 1.0)
        L.d.line([(cx + s * R * 0.42 - R * 0.2, cy - 14 * esc - salto), (cx + s * R * 0.42 + R * 0.2, cy - 14 * esc - salto)], fill=TINTA, width=g)
    # cuerpo
    L.trazo(circ(cx + tilt * 0.3, yc, R * resp), g + 2, TINTA, 1.0, 1.8, fill=BLANCO, cerrado=True)
    # antena
    ax = cx + tilt * 0.6 + 4 * esc * math.sin(2 * math.pi * 0.9 * t)
    L.trazo([(cx + tilt * 0.3, yc - R * resp), (ax, yc - R * 1.32)], g, TINTA, 1.0, 1.0)
    L.trazo(circ(ax, yc - R * 1.44, R * 0.11, 20), g - 2, TINTA, 1.0, 0.8, fill=CIAN, cerrado=True)
    # pantalla-cara
    sw, sh = R * 1.28, R * 0.9
    sx0 = cx + tilt * 0.5 - sw / 2; sy0 = yc - sh / 2 - R * 0.1
    L.trazo(rrect(sx0, sy0, sx0 + sw, sy0 + sh, R * 0.2), g, TINTA, 1.0, 1.2, fill=CIAN, cerrado=True)
    # ojos (parpadean)
    pa = parpadeo(t, 0.7)
    grande = accion == "sorpresa"
    rx = R * (0.11 if grande else 0.085); ry = rx * 1.15 * pa
    ey = yc - R * 0.2 + (R * 0.05 if accion == "piensa" else 0)
    dx = mira * R * 0.04
    for s in (-1, 1):
        ex = sx0 + sw / 2 + s * R * 0.3 + dx
        if accion == "celebra":   # ojos felices ^ ^
            L.trazo(arco(ex, ey + rx * 0.4, rx * 1.1, rx * 0.9, 200, 340, 10), g - 2, TINTA, 1.0, 0.6)
        else:
            L.d.ellipse([ex - rx, ey - ry, ex + rx, ey + ry], fill=TINTA)
            if pa > 0.5: L.d.ellipse([ex + rx * 0.25, ey - ry * 0.55, ex + rx * 0.65, ey - ry * 0.1], fill=BLANCO)
    if accion == "encoge":   # cejas de duda
        for s in (-1, 1):
            ex = sx0 + sw / 2 + s * R * 0.3 + dx
            L.trazo([(ex - rx, ey - R * 0.2 + s * 3), (ex + rx, ey - R * 0.2 - s * 3)], g - 2, TINTA, 1.0, 0.5)
    # boca (se mueve mientras habla)
    mx = sx0 + sw / 2 + dx * 0.5; my = yc + R * 0.17
    if hablando:
        ap = 0.5 + 0.5 * math.sin(2 * math.pi * 8.5 * t + 1.0)
        bw = R * (0.16 + 0.06 * ap); bh = R * (0.03 + 0.13 * ap)
        L.d.ellipse([mx - bw, my - bh, mx + bw, my + bh], fill=TINTA)
        if bh > R * 0.07: L.d.ellipse([mx - bw * 0.6, my + bh * 0.1, mx + bw * 0.6, my + bh * 0.85], fill=CIAN_OSCURO)
    elif accion == "sorpresa":
        L.trazo(circ(mx, my, R * 0.09, 20), g - 2, TINTA, 1.0, 0.5, fill=TINTA, cerrado=True)
    elif accion in ("celebra", "saluda"):
        L.trazo(arco(mx, my - R * 0.06, R * 0.22, R * 0.16, 15, 165, 14), g - 2, TINTA, 1.0, 0.6)
    elif accion in ("encoge", "piensa"):
        L.trazo([(mx - R * 0.14, my), (mx + R * 0.14, my - R * 0.02)], g - 2, TINTA, 1.0, 0.6)
    else:
        L.trazo(arco(mx, my - R * 0.03, R * 0.17, R * 0.1, 20, 160, 12), g - 2, TINTA, 1.0, 0.6)
    # brazos y manos
    hy = yc + R * 0.12
    def mano(hx, hy2, dedo=None):
        L.trazo(circ(hx, hy2, R * 0.12, 16), g - 2, TINTA, 1.0, 0.8, fill=BLANCO, cerrado=True)
        if dedo: L.trazo([(hx, hy2), (hx + dedo[0], hy2 + dedo[1])], g - 1, TINTA, 1.0, 0.6)
    for s in (-1, 1):
        hx0 = cx + s * R * 0.96; sway = math.sin(2 * math.pi * 1.1 * t + (0 if s > 0 else 1.2))
        if accion == "senala" and s == mira:
            hx, hy2 = hx0 + s * R * 0.75, hy - R * 0.25 + 4 * esc * sway
            L.trazo([(hx0, hy), (hx, hy2)], g, TINTA, 1.0, 1.0); mano(hx, hy2, (s * R * 0.14, -R * 0.02))
        elif accion in ("celebra", "sorpresa"):
            w = (18 * esc * sway) if accion == "celebra" else 0
            hx, hy2 = hx0 + s * R * 0.35 + w, hy - R * 0.95
            L.trazo([(hx0, hy), (hx0 + s * R * 0.5, hy - R * 0.4), (hx, hy2)], g, TINTA, 1.0, 1.0); mano(hx, hy2)
        elif accion == "encoge":
            hx, hy2 = hx0 + s * R * 0.42, hy - R * 0.3 + tilt * 0.3
            L.trazo([(hx0, hy), (hx, hy2)], g, TINTA, 1.0, 1.0); mano(hx, hy2)
        elif accion == "saluda" and s == mira:
            hx, hy2 = hx0 + s * R * 0.35 + 16 * esc * sway, hy - R * 0.9
            L.trazo([(hx0, hy), (hx0 + s * R * 0.45, hy - R * 0.4), (hx, hy2)], g, TINTA, 1.0, 1.0); mano(hx, hy2)
        elif accion == "piensa" and s == mira:
            hx, hy2 = cx + s * R * 0.62, yc + R * 0.42
            L.trazo([(hx0, hy), (hx0 + s * R * 0.2, hy + R * 0.35), (hx, hy2)], g, TINTA, 1.0, 1.0); mano(hx, hy2)
        elif accion in ("explica",) and s == mira:
            hx, hy2 = hx0 + s * R * 0.5, hy - R * 0.1 - R * 0.22 * sway
            L.trazo([(hx0, hy), (hx, hy2)], g, TINTA, 1.0, 1.0); mano(hx, hy2)
        else:
            hx, hy2 = hx0 + s * R * 0.3, hy + R * 0.42 + 3 * esc * sway
            L.trazo([(hx0, hy), (hx, hy2)], g, TINTA, 1.0, 1.0); mano(hx, hy2)
    # extras
    if accion == "celebra":
        rng = random.Random(7)
        for i in range(7):
            a = rng.uniform(0, 2 * math.pi); rr = R * (1.5 + 0.5 * ((t * 1.3 + i * 0.37) % 1.0))
            px, py = cx + rr * math.cos(a), yc - R * 0.3 + rr * 0.8 * math.sin(a)
            L.trazo([(px - 10 * esc, py), (px + 10 * esc, py)], g - 2, CIAN, 1.0, 0.4)
            L.trazo([(px, py - 10 * esc), (px, py + 10 * esc)], g - 2, CIAN, 1.0, 0.4)
    if accion == "piensa":
        for i in range(3):
            on = (t * 2.2) % 3.0 >= i
            if on: L.punto(cx + mira * R * (0.9 + 0.25 * i), yc - R * (1.1 + 0.3 * i), R * (0.06 + 0.03 * i), CIAN)
    if accion == "sorpresa" and t < 1.2:
        letras(L.img, cx + mira * R * 1.15, yc - R * 1.75, "!", int(R * 0.9), CIAN, centrado=True)

def paco(L, cx, cy, esc, t, accion, hablando, k=1.0, mira=1):
    """«Paco»: muneco de palo que se agobia con la tecnologia. (cx, cy) = suelo bajo los pies."""
    if k <= 0: return
    Hp = 440 * esc * pop(k)
    if Hp < 10: return
    g = max(4, int(8 * esc))
    r = 0.135 * Hp
    bob = 3 * esc * math.sin(2 * math.pi * 0.5 * t)
    salto = 0.0
    if accion == "celebra": salto = 26 * esc * abs(math.sin(2 * math.pi * 1.5 * t + 0.8))
    if accion == "sorpresa": salto = 30 * esc * max(0.0, math.sin(min(1.0, t / 0.4) * math.pi))
    wob = 4 * esc * math.sin(2 * math.pi * 2.2 * t) if accion == "agobiado" else 0.0
    cad = cy - 0.42 * Hp - salto
    cue = cy - 0.72 * Hp - salto + bob
    hx_c = cx + wob; hy_c = cue - r - 4 * esc
    L.d.ellipse([cx - Hp * 0.22, cy - 7 * esc, cx + Hp * 0.22, cy + 7 * esc], fill=SOMBRA)
    # piernas (caminan si entra)
    paso = math.sin(2 * math.pi * 3 * t) * (1 if accion == "entrar" and t < 0.8 else 0)
    for s in (-1, 1):
        px = cx + s * 0.11 * Hp + s * paso * 10 * esc
        py = cy - (abs(paso) * 12 * esc if s * paso > 0 else 0)
        L.trazo([(cx, cad), (px, py)], g, TINTA, kparte(k, 0, 1), 1.2)
        L.trazo([(px - s * 2, py), (px + s * 0.07 * Hp, py)], g, TINTA, 1.0, 0.6)
    # tronco y cabeza
    L.trazo([(cx, cad), (cx + wob * 0.5, cue)], g, TINTA, 1.0, 1.2)
    L.trazo(circ(hx_c, hy_c, r), g, TINTA, 1.0, 1.6, fill=PAPEL, cerrado=True)
    # pelo: tres trazos
    for i, a in enumerate((-125, -95, -62)):
        x0, y0 = hx_c + r * math.cos(math.radians(a)), hy_c + r * math.sin(math.radians(a))
        L.trazo([(x0, y0), (x0 + 0.22 * r * math.cos(math.radians(a - 25)), y0 + 0.32 * r * math.sin(math.radians(a - 25)) - 0.2 * r)], g - 2, TINTA, 1.0, 0.5)
    # cara
    pa = parpadeo(t, 1.9)
    ex0 = hx_c + mira * r * 0.12
    grande = accion == "sorpresa"
    for s in (-1, 1):
        ex = ex0 + s * r * 0.3; ey = hy_c - r * 0.12
        if pa < 0.5 and not grande:
            L.trazo([(ex - r * 0.1, ey), (ex + r * 0.1, ey)], g - 2, TINTA, 1.0, 0.3)
        else:
            rr = r * (0.14 if grande else 0.075)
            L.d.ellipse([ex - rr, ey - rr * 1.15, ex + rr, ey + rr * 1.15], fill=TINTA)
            if grande: L.d.ellipse([ex - rr * 0.35, ey - rr * 0.5, ex + rr * 0.35, ey + rr * 0.2], fill=PAPEL)
        if accion == "agobiado":   # cejas inclinadas
            L.trazo([(ex - r * 0.16, ey - r * 0.28 + s * r * 0.06), (ex + r * 0.16, ey - r * 0.28 - s * r * 0.06)], g - 2, TINTA, 1.0, 0.4)
        if accion == "sorpresa":
            L.trazo([(ex - r * 0.16, ey - r * 0.42), (ex + r * 0.16, ey - r * 0.45)], g - 2, TINTA, 1.0, 0.4)
    mx, my = hx_c + mira * r * 0.08, hy_c + r * 0.4
    if hablando:
        ap = 0.5 + 0.5 * math.sin(2 * math.pi * 8.0 * t)
        L.trazo(arco(mx, my, r * 0.26, r * (0.06 + 0.2 * ap), 0, 360, 16), g - 2, TINTA, 1.0, 0.5, fill=TINTA, cerrado=True)
    elif accion == "agobiado":
        pts = [(mx - r * 0.3 + i * r * 0.12, my + (r * 0.07 if i % 2 else -r * 0.07)) for i in range(6)]
        L.trazo(pts, g - 2, TINTA, 1.0, 0.4)
    elif accion == "sorpresa":
        L.trazo(circ(mx, my + r * 0.05, r * 0.14, 16), g - 2, TINTA, 1.0, 0.4, fill=TINTA, cerrado=True)
    elif accion in ("piensa", "encoge"):
        L.trazo([(mx - r * 0.22, my + r * 0.02), (mx + r * 0.22, my - r * 0.04)], g - 2, TINTA, 1.0, 0.4)
    else:
        L.trazo(arco(mx, my - r * 0.08, r * 0.3, r * 0.2, 20, 160, 12), g - 2, TINTA, 1.0, 0.5)
    # brazos
    hom = (cx + wob * 0.4, cue + 0.06 * Hp)
    def brazo(s, codo, mano):
        L.trazo([hom, codo, mano], g, TINTA, 1.0, 1.1)
        L.trazo(circ(mano[0], mano[1], r * 0.18, 12), g - 2, TINTA, 1.0, 0.5, fill=PAPEL, cerrado=True)
    sway = math.sin(2 * math.pi * 1.0 * t)
    for s in (-1, 1):
        if accion == "agobiado":
            brazo(s, (cx + s * 0.3 * Hp, cue - 0.12 * Hp), (hx_c + s * r * 0.75, hy_c - r * 0.75 + wob))
        elif accion in ("celebra", "sorpresa"):
            w = 14 * esc * sway if accion == "celebra" else 0
            brazo(s, (cx + s * 0.26 * Hp, cue - 0.1 * Hp), (cx + s * 0.3 * Hp + w, cue - 0.36 * Hp))
        elif accion == "encoge":
            brazo(s, (cx + s * 0.2 * Hp, cue + 0.1 * Hp), (cx + s * 0.34 * Hp, cue - 0.02 * Hp + 2 * sway))
        elif accion == "senala" and s == mira:
            brazo(s, (cx + s * 0.22 * Hp, cue), (cx + s * 0.42 * Hp, cue - 0.08 * Hp + 3 * sway))
        elif accion == "piensa" and s == mira:
            brazo(s, (cx + s * 0.2 * Hp, cue + 0.12 * Hp), (hx_c + s * r * 0.35, hy_c + r * 0.95))
        elif accion == "saluda" and s == mira:
            brazo(s, (cx + s * 0.24 * Hp, cue - 0.1 * Hp), (cx + s * 0.3 * Hp + 16 * esc * sway, cue - 0.36 * Hp))
        elif accion == "explica" and s == mira:
            brazo(s, (cx + s * 0.2 * Hp, cue + 0.1 * Hp), (cx + s * 0.34 * Hp, cue - 0.02 * Hp - 0.08 * Hp * sway))
        else:
            brazo(s, (cx + s * 0.16 * Hp, cue + 0.16 * Hp), (cx + s * 0.22 * Hp, cue + 0.3 * Hp + 2 * esc * sway))
    # extras
    if accion == "agobiado":   # gotas de sudor (cian) y rayitas
        for i in range(3):
            f = (t * 1.6 + i * 0.33) % 1.0
            gx = hx_c + (-1 if i % 2 else 1) * r * (1.2 + 0.5 * f); gy = hy_c - r * 0.6 + f * r * 0.9
            L.trazo([(gx, gy - r * 0.16), (gx - r * 0.07, gy), (gx + r * 0.07, gy), (gx, gy - r * 0.16)], g - 3, CIAN, 1.0, 0.3, fill=CIAN, cerrado=True)
        for i in range(3):
            a = math.radians(-70 + 20 * i)
            L.trazo([(hx_c + r * 1.2 * math.cos(a), hy_c + r * 1.2 * math.sin(a)), (hx_c + r * 1.55 * math.cos(a), hy_c + r * 1.55 * math.sin(a))], g - 2, TINTA, 1.0, 0.3)
    if accion in ("encoge", "piensa"):
        if (t * 1.5) % 1.0 < 0.85:
            letras(L.img, hx_c + mira * r * 1.3, hy_c - r * 2.3, "?", int(r * 1.3), CIAN, centrado=True)
    if accion == "sorpresa" and t < 1.2:
        letras(L.img, hx_c + mira * r * 1.3, hy_c - r * 2.4, "!", int(r * 1.3), CIAN, centrado=True)

def invitado(L, cx, cy, esc, t, nombre, k=1.0):
    """Personaje generico inventado para ChatGPT / Claude / Gemini: forma simple distinta por nombre y su nombre
    en texto debajo (nunca su logo)."""
    if k <= 0: return
    s = 110 * esc * pop(k)
    if s < 4: return
    g = max(4, int(8 * esc))
    bob = 5 * esc * math.sin(2 * math.pi * 0.6 * t + 1.0)
    yc = cy - s - bob
    if nombre == "gemini":
        cuerpo = [(cx, yc - s), (cx + s, yc), (cx, yc + s), (cx - s, yc)]
    elif nombre == "claude":
        cuerpo = [(cx + s * math.cos(math.radians(30 + 60 * i)), yc + s * math.sin(math.radians(30 + 60 * i))) for i in range(6)]
    else:
        cuerpo = rrect(cx - s, yc - s, cx + s, yc + s, s * 0.3)
    L.trazo(cuerpo, g, TINTA, 1.0, 1.4, fill=BLANCO, cerrado=True)
    L.trazo([(cx, yc - s), (cx, yc - s * 1.3)], g, TINTA, 1.0, 0.8)
    L.punto(cx, yc - s * 1.4, s * 0.1, CIAN)
    pa = parpadeo(t, 2.6)
    for sx in (-1, 1):
        ex, ey = cx + sx * s * 0.3, yc - s * 0.12
        if pa < 0.5: L.trazo([(ex - s * 0.1, ey), (ex + s * 0.1, ey)], g - 2, TINTA, 1.0, 0.3)
        else: L.punto(ex, ey, s * 0.085, TINTA)
    L.trazo(arco(cx, yc + s * 0.18, s * 0.28, s * 0.2, 20, 160, 12), g - 2, TINTA, 1.0, 0.5)
    etiqueta = INVITADOS.get(nombre, nombre.capitalize())
    tam = int(44 * esc)
    aw = ancho_letras(etiqueta, tam) + 36 * esc
    L.trazo(rrect(cx - aw / 2, cy + 10, cx + aw / 2, cy + 10 + tam * 1.45, 14), g - 2, CIAN, 1.0, 0.8, fill=BLANCO, cerrado=True)
    letras(L.img, cx, cy + 10 + tam * 0.16, etiqueta, tam, TINTA, centrado=True)

# ---------------------------------------------------------------- objetos
def dispositivo(L, tipo, box, k):
    """Movil o portatil dibujado; devuelve la caja interior de la pantalla."""
    x0, y0, x1, y1 = box
    if tipo == "portatil":
        sy1 = y1 - 110
        L.trazo(rrect(x0, y0, x1, sy1, 26), 11, TINTA, kparte(k, 0, 3), 1.6, fill=BLANCO, cerrado=True)
        L.trazo([(x0 - 40, sy1), (x1 + 40, sy1), (x1 + 70, sy1 + 70), (x0 - 70, sy1 + 70)], 11, TINTA, kparte(k, 1, 3), 1.6, fill=BLANCO, cerrado=True)
        L.trazo([(x0 + (x1 - x0) * 0.38, sy1 + 22), (x0 + (x1 - x0) * 0.62, sy1 + 22)], 7, TINTA, kparte(k, 2, 3), 0.6)
        return (x0 + 26, y0 + 26, x1 - 26, sy1 - 26)
    L.trazo(rrect(x0, y0, x1, y1, 64), 11, TINTA, kparte(k, 0, 3), 1.6, fill=BLANCO, cerrado=True)
    cx = (x0 + x1) / 2
    L.trazo([(cx - 70, y0 + 30), (cx + 70, y0 + 30)], 8, TINTA, kparte(k, 1, 3), 0.5)
    L.trazo([(cx - 80, y1 - 34), (cx + 80, y1 - 34)], 8, TINTA, kparte(k, 2, 3), 0.5)
    return (x0 + 26, y0 + 72, x1 - 26, y1 - 72)

def pantalla_texto(L, caja, lineas, nvis, t, etiqueta=None):
    """Caja de prompt cian dentro de la pantalla con texto tecleado (monoespaciada) y cursor parpadeante."""
    x0, y0, x1, y1 = caja
    anchow = x1 - x0 - 60
    tam = 44 if (x1 - x0) > 560 else 38
    f = fuente(F_MONO, tam)
    # las lineas largas se parten por palabras al ancho de la pantalla (la letra no baja de 30 px)
    def partir(ls, f_):
        out = []
        for l in ls:
            cur = ""
            for w in l.split():
                t2 = (cur + " " + w).strip()
                if f_.getlength(t2) <= anchow or not cur: cur = t2
                else: out.append(cur); cur = w
            out.append(cur)
        return out
    # los renglones del guion se juntan en parrafos (salvo los que empiezan por numero, guion o vineta)
    parr, cur = [], ""
    for l in lineas:
        if cur and not re.match(r"^\s*(\d+[.)]|[-•·*])", l): cur = (cur + " " + l.strip()).strip()
        else:
            if cur: parr.append(cur)
            cur = l.strip()
    if cur: parr.append(cur)
    lineas = partir(parr, f)
    while tam > 30 and len(lineas) > 5:
        tam -= 2; f = fuente(F_MONO, tam); lineas = partir(lineas, f)
    lineas = lineas[:6]
    lh = int(tam * 1.4)
    alto = lh * len(lineas) + 50
    by0 = y0 + max(40, ((y1 - y0) - alto) * 0.42)   # caja de prompt algo por encima del centro de la pantalla
    if etiqueta:
        L.d.text((x0 + 30, by0 - 6), etiqueta, font=fuente(F_LETRA, 28), fill=CIAN_OSCURO)
        by0 += 38
    L.trazo(rrect(x0 + 16, by0, x1 - 16, by0 + alto, 22), 7, CIAN, 1.0, 0.9, fill=CIAN_CLARO, cerrado=True)
    rest = nvis; cx, cy = None, None
    for i, l in enumerate(lineas):
        part = l[:max(0, rest)]; rest -= len(l)
        y = by0 + 25 + i * lh
        if part:
            L.d.text((x0 + 30, y), part, font=f, fill=TINTA)
        if rest <= 0 or i == len(lineas) - 1:
            cx, cy = x0 + 30 + f.getlength(part), y
            break
    if cx is not None and int(t * 2.5) % 2 == 0:
        L.d.rectangle([cx + 2, cy + 2, cx + tam * 0.5, cy + tam * 1.05], fill=CIAN)

def pizarra_marco(L, box, k):
    x0, y0, x1, y1 = box
    L.trazo(rrect(x0, y0, x1, y1, 18), 12, TINTA, kparte(k, 0, 2), 1.8, fill=BLANCO, cerrado=True)
    cx = (x0 + x1) / 2
    L.trazo(rrect(cx - 60, y0 - 22, cx + 60, y0 + 18, 10), 8, TINTA, kparte(k, 1, 2), 0.8, fill=CIAN, cerrado=True)

def lapiz(L, x, y, esc=1.0):
    """Lapiz pequeno con punta cian en la posicion de escritura."""
    x += 14 * esc
    L.trazo([(x + 6, y - 2), (x + 44 * esc, y - 54 * esc)], 11 * esc, TINTA, 1.0, 0.4)
    L.trazo([(x + 44 * esc, y - 54 * esc), (x + 52 * esc, y - 64 * esc)], 7 * esc, CIAN, 1.0, 0.2)
    L.punto(x + 2, y + 2, 5 * esc, CIAN)

def pizarra_texto(L, box, lineas, numerada, nvis, escribiendo):
    """Lineas rotuladas que se escriben letra a letra; con numerada, un circulo cian numerado por linea."""
    x0, y0, x1, y1 = box
    margen = 110 if numerada else 46
    anchow = x1 - x0 - margen - 40
    tam = 74
    def alto_total(tam_):
        return sum(len(envolver(l, tam_, anchow, 3)) for l in lineas) * int(tam_ * 1.3) + (len(lineas) - 1) * 26
    while tam > 30 and alto_total(tam) > (y1 - y0 - 80):
        tam -= 4
    lh = int(tam * 1.3)
    y = y0 + 48
    rest = nvis
    for i, l in enumerate(lineas):
        subl = envolver(l, tam, anchow, 3)
        if numerada and rest > 0:
            r = tam * 0.46
            cxn, cyn = x0 + 60, y + lh * 0.55
            L.trazo(circ(cxn, cyn, r, 24), 6, CIAN, 1.0, 0.8, fill=CIAN, cerrado=True)
            letras(L.img, cxn, cyn - tam * 0.5, str(i + 1), int(tam * 0.8), BLANCO, centrado=True)
        for sl in subl:
            n = max(0, min(len(sl), rest)); rest -= len(sl)
            if n > 0:
                letras(L.img, x0 + margen, y, sl, tam, TINTA, n=n)
                if escribiendo and 0 <= rest < 0 + 1 and n < len(sl) + 1:
                    pass
            if rest <= 0 and escribiendo:
                lapiz(L, x0 + margen + ancho_letras(sl[:n], tam), y + tam * 0.95)
                return
            y += lh
        y += 26

def flecha(L, p0, p1, k, color=CIAN, grosor=14, curva=0.18):
    """Flecha curva a mano que se dibuja de p0 a p1 (k = progreso)."""
    if k <= 0: return
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0; Lg = math.hypot(dx, dy) or 1.0
    cx, cy = (x0 + x1) / 2 - dy / Lg * Lg * curva, (y0 + y1) / 2 + dx / Lg * Lg * curva
    pts = [((1 - u) ** 2 * x0 + 2 * (1 - u) * u * cx + u * u * x1, (1 - u) ** 2 * y0 + 2 * (1 - u) * u * cy + u * u * y1) for u in np.linspace(0, 1, 26)]
    L.trazo(pts, grosor, color, min(1.0, k / 0.85), 1.4)
    if k > 0.85:
        kk = min(1.0, (k - 0.85) / 0.15)
        tx, ty = pts[-1]; px, py = pts[-3]
        a = math.atan2(ty - py, tx - px); h = grosor * 3.2 * kk
        for s in (-1, 1):
            L.trazo([(tx, ty), (tx - h * math.cos(a + s * 0.5), ty - h * math.sin(a + s * 0.5))], grosor, color, 1.0, 0.6)

def icono(L, nombre, cx, cy, s, t, k, agobio=False):
    """Iconos doodle de apoyo (correo, calendario, reloj, bombilla, chat, carpeta, lista, movil, portatil)."""
    if k <= 0: return
    s = s * pop(k)
    if s < 4: return
    g = 9
    cy = cy + 6 * math.sin(2 * math.pi * 0.7 * t)
    if nombre == "correo":
        L.trazo(rrect(cx - s, cy - s * 0.65, cx + s, cy + s * 0.65, 10), g, TINTA, 1.0, 1.4, fill=BLANCO, cerrado=True)
        L.trazo([(cx - s, cy - s * 0.65), (cx, cy + s * 0.1), (cx + s, cy - s * 0.65)], g, TINTA, 1.0, 1.0)
        L.punto(cx + s * 0.85, cy - s * 0.6, s * 0.22, CIAN)
    elif nombre == "calendario":
        L.trazo(rrect(cx - s, cy - s * 0.8, cx + s, cy + s * 0.8, 12), g, TINTA, 1.0, 1.4, fill=BLANCO, cerrado=True)
        L.trazo([(cx - s, cy - s * 0.4), (cx + s, cy - s * 0.4)], g, TINTA, 1.0, 0.8)
        L.d.rectangle([cx - s + 5, cy - s * 0.8 + 5, cx + s - 5, cy - s * 0.42], fill=CIAN)
        for i in range(3):
            for j in range(2):
                L.punto(cx - s * 0.5 + i * s * 0.5, cy + s * 0.05 + j * s * 0.4, s * 0.07, TINTA)
        for sx in (-0.5, 0.5):
            L.trazo([(cx + sx * s, cy - s * 1.0), (cx + sx * s, cy - s * 0.6)], g, TINTA, 1.0, 0.5)
    elif nombre == "reloj":
        L.trazo(circ(cx, cy, s), g, TINTA, 1.0, 1.4, fill=BLANCO, cerrado=True)
        for i in range(12):
            a = math.radians(i * 30); L.punto(cx + s * 0.85 * math.cos(a), cy + s * 0.85 * math.sin(a), 4, TINTA)
        vel = 6.0 if agobio else 0.3
        a1 = math.radians(-90 + t * 360 * vel / 12); a2 = math.radians(-90 + t * 360 * vel)
        L.trazo([(cx, cy), (cx + s * 0.5 * math.cos(a1), cy + s * 0.5 * math.sin(a1))], g, TINTA, 1.0, 0.4)
        L.trazo([(cx, cy), (cx + s * 0.72 * math.cos(a2), cy + s * 0.72 * math.sin(a2))], g - 2, CIAN, 1.0, 0.4)
    elif nombre == "bombilla":
        pul = 0.5 + 0.5 * math.sin(2 * math.pi * 1.5 * t)
        for i in range(8):
            a = math.radians(-90 + i * 45 - 22)
            L.trazo([(cx + s * 1.25 * math.cos(a), cy + s * 1.25 * math.sin(a)), (cx + s * (1.5 + 0.25 * pul) * math.cos(a), cy + s * (1.5 + 0.25 * pul) * math.sin(a))], g - 2, CIAN, 1.0, 0.4)
        L.trazo(circ(cx, cy, s), g, TINTA, 1.0, 1.4, fill=CIAN_CLARO, cerrado=True)
        L.trazo(rrect(cx - s * 0.4, cy + s * 0.85, cx + s * 0.4, cy + s * 1.35, 8), g, TINTA, 1.0, 0.8, fill=BLANCO, cerrado=True)
    elif nombre == "chat":
        L.trazo(rrect(cx - s, cy - s * 0.75, cx + s * 0.4, cy + s * 0.15, 24) + [(cx - s * 0.7, cy + s * 0.5)], g, TINTA, 1.0, 1.2, fill=BLANCO, cerrado=False)
        L.trazo(rrect(cx - s * 0.2, cy - s * 0.1, cx + s * 1.1, cy + s * 0.75, 24), g, TINTA, 1.0, 1.2, fill=CIAN, cerrado=True)
        for i in range(3): L.punto(cx + s * 0.2 + i * s * 0.25, cy + s * 0.33, s * 0.06, BLANCO)
    elif nombre == "carpeta":
        L.trazo([(cx - s, cy - s * 0.5), (cx - s * 0.4, cy - s * 0.5), (cx - s * 0.25, cy - s * 0.7), (cx + s * 0.3, cy - s * 0.7), (cx + s * 0.3, cy - s * 0.5), (cx + s, cy - s * 0.5), (cx + s, cy + s * 0.7), (cx - s, cy + s * 0.7)], g, TINTA, 1.0, 1.4, fill=CIAN, cerrado=True)
    elif nombre == "lista":
        L.trazo(rrect(cx - s * 0.8, cy - s, cx + s * 0.8, cy + s, 14), g, TINTA, 1.0, 1.4, fill=BLANCO, cerrado=True)
        for i in range(3):
            y = cy - s * 0.55 + i * s * 0.55
            L.trazo([(cx - s * 0.5, y), (cx - s * 0.35, y + s * 0.15), (cx - s * 0.15, y - s * 0.15)], g - 2, CIAN, 1.0, 0.4)
            L.trazo([(cx, y), (cx + s * 0.55, y)], g - 2, TINTA, 1.0, 0.4)
    elif nombre == "portatil":
        dispositivo(L, "portatil", (cx - s, cy - s * 0.7, cx + s, cy + s * 0.7 + 60), 1.0)
    else:   # movil
        dispositivo(L, "movil", (cx - s * 0.55, cy - s, cx + s * 0.55, cy + s), 1.0)

def sello_img(txt):
    """Sello a mano: caja redondeada blanca con borde y texto cian (rojo si es FALSO/MITO/NO), girado."""
    col = ROJO if (txt.startswith("FALS") or txt in ("MITO", "BULO", "NO", "MENTIRA", "ERROR")) else CIAN
    tam = 120
    while tam > 60 and ancho_letras(txt, tam) > 700: tam -= 8
    tw = ancho_letras(txt, tam)
    bw, bh = int(tw + 110), int(tam * 1.5 + 50)
    im = Image.new("RGBA", (bw + 40, bh + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    trazo(d, rrect(20, 20, bw + 20, bh + 20, 24), 12, col, 1.0, 1.8, 0.0, fill=BLANCO, cerrado=True)
    letras(im, (bw + 40) / 2, 20 + 36, txt, tam, col, centrado=True)
    return im.rotate(-7, expand=True, resample=Image.BICUBIC)

# ---------------------------------------------------------------- escena
def _lista_str(v):
    if v is None: return []
    if isinstance(v, str): return [v.strip()] if v.strip() else []
    if isinstance(v, (list, tuple)): return [str(x).strip() for x in v if str(x).strip()]
    return [str(v)]

def normalizar(spec):
    """Admite los dos formatos: los elementos sueltos en la escena ("personajes", "pizarra", "pantalla", "flecha",
    "antes_despues"...) y el bloque "dibujo": {"personajes", "accion", "objeto", "pantalla", "invitados"}."""
    dib = spec.get("dibujo") if isinstance(spec.get("dibujo"), dict) else {}
    estilo = str(spec.get("estilo") or "paso").strip().lower()
    out = {"estilo": estilo}
    # personajes: ["paco", "bit"] | ["paco:agobiado", "bit:senala"] | [{"nombre": "bit", "accion": "senala"}]
    raw = spec.get("personajes", dib.get("personajes"))
    accion_gen = str(spec.get("accion") or dib.get("accion") or "").strip().lower()
    pers = []
    if raw is None:
        if estilo == "gancho": pers = [("paco", "sorpresa"), ("bit", "explica")]
        elif estilo == "problema": pers = [("paco", "agobiado")]
        elif estilo in ("resultado", "cierre"): pers = [("paco", "celebra" if estilo == "resultado" else "explica"), ("bit", "celebra" if estilo == "resultado" else "saluda")]
        else: pers = [("bit", "explica")]
    else:
        for p in (raw if isinstance(raw, (list, tuple)) else [raw]):
            if isinstance(p, dict):
                nom = str(p.get("nombre") or p.get("quien") or "").strip().lower(); acc = str(p.get("accion") or "").strip().lower()
            else:
                s = str(p).strip().lower(); nom, _, acc = s.partition(":")
            nom = nom.strip(); acc = acc.strip()
            if nom not in ("paco", "bit"): continue
            if not acc:
                if accion_gen in ("agobiado", "piensa", "sorpresa", "sorprendido", "encoge"):
                    acc = accion_gen if nom == "paco" else "explica"
                elif accion_gen in ("celebra",):
                    acc = "celebra"
                elif accion_gen in ("explica", "senala", "saluda", "entrar"):
                    acc = accion_gen if nom == "bit" else "escucha"
                else:
                    acc = "explica" if nom == "bit" else ("agobiado" if estilo == "problema" else "escucha")
            acc = {"sorprendido": "sorpresa", "señala": "senala", "celebrar": "celebra", "encogerse": "encoge", "entra": "entrar", "agobio": "agobiado"}.get(acc, acc)
            if acc not in ACCIONES: acc = "explica"
            if nom not in [q[0] for q in pers]: pers.append((nom, acc))
    out["personajes"] = pers
    # objeto principal
    pant = spec.get("pantalla", dib.get("pantalla"))
    out["pantalla"] = None
    if pant:
        if isinstance(pant, dict):
            tipo = str(pant.get("tipo") or pant.get("dispositivo") or "").strip().lower()
            lineas = _lista_str(pant.get("texto") or pant.get("lineas"))
            etiqueta = str(pant.get("etiqueta") or "").strip() or None
        else:
            tipo, lineas, etiqueta = "", _lista_str(pant), None
        if not tipo:
            tipo = "portatil" if str(spec.get("objeto") or dib.get("objeto") or "").lower() == "portatil" else "movil"
        if lineas: out["pantalla"] = {"tipo": "portatil" if tipo.startswith("port") else "movil", "lineas": lineas[:4], "etiqueta": etiqueta}
    piz = spec.get("pizarra", dib.get("pizarra"))
    lista = _lista_str(spec.get("lista"))[:3]
    out["pizarra"] = None
    if piz:
        if isinstance(piz, dict):
            ls = _lista_str(piz.get("pasos") or piz.get("lineas") or piz.get("texto")); num = bool(piz.get("numerada", len(ls) > 1))
            titulo = str(piz.get("titulo") or "").strip()
        else:
            ls = _lista_str(piz); num = isinstance(piz, (list, tuple)) and len(ls) > 1; titulo = ""
        if ls: out["pizarra"] = {"lineas": ls[:4], "numerada": num, "titulo": titulo}
    elif lista:
        out["pizarra"] = {"lineas": lista, "numerada": True, "titulo": ""}
    ad = spec.get("antes_despues", dib.get("antes_despues"))
    out["antes_despues"] = None
    if isinstance(ad, dict) and (ad.get("antes") or ad.get("despues")):
        out["antes_despues"] = {"antes": str(ad.get("antes") or "")[:60], "despues": str(ad.get("despues") or "")[:60]}
    elif isinstance(ad, (list, tuple)) and len(ad) >= 2:
        out["antes_despues"] = {"antes": str(ad[0])[:60], "despues": str(ad[1])[:60]}
    out["cifra"] = str(spec.get("cifra") or "").strip()
    out["unidad"] = str(spec.get("unidad") or "").strip()
    fl = spec.get("flecha", dib.get("flecha"))
    out["flecha"] = (str(fl).strip().lower() if isinstance(fl, str) else ("auto" if fl else None)) if fl is not None else None
    obj = str(spec.get("objeto") or dib.get("objeto") or "").strip().lower()
    out["objeto"] = obj if obj in OBJETOS else None
    inv = [str(x).strip().lower() for x in (spec.get("invitados") or dib.get("invitados") or []) if str(x).strip()]
    out["invitados"] = [x for x in inv if x in INVITADOS][:2]
    out["sello"] = str(spec.get("sello") or "").strip().upper()[:12]
    return out

PALETA_SUB = {"normal": TINTA, "activo": CIAN, "enfasis": ROJO, "borde": BLANCO}

def preparar_escena(sc, spec, seed):
    """Rellena la escena (objeto Scene de hacer_reel.py) con todo lo que necesita el modo dibujo."""
    rng = random.Random(seed * 1000 + sc.idx * 7 + 3)
    D = normalizar(spec)
    sc.D = D
    sc.style = D["estilo"]
    es_gancho = sc.style == "gancho"
    # subtitulos (misma clase que el modo humano, colores del papel)
    voz, enf_voz = HR.parsear_enfasis(spec.get("voz") or "")
    sub, enf_sub = HR.parsear_enfasis(spec.get("subtitulos") or "")
    texto, enf_txt = HR.parsear_enfasis(spec.get("texto") or "")
    dv = float(spec.get("_voz_dur") or 0)
    sc.voz_t0, sc.voz_t1, sc.tiempos_voz = 0.12, 0.12, None
    if es_gancho:
        base, enf = (texto, enf_txt) if texto else ((sub, enf_sub) if sub else (voz, enf_voz))
        sc.sub = HR.Subtitulos(base, HR.WPS_HUMANO, 0.0, sc.dur, entero=True, enfasis=enf, paleta=PALETA_SUB, cy=1385)
        sc.rotulo = None
        nw = len(voz.split())
        sc.voz_t1 = 0.12 + (dv if dv > 0.2 else nw / 2.6)
    else:
        base, enf = (sub, enf_sub) if sub else ((voz, enf_voz) if voz else (texto, enf_txt))
        tiempos = spec.get("_voz_palabras")
        if tiempos and len(tiempos) == len(base.split()):
            tiempos = [float(x) + 0.12 for x in tiempos]
        else:
            tiempos = None
        if dv > 0.2:
            wps = len(base.split()) / max(0.3, dv - 0.1)
        else:
            wps = max(HR.WPS_HUMANO, len(base.split()) / max(0.3, sc.dur * 0.8))
        sc.sub = HR.Subtitulos(base, wps, 0.12, sc.dur, enfasis=enf, tiempos=tiempos, paleta=PALETA_SUB, cy=1400) if base else None
        sc.rotulo = texto if (texto and base != texto) else None
        sc.tiempos_voz = tiempos
        sc.voz_t1 = 0.12 + (dv if dv > 0.2 else len(base.split()) / max(0.1, wps))
    # disposicion
    obj = None
    if D["pantalla"]: obj = "pantalla"
    elif D["antes_despues"]: obj = "antes_despues"
    elif D["pizarra"]: obj = "pizarra"
    elif D["cifra"]: obj = "cifra"
    sc.obj = obj
    pers = D["personajes"]
    suelo = 1235 if not es_gancho else 1150
    pos = {}
    if obj == "antes_despues":
        pers = []   # los personajes van dentro de los paneles
    if obj:
        esc = 0.66 if len(pers) else 1.0
        for nom, acc in pers:
            if nom == "paco": pos["paco"] = (200, suelo, esc, 1)
            else: pos["bit"] = (868, suelo, esc, -1)
        if obj == "pantalla" and D["pantalla"]["tipo"] == "movil":
            sc.caja = (320, 380, 760, 1130) if len(pers) else (280, 340, 800, 1210)
        elif obj == "pantalla":
            sc.caja = (190, 450, 890, 1000)
        elif obj == "pizarra":
            sc.caja = (120, 400, 960, 1010) if len(pers) else (100, 380, 980, 1120)
        elif obj == "antes_despues":
            sc.caja = (80, 400, 1000, 1020)
        else:
            sc.caja = (120, 430, 960, 900)
    else:
        if len(pers) == 2:
            for nom, acc in pers:
                pos[nom] = (330, suelo, 1.0, 1) if nom == "paco" else (760, suelo, 1.0, -1)
        elif len(pers) == 1:
            nom = pers[0][0]
            pos[nom] = (540 if not (D["invitados"] or D["objeto"]) else (330 if nom == "paco" else 750), suelo, 1.12, 1 if nom == "paco" else -1)
        sc.caja = None
    sc.pos = pos
    sc.acciones = dict(pers)
    # tiempos de aparicion
    sc.t_obj = 0.25 if pers else 0.1
    sc.dur_obj = 0.8 if obj in ("pizarra", "pantalla") else 0.5
    sc.cps = 20.0
    if obj in ("pizarra", "pantalla"):
        lineas = (D["pizarra"] or D["pantalla"])["lineas"]
        nchars = sum(len(l) for l in lineas)
        sc.t_texto = sc.t_obj + sc.dur_obj * 0.55
        disponible = max(0.6, sc.dur * 0.78 - sc.t_texto)   # que termine de escribirse hacia el 80 % de la escena
        sc.cps = max(26.0 if obj == "pizarra" else 22.0, nchars / disponible)
        sc.nchars = nchars
    # camara: segmentos de 2-4 s con un encuadre distinto cada uno (cortes)
    nseg = max(1, int(round(sc.dur / 3.0)))
    sc.segs = []
    for i in range(nseg):
        z0 = rng.choice([1.0, 1.02, 1.04, 1.06]); z1 = z0 + rng.choice([-0.02, 0.015, 0.025, 0.03])
        z1 = max(1.0, min(1.08, z1))
        sc.segs.append((z0, z1, rng.uniform(-18, 18), rng.uniform(-14, 10)))
    sc.seg_dur = sc.dur / nseg
    # eventos de sonido (tiempos relativos a la escena)
    ev = []
    for i, (nom, acc) in enumerate(pers):
        ev.append((0.05 + 0.12 * i, "pop"))
        if acc == "celebra": ev.append((0.3, "tada"))
    if obj in ("pizarra", "pantalla", "antes_despues", "cifra"):
        ev.append((sc.t_obj, "lapiz", sc.dur_obj))
    if obj in ("pizarra", "pantalla"):
        for j in range(min(sc.nchars, 400)):
            ev.append((sc.t_texto + j / sc.cps, "tecla" if obj == "pantalla" else "trazo"))
    if obj == "antes_despues":
        ev.append((sc.t_obj + 0.55, "silbido")); ev.append((sc.t_obj + 1.1, "pop"))
    if D["sello"]:
        ev.append((sc.sello_t + 0.13, "sello"))
    if D["flecha"]:
        ev.append((sc.t_obj + sc.dur_obj + 0.2, "silbido"))
    sc.eventos = ev
    sc.seed = seed
    sc.sello_im = sello_img(D["sello"]) if D["sello"] else None

def hablando(sc, t):
    if sc.tiempos_voz:
        return any(ti - 0.05 <= t <= ti + 0.32 for ti in sc.tiempos_voz)
    return sc.voz_t0 <= t <= sc.voz_t1

def camara(img, sc, t):
    """Zoom leve con deriva; un encuadre distinto en cada segmento (corte cada 2-4 s)."""
    i = min(len(sc.segs) - 1, int(t / sc.seg_dur)); p = (t - i * sc.seg_dur) / sc.seg_dur
    z0, z1, dx, dy = sc.segs[i]
    z = z0 + (z1 - z0) * p
    if abs(z - 1.0) < 1e-3 and abs(dx) < 1 and abs(dy) < 1: return img
    cw, ch = int(W / z), int(H / z)
    cx = (W - cw) / 2 + dx * p; cy = (H - ch) / 2 - 40 * (z - 1) * 10 + dy * p
    cx = max(0, min(W - cw, cx)); cy = max(0, min(H - ch, cy))
    return img.crop((int(cx), int(cy), int(cx) + cw, int(cy) + ch)).resize((W, H), Image.BILINEAR)

def rotulo(img, texto):
    tam, ls = ajustar(texto.strip()[:48], 820, 54, 36, 1)
    tx = ls[0] if ls else ""
    aw = ancho_letras(tx, tam) + 70
    L = Lienzo(img, 0)
    x0 = (W - aw) / 2
    L.trazo(rrect(x0, 180, x0 + aw, 180 + tam * 1.5 + 20, 18), 8, CIAN, 1.0, 1.4, fill=BLANCO, cerrado=True)
    letras(img, W / 2, 180 + 10 + tam * 0.12, tx, tam, TINTA, centrado=True)

def dibujar_objeto(L, sc, t):
    D = sc.D; obj = sc.obj
    if not obj: return
    k = ease_out((t - sc.t_obj) / sc.dur_obj)
    if k <= 0: return
    if obj == "pantalla":
        P = D["pantalla"]
        caja = dispositivo(L, P["tipo"], sc.caja, k)
        if t >= sc.t_texto:
            nvis = int((t - sc.t_texto) * sc.cps)
            pantalla_texto(L, caja, P["lineas"], nvis, t, P.get("etiqueta"))
    elif obj == "pizarra":
        P = D["pizarra"]
        pizarra_marco(L, sc.caja, k)
        if t >= sc.t_texto:
            nvis = int((t - sc.t_texto) * sc.cps)
            pizarra_texto(L, sc.caja, P["lineas"], P["numerada"], nvis, nvis < sc.nchars)
    elif obj == "cifra":
        parts = HR._cifra_parts(D["cifra"])
        kk = min(1.0, max(0.0, (t - sc.t_obj - 0.1) / 1.3)); kk = 1 - (1 - kk) ** 3
        if parts:
            pre, val, post, sep = parts
            cur = int(round(val * kk))
            txt = pre + ("{:,}".format(cur).replace(",", sep) if sep else str(cur)) + post
        else:
            txt = D["cifra"]
        tam = 230
        while tam > 100 and ancho_letras(D["cifra"], tam) > 880: tam -= 10
        cx, cy = 540, 600
        letras(L.img, cx, cy - tam * 0.6, txt, tam, TINTA, centrado=True)
        aw = ancho_letras(D["cifra"], tam)
        L.trazo([(cx - aw / 2 - 20, cy + tam * 0.72), (cx + aw / 2 + 20, cy + tam * 0.66)], 14, CIAN, k, 2.2)
        if D["unidad"] and kk > 0.5:
            letras(L.img, cx, cy + tam * 0.85, D["unidad"][:28], 56, CIAN_OSCURO, centrado=True)
    elif obj == "antes_despues":
        A = D["antes_despues"]; x0, y0, x1, y1 = sc.caja
        mid = (x0 + x1) / 2
        def panel(px0, px1, titulo, txt, col, kp, quien):
            if kp <= 0: return
            L.trazo(rrect(px0, y0, px1, y1, 20), 10, col, kp, 1.8, fill=BLANCO, cerrado=True)
            if kp >= 1:
                letras(L.img, (px0 + px1) / 2, y0 + 26, titulo, 50, col, centrado=True)
                tam, ls = ajustar(txt, px1 - px0 - 50, 68, 44, 1)
                if ancho_letras(ls[0] if ls else "", tam) > px1 - px0 - 50 or len(ls) > 1 or (ls and ls[0] != txt.strip()):
                    tam, ls = ajustar(txt, px1 - px0 - 50, 56, 34, 2)
                yy = y0 + 110
                for l in ls:
                    letras(L.img, (px0 + px1) / 2, yy, l, tam, TINTA if col == TINTA else CIAN_OSCURO, centrado=True); yy += tam * 1.3
                if quien == "paco": paco(L, (px0 + px1) / 2, y1 - 30, 0.42, t, "agobiado", False, 1.0, 1)
                else: bit(L, (px0 + px1) / 2, y1 - 30, 0.42, t, "celebra", False, 1.0, -1)
        panel(x0, mid - 50, "ANTES", A["antes"], TINTA, k, "paco")
        kf = ease_out((t - sc.t_obj - 0.55) / 0.4)
        flecha(L, (mid - 36, (y0 + y1) / 2 - 20), (mid + 36, (y0 + y1) / 2 - 20), kf, CIAN, 12, 0.0)
        panel(mid + 50, x1, "DESPUÉS", A["despues"], CIAN, ease_out((t - sc.t_obj - 0.8) / 0.5), "bit")

def dibujar_escena(L, sc, t):
    D = sc.D
    hab = hablando(sc, t)
    quien_habla = "bit" if "bit" in sc.pos else ("paco" if "paco" in sc.pos else None)
    # objeto de apoyo (icono) cuando no hay objeto principal
    if not sc.obj and D["objeto"] and not D["invitados"]:
        cx = 540 if len(sc.pos) != 1 else (760 if "paco" in sc.pos else 330)
        icono(L, D["objeto"], cx, 640, 130, t, ease_out((t - 0.2) / 0.5), agobio=(sc.acciones.get("paco") == "agobiado"))
    dibujar_objeto(L, sc, t)
    # invitados
    for i, nom in enumerate(D["invitados"]):
        cx = 540 if len(D["invitados"]) == 1 else (330 + 420 * i)
        if sc.obj: cx = 540; cy = 1230; e = 0.5
        else: cy = 900 if len(sc.pos) else 1000; e = 0.85
        invitado(L, cx, cy, e, t, nom, ease_out((t - 0.3 - 0.2 * i) / 0.5))
    # personajes
    for i, (nom, acc) in enumerate(D["personajes"]):
        if nom not in sc.pos: continue
        x, y, e, mira = sc.pos[nom]
        k = ease_out((t - 0.05 - 0.12 * i) / 0.45)
        if acc == "entrar":   # entra andando desde fuera
            p = ease_out(t / 0.8); x = x + (-mira) * (1 - p) * 520 if mira else x
            k = 1.0
        if nom == "bit": bit(L, x, y, e, t, acc, hab and quien_habla == "bit", k, mira)
        else: paco(L, x, y, e, t, acc, hab and quien_habla == "paco", k, mira)
    # flecha
    if D["flecha"]:
        kf = ease_out((t - sc.t_obj - sc.dur_obj - 0.2) / 0.6)
        f = D["flecha"]
        if f in ("auto", "true", "si", "sí"):
            if "bit" in sc.pos and (sc.obj or "paco" in sc.pos):
                bx, by, be, _ = sc.pos["bit"]
                p0 = (bx - 150 * be * 1.95, by - 150 * be * 1.35)
                if sc.obj and sc.caja:
                    p1 = (sc.caja[2] + 16, sc.caja[1] + (sc.caja[3] - sc.caja[1]) * 0.45)
                    flecha(L, p0, p1, kf, CIAN, 14, 0.42)
                else:
                    px, py, pe, _ = sc.pos["paco"]; p1 = (px + 90 * pe, py - 330 * pe)
                    flecha(L, p0, p1, kf)
            else:
                flecha(L, (300, 760), (780, 760), kf)
        elif f.startswith("izq"): flecha(L, (800, 720), (280, 720), kf)
        elif f.startswith("aba"): flecha(L, (540, 420), (540, 900), kf)
        elif f.startswith("arr"): flecha(L, (540, 900), (540, 420), kf)
        else: flecha(L, (280, 720), (800, 720), kf)

def render_frame(fi, sc, rg):
    lf = fi - sc.start; t = lf / FPS
    img = Image.fromarray(papel(sc.seed))
    L = Lienzo(img, fi)
    dibujar_escena(L, sc, t)
    img = camara(img, sc, t)
    if sc.rotulo:
        rotulo(img, sc.rotulo)
    if sc.sub is not None:
        capa = sc.sub.capa(t)
        if capa:
            timg, ty = capa
            img.paste(timg, (0, ty), timg)
    if sc.sello_im is not None and t >= sc.sello_t:
        st = sc.sello_im; k = min(1.0, (t - sc.sello_t) / 0.14)
        if k < 1.0:
            z = 2.0 - 1.0 * k
            st = st.resize((int(st.width * z), int(st.height * z)))
        imp = int((t - sc.sello_t - 0.14) * FPS)
        sx, sy = (rg.randint(-8, 8), rg.randint(-6, 6)) if 0 <= imp < 3 and k >= 1.0 else (0, 0)
        ys = 980 if sc.obj == "antes_despues" else 760
        img.paste(st, (540 - st.width // 2 + sx, ys - st.height // 2 + sy), st)
    return np.asarray(img, dtype=np.uint8)

# ---------------------------------------------------------------- sonido
def efectos(scenes, n, seed, SR):
    """Efectos discretos: pop al aparecer, lapiz al dibujar, teclas al teclear, trazo al rotular, silbido de la
    flecha, golpe del sello y un ta-da al celebrar. Niveles bajos (la voz manda)."""
    rg = np.random.default_rng(seed + 77)
    out = np.zeros((n, 2), np.float64)
    def add(sig, t0, pan=0.5):
        i0 = int(t0 * SR)
        if i0 >= n or i0 < 0: return
        m = min(len(sig), n - i0)
        out[i0:i0 + m, 0] += sig[:m] * (1 - pan) * 2
        out[i0:i0 + m, 1] += sig[:m] * pan * 2
    def tono(f0, f1, dur, amp, forma="sin"):
        m = int(dur * SR); tt = np.arange(m) / SR
        f = f0 + (f1 - f0) * tt / dur
        ph = 2 * np.pi * np.cumsum(f) / SR
        s = np.sin(ph) + (0.3 * np.sin(2 * ph) if forma == "tri" else 0)
        env = np.minimum(1, tt / 0.004) * np.exp(-tt / (dur * 0.35))
        return s * env * amp
    def ruido(dur, fc, amp):
        m = int(dur * SR)
        x = rg.standard_normal(m)
        x = HR.lp_fft(x, fc, 2)
        return x * amp
    for s in scenes:
        base = s.start / FPS
        for e in getattr(s, "eventos", []):
            t0 = base + e[0]; tipo = e[1]
            if tipo == "pop":
                add(tono(620, 330, 0.09, 0.16), t0)
            elif tipo == "tada":
                for j, f in enumerate((523.3, 659.3, 784.0, 1046.5)):
                    add(tono(f, f, 0.22, 0.09, "tri"), t0 + j * 0.09)
            elif tipo == "lapiz":
                dur = e[2]; m = int(dur * SR); tt = np.arange(m) / SR
                r = ruido(dur, 1800, 0.05) * (0.6 + 0.4 * np.sin(2 * np.pi * 11 * tt)) * np.minimum(1, tt / 0.05) * np.minimum(1, (dur - tt) / 0.1)
                add(r, t0)
            elif tipo == "tecla":
                add(ruido(0.012, 3500, 0.5) * np.exp(-np.arange(int(0.012 * SR)) / (0.003 * SR)) * 0.25, t0, 0.5 + 0.1 * rg.uniform(-1, 1))
            elif tipo == "trazo":
                add(ruido(0.03, 1500, 0.5) * np.exp(-np.arange(int(0.03 * SR)) / (0.01 * SR)) * 0.12, t0)
            elif tipo == "silbido":
                add(tono(500, 1500, 0.35, 0.07), t0)
            elif tipo == "sello":
                m = int(0.3 * SR); tt = np.arange(m) / SR
                f = 70 + 180 * np.exp(-tt * 25)
                thud = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 12) * 0.35
                thud += HR.lp_fft(rg.standard_normal(m), 900, 2) * np.exp(-tt * 40) * 0.4
                add(thud, t0)
    return out
