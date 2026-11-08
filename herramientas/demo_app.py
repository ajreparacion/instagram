#!/usr/bin/env python3
"""Piezas de presentación de las apps de Neogest Lab a partir de las capturas REALES de demo del
«Centro de Contenido Apps» (entidad Producto, campo demo[].imagen). Creado por el agente de demos (8/11/2026).

Uso (lo lanza .github/workflows/demo_app.yml, que es quien tiene acceso a *.base44.app):
  python3 herramientas/demo_app.py descargar [slug ...]   -> herramientas/demos/<slug>/NN.png
  python3 herramientas/demo_app.py generar   [slug ...] [--sin-reel] [--subir]
        -> cola/<NNN>_demo_<slug>_carrusel/ (slides 1080x1350)
           cola/<NNN>_demo_<slug>_historia_<k>/ (1080x1920, "tipo": "historia")
           cola/<NNN>_demo_<slug>_reel/ (slideshow 1080x1920 con música y efectos; con --subir va a la release 'cola')
Sin slugs = todas las apps de herramientas/demo_apps.json.

Textos, horas y públicos: herramientas/demo_apps.json (sacados de demo[], hechos_verificados y prohibido_afirmar
de cada Producto; nada inventado). Nunca pisa un calidad.json existente: la revisión la hace un humano o agente.
"""
import json
import math
import os
import shutil
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERR = os.path.join(BASE, "herramientas")
CONFIG = os.path.join(HERR, "demo_apps.json")
DEMOS = os.path.join(HERR, "demos")
COLA = os.path.join(BASE, "cola")
FUENTE = os.path.join(HERR, "fonts", "Montserrat-VF.ttf")
LOGO = os.path.join(BASE, "equipo", "perfil_kit", "perfil_neogest_lab_1080.jpg")
ORIGEN = "https://centro-de-contenido-apps-2f0a3cd6.base44.app"
RELEASE = "cola"

# Paleta de los carruseles ya publicados (101-108): fondo morado oscuro, acento magenta.
FONDO_A = (18, 15, 30)
FONDO_B = (66, 38, 82)
ACENTO = (232, 121, 249)
BLANCO = (246, 243, 250)
GRIS = (205, 198, 220)
GRIS_OSC = (150, 140, 170)
CIAN = (34, 211, 238)


def cfg():
    with open(CONFIG, encoding="utf-8") as f:
        return json.load(f)


def apps_pedidas(c, slugs):
    apps = c["apps"]
    if slugs and slugs != ["todas"]:
        apps = [a for a in apps if a["slug"] in slugs]
    return apps


# ------------------------------------------------------------------ descarga
def descargar(c, slugs):
    for app in apps_pedidas(c, slugs):
        d = os.path.join(DEMOS, app["slug"])
        os.makedirs(d, exist_ok=True)
        for i, paso in enumerate(app["pasos"], 1):
            ruta = paso["imagen"]
            url = ruta if ruta.startswith("http") else ORIGEN + ruta
            destino = os.path.join(d, f"{i:02d}.png")
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (demo_app Neogest Lab)"})
            with urllib.request.urlopen(req, timeout=60) as r:
                datos = r.read()
            tmp = destino + ".tmp"
            with open(tmp, "wb") as f:
                f.write(datos)
            im = Image.open(tmp)
            im.load()
            im.convert("RGB").save(destino, optimize=True)
            os.remove(tmp)
            print(f"{app['slug']} {i:02d}: {url} -> {im.size}")


# ------------------------------------------------------------------ dibujo: utilidades
_FUENTES = {}


def fnt(size, peso="Bold"):
    clave = (int(size), peso)
    if clave not in _FUENTES:
        f = ImageFont.truetype(FUENTE, int(size))
        f.set_variation_by_name(peso)
        _FUENTES[clave] = f
    return _FUENTES[clave]


def fondo(w, h, semilla=0, brillo=None):
    """Degradado diagonal morado (como 101-108) con un leve resplandor magenta y grano para evitar bandas."""
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    t = np.clip((x / w) * 0.35 + (y / h) * 0.65, 0, 1) ** 1.6
    a = np.array(FONDO_A, np.float32)
    b = np.array(FONDO_B, np.float32)
    img = a[None, None, :] * (1 - t[..., None]) + b[None, None, :] * t[..., None]
    if brillo:
        cx, cy, r, k = brillo
        d = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) / r
        g = np.clip(1 - d, 0, 1) ** 2 * k
        img += g[..., None] * (np.array(ACENTO, np.float32) - img) * 0.5
    rng = np.random.default_rng(semilla)
    img += rng.normal(0, 1.2, img.shape[:2])[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")


def palabras_lineas(texto, f, maxw):
    lineas, actual = [], []
    for p in texto.split():
        prueba = " ".join(actual + [p])
        if actual and f.getlength(prueba) > maxw:
            lineas.append(actual)
            actual = [p]
        else:
            actual.append(p)
    if actual:
        lineas.append(actual)
    return lineas


def equilibrar(texto, f, maxw, ls):
    """Mismo número de líneas, pero con el ancho mínimo posible (evita una palabra sola en la última línea)."""
    lo = max(f.getlength(p) for p in texto.split())
    hi = maxw
    for _ in range(14):
        mid = (lo + hi) / 2
        if len(palabras_lineas(texto, f, mid)) <= len(ls):
            hi = mid
        else:
            lo = mid
    return palabras_lineas(texto, f, hi + 1)


def ajustar(texto, peso, maxw, maxlineas, smax, smin):
    for s in range(smax, smin - 1, -2):
        f = fnt(s, peso)
        ls = palabras_lineas(texto, f, maxw)
        if len(ls) <= maxlineas and all(f.getlength(" ".join(l)) <= maxw for l in ls):
            return f, (equilibrar(texto, f, maxw, ls) if len(ls) > 1 else ls)
    f = fnt(smin, peso)
    return f, palabras_lineas(texto, f, maxw)


def _norm(s):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")


def dibujar_lineas(d, x, y, lineas, f, color, destacar=None, alto=1.12, centro=None):
    """Dibuja líneas de palabras; la palabra que contiene 'destacar' va en el color de acento. Devuelve la y final."""
    lh = int(f.size * alto)
    for l in lineas:
        ancho = f.getlength(" ".join(l))
        cx = x if centro is None else int(centro - ancho / 2)
        for k, p in enumerate(l):
            tramo = p + (" " if k < len(l) - 1 else "")
            pos = _norm(p).find(_norm(destacar)) if destacar else -1
            if pos >= 0:
                a, b = p[:pos], p[pos:pos + len(destacar)]
                c = p[pos + len(destacar):] + (" " if k < len(l) - 1 else "")
                for trozo, col in ((a, color), (b, ACENTO), (c, color)):
                    if trozo:
                        d.text((cx, y), trozo, font=f, fill=col)
                        cx += f.getlength(trozo)
            else:
                d.text((cx, y), tramo, font=f, fill=color)
                cx += f.getlength(tramo)
        y += lh
    return y


def texto_espaciado(d, x, y, texto, f, color, esp=4, derecha=False):
    ancho = sum(f.getlength(c) + esp for c in texto) - esp
    if derecha:
        x -= ancho
    for c in texto:
        d.text((x, y), c, font=f, fill=color)
        x += f.getlength(c) + esp
    return ancho


def mascara_redondeada(w, h, r, ss=3):
    m = Image.new("L", (w * ss, h * ss), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w * ss - 1, h * ss - 1), r * ss, fill=255)
    return m.resize((w, h), Image.LANCZOS)


_LOGO = {}


def logo_circular(diam):
    if diam not in _LOGO:
        im = Image.open(LOGO).convert("RGB").resize((diam, diam), Image.LANCZOS)
        m = Image.new("L", (diam * 3, diam * 3), 0)
        ImageDraw.Draw(m).ellipse((0, 0, diam * 3 - 1, diam * 3 - 1), fill=255)
        im.putalpha(m.resize((diam, diam), Image.LANCZOS))
        _LOGO[diam] = im
    return _LOGO[diam]


def flecha(d, x, y, l, col, dir="derecha", grosor=5):
    if dir == "derecha":
        d.line((x, y, x + l, y), fill=col, width=grosor)
        d.polygon([(x + l + 4, y), (x + l - 12, y - 11), (x + l - 12, y + 11)], fill=col)
    else:  # abajo
        d.line((x, y, x, y + l), fill=col, width=grosor)
        d.polygon([(x, y + l + 6), (x - 13, y + l - 12), (x + 13, y + l - 12)], fill=col)


def check(d, cx, cy, s, col, grosor=8):
    d.line((cx - s, cy, cx - s * 0.3, cy + s * 0.7, cx + s, cy - s * 0.7), fill=col, width=grosor, joint="curve")


def cruz(d, cx, cy, s, col, grosor=8):
    d.line((cx - s, cy - s, cx + s, cy + s), fill=col, width=grosor)
    d.line((cx - s, cy + s, cx + s, cy - s), fill=col, width=grosor)


# ------------------------------------------------------------------ marco de móvil
class Movil:
    """Marco de móvil (cuerpo oscuro, bisel, botones laterales y sombra) con la captura dentro.
    La pantalla muestra la captura ajustada al ancho; si es más alta que la pantalla, se ve desde arriba (o desde
    'desplaz' px de la captura) y se puede hacer zoom/paneo (Ken Burns) en el vídeo."""

    def __init__(self, ancho_pantalla, alto_pantalla, bisel=16, sombra=46):
        self.sw, self.sh, self.b, self.sp = ancho_pantalla, alto_pantalla, bisel, sombra
        self.R = int(ancho_pantalla * 0.12)
        bw, bh = self.sw + 2 * bisel, self.sh + 2 * bisel
        self.bw, self.bh = bw, bh
        m = 10  # hueco para los botones laterales
        W, H = bw + 2 * m + 2 * sombra, bh + 2 * sombra + 30
        self.ox, self.oy = m + sombra, sombra  # esquina del cuerpo dentro de la capa
        capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        # sombra
        sm = Image.new("L", (W, H), 0)
        ImageDraw.Draw(sm).rounded_rectangle((self.ox + 10, self.oy + 34, self.ox + bw - 10, self.oy + bh + 24),
                                             self.R + bisel, fill=150)
        sm = sm.filter(ImageFilter.GaussianBlur(sombra * 0.55))
        capa.paste(Image.new("RGBA", (W, H), (5, 3, 10, 255)), (0, 0), sm)
        # botones laterales
        dd = ImageDraw.Draw(capa)
        for (y0, y1) in ((0.17, 0.22), (0.26, 0.34), (0.36, 0.44)):
            dd.rounded_rectangle((self.ox - 6, self.oy + int(bh * y0), self.ox + 4, self.oy + int(bh * y1)), 3,
                                 fill=(52, 46, 66, 255))
        dd.rounded_rectangle((self.ox + bw - 4, self.oy + int(bh * 0.28), self.ox + bw + 6, self.oy + int(bh * 0.40)), 3,
                             fill=(52, 46, 66, 255))
        # cuerpo con borde metálico
        cuerpo = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        cm = mascara_redondeada(bw, bh, self.R + bisel)
        relleno = Image.new("RGBA", (bw, bh), (84, 76, 104, 255))
        cuerpo.paste(relleno, (0, 0), cm)
        interior = mascara_redondeada(bw - 6, bh - 6, self.R + bisel - 3)
        cuerpo.paste(Image.new("RGBA", (bw - 6, bh - 6), (12, 10, 18, 255)), (3, 3), interior)
        capa.alpha_composite(cuerpo, (self.ox, self.oy))
        self.capa = capa
        self.mascara = mascara_redondeada(self.sw, self.sh, self.R)
        self.tam = (W, H)

    def vista(self, cap, zoom=1.0, desplaz=0.0, cx=0.5, filtro=Image.LANCZOS):
        """Recorte de la captura que cabe en la pantalla. zoom>=1 acerca; desplaz en px de la captura."""
        esc = self.sw / cap.width * zoom
        rw, rh = self.sw / esc, self.sh / esc
        x0 = (cap.width - rw) * cx
        y0 = max(0.0, min(desplaz, cap.height - rh))
        if rh > cap.height:  # captura más baja que la pantalla: se centra sobre fondo blanco
            lienzo = Image.new("RGB", (self.sw, self.sh), cap.getpixel((5, cap.height - 5)))
            im = cap.resize((self.sw, int(cap.height * self.sw / cap.width)), filtro)
            lienzo.paste(im, (0, 0))
            return lienzo
        return cap.resize((self.sw, self.sh), filtro, box=(x0, y0, x0 + rw, y0 + rh))

    def componer(self, cap, **kw):
        capa = self.capa.copy()
        capa.paste(self.vista(cap, **kw), (self.ox + self.b, self.oy + self.b), self.mascara)
        return capa

    def pegar(self, lienzo, x_centro, y_arriba, cap, alfa=1.0, **kw):
        """Pega el móvil con el borde superior del cuerpo en y_arriba (puede salirse por abajo)."""
        capa = self.componer(cap, **kw)
        if alfa < 1.0:
            a = capa.getchannel("A").point(lambda v: int(v * alfa))
            capa.putalpha(a)
        x = int(x_centro - self.ox - self.bw / 2)
        y = int(y_arriba - self.oy)
        if lienzo.mode == "RGBA":
            lienzo.alpha_composite(capa, (x, y)) if x >= 0 and y >= 0 else lienzo.paste(capa, (x, y), capa)
        else:
            lienzo.paste(capa, (x, y), capa)


def cargar_capturas(slug):
    d = os.path.join(DEMOS, slug)
    fs = sorted(f for f in os.listdir(d) if f.endswith(".png"))
    if not fs:
        raise SystemExit(f"{slug}: no hay capturas en {d} (ejecuta antes «descargar»)")
    return [Image.open(os.path.join(d, f)).convert("RGB") for f in fs]


# ------------------------------------------------------------------ carrusel 1080x1350
CW, CH = 1080, 1350
MX = 96


def cabecera(d, etiqueta, k, n):
    texto_espaciado(d, MX, 78, etiqueta.upper(), fnt(29, "Bold"), ACENTO, esp=4)
    f = fnt(29, "Bold")
    t = f"{k:02d}/{n:02d}"
    d.text((CW - MX - f.getlength(t), 78), t, font=f, fill=GRIS_OSC)


def puntos(d, k, n, y=1290):
    x = CW - MX - (n - 1) * 26
    for i in range(n):
        r = 9 if i == k - 1 else 6
        col = ACENTO if i == k - 1 else (110, 100, 130)
        d.ellipse((x + i * 26 - r, y - r, x + i * 26 + r, y + r), fill=col)


def insignia(d, x, y, texto, f=None):
    f = f or fnt(24, "SemiBold")
    w = f.getlength(texto)
    d.rounded_rectangle((x, y, x + w + 36, y + 46), 23, fill=(34, 26, 48), outline=(120, 106, 148), width=2)
    d.text((x + 18, y + 9), texto, font=f, fill=GRIS)
    return w + 36


def slide_portada(app, caps, n):
    im = fondo(CW, CH, 1, brillo=(760, 1100, 620, 0.55))
    d = ImageDraw.Draw(im)
    cabecera(d, app["etiqueta"], 1, n)
    f, ls = ajustar(app["gancho"], "ExtraBold", CW - 2 * MX, 3, 104, 70)
    y = dibujar_lineas(d, MX, 150, ls, f, BLANCO, app["gancho_destacar"], alto=1.1)
    d.rectangle((MX, y + 22, MX + 92, y + 30), fill=ACENTO)
    fs, lss = ajustar(app["gancho_sub"], "Medium", 405, 4, 36, 28)
    ysub = y + 62
    dibujar_lineas(d, MX, ysub, lss, fs, GRIS, alto=1.35)
    # móvil a la derecha, saliendo por abajo
    mv = Movil(460, 1000, bisel=15)
    cap = caps[app["portada"] - 1]
    mv.pegar(im, 775, max(y + 60, 560), cap)
    # pie a la izquierda
    d = ImageDraw.Draw(im)
    fb = fnt(38, "Bold")
    t = "Desliza"
    w = fb.getlength(t)
    d.rounded_rectangle((MX, 1150, MX + w + 120, 1226), 38, fill=ACENTO)
    d.text((MX + 36, 1166), t, font=fb, fill=(20, 12, 28))
    flecha(d, MX + 36 + w + 16, 1189, 34, (20, 12, 28), grosor=5)
    d.text((MX, 1262), "@neogestlab", font=fnt(28, "SemiBold"), fill=GRIS_OSC)
    return im


def slide_paso(app, cap, k, n, paso, num_paso, total_pasos):
    im = fondo(CW, CH, k, brillo=(540, 900, 560, 0.45))
    d = ImageDraw.Draw(im)
    cabecera(d, f"{app['nombre']} · paso {num_paso}", k, n)
    f, ls = ajustar(paso["titulo"], "ExtraBold", CW - 2 * MX, 2, 66, 50)
    y = dibujar_lineas(d, MX, 140, ls, f, BLANCO, alto=1.1)
    fl, lsl = ajustar(paso["linea"], "Medium", CW - 2 * MX, 2, 36, 28)
    y = dibujar_lineas(d, MX, y + 10, lsl, fl, GRIS, alto=1.32)
    top = y + 34
    alto = 1240 - top
    mv = Movil(500, alto - 32, bisel=16)
    mv.pegar(im, CW // 2, top, cap)
    d = ImageDraw.Draw(im)
    d.text((MX, 1272), "@neogestlab", font=fnt(28, "SemiBold"), fill=GRIS_OSC)
    if app.get("aviso") and app["aviso"].startswith("Demo"):
        insignia(d, MX + 230, 1262, app["aviso"])
    puntos(d, k, n)
    return im


def slide_cierre(app, k, n):
    im = fondo(CW, CH, 99, brillo=(540, 1000, 520, 0.5))
    d = ImageDraw.Draw(im)
    cabecera(d, app["nombre"], k, n)
    f, ls = ajustar(app["cierre"], "ExtraBold", CW - 2 * MX, 3, 96, 64)
    y = dibujar_lineas(d, 0, 200, ls, f, BLANCO, app["cierre_destacar"], alto=1.1, centro=CW // 2)
    fs, lss = ajustar(app["cierre_sub"], "Medium", CW - 2 * MX - 40, 3, 38, 30)
    y = dibujar_lineas(d, 0, y + 18, lss, fs, GRIS, alto=1.35, centro=CW // 2)
    # caja IDEA
    fb = fnt(40, "Bold")
    y0 = y + 44
    d.rounded_rectangle((120, y0, CW - 120, y0 + 94), 30, outline=ACENTO, width=4)
    partes = [("Escríbeme ", BLANCO), ("IDEA", ACENTO), (" por privado", BLANCO)]
    total = sum(fb.getlength(p) for p, _ in partes)
    x = CW / 2 - total / 2
    for p, col in partes:
        d.text((x, y0 + 23), p, font=fb, fill=col)
        x += fb.getlength(p)
    yl = max(y0 + 150, 830)
    diam = 250
    im.paste(logo_circular(diam), (CW // 2 - diam // 2, yl), logo_circular(diam))
    d = ImageDraw.Draw(im)
    ff = fnt(44, "Bold")
    t = "By Neogest Lab"
    d.text((CW / 2 - ff.getlength(t) / 2, yl + diam + 30), t, font=ff, fill=BLANCO)
    fa = fnt(28, "SemiBold")
    t2 = "@neogestlab"
    if app.get("aviso") and not app["aviso"].startswith("Demo"):
        t2 = app["aviso"] + "  ·  @neogestlab"
    d.text((CW / 2 - fa.getlength(t2) / 2, yl + diam + 96), t2, font=fa, fill=GRIS_OSC)
    return im


def carrusel(app, caps, carpeta):
    pasos = app["pasos"]
    n = len(pasos) + 2
    slides = [slide_portada(app, caps, n)]
    for i, p in enumerate(pasos):
        slides.append(slide_paso(app, caps[i], i + 2, n, p, i + 1, len(pasos)))
    slides.append(slide_cierre(app, n, n))
    d = os.path.join(carpeta, "slides")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    for i, s in enumerate(slides, 1):
        s.convert("RGB").save(os.path.join(d, f"{i:02d}.jpg"), quality=93, subsampling=0, optimize=True)
    return n


# ------------------------------------------------------------------ historias 1080x1920
SW, SH = 1080, 1920
SAFE_T, SAFE_B = 250, 1680  # Instagram tapa arriba (barra y nombre) y abajo (responder)


def pastilla(d, x, y, texto, f, fondo_col=ACENTO, texto_col=(20, 12, 28)):
    w = f.getlength(texto)
    d.rounded_rectangle((x, y, x + w + 48, y + f.size + 30), (f.size + 30) // 2, fill=fondo_col)
    d.text((x + 24, y + 13), texto, font=f, fill=texto_col)
    return w + 48


def pie_marca(im, y=SAFE_B - 70):
    diam = 70
    d = ImageDraw.Draw(im)
    f = fnt(32, "Bold")
    t = "By Neogest Lab"
    w = diam + 18 + f.getlength(t)
    x = int(SW / 2 - w / 2)
    im.paste(logo_circular(diam), (x, y), logo_circular(diam))
    d.text((x + diam + 18, y + 16), t, font=f, fill=BLANCO)


def movil_fundido(im, cap, top, bottom, ancho=560, cx=SW // 2):
    """Móvil que se corta en 'bottom' con fundido al fondo (para historias)."""
    alto_pant = 1500
    mv = Movil(ancho, alto_pant, bisel=17)
    capa = Image.new("RGBA", im.size, (0, 0, 0, 0))
    mv.pegar(capa, cx, top, cap)
    # fundido de los últimos 170 px
    a = np.array(capa.getchannel("A"), np.float32)
    ys = np.arange(im.height, dtype=np.float32)[:, None]
    k = np.clip((bottom - ys) / 170.0, 0, 1)
    capa.putalpha(Image.fromarray((a * k).astype(np.uint8)))
    im.paste(capa, (0, 0), capa)


def historia(app, caps, h, idx):
    im = fondo(SW, SH, 300 + idx, brillo=(540, 1350, 650, 0.5))
    d = ImageDraw.Draw(im)
    x = 90
    fp = fnt(30, "ExtraBold")
    cap = caps[h["captura"] - 1]
    if h["tipo"] == "sabias":
        pastilla(d, x, SAFE_T + 20, "¿SABÍAS QUE…?", fp)
        f, ls = ajustar(h["titulo"], "ExtraBold", SW - 2 * x, 4, 82, 58)
        y = dibujar_lineas(d, x, SAFE_T + 110, ls, f, BLANCO, h.get("destacar"), alto=1.1)
        ft, lst = ajustar(h["texto"], "Medium", SW - 2 * x, 3, 40, 32)
        y = dibujar_lineas(d, x, y + 30, lst, ft, GRIS, alto=1.35)
        movil_fundido(im, cap, y + 50, SAFE_B - 140)
    elif h["tipo"] == "antes_despues":
        pastilla(d, x, SAFE_T + 20, "ANTES / DESPUÉS", fp)
        fn = fnt(46, "ExtraBold")
        d.text((x, SAFE_T + 104), f"Con {app['nombre']}", font=fn, fill=BLANCO)
        y = SAFE_T + 184
        ftx = fnt(36, "SemiBold")
        for etiqueta, texto, col, borde, icono in (
                ("ANTES", h["antes"], GRIS, (110, 98, 130), "cruz"),
                ("DESPUÉS", h["despues"], BLANCO, ACENTO, "check")):
            ls = palabras_lineas(texto, ftx, SW - 2 * x - 150)
            alto = 70 + len(ls) * int(36 * 1.3) + 26
            d.rounded_rectangle((x, y, SW - x, y + alto), 30, fill=(30, 22, 44) if icono == "cruz" else (52, 30, 66),
                                outline=borde, width=3)
            cx, cy = x + 58, y + alto // 2
            d.ellipse((cx - 34, cy - 34, cx + 34, cy + 34), fill=(70, 58, 90) if icono == "cruz" else ACENTO)
            (cruz if icono == "cruz" else check)(d, cx, cy, 14 if icono == "cruz" else 17,
                                                 (230, 140, 150) if icono == "cruz" else (20, 12, 28), grosor=7)
            texto_espaciado(d, x + 122, y + 24, etiqueta, fnt(24, "ExtraBold"), borde if icono == "cruz" else ACENTO, esp=3)
            dibujar_lineas(d, x + 122, y + 62, ls, ftx, col, alto=1.3)
            y += alto + 24
        movil_fundido(im, cap, y + 30, SAFE_B - 140, ancho=520)
    else:  # pregunta
        pastilla(d, x, SAFE_T + 20, "PREGUNTA RÁPIDA", fp)
        f, ls = ajustar(h["titulo"], "ExtraBold", SW - 2 * x, 3, 92, 62)
        y = dibujar_lineas(d, x, SAFE_T + 110, ls, f, BLANCO, h.get("destacar"), alto=1.1)
        caja_top = SAFE_B - 300
        movil_fundido(im, cap, y + 46, caja_top - 30, ancho=500)
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((x, caja_top, SW - x, caja_top + 200), 36, fill=(40, 26, 56), outline=ACENTO, width=4)
        ft, lst = ajustar(h["texto"], "Bold", SW - 2 * x - 160, 2, 42, 32)
        yy = caja_top + 100 - len(lst) * int(ft.size * 1.3) // 2
        dibujar_lineas(d, x + 44, yy, lst, ft, BLANCO, alto=1.3)
        flecha(d, SW - x - 70, caja_top + 60, 60, ACENTO, dir="abajo", grosor=7)
    if app.get("aviso"):
        d = ImageDraw.Draw(im)
        fa = fnt(26, "SemiBold")
        d.text((SW / 2 - fa.getlength(app["aviso"]) / 2, SAFE_B - 118), app["aviso"], font=fa, fill=GRIS_OSC)
    pie_marca(im)
    return im


# ------------------------------------------------------------------ reel de presentación 1080x1920
FPS = 30
SR = 44100
BPM = 120
COMPAS = 4 * 60 / BPM          # 2 s
T_GANCHO = 2 * COMPAS          # 4 s
T_PASO = 2 * COMPAS            # 4 s
T_CIERRE = 2.25 * COMPAS       # 4,5 s
T_TRANS = 0.3


def ease(k):
    k = min(1.0, max(0.0, k))
    return 1 - (1 - k) ** 3


def ease_back(k, c=1.7):
    k = min(1.0, max(0.0, k))
    return 1 + (c + 1) * (k - 1) ** 3 + c * (k - 1) ** 2


def capa_texto(lineas, f, color, destacar=None, alto=1.1, ancho=SW, centro=False):
    lh = int(f.size * alto)
    im = Image.new("RGBA", (ancho, lh * len(lineas) + int(f.size * 0.4)), (0, 0, 0, 0))
    dibujar_lineas(ImageDraw.Draw(im), 0, 0, lineas, f, color, destacar, alto=alto,
                   centro=(ancho // 2) if centro else None)
    return im


def pegar_alfa(lienzo, capa, x, y, alfa):
    if alfa <= 0.01:
        return
    if alfa < 0.99:
        capa = capa.copy()
        capa.putalpha(capa.getchannel("A").point(lambda v, a=alfa: int(v * a)))
    lienzo.paste(capa, (int(x), int(y)), capa)


class Escena:
    def __init__(self, tipo, dur, **kw):
        self.tipo, self.dur = tipo, dur
        self.__dict__.update(kw)


def preparar_reel(app, caps):
    x = 90
    escenas = []
    # gancho
    f, ls = ajustar(app["gancho"], "ExtraBold", SW - 2 * x, 4, 112, 76)
    palabras = []
    lh = int(f.size * 1.08)
    y = 330
    for li, l in enumerate(ls):
        cx = x
        for p in l:
            capa = capa_texto([[p]], f, BLANCO, app["gancho_destacar"], alto=1.08, ancho=int(f.getlength(p)) + 20)
            palabras.append((capa, cx, y + li * lh))
            cx += f.getlength(p + " ")
    y_fin = y + len(ls) * lh
    fs, lss = ajustar(app["gancho_sub"], "Medium", SW - 2 * x, 2, 42, 32)
    escenas.append(Escena("gancho", T_GANCHO, palabras=palabras,
                          etiqueta=capa_texto([[app["etiqueta"].upper()]], fnt(32, "Bold"), ACENTO, ancho=SW),
                          sub=capa_texto(lss, fs, GRIS, alto=1.32), y_sub=y_fin + 24,
                          movil=Movil(560, 1300, bisel=17), cap=caps[app["portada"] - 1],
                          y_movil=y_fin + 60 + len(lss) * int(fs.size * 1.32),
                          fondo=fondo(SW, SH, 7, brillo=(540, 1500, 700, 0.6))))
    n = len(app["pasos"])
    for i, p in enumerate(app["pasos"]):
        ft, lst = ajustar(p["titulo"], "ExtraBold", SW - 2 * x, 2, 80, 58)
        fl, lsl = ajustar(p["linea"], "Medium", SW - 2 * x, 3, 40, 32)
        tit = capa_texto(lst, ft, BLANCO, alto=1.08)
        lin = capa_texto(lsl, fl, GRIS, alto=1.3)
        y_tit = 330
        y_lin = y_tit + int(ft.size * 1.08) * len(lst) + 14
        y_mov = y_lin + int(fl.size * 1.3) * len(lsl) + 46
        alto_pant = 1640 - y_mov - 34
        cap = caps[i]
        mv = Movil(600, alto_pant, bisel=18)
        # paneo vertical: baja por la pantalla si la captura es más alta que lo que se ve
        esc = mv.sw / cap.width
        sobra = max(0.0, cap.height - mv.sh / esc)
        escenas.append(Escena("paso", T_PASO, tit=tit, lin=lin, y_tit=y_tit, y_lin=y_lin, y_mov=y_mov, movil=mv, cap=cap,
                              chip=capa_texto([[f"PASO {i + 1} DE {n}"]], fnt(30, "ExtraBold"), ACENTO, ancho=SW),
                              pan=min(sobra, 260.0) * (1 if i % 2 == 0 else 0.6), cx=0.5,
                              zoom=(1.0, 1.07) if i % 2 == 0 else (1.07, 1.0),
                              fondo=fondo(SW, SH, 20 + i, brillo=(540, 1200, 650, 0.5))))
    # cierre
    fc, lsc = ajustar(app["cierre"], "ExtraBold", SW - 2 * x, 3, 100, 70)
    fs2, lss2 = ajustar(app["cierre_sub"], "Medium", SW - 2 * x - 40, 3, 42, 32)
    tit = capa_texto(lsc, fc, BLANCO, app["cierre_destacar"], alto=1.08, centro=True)
    sub = capa_texto(lss2, fs2, GRIS, alto=1.32, centro=True)
    caja = Image.new("RGBA", (SW, 120), (0, 0, 0, 0))
    dc = ImageDraw.Draw(caja)
    dc.rounded_rectangle((100, 6, SW - 100, 114), 34, outline=ACENTO, width=5, fill=(40, 26, 56, 255))
    fb = fnt(44, "Bold")
    partes = [("Escríbeme ", BLANCO), ("IDEA", ACENTO), (" por privado", BLANCO)]
    tx = SW / 2 - sum(fb.getlength(q) for q, _ in partes) / 2
    for q, col in partes:
        dc.text((tx, 32), q, font=fb, fill=col)
        tx += fb.getlength(q)
    firma = Image.new("RGBA", (SW, 140), (0, 0, 0, 0))
    df = ImageDraw.Draw(firma)
    ff = fnt(50, "Bold")
    df.text((SW / 2 - ff.getlength("By Neogest Lab") / 2, 0), "By Neogest Lab", font=ff, fill=BLANCO)
    fa = fnt(30, "SemiBold")
    t2 = "@neogestlab" if not (app.get("aviso") and not app["aviso"].startswith("Demo")) else app["aviso"] + "  ·  @neogestlab"
    df.text((SW / 2 - fa.getlength(t2) / 2, 78), t2, font=fa, fill=GRIS_OSC)
    y_tit = 360
    y_sub = y_tit + tit.height + 6
    y_caja = y_sub + sub.height + 30
    escenas.append(Escena("cierre", T_CIERRE, tit=tit, sub=sub, caja=caja, firma=firma, y_tit=y_tit, y_sub=y_sub,
                          y_caja=y_caja, y_logo=max(y_caja + 190, 1020),
                          fondo=fondo(SW, SH, 99, brillo=(540, 1150, 600, 0.6))))
    return escenas


def frame_escena(sc, t, app):
    im = sc.fondo.copy()
    if sc.tipo == "gancho":
        pegar_alfa(im, sc.etiqueta, 90, 250, ease(t / 0.3))
        for k, (capa, x, y) in enumerate(sc.palabras):
            a = ease((t - 0.1 - k * 0.11) / 0.25)
            pegar_alfa(im, capa, x, y + (1 - a) * 40, a)
        a = ease((t - 0.5) / 0.6)
        if a > 0:
            sc.movil.pegar(im, SW // 2, sc.y_movil + (1 - a) * 380, sc.cap, alfa=min(1, a * 1.4),
                           zoom=1.0 + 0.04 * (t / sc.dur), desplaz=0, filtro=Image.BILINEAR)
        pegar_alfa(im, sc.sub, 90, sc.y_sub, ease((t - 1.1) / 0.4))
    elif sc.tipo == "paso":
        k = t / sc.dur
        a = ease(t / 0.45)
        z = sc.zoom[0] + (sc.zoom[1] - sc.zoom[0]) * k
        sc.movil.pegar(im, SW // 2, sc.y_mov + (1 - a) * 120, sc.cap, alfa=min(1, 0.3 + a),
                       zoom=z, desplaz=sc.pan * ease(max(0, (t - 0.8) / (sc.dur - 1.0))), cx=sc.cx,
                       filtro=Image.BILINEAR)
        pegar_alfa(im, sc.chip, 90, 252, ease(t / 0.25))
        a1 = ease((t - 0.12) / 0.35)
        pegar_alfa(im, sc.tit, 90 + (1 - a1) * 70, sc.y_tit, a1)
        a2 = ease((t - 0.35) / 0.35)
        pegar_alfa(im, sc.lin, 90, sc.y_lin + (1 - a2) * 24, a2)
    else:
        a1 = ease(t / 0.35)
        pegar_alfa(im, sc.tit, 0, sc.y_tit + (1 - a1) * 40, a1)
        pegar_alfa(im, sc.sub, 0, sc.y_sub, ease((t - 0.25) / 0.35))
        pegar_alfa(im, sc.caja, 0, sc.y_caja, ease((t - 0.45) / 0.35))
        s = ease_back((t - 0.7) / 0.45)
        if t > 0.7:
            diam = max(10, int(300 * s))
            logo = logo_circular(diam)
            im.paste(logo, (SW // 2 - diam // 2, sc.y_logo + 150 - diam // 2), logo)
        pegar_alfa(im, sc.firma, 0, sc.y_logo + 330, ease((t - 1.0) / 0.35))
    return im


def tiempos(escenas):
    t, cortes = 0.0, []
    for sc in escenas:
        cortes.append(t)
        t += sc.dur
    return cortes, t


def render_video(app, caps, salida, trabajo):
    escenas = preparar_reel(app, caps)
    cortes, total = tiempos(escenas)
    wav = os.path.join(trabajo, "audio.wav")
    escribir_wav(wav, audio_reel(cortes, total, semilla=sum(map(ord, app["slug"]))))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{SW}x{SH}",
           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-pix_fmt", "yuv420p", "-profile:v", "high", "-c:a", "aac", "-b:a", "192k", "-ar", str(SR),
           "-shortest", "-movflags", "+faststart", salida]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nf = int(round(total * FPS))
    nt = int(T_TRANS * FPS)
    for fi in range(nf):
        t = fi / FPS
        i = max(j for j, c in enumerate(cortes) if c <= t + 1e-9)
        sc = escenas[i]
        tl = t - cortes[i]
        fr = frame_escena(sc, tl, app)
        # transición de empuje: la escena anterior sale por la izquierda durante T_TRANS
        if i > 0 and tl < T_TRANS:
            e = ease(tl / T_TRANS)
            prev = frame_escena(escenas[i - 1], escenas[i - 1].dur, app)
            comp = Image.new("RGB", (SW, SH))
            dx = int(SW * e)
            comp.paste(prev, (-dx, 0))
            comp.paste(fr, (SW - dx, 0))
            fr = comp
        p.stdin.write(fr.tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise RuntimeError("ffmpeg falló al crear el reel")
    return total


# ------------------------------------------------------------------ audio: música con ritmo y efectos
def _lp(x, fc):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (f / fc) ** 4)
    return np.fft.irfft(X, len(x))


def _hp(x, fc):
    return x - _lp(x, fc)


def _saw(fr, n, rng):
    t = np.arange(n) / SR
    ph = rng.uniform(0, 1)
    return 2 * ((t * fr + ph) % 1) - 1


def _hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def _poner(buf, sig, t0, g=1.0):
    i = int(t0 * SR)
    if i >= len(buf) or i + len(sig) <= 0:
        return
    a, b = max(0, i), min(len(buf), i + len(sig))
    buf[a:b] += sig[a - i:b - i] * g


def audio_reel(cortes, total, semilla=0):
    rng = np.random.default_rng(semilla)
    n = int((total + 0.5) * SR)
    beat = 60 / BPM
    kick_bus, perc, bajo, pad, arp, sfx = (np.zeros(n) for _ in range(6))
    # acordes vi-IV-I-V (La menor, Fa, Do, Sol), uno por compás
    acordes = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]
    nb = int(total / beat) + 2
    # bombo
    tk = np.arange(int(0.35 * SR)) / SR
    fk = 45 + 75 * np.exp(-tk / 0.035)
    kick = np.sin(2 * np.pi * np.cumsum(fk) / SR) * np.exp(-tk / 0.16)
    kick[:60] += np.linspace(0.6, 0, 60) * rng.uniform(-1, 1, 60)
    ruido = rng.uniform(-1, 1, int(0.25 * SR))
    palmada = _hp(_lp(ruido, 2600), 900) * np.exp(-np.arange(len(ruido)) / SR / 0.06)
    hat = _hp(rng.uniform(-1, 1, int(0.06 * SR)), 7000) * np.exp(-np.arange(int(0.06 * SR)) / SR / 0.015)
    for b in range(nb):
        t0 = b * beat
        _poner(kick_bus, kick, t0, 0.95)
        if b % 2 == 1:
            _poner(perc, palmada, t0, 0.55)
        _poner(perc, hat, t0 + beat / 2, 0.35)
        if b % 4 == 3:
            _poner(perc, hat, t0 + beat * 0.75, 0.2)
    # bajo (corcheas a contratiempo + tierra en el 1) y arpegio en semicorcheas
    for c in range(int(total / COMPAS) + 2):
        ac = acordes[c % 4]
        raiz = ac[0] - 24 if ac[0] >= 52 else ac[0] - 12
        for k in range(8):
            t0 = c * COMPAS + k * beat / 2
            if k % 2 == 1 or k == 0:
                m = int(0.22 * SR)
                s = (_saw(_hz(raiz), m, rng) * 0.5 + np.sin(2 * np.pi * _hz(raiz) * np.arange(m) / SR))
                s *= np.minimum(1, np.arange(m) / 200) * np.exp(-np.arange(m) / SR / 0.12)
                _poner(bajo, s, t0, 0.5)
        for k in range(16):
            m = int(0.18 * SR)
            nota = ac[k % 3] + (12 if (k // 3) % 2 == 0 else 24)
            tt = np.arange(m) / SR
            s = (np.sin(2 * np.pi * _hz(nota) * tt) + 0.3 * np.sin(4 * np.pi * _hz(nota) * tt)) * np.exp(-tt / 0.07)
            _poner(arp, s, c * COMPAS + k * beat / 4, 0.12 if c > 0 else 0.07)
        m = int(COMPAS * SR)
        s = sum(_saw(_hz(no) * dt, m, rng) for no in ac for dt in (0.997, 1.003))
        env = np.minimum(1, np.arange(m) / (0.05 * SR)) * np.minimum(1, (m - np.arange(m)) / (0.08 * SR))
        _poner(pad, s * env, c * COMPAS, 0.06)
    bajo = _lp(bajo, 420)
    pad = _lp(pad, 1700)
    # bombeo (sidechain) del pad y el bajo con el bombo
    tt = np.arange(n) / SR
    fase = (tt % beat)
    duck = 1 - 0.55 * np.exp(-fase / 0.09)
    musica = kick_bus + perc + bajo * duck + pad * duck + _lp(arp, 5000)
    # efectos: whoosh en cada corte, pop cuando entra el título, ding con el logo
    for c in cortes[1:]:
        m = int(0.5 * SR)
        r = rng.uniform(-1, 1, m)
        env = np.concatenate([np.linspace(0, 1, int(0.32 * SR)) ** 2, np.exp(-np.arange(m - int(0.32 * SR)) / SR / 0.06)])
        w = _hp(_lp(r, 3500), 400) * env
        _poner(sfx, w, c - 0.32, 0.55)
        tp = np.arange(int(0.09 * SR)) / SR
        pop = np.sin(2 * np.pi * np.cumsum(900 - 4500 * tp) / SR) * np.exp(-tp / 0.025)
        _poner(sfx, pop, c + 0.18, 0.35)
    tg = np.arange(int(0.9 * SR)) / SR
    ding = (np.sin(2 * np.pi * 1318.5 * tg) + 0.4 * np.sin(2 * np.pi * 1975.5 * tg)) * np.exp(-tg / 0.25)
    _poner(sfx, ding, cortes[-1] + 0.75, 0.22)
    # impacto inicial
    tg = np.arange(int(0.8 * SR)) / SR
    _poner(sfx, _lp(rng.uniform(-1, 1, len(tg)), 6000) * np.exp(-tg / 0.18), 0.0, 0.3)
    musica = musica / (np.sqrt(np.mean(musica ** 2)) + 1e-9) * 0.16
    mezcla = musica + sfx * 0.9
    # fundido final y limitador suave
    fin = int(total * SR)
    mezcla[fin - int(1.2 * SR):fin] *= np.linspace(1, 0, int(1.2 * SR)) ** 1.5
    mezcla[fin:] = 0
    mezcla = np.tanh(mezcla * 1.6) / np.tanh(1.6)
    mezcla *= 0.89 / (np.max(np.abs(mezcla)) + 1e-9)
    est = np.stack([mezcla, np.roll(mezcla, 9) * 0.98 + _lp(arp, 5000) * 0.0], axis=1)
    return est[:fin]


def escribir_wav(ruta, est):
    import wave
    datos = (np.clip(est, -1, 1) * 32767).astype("<i2").tobytes()
    with wave.open(ruta, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(datos)


# ------------------------------------------------------------------ cola
FUENTES_TXT = ("Centro de Contenido Apps (Base44, appId 6ae5244d4e2b32702f0a3cd6), entidad Producto «{n}»: demo[] "
               "(capturas reales de la demo y sus textos), hechos_verificados y prohibido_afirmar (consulta 8/11/2026).")


def ya_publicado(nombre):
    for d in ("publicados", "errores", "descartados"):
        ruta = os.path.join(BASE, d)
        if os.path.isdir(ruta) and any(f == nombre or f.startswith(nombre + "_") for f in os.listdir(ruta)):
            return True
    return False


def escribir_post(carpeta, datos):
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, "post.json")
    previo = {}
    if os.path.exists(ruta):
        with open(ruta, encoding="utf-8") as f:
            previo = json.load(f)
    for k in ("_intentos",):
        if k in previo:
            datos[k] = previo[k]
    with open(ruta + ".tmp", "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
    os.replace(ruta + ".tmp", ruta)


def generar(c, slugs, reel=True, subir=False):
    for app in apps_pedidas(c, slugs):
        caps = cargar_capturas(app["slug"])
        if len(caps) != len(app["pasos"]):
            raise SystemExit(f"{app['slug']}: {len(caps)} capturas y {len(app['pasos'])} pasos")
        base = f"{app['numero']}_{app['slug'].replace('-', '_')}"
        comun = {"app": app["nombre"], "publico": app["publico"], "fuentes": [FUENTES_TXT.format(n=app["nombre"])],
                 "origen": "herramientas/demo_app.py"}
        # carrusel
        nom = base + "_carrusel"
        if not ya_publicado(nom):
            carpeta = os.path.join(COLA, nom)
            os.makedirs(carpeta, exist_ok=True)
            n = carrusel(app, caps, carpeta)
            escribir_post(carpeta, dict(tipo="carrusel", texto=app["texto_carrusel"], cuando=app["cuando_carrusel"],
                                        renderizado="no aplica (carrusel)", diapositivas=n, **comun))
            print(f"{nom}: carrusel de {n} diapositivas")
        # historias
        for k, h in enumerate(app["historias"], 1):
            nom = f"{base}_historia{k}"
            if ya_publicado(nom):
                continue
            carpeta = os.path.join(COLA, nom)
            d = os.path.join(carpeta, "slides")
            shutil.rmtree(d, ignore_errors=True)
            os.makedirs(d)
            historia(app, caps, h, k).convert("RGB").save(os.path.join(d, "01.jpg"), quality=93, subsampling=0)
            escribir_post(carpeta, dict(tipo="historia", texto="", cuando=h["cuando"], renderizado="no aplica (historia)",
                                        formato=h["tipo"], **comun))
            print(f"{nom}: historia «{h['tipo']}»")
        # reel
        nom = base + "_reel"
        if reel and not ya_publicado(nom):
            trabajo = os.path.join("/tmp", "demo_" + nom)
            shutil.rmtree(trabajo, ignore_errors=True)
            os.makedirs(trabajo)
            video = os.path.join(trabajo, nom + ".mp4")
            total = render_video(app, caps, video, trabajo)
            print(f"{nom}: reel de {total:.1f} s -> {video}")
            # fotogramas de control (para revisar sin descargar el vídeo)
            control = os.path.join(COLA, nom, "control")
            os.makedirs(control, exist_ok=True)
            for etiqueta, t in (("gancho", 2.6), ("paso", T_GANCHO + T_PASO * 1.6), ("cierre", total - 1.0)):
                jpg = os.path.join(control, f"{etiqueta}.jpg")
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1",
                                "-vf", "scale=540:-1", "-q:v", "3", jpg], check=True)
            if subir:
                if subprocess.run(["gh", "release", "view", RELEASE], capture_output=True).returncode != 0:
                    subprocess.run(["gh", "release", "create", RELEASE, "--title", "Vídeos en cola", "--notes",
                                    "Vídeos renderizados pendientes de publicar. Se borran solos al publicarse."], check=True)
                subprocess.run(["gh", "release", "upload", RELEASE, video, "--clobber"], check=True)
                escribir_post(os.path.join(COLA, nom), dict(
                    tipo="reel", texto=app["texto_reel"], cuando=app["cuando_reel"],
                    renderizado=datetime.now(timezone.utc).isoformat(timespec="seconds"), asset=nom + ".mp4",
                    portada_ms=2900, compartir_en_feed=True, duracion_s=round(total, 1),
                    formato="presentación (capturas reales con Ken Burns, música y efectos; sin voz)", **comun))
                print(f"{nom}: subido a la release '{RELEASE}'")
            else:
                shutil.copy(video, os.path.join("/tmp", nom + ".mp4"))


# ------------------------------------------------------------------ principal
def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opciones = {a for a in sys.argv[1:] if a.startswith("--")}
    orden = args[0] if args else "generar"
    slugs = [s for a in args[1:] for s in a.replace(",", " ").split() if s]
    c = cfg()
    if orden == "descargar":
        descargar(c, slugs)
    elif orden == "generar":
        generar(c, slugs, reel="--sin-reel" not in opciones, subir="--subir" in opciones)
    else:
        sys.exit(f"orden desconocida: {orden}")


if __name__ == "__main__":
    main()
