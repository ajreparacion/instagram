#!/usr/bin/env python3
"""Piezas de presentación de las apps de Neogest Lab a partir de las capturas REALES de demo del
«Centro de Contenido Apps» (entidad Producto, campo demo[].imagen). Creado por el agente de demos (8/11/2026).

Uso (lo lanza .github/workflows/demo_app.yml, que es quien tiene acceso a *.base44.app):
  python3 herramientas/demo_app.py descargar [slug ...]   -> herramientas/demos/<slug>/NN.png
  python3 herramientas/demo_app.py generar   [slug ...] [--sin-reel] [--subir] [--solo=carpeta1,carpeta2]
        (--solo: regenera solo esas piezas, p. ej. 203_studio_beats_pro_reel; la hora "cuando" de un post.json ya
         existente no se pisa)
        -> cola/<NNN>_demo_<slug>_carrusel/ (slides 1080x1350)
           cola/<NNN>_demo_<slug>_historia_<k>/ (1080x1920, "tipo": "historia")
           cola/<NNN>_demo_<slug>_reel/ (slideshow 1080x1920 con música y efectos; con --subir va a la release 'cola')
Sin slugs = todas las apps de herramientas/demo_apps.json.

Textos, horas y públicos: herramientas/demo_apps.json (sacados de demo[], hechos_verificados y prohibido_afirmar
de cada Producto; nada inventado). Nunca pisa un calidad.json existente: la revisión la hace un humano o agente.
"""
import json
import math
import re
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
    img += rng.normal(0, 0.6, img.shape[:2])[..., None]
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

    def vista(self, cap, zoom=1.0, desplaz=0.0, cx=0.5, filtro=Image.LANCZOS, cy=None):
        """Recorte de la captura que cabe en la pantalla. zoom>=1 acerca; desplaz en px de la captura (borde superior
        de lo que se ve); cy (0-1, opcional) centra el recorte en esa altura de la captura y manda sobre desplaz."""
        zoom = max(1.0, zoom)
        esc = self.sw / cap.width * zoom
        rw, rh = self.sw / esc, self.sh / esc
        x0 = (cap.width - rw) * cx
        if cy is not None:
            desplaz = cy * cap.height - rh / 2
        y0 = max(0.0, min(desplaz, cap.height - rh))
        x0 = max(0.0, x0)
        if rh > cap.height:  # captura más baja que la pantalla: se ve entera sobre el color del pie (o desde 'desplaz')
            lienzo = Image.new("RGB", (self.sw, self.sh), cap.getpixel((5, cap.height - 5)))
            im = cap.resize((self.sw, int(cap.height * self.sw / cap.width)), filtro)
            lienzo.paste(im, (0, -int(max(0.0, desplaz) * self.sw / cap.width)))
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
    # caja de cierre: prueba gratuita
    fb = fnt(40, "Bold")
    y0 = y + 44
    d.rounded_rectangle((120, y0, CW - 120, y0 + 94), 30, outline=ACENTO, width=4)
    partes = [("Prueba gratuita", ACENTO), (" · sin tarjeta · sin compromiso", BLANCO)]
    while sum(fb.getlength(p) for p, _ in partes) > CW - 240 - 60 and fb.size > 24:  # cierre de la directiva del 10/11
        fb = fnt(fb.size - 2, "Bold")
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
        s.convert("RGB").save(os.path.join(d, f"{i:02d}.jpg"), quality=88, subsampling=2, optimize=True)
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


def movil_fundido(cap, top, bottom, ancho=560, cx=SW // 2, zona=None):
    """Capa RGBA (tamaño historia) con el móvil, cortado en 'bottom' con fundido al fondo.
    zona (0-1, opcional): altura de la captura donde empieza lo que se ve (zoom intencionado a una tarjeta completa,
    en vez de enseñar siempre el principio de la captura con el botón cortado)."""
    mv = Movil(ancho, 1500, bisel=17)
    capa = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    mv.pegar(capa, cx, top, cap, desplaz=(zona or 0.0) * cap.height)
    a = np.array(capa.getchannel("A"), np.float32)
    ys = np.arange(SH, dtype=np.float32)[:, None]
    k = np.clip((bottom - ys) / 170.0, 0, 1)
    capa.putalpha(Image.fromarray((a * k).astype(np.uint8)))
    return capa


class Capas:
    """Elementos de la historia en capas separadas (para animarlos en el vídeo). t = segundo de entrada."""

    def __init__(self):
        self.lista = []

    def nueva(self, t):
        im = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
        self.lista.append([im, t])
        return im, ImageDraw.Draw(im)

    def recortadas(self):
        salida = []
        for im, t in self.lista:
            bb = im.getbbox()
            if bb:
                salida.append((im.crop(bb), bb[0], bb[1], t))
        return salida


def historia_capas(app, caps, h, idx):
    """Devuelve (fondo, móvil RGBA, [(capa, x, y, t_entrada)]) de una historia."""
    fondo_im = fondo(SW, SH, 300 + idx, brillo=(540, 1350, 650, 0.5))
    C = Capas()
    x = 90
    fp = fnt(30, "ExtraBold")
    cap = caps[h["captura"] - 1]
    if h["tipo"] == "sabias":
        _, d = C.nueva(0.15)
        pastilla(d, x, SAFE_T + 20, "¿SABÍAS QUE…?", fp)
        f, ls = ajustar(h["titulo"], "ExtraBold", SW - 2 * x, 4, 82, 58)
        _, d = C.nueva(0.4)
        y = dibujar_lineas(d, x, SAFE_T + 110, ls, f, BLANCO, h.get("destacar"), alto=1.1)
        ft, lst = ajustar(h["texto"], "Medium", SW - 2 * x, 3, 40, 32)
        _, d = C.nueva(0.9)
        y = dibujar_lineas(d, x, y + 30, lst, ft, GRIS, alto=1.35)
        movil = movil_fundido(cap, y + 50, SAFE_B - 140, zona=h.get("zona"))
    elif h["tipo"] == "antes_despues":
        _, d = C.nueva(0.15)
        pastilla(d, x, SAFE_T + 20, "ANTES / DESPUÉS", fp)
        d.text((x, SAFE_T + 104), f"Con {app['nombre']}", font=fnt(46, "ExtraBold"), fill=BLANCO)
        y = SAFE_T + 184
        ftx = fnt(36, "SemiBold")
        for k, (etiqueta, texto, col, borde, icono) in enumerate((
                ("ANTES", h["antes"], GRIS, (110, 98, 130), "cruz"),
                ("DESPUÉS", h["despues"], BLANCO, ACENTO, "check"))):
            _, d = C.nueva(0.5 + k * 0.9)
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
        movil = movil_fundido(cap, y + 30, SAFE_B - 140, ancho=520, zona=h.get("zona"))
    else:  # pregunta
        _, d = C.nueva(0.15)
        pastilla(d, x, SAFE_T + 20, "PREGUNTA RÁPIDA", fp)
        f, ls = ajustar(h["titulo"], "ExtraBold", SW - 2 * x, 3, 92, 62)
        _, d = C.nueva(0.4)
        y = dibujar_lineas(d, x, SAFE_T + 110, ls, f, BLANCO, h.get("destacar"), alto=1.1)
        caja_top = SAFE_B - 340
        movil = movil_fundido(cap, y + 46, caja_top - 30, ancho=500, zona=h.get("zona"))
        _, d = C.nueva(1.3)
        d.rounded_rectangle((x, caja_top, SW - x, caja_top + 190), 36, fill=(40, 26, 56), outline=ACENTO, width=4)
        ft, lst = ajustar(h["texto"], "Bold", SW - 2 * x - 160, 2, 42, 32)
        yy = caja_top + 95 - len(lst) * int(ft.size * 1.3) // 2
        dibujar_lineas(d, x + 44, yy, lst, ft, BLANCO, alto=1.3)
        flecha(d, SW - x - 70, caja_top + 55, 60, ACENTO, dir="abajo", grosor=7)
    im, d = C.nueva(1.7)
    if app.get("aviso"):
        fa = fnt(26, "SemiBold")
        d.text((SW / 2 - fa.getlength(app["aviso"]) / 2, SAFE_B - 118), app["aviso"], font=fa, fill=GRIS_OSC)
    pie_marca(im)
    return fondo_im, movil, C.recortadas()


def historia(app, caps, h, idx):
    """Imagen fija de la historia (portada de control del vídeo)."""
    fondo_im, movil, capas = historia_capas(app, caps, h, idx)
    im = fondo_im.copy()
    im.paste(movil, (0, 0), movil)
    for capa, x, y, _ in capas:
        im.paste(capa, (x, y), capa)
    return im


def video_historia(app, caps, h, idx, salida, trabajo, mus):
    """Historia en vídeo (8-12 s, 30 fps): zoom suave, textos que entran animados, móvil que sube, música y efectos."""
    fondo_im, movil, capas = historia_capas(app, caps, h, idx)
    beat = 60.0 / mus["bpm"]
    total = beat * max(4, round(10.0 / beat / 2) * 2)
    entradas = sorted({round(t, 2) for _, _, _, t in capas} | {0.55})
    wav = os.path.join(trabajo, "audio.wav")
    # 12/11/2026: las historias SIEMPRE con música dentro del vídeo y máster a -14 LUFS (Instagram no pone canción por API en historias)
    escribir_wav(wav, audio_pieza([0.0], total, mus, entradas=entradas, whoosh_inicio=True, solo_efectos=False))
    masterizar(wav, trabajo, forzar=True)
    mb = movil.getbbox()
    mov = movil.crop(mb)

    def cuadro(t):
        im = fondo_im.copy()
        a = ease((t - 0.55) / 0.6)
        if a > 0:
            dy = (1 - a) * 260 - 30 * (t / total)
            pegar_alfa(im, mov, mb[0], mb[1] + dy, min(1.0, a * 1.3))
        for capa, x, y, t0 in capas:
            k = ease((t - t0) / 0.4)
            pegar_alfa(im, capa, x, y + (1 - k) * 46, k)
        z = 1.0 + 0.035 * (t / total)
        if z > 1.001:
            w2, h2 = int(SW * z), int(SH * z)
            im = im.resize((w2, h2), Image.BILINEAR).crop(((w2 - SW) // 2, (h2 - SH) // 2, (w2 - SW) // 2 + SW, (h2 - SH) // 2 + SH))
        return im

    codificar(cuadro, total, wav, salida)
    return total


# ------------------------------------------------------------------ reel de presentación 1080x1920
FPS = 30
SR = 44100
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


def chip_paso(texto, aviso=""):
    """«PASO n DE N» y, si la app lo pide, la insignia «Demo con datos ficticios» a la derecha."""
    capa = Image.new("RGBA", (SW - 180, 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    d.text((0, 6), texto, font=fnt(30, "ExtraBold"), fill=ACENTO)
    if aviso:
        f = fnt(26, "SemiBold")
        w = f.getlength(aviso)
        x = SW - 180 - w - 40
        d.rounded_rectangle((x, 0, x + w + 38, 50), 25, fill=(34, 26, 48, 255), outline=(120, 106, 148, 255), width=2)
        d.text((x + 19, 9), aviso, font=f, fill=GRIS)
    return capa


class Escena:
    def __init__(self, tipo, dur, **kw):
        self.tipo, self.dur = tipo, dur
        self.__dict__.update(kw)


LUPA_W = SW - 120       # ancho de la lupa (franja de la captura a todo el ancho, sin recortar los lados)
LUPA_H_MAX = 800        # alto máximo: no tapa el texto de arriba
LUPA_BASE = 1640        # borde inferior (igual que el del móvil)


def lupa_zona(cap, cy, hz):
    """Lupa de una franja de la captura (petición de Calidad 9/11: letra pequeña dentro del móvil). La captura se ve
    ENTERA en el móvil; durante la escena aparece esta tarjeta con la franja que explica el texto, a todo el ancho de
    la captura (nunca se cortan palabras por los lados), y un recuadro en el móvil marca de dónde sale.
    Devuelve (RGBA de la tarjeta, (cy, hz) ya ajustados)."""
    esc = LUPA_W / cap.width
    hz = min(max(0.15, hz), LUPA_H_MAX / (cap.height * esc))
    cy = min(max(cy, hz / 2), 1 - hz / 2)
    y0 = int(round((cy - hz / 2) * cap.height)); y1 = int(round((cy + hz / 2) * cap.height))
    tira = cap.crop((0, y0, cap.width, y1)).resize((LUPA_W, int((y1 - y0) * esc)), Image.LANCZOS)
    b = 6; r = 34; sombra = 40
    W2, H2 = tira.width + 2 * b + 2 * sombra, tira.height + 2 * b + 2 * sombra
    capa = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    sm = Image.new("L", (W2, H2), 0)
    ImageDraw.Draw(sm).rounded_rectangle((sombra + 8, sombra + 20, W2 - sombra - 8, H2 - sombra + 12), r + b, fill=170)
    sm = sm.filter(ImageFilter.GaussianBlur(sombra * 0.5))
    capa.paste(Image.new("RGBA", (W2, H2), (5, 3, 10, 255)), (0, 0), sm)
    cuerpo = Image.new("RGBA", (tira.width + 2 * b, tira.height + 2 * b), (0, 0, 0, 0))
    cuerpo.paste(Image.new("RGBA", cuerpo.size, ACENTO + (255,)), (0, 0), mascara_redondeada(cuerpo.width, cuerpo.height, r + b))
    cuerpo.paste(tira, (b, b), mascara_redondeada(tira.width, tira.height, r))
    capa.alpha_composite(cuerpo, (sombra, sombra))
    return capa, (cy, hz)


def preparar_reel(app, caps, dur):
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
    escenas.append(Escena("gancho", dur["gancho"], palabras=palabras,
                          etiqueta=capa_texto([[app["etiqueta"].upper()]], fnt(32, "Bold"), ACENTO, ancho=SW),
                          sub=capa_texto(lss, fs, GRIS, alto=1.32), y_sub=y_fin + 24,
                          movil=Movil(560, 1300, bisel=17), cap=caps[app["portada"] - 1],
                          y_movil=y_fin + 60 + len(lss) * int(fs.size * 1.32),
                          fondo=fondo(SW, SH, 7, brillo=(540, 1500, 700, 0.6))))
    n = len(app["pasos"])
    # Una sola numeración (petición de Calidad 9/11, 203): si los titulares de la app ya dicen «Paso k: …», el rótulo
    # pasa a «PASO k DE T» con ese mismo k (T = el mayor k) y el titular pierde el prefijo; el resto de escenas llevan
    # el nombre de la app en el rótulo. Las apps sin «Paso k» en los titulares no cambian.
    num_titular = [re.match(r"^\s*paso\s+(\d+)\s*[:.\-–]\s*(.+)$", p["titulo"], re.I) for p in app["pasos"]]
    total_titular = max([int(m.group(1)) for m in num_titular if m] or [0])
    for i, p in enumerate(app["pasos"]):
        m_num = num_titular[i]
        if m_num:
            titulo = m_num.group(2)[:1].upper() + m_num.group(2)[1:]
            rotulo = f"PASO {int(m_num.group(1))} DE {total_titular}"
        else:
            titulo = p["titulo"]
            rotulo = app["nombre"].upper() if total_titular else f"PASO {i + 1} DE {n}"
        ft, lst = ajustar(titulo, "ExtraBold", SW - 2 * x, 2, 80, 58)
        fl, lsl = ajustar(p["linea"], "Medium", SW - 2 * x, 3, 40, 32)
        tit = capa_texto(lst, ft, BLANCO, alto=1.08)
        lin = capa_texto(lsl, fl, GRIS, alto=1.3)
        y_tit = 330
        y_lin = y_tit + int(ft.size * 1.08) * len(lst) + 14
        y_mov = y_lin + int(fl.size * 1.3) * len(lsl) + 46
        alto_pant = 1640 - y_mov - 34
        cap = caps[i]
        # Encuadre (petición de Calidad 9/11, 201/203/206): la pantalla del móvil tiene la proporción de la captura, así
        # que se ve ENTERA (título y botón incluidos) al entrar; después un zoom suave y deliberado a la zona que explica
        # el texto ("zona": [altura 0-1, zoom] en demo_apps.json) para que la letra se lea grande. Sin "zona", se queda entera.
        r = cap.height / cap.width
        sw = int(max(400, min(620, alto_pant / r)))
        sh = min(alto_pant, int(round(sw * r)))
        mv = Movil(sw, sh, bisel=18)
        zona, lupa = p.get("zona"), None
        if zona:  # "zona": [altura del centro 0-1, fracción de altura 0-1] -> lupa a todo el ancho con esa franja
            lupa, zona = lupa_zona(cap, float(zona[0]), float(zona[1]))
        escenas.append(Escena("paso", dur["paso"], tit=tit, lin=lin, y_tit=y_tit, y_lin=y_lin, y_mov=y_mov, movil=mv, cap=cap,
                              chip=chip_paso(rotulo, app.get("aviso", "") if app.get("aviso", "").startswith("Demo") else ""),
                              zona=zona, lupa=lupa, fondo=fondo(SW, SH, 20 + i, brillo=(540, 1200, 650, 0.5))))
    # cierre
    fc, lsc = ajustar(app["cierre"], "ExtraBold", SW - 2 * x, 3, 100, 70)
    fs2, lss2 = ajustar(app["cierre_sub"], "Medium", SW - 2 * x - 40, 3, 42, 32)
    tit = capa_texto(lsc, fc, BLANCO, app["cierre_destacar"], alto=1.08, centro=True)
    sub = capa_texto(lss2, fs2, GRIS, alto=1.32, centro=True)
    caja = Image.new("RGBA", (SW, 120), (0, 0, 0, 0))
    dc = ImageDraw.Draw(caja)
    dc.rounded_rectangle((100, 6, SW - 100, 114), 34, outline=ACENTO, width=5, fill=(40, 26, 56, 255))
    fb = fnt(44, "Bold")
    partes = [("Prueba gratuita", ACENTO), (" · sin tarjeta · sin compromiso", BLANCO)]
    while sum(fb.getlength(q) for q, _ in partes) > SW - 200 - 60 and fb.size > 24:  # cierre de la directiva del 10/11
        fb = fnt(fb.size - 2, "Bold")
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
    escenas.append(Escena("cierre", dur["cierre"], tit=tit, sub=sub, caja=caja, firma=firma, y_tit=y_tit, y_sub=y_sub,
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
        a = ease(t / 0.45)
        mv = sc.movil
        mv.pegar(im, SW // 2, sc.y_mov + (1 - a) * 120, sc.cap, alfa=min(1, 0.3 + a), filtro=Image.LANCZOS)
        if sc.zona and sc.lupa is not None:
            cy, hz = sc.zona
            k_r = ease((t - 0.9) / 0.3)
            if k_r > 0:  # recuadro en el móvil: de dónde sale la lupa
                esc = mv.sw / sc.cap.width
                x0 = SW // 2 - mv.bw // 2 + mv.b; y0 = sc.y_mov + mv.b
                rect = (x0 + 6, y0 + (cy - hz / 2) * sc.cap.height * esc, x0 + mv.sw - 6, y0 + (cy + hz / 2) * sc.cap.height * esc)
                ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
                ImageDraw.Draw(ov).rounded_rectangle(rect, 14, outline=ACENTO + (int(255 * k_r),), width=5)
                im.paste(ov, (0, 0), ov)
            k_l = ease_back((t - 1.1) / 0.45, 1.2)
            if k_l > 0:
                lw, lh = sc.lupa.size
                pegar_alfa(im, sc.lupa, (SW - lw) // 2, LUPA_BASE - lh + 40 + (1 - min(1.0, k_l)) * 90, min(1.0, ease((t - 1.1) / 0.3)))
        pegar_alfa(im, sc.chip, 90, 246, ease(t / 0.25))
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


def render_video(app, caps, salida, trabajo, mus):
    dur = duraciones(mus["bpm"], len(app["pasos"]))
    escenas = preparar_reel(app, caps, dur)
    cortes, total = tiempos(escenas)
    wav = os.path.join(trabajo, "audio.wav")
    escribir_wav(wav, audio_pieza(cortes, total, mus, entradas=[c + 0.18 for c in cortes[1:]] + [cortes[-1] + 0.75]))
    masterizar(wav, trabajo)
    nt = int(T_TRANS * FPS)

    def cuadro(t):
        i = max(j for j, c in enumerate(cortes) if c <= t + 1e-9)
        sc = escenas[i]
        tl = t - cortes[i]
        fr = frame_escena(sc, tl, app)
        if i > 0 and tl < T_TRANS:
            e = ease(tl / T_TRANS)
            prev = frame_escena(escenas[i - 1], escenas[i - 1].dur, app)
            comp = Image.new("RGB", (SW, SH))
            dx = int(SW * e)
            comp.paste(prev, (-dx, 0))
            comp.paste(fr, (SW - dx, 0))
            fr = comp
        return fr

    codificar(cuadro, total, wav, salida)
    return total, dur


def duraciones(bpm, n_pasos, max_total=33.0):
    """Escenas en número entero de pulsos (los cortes caen en el golpe)."""
    beat = 60.0 / bpm
    for bp in (8, 7, 6, 5, 4):
        total = (8 + bp * n_pasos + 9) * beat
        if total <= max_total:
            return {"gancho": 8 * beat, "paso": bp * beat, "cierre": 9 * beat}
    return {"gancho": 6 * beat, "paso": 4 * beat, "cierre": 8 * beat}


def codificar(cuadro, total, wav, salida):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{SW}x{SH}",
           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-pix_fmt", "yuv420p", "-profile:v", "high", "-c:a", "aac", "-b:a", "192k", "-ar", str(SR),
           "-shortest", "-movflags", "+faststart", salida]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(int(round(total * FPS))):
        p.stdin.write(cuadro(fi / FPS).convert("RGB").tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise RuntimeError("ffmpeg falló al crear el vídeo")


# ------------------------------------------------------------------ música (generada por código, sin licencias)
# Cada pieza lleva su propia pista: estilo, tempo y tono distintos (orden del dueño 8/11: que no suenen igual y
# que la música RESALTE: primer plano, con pegada, máster a -14 LUFS integrados).
ESTILOS = {
    # bpm por defecto, modo (m/M), progresiones posibles (grados en semitonos desde la tónica)
    "house": (124, "m", [[0, 8, 3, 10], [0, 5, 8, 7]]),
    "pop": (110, "M", [[0, 7, 9, 5], [0, 9, 5, 7]]),
    "disco": (118, "m", [[0, 10, 8, 7], [0, 5, 10, 3]]),
    "dembow": (96, "m", [[0, 8, 3, 10], [0, 10, 8, 10]]),
    "trap": (140, "m", [[0, 8, 5, 7], [0, 3, 8, 7]]),
    "funk": (112, "m", [[0, 5, 0, 7], [0, 10, 5, 7]]),
}
CALIDADES = {0: "m", 3: "M", 5: "m", 7: "M", 8: "M", 10: "M", 9: "m", 2: "m"}


def musica_de(estilo, tono=0, bpm=None, prog=0):
    b, modo, progs = ESTILOS[estilo]
    return {"estilo": estilo, "bpm": float(bpm or b), "tono": int(tono), "prog": progs[prog % len(progs)], "modo": modo}


def _lp(x, fc):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (f / fc) ** 4)
    return np.fft.irfft(X, len(x))


def _hp(x, fc):
    return x - _lp(x, fc)


def _hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def _poner(buf, sig, t0, g=1.0):
    i = int(round(t0 * SR))
    if i >= len(buf) or i + len(sig) <= 0:
        return
    a, b = max(0, i), min(len(buf), i + len(sig))
    buf[a:b] += sig[a - i:b - i] * g


def _env(n, ataque=0.004, caida=0.2):
    t = np.arange(n) / SR
    return np.minimum(1, t / ataque) * np.exp(-t / caida)


def _saw(fr, n, ph=0.0):
    t = np.arange(n) / SR
    return 2 * ((t * fr + ph) % 1) - 1


def _sq(fr, n):
    t = np.arange(n) / SR
    return np.sign(np.sin(2 * np.pi * fr * t))


def _acorde(raiz, grado, modo):
    q = CALIDADES.get(grado % 12, "M") if modo == "m" else {0: "M", 5: "M", 7: "M", 9: "m", 2: "m", 4: "m"}.get(grado % 12, "M")
    r = raiz + grado
    while r > raiz + 6:
        r -= 12
    return [r, r + (3 if q == "m" else 4), r + 7]


def ig_activo():
    """equipo/musica_instagram.json → «activo»: la musica la pone Instagram al publicar (audio_configuration); el video
    lleva solo efectos suaves (whoosh en cada corte y «pop» de entrada)."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import pistas
        if pistas.hay_pistas():      # hay pistas reales en musica/: van dentro del video y no se usa la de Instagram
            return False
        return bool(json.load(open(os.path.join(BASE, "equipo", "musica_instagram.json"), encoding="utf-8")).get("activo"))
    except Exception:
        return False


FICHA_ACTUAL = {}


def _audio_pistas(cortes, total, mus, entradas, whoosh_inicio):
    """Pista real de musica/ (pistas.py) + los efectos de siempre; None si no hay pistas."""
    import pistas
    ficha = pistas.elegir("%s%s%s" % (mus["estilo"], mus["bpm"], mus["tono"])) if pistas.hay_pistas() else None
    if not ficha:
        return None
    n = int((total + 1.0) * SR)
    izq, der, info = pistas.segmento(ficha, n, SR, list(cortes), total + 1.0)
    FICHA_ACTUAL.clear()
    FICHA_ACTUAL.update(info, atribucion=ficha.get("atribucion", ""), url=ficha.get("url", ""))
    rng = np.random.default_rng(int(mus["bpm"] * 7 + mus["tono"] * 31))
    sfx = np.zeros(n)
    for c in list(cortes[1:]) + ([0.0] if whoosh_inicio else []):
        m = int(0.5 * SR)
        env = np.concatenate([np.linspace(0, 1, int(0.32 * SR)) ** 2, np.exp(-np.arange(m - int(0.32 * SR)) / SR / 0.06)])
        _poner(sfx, _hp(_lp(rng.uniform(-1, 1, m), 4000), 500) * env, max(0.0, c - 0.32), 0.3)
    for e in entradas:
        tp = np.arange(int(0.08 * SR)) / SR
        _poner(sfx, np.sin(2 * np.pi * np.cumsum(1100 - 5000 * tp) / SR) * np.exp(-tp / 0.02), e, 0.2)
    est = np.stack([izq + sfx * 0.5, der + sfx * 0.5], axis=1)
    est /= max(1.0, float(np.max(np.abs(est))) / 0.95)
    est = est[:int(total * SR)]
    est[-int(0.6 * SR):] *= np.linspace(1, 0, int(0.6 * SR))[:, None] ** 1.5
    return est * 0.9


def audio_pieza(cortes, total, mus, entradas=(), whoosh_inicio=False, solo_efectos=None):
    """solo_efectos=None: lo decide ig_activo() (reels: la canción la pone Instagram al publicar). solo_efectos=False
    fuerza la música dentro del vídeo: lo usan las HISTORIAS, porque la API de Instagram no admite canción en historias
    (probado el 12/11/2026: error 100/2207065) y salían solo con efectos, casi mudas (-23 LUFS; queja del dueño)."""
    if solo_efectos is None:
        solo_efectos = ig_activo()
    try:
        r = _audio_pistas(cortes, total, mus, entradas, whoosh_inicio)
        if r is not None:
            return r
    except Exception as e:
        print("pistas no disponibles (%s)" % e)
    if solo_efectos:
        rng = np.random.default_rng(int(mus["bpm"] * 7 + mus["tono"] * 31))
        n = int((total + 1.0) * SR)
        sfx = np.zeros(n)
        for c in list(cortes[1:]) + ([0.0] if whoosh_inicio else []):
            m = int(0.5 * SR)
            r = rng.uniform(-1, 1, m)
            env = np.concatenate([np.linspace(0, 1, int(0.32 * SR)) ** 2, np.exp(-np.arange(m - int(0.32 * SR)) / SR / 0.06)])
            _poner(sfx, _hp(_lp(r, 4000), 500) * env, max(0.0, c - 0.32), 0.5)
        for e in entradas:
            tp = np.arange(int(0.08 * SR)) / SR
            _poner(sfx, np.sin(2 * np.pi * np.cumsum(1100 - 5000 * tp) / SR) * np.exp(-tp / 0.02), e, 0.35)
        sfx = sfx / (np.max(np.abs(sfx)) + 1e-9) * 0.35
        est = np.stack([sfx, sfx], axis=1)[:int(total * SR)]
        est[-int(0.3 * SR):] *= np.linspace(1, 0, int(0.3 * SR))[:, None]
        return est
    """10/11/2026 (queja «parece de ascensor»): pista de musica_viral.py (bombo + 808 + palmas + hats + melodia pegadiza,
    cortes al golpe) con los efectos de siempre encima. Si el motor falla, la pista antigua (_audio_pieza_antiguo)."""
    try:
        import musica_viral as mv
        beat = 60.0 / float(mus["bpm"])
        if cortes and len(cortes) > 1:      # el compas cae en el corte: la duracion de la diapositiva = nº entero de pulsos
            d = float(cortes[1]) - float(cortes[0])
            k = max(1, round(d / beat))
            if 0.8 <= (d / k) / beat <= 1.25:
                beat = d / k
        n = int((total + 1.0) * SR)
        rng = np.random.default_rng(int(mus["bpm"] * 7 + mus["tono"] * 31 + len(mus["estilo"])))
        izq, der, _info = mv.generar(n, SR, beat, 0.0, list(cortes), int(mus["bpm"] * 7 + mus["tono"] * 31), estilo=mus["estilo"], total=total + 1.0)
        sfx = np.zeros(n)
        for c in list(cortes[1:]) + ([0.0] if whoosh_inicio else []):
            m = int(0.5 * SR)
            r = rng.uniform(-1, 1, m)
            env = np.concatenate([np.linspace(0, 1, int(0.32 * SR)) ** 2, np.exp(-np.arange(m - int(0.32 * SR)) / SR / 0.06)])
            _poner(sfx, _hp(_lp(r, 4000), 500) * env, max(0.0, c - 0.32), 0.35)
        for e in entradas:
            tp = np.arange(int(0.08 * SR)) / SR
            _poner(sfx, np.sin(2 * np.pi * np.cumsum(1100 - 5000 * tp) / SR) * np.exp(-tp / 0.02), e, 0.25)
        est = np.stack([izq + sfx * 0.6, der + sfx * 0.6], axis=1)
        est /= max(1.0, float(np.max(np.abs(est))) / 0.95)
        fin = int(total * SR)
        est = est[:fin]
        caida = int(0.6 * SR)
        est[-caida:] *= np.linspace(1, 0, caida)[:, None] ** 1.5
        est[:int(0.01 * SR)] *= np.linspace(0, 1, int(0.01 * SR))[:, None]
        return est * 0.9
    except Exception as e:
        print("musica_viral no disponible (%s): pista antigua" % e)
        return _audio_pieza_antiguo(cortes, total, mus, entradas, whoosh_inicio)


def _audio_pieza_antiguo(cortes, total, mus, entradas=(), whoosh_inicio=False):
    estilo, bpm = mus["estilo"], mus["bpm"]
    rng = np.random.default_rng(int(bpm * 7 + mus["tono"] * 31 + len(estilo)))
    beat = 60.0 / bpm
    bar = 4 * beat
    n = int((total + 1.0) * SR)
    raiz = 57 + mus["tono"]            # La3 + tono
    prog = mus["prog"]
    K, S, H, B, C, L = (np.zeros(n) for _ in range(6))
    # --- sonidos
    tk = np.arange(int(0.45 * SR)) / SR
    kick = np.sin(2 * np.pi * np.cumsum(50 + 130 * np.exp(-tk / 0.028)) / SR) * np.exp(-tk / 0.20)
    kick[:90] += np.linspace(1, 0, 90) * rng.uniform(-0.7, 0.7, 90)
    kick = np.tanh(kick * 2.2)
    rn = rng.uniform(-1, 1, int(0.3 * SR))
    tn = np.arange(len(rn)) / SR
    snare = _hp(_lp(rn, 7000), 1500) * np.exp(-tn / 0.09) * 0.9 + np.sin(2 * np.pi * 185 * tn) * np.exp(-tn / 0.05) * 0.6
    clap = np.zeros(int(0.35 * SR))
    for k, d0 in enumerate((0.0, 0.009, 0.018)):
        seg = _hp(_lp(rng.uniform(-1, 1, int(0.3 * SR)), 3500), 900) * np.exp(-np.arange(int(0.3 * SR)) / SR / (0.012 if k < 2 else 0.11))
        _poner(clap, seg, d0)
    hh = _hp(rng.uniform(-1, 1, int(0.05 * SR)), 8000) * np.exp(-np.arange(int(0.05 * SR)) / SR / 0.012)
    oh = _hp(rng.uniform(-1, 1, int(0.25 * SR)), 7000) * np.exp(-np.arange(int(0.25 * SR)) / SR / 0.09)

    def nota_bajo(m, dur, tipo="saw"):
        k = int(dur * SR)
        f = _hz(m)
        if tipo == "808":
            t = np.arange(k) / SR
            s = np.sin(2 * np.pi * np.cumsum(f * (1 + 0.6 * np.exp(-t / 0.03))) / SR)
            return np.tanh(s * 2.0) * np.minimum(1, t / 0.005) * np.exp(-t / max(0.25, dur))
        s = _saw(f, k) * 0.6 + np.sin(2 * np.pi * f * np.arange(k) / SR)
        return s * _env(k, 0.003, dur * 0.6)

    def pluck(m, dur=0.22):
        k = int(dur * SR)
        t = np.arange(k) / SR
        f = _hz(m)
        return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(4 * np.pi * f * t) + 0.25 * _sq(f, k) * np.exp(-t / 0.02)) * np.exp(-t / 0.09)

    nb = int(total / bar) + 2
    for c in range(nb):
        t0 = c * bar
        ac = _acorde(raiz, prog[c % len(prog)], mus["modo"])
        rb = ac[0] - 24
        intro = c == 0 and cortes and len(cortes) > 1   # primer compás un poco más ligero en los reels
        # --- batería por estilo
        if estilo in ("house", "disco"):
            for b4 in range(4):
                _poner(K, kick, t0 + b4 * beat, 1.0)
                _poner(H, oh, t0 + (b4 + 0.5) * beat, 0.55 if estilo == "disco" else 0.4)
                for s16 in (0.25, 0.75):
                    _poner(H, hh, t0 + (b4 + s16) * beat, 0.3)
            for b4 in (1, 3):
                _poner(S, clap, t0 + b4 * beat, 0.9)
        elif estilo in ("pop", "funk"):
            pat = [0, 1.5, 2, 2.75] if estilo == "pop" else [0, 0.75, 1.75, 2.5, 3.25]
            for p in pat:
                _poner(K, kick, t0 + p * beat, 1.0)
            for b4 in (1, 3):
                _poner(S, snare, t0 + b4 * beat, 1.0)
                _poner(S, clap, t0 + b4 * beat, 0.4)
            for e in range(8):
                _poner(H, hh, t0 + e * beat / 2, 0.45 if e % 2 else 0.3)
            if estilo == "funk":
                for e in range(16):
                    if e % 4 == 3:
                        _poner(H, hh, t0 + e * beat / 4, 0.25)
        elif estilo == "dembow":
            for b4 in range(4):
                _poner(K, kick, t0 + b4 * beat, 1.0)
                _poner(S, snare, t0 + (b4 + 0.75) * beat, 0.85)
                if b4 % 2 == 1:
                    _poner(S, snare, t0 + (b4 + 0.5) * beat, 0.75)
                _poner(H, hh, t0 + (b4 + 0.5) * beat, 0.35)
                _poner(H, hh, t0 + b4 * beat, 0.25)
        elif estilo == "trap":
            for p in ([0, 1.75, 2.5] if c % 2 == 0 else [0, 0.75, 2.5, 3.25]):
                _poner(K, kick, t0 + p * beat, 0.9)
            _poner(S, clap, t0 + 2 * beat, 1.0)
            _poner(S, snare, t0 + 2 * beat, 0.7)
            for e in range(8):
                _poner(H, hh, t0 + e * beat / 2, 0.4)
            for r in range(6):          # redoble de charles al final del compás
                _poner(H, hh, t0 + 3.5 * beat + r * beat / 12, 0.3)
        # --- bajo
        if estilo == "trap":
            for p, du in zip(*(([0, 1.75, 2.5], [1.6, 0.7, 1.4]) if c % 2 == 0 else ([0, 0.75, 2.5, 3.25], [0.7, 1.6, 0.7, 0.7]))):
                _poner(B, nota_bajo(rb + 12, du * beat, "808"), t0 + p * beat, 0.9)
        elif estilo == "dembow":
            for p in (0, 1.5, 2, 3.5):
                _poner(B, nota_bajo(rb + 12, 0.45 * beat, "808"), t0 + p * beat, 0.8)
        elif estilo == "disco":
            for e in range(8):
                _poner(B, nota_bajo(rb + (12 if e % 2 else 0), 0.45 * beat), t0 + e * beat / 2, 0.55)
        elif estilo == "house":
            for b4 in range(4):
                _poner(B, nota_bajo(rb, 0.4 * beat), t0 + (b4 + 0.5) * beat, 0.6)
        else:  # pop / funk
            pat = [0, 0.75, 1.5, 2, 2.75, 3.5] if estilo == "funk" else [0, 0.5, 1.5, 2, 2.5, 3.5]
            for p in pat:
                _poner(B, nota_bajo(rb + (12 if (estilo == "funk" and p in (0.75, 2.75)) else 0), 0.4 * beat), t0 + p * beat, 0.6)
        # --- acordes (stabs con pegada) y melodía
        k = int(bar * SR)
        if estilo in ("house", "disco", "funk"):
            stab_pos = [0.5, 1.5, 2.5, 3.5] if estilo != "funk" else [0.25, 1.25, 2.0, 3.25]
            for p in stab_pos:
                kk = int(0.22 * SR)
                s = sum(_saw(_hz(m + 12) * dt, kk) for m in ac for dt in (0.996, 1.004))
                _poner(C, s * _env(kk, 0.002, 0.08), t0 + p * beat, 0.16)
        else:
            s = sum(_saw(_hz(m + 12) * dt, k) for m in ac for dt in (0.995, 1.005))
            env = np.minimum(1, np.arange(k) / (0.03 * SR)) * np.minimum(1, (k - np.arange(k)) / (0.06 * SR))
            _poner(C, s * env, t0, 0.07)
        if not intro:
            escala = [ac[0] + 24, ac[1] + 24, ac[2] + 24, ac[0] + 36]
            paso = 0.5 if estilo in ("trap", "dembow") else 0.25
            figura = rng.permutation(4)
            for e in range(int(4 / paso)):
                if estilo in ("trap", "dembow") and e % 3 == 2:
                    continue
                _poner(L, pluck(escala[figura[e % 4]]), t0 + e * paso * beat, 0.16 if paso == 0.25 else 0.22)
    # --- mezcla: bombeo de acordes/bajo con el bombo (no en trap)
    t = np.arange(n) / SR
    if estilo != "trap":
        duck = 1 - 0.5 * np.exp(-((t % beat)) / 0.10)
    else:
        duck = np.ones(n)
    B = _lp(B, 900 if estilo in ("trap", "dembow") else 650)
    C = _lp(C, 3200)
    musica = K * 1.0 + S * 0.75 + H * 0.5 + B * duck * 0.9 + C * duck + _lp(L, 6500)
    # --- efectos (suaves: la música manda)
    sfx = np.zeros(n)
    for c in list(cortes[1:]) + ([0.0] if whoosh_inicio else []):
        m = int(0.5 * SR)
        r = rng.uniform(-1, 1, m)
        env = np.concatenate([np.linspace(0, 1, int(0.32 * SR)) ** 2, np.exp(-np.arange(m - int(0.32 * SR)) / SR / 0.06)])
        _poner(sfx, _hp(_lp(r, 4000), 500) * env, max(0.0, c - 0.32), 0.5)
    for e in entradas:
        tp = np.arange(int(0.08 * SR)) / SR
        _poner(sfx, np.sin(2 * np.pi * np.cumsum(1100 - 5000 * tp) / SR) * np.exp(-tp / 0.02), e, 0.35)
    # estéreo: acordes/melodía abiertos, bombo y bajo al centro
    ancho = np.roll(C * duck + _lp(L, 6500), int(0.011 * SR))
    izq = musica + sfx * 0.8 + 0.25 * (ancho - (C * duck + _lp(L, 6500)))
    der = musica + sfx * 0.8 - 0.25 * (ancho - (C * duck + _lp(L, 6500)))
    est = np.stack([izq, der], axis=1)
    est /= (np.max(np.abs(est)) + 1e-9)
    est = np.tanh(est * 1.4) / np.tanh(1.4)          # pegada: saturación suave
    fin = int(total * SR)
    est = est[:fin]
    caida = int(0.6 * SR)
    est[-caida:] *= np.linspace(1, 0, caida)[:, None] ** 1.5
    est[:int(0.01 * SR)] *= np.linspace(0, 1, int(0.01 * SR))[:, None]
    return est * 0.9


def escribir_wav(ruta, est):
    import wave
    datos = (np.clip(est, -1, 1) * 32767).astype("<i2").tobytes()
    with wave.open(ruta, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(datos)


def masterizar(wav, trabajo, objetivo=-14.0, pico=-1.0, forzar=False):
    """Máster a -14 LUFS integrados y pico real ≤ -1 dBTP (loudnorm de ffmpeg en dos pasadas, modo lineal).
    forzar=True: masteriza aunque la música de Instagram esté activa (historias: llevan la música dentro del vídeo)."""
    if ig_activo() and not forzar:
        return   # solo efectos: no se sube a -14 LUFS (la musica y el volumen los pone Instagram)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", wav, "-af",
                        f"loudnorm=I={objetivo}:TP={pico}:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    txt = r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1]
    m = json.loads(txt)
    salida = os.path.join(trabajo, "master.wav")
    filtro = (f"loudnorm=I={objetivo}:TP={pico}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
              f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-af", filtro, "-ar", str(SR), salida], check=True)
    os.replace(salida, wav)


def medir(video):
    """Sonoridad integrada (LUFS) y pico real (dBTP) del vídeo final, con ebur128 de ffmpeg."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", video, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    res = r.stderr[r.stderr.rindex("Summary:"):]
    import re
    i = float(re.search(r"I:\s+(-?[\d.]+) LUFS", res).group(1))
    tp = float(re.search(r"Peak:\s+(-?[\d.]+) dBFS", res).group(1))
    lra = float(re.search(r"LRA:\s+(-?[\d.]+) LU", res).group(1))
    return {"lufs_integrados": i, "pico_real_dbtp": tp, "lra_lu": lra, "medido_con": "ffmpeg ebur128=peak=true"}


# ------------------------------------------------------------------ reel a partir de un carrusel ya aprobado
def slides_de(carpeta):
    for base in ("cola", "publicados"):
        d = os.path.join(BASE, base, carpeta, "slides")
        if os.path.isdir(d) and any(f.endswith(".jpg") for f in os.listdir(d)):
            return [Image.open(os.path.join(d, f)).convert("RGB") for f in sorted(os.listdir(d)) if f.endswith(".jpg")]
    # ya publicado (slides/ borradas del árbol): se sacan del historial de git
    ruta = f"cola/{carpeta}/slides"
    # --diff-filter=AM: último commit que añadió o cambió la diapositiva (el último a secas es el que la borró y ahí ya no está)
    sha = subprocess.run(["git", "log", "-1", "--diff-filter=AM", "--format=%H", "--", ruta + "/01.jpg"], cwd=BASE, capture_output=True,
                         text=True).stdout.strip()
    if not sha:
        raise SystemExit(f"{carpeta}: no encuentro sus diapositivas")
    nombres = subprocess.run(["git", "ls-tree", "--name-only", sha, ruta + "/"], cwd=BASE, capture_output=True,
                             text=True).stdout.split()
    import io
    out = []
    for nme in sorted(x for x in nombres if x.endswith(".jpg")):
        datos = subprocess.run(["git", "show", f"{sha}:{nme}"], cwd=BASE, capture_output=True).stdout
        out.append(Image.open(io.BytesIO(datos)).convert("RGB"))
    return out


def corregir_cierre(im, sub=None):
    """10/11/2026 (orden del dueño 00:00 + Calidad): diapositiva de cierre con el cierre antiguo cocido
    («Escríbeme IDEA por privado») -> caja «Prueba gratuita · sin tarjeta · sin compromiso». Detecta la caja redondeada
    por su borde, repinta esa franja con el degradado del fondo y dibuja la caja nueva con el mismo color de acento. Si se
    pasa `sub`, repinta también el subtítulo (p. ej. «… Pide la demo: enlace en el perfil.»). Idempotente."""
    im = im.convert("RGB")
    a = np.asarray(im).astype(np.int32)
    H_, W_ = a.shape[:2]

    def degradado(y0, y1, x0=96, x1=W_ - 96):
        izq = a[y0:y1, 56:64].mean(axis=1)
        der = a[y0:y1, W_ - 64:W_ - 56].mean(axis=1)
        t = np.clip((np.arange(x0, x1) - 60) / float(W_ - 120), 0, 1)[None, :, None]
        return (izq[:, None, :] * (1 - t) + der[:, None, :] * t)

    # 1) caja: filas entre 605 y 860 donde, en x 300-760, hay algo distinto del fondo (borde superior e inferior; el
    #    texto queda entre ambos). El color del borde se toma en el lado izquierdo, ya en el tramo recto.
    ref = degradado(605, 860, 300, 760)
    dif_c = np.abs(a[605:860, 300:760] - ref).sum(axis=2)
    filas = [605 + int(y) for y in np.where(dif_c.max(axis=1) > 120)[0]]
    if not filas:
        return im
    top, bot = min(filas), max(filas)
    # borde: el píxel más lejano al fondo en la franja del borde superior (3 filas)
    franja = a[top:top + 4, 300:760].reshape(-1, 3)
    bg_top = a[top, 56:60].mean(axis=0)
    acento = tuple(int(v) for v in franja[np.abs(franja - bg_top).sum(axis=1).argmax()])
    # color del texto: el píxel más lejano al fondo en «By Neogest Lab»
    reg = a[1170:1225, 370:710].reshape(-1, 3)
    bg_pie = a[1195, 56:60].mean(axis=0)
    txt = tuple(int(v) for v in reg[np.abs(reg - bg_pie).sum(axis=1).argmax()])
    out = a.copy()
    out[top - 8:bot + 9, 96:W_ - 96] = degradado(top - 8, bot + 9)
    # 2) subtítulo (opcional)
    if sub:
        sy0, sy1 = 470, top - 14
        sub_col = None
        reg_s = a[sy0:sy1, 96:W_ - 96]
        bgs = degradado(sy0, sy1)
        dif = np.abs(reg_s - bgs).sum(axis=2)
        filas_s = np.where(dif.max(axis=1) > 150)[0]
        if len(filas_s):
            sub_col = tuple(int(v) for v in reg_s.reshape(-1, 3)[dif.reshape(-1).argmax()])
            ytxt = sy0 + int(filas_s.min())
            out[sy0:sy1, 96:W_ - 96] = bgs
    im2 = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im2)
    if sub and sub_col is not None:
        fs, lss = ajustar(sub, "Medium", CW - 2 * MX - 40, 2, 40, 30)
        dibujar_lineas(d, 0, ytxt - int(fs.size * 0.28), lss, fs, sub_col, alto=1.35, centro=CW // 2)
    fb = fnt(40, "Bold")
    y0 = top
    d.rounded_rectangle((120, y0, CW - 120, y0 + 94), 30, outline=acento, width=4)
    partes = [("Prueba gratuita", acento), (" · sin tarjeta · sin compromiso", txt)]
    while sum(fb.getlength(p_) for p_, _ in partes) > CW - 240 - 60 and fb.size > 24:
        fb = fnt(fb.size - 2, "Bold")
    total = sum(fb.getlength(p_) for p_, _ in partes)
    x = CW / 2 - total / 2
    for p_, col in partes:
        d.text((x, y0 + 23), p_, font=fb, fill=col)
        x += fb.getlength(p_)
    return im2


def video_carrusel(slides, salida, trabajo, mus, max_total=30.0):
    beat = 60.0 / mus["bpm"]
    n = len(slides)
    for bp in (8, 7, 6, 5, 4):
        if (bp * n + 2) * beat <= max_total:
            break
    durs = [bp * beat] * n
    durs[0] += 2 * beat        # el gancho, un poco más
    cortes = [sum(durs[:i]) for i in range(n)]
    total = sum(durs)
    wav = os.path.join(trabajo, "audio.wav")
    escribir_wav(wav, audio_pieza(cortes, total, mus, entradas=[c + 0.3 for c in cortes]))
    masterizar(wav, trabajo)
    esc = 0.9
    cw, ch = int(1080 * esc), int(1350 * esc)
    x0, y0 = (SW - cw) // 2, 255
    # fondo: la portada del carrusel ampliada, desenfocada y oscurecida (mismos colores que el carrusel)
    portada = slides[0].resize((int(1350 * SW / 1080 * 1.45), int(SH * 1.0)), Image.BILINEAR)
    portada = portada.crop(((portada.width - SW) // 2, 0, (portada.width - SW) // 2 + SW, SH))
    fondo_im = Image.blend(portada.filter(ImageFilter.GaussianBlur(48)), Image.new("RGB", (SW, SH), (8, 6, 12)), 0.55)
    # sombra y esquinas redondeadas de la tarjeta
    sm = Image.new("L", (SW, SH), 0)
    ImageDraw.Draw(sm).rounded_rectangle((x0 + 8, y0 + 30, x0 + cw - 8, y0 + ch + 26), 40, fill=170)
    fondo_im.paste(Image.new("RGB", (SW, SH), (6, 3, 12)), (0, 0), sm.filter(ImageFilter.GaussianBlur(30)))
    mascara = mascara_redondeada(cw, ch, 36)
    corte_txt = int(ch * 0.47)
    fh = fnt(30, "Bold")

    def tarjeta(i, t, z=True):
        im = slides[i]
        k = 1.0 + (0.045 * min(1.0, t / durs[i]) if z else 0.0)
        rw, rh = 1080 / k, 1350 / k
        bx = (1080 - rw) / 2
        by = (1350 - rh) * 0.35
        card = im.resize((cw, ch), Image.BILINEAR, box=(bx, by, bx + rw, by + rh))
        # «textos animados»: la franja de arriba (titulares) entra con fundido y subida
        a = ease((t - 0.08) / 0.45)
        if a < 0.999:
            arriba = card.crop((0, 0, cw, corte_txt))
            base = card.copy()
            base.paste(card.crop((6, 0, 7, corte_txt)).resize((cw, corte_txt)), (0, 0))   # fondo sin texto
            base.paste(arriba, (0, int((1 - a) * 40)), Image.new("L", arriba.size, int(255 * a)))
            card = base
        return card

    def cuadro(t):
        i = max(j for j, c in enumerate(cortes) if c <= t + 1e-9)
        tl = t - cortes[i]
        im = fondo_im.copy()
        d = ImageDraw.Draw(im)
        # cabecera: @neogestlab y contador que salta en cada corte
        d.text((x0, 180), "@neogestlab", font=fh, fill=GRIS)
        s = ease_back(tl / 0.3)
        txt = f"{i + 1:02d}/{n:02d}"
        ft = fnt(max(8, int(30 * (0.6 + 0.4 * s))), "ExtraBold")
        d.text((x0 + cw - ft.getlength(txt), 180 + (30 - ft.size) / 2), txt, font=ft, fill=ACENTO)
        actual = tarjeta(i, tl)
        if i > 0 and tl < T_TRANS:
            e = ease(tl / T_TRANS)
            prev = tarjeta(i - 1, durs[i - 1])
            dx = int((cw + 80) * e)
            im.paste(prev, (x0 - dx, y0), mascara)
            im.paste(actual, (x0 + cw + 80 - dx, y0), mascara)
        else:
            im.paste(actual, (x0, y0), mascara)
        # barra de progreso
        yb = y0 + ch + 34
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((x0, yb, x0 + cw, yb + 8), 4, fill=(70, 58, 90))
        d.rounded_rectangle((x0, yb, x0 + int(cw * min(1.0, t / total)), yb + 8), 4, fill=ACENTO)
        return im

    codificar(cuadro, total, wav, salida)
    return total


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
    if FICHA_ACTUAL and datos.get("tipo") in ("reel", "historia"):   # pista real de musica/: licencia (y atribucion si la exige)
        datos["musica"] = {k: FICHA_ACTUAL.get(k) for k in ("titulo", "autor", "licencia", "url", "archivo", "bpm")}
        datos["musica"]["origen"] = "pista sin derechos de la biblioteca musica/ (licencia en musica/pistas.json)"
        at = FICHA_ACTUAL.get("atribucion")
        if at and datos.get("texto") is not None and at not in datos["texto"] and datos.get("tipo") == "reel":
            datos["texto"] = datos["texto"].rstrip() + "\n\n" + at
    if ig_activo() and datos.get("tipo") == "reel":   # musica de la biblioteca de Instagram al publicar
        sys.path.insert(0, BASE)
        import publicar_gh as _P
        est = (datos.get("musica") or {}).get("estilo") if isinstance(datos.get("musica"), dict) else None
        ig = _P.audio_ig_para(os.path.basename(carpeta), False, est)
        if ig:
            datos["audio_ig"] = ig
            datos["musica"] = {"origen": ig["origen"], "titulo": ig["titulo"], "audio_id": ig["audio_id"],
                               "nota": "música puesta por Instagram al publicar (audio_configuration); el vídeo lleva solo efectos"}
    if previo.get("cuando"):   # la hora de publicación que ya esté en la cola manda (Calidad/Estratega la mueven en post.json)
        datos["cuando"] = previo["cuando"]
    with open(ruta + ".tmp", "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
    os.replace(ruta + ".tmp", ruta)


def subir_release(video):
    if subprocess.run(["gh", "release", "view", RELEASE], capture_output=True).returncode != 0:
        subprocess.run(["gh", "release", "create", RELEASE, "--title", "Vídeos en cola", "--notes",
                        "Vídeos renderizados pendientes de publicar. Se borran solos al publicarse."], check=True)
    subprocess.run(["gh", "release", "upload", RELEASE, video, "--clobber"], check=True)


def fotogramas_control(video, carpeta, momentos):
    control = os.path.join(carpeta, "control")
    shutil.rmtree(control, ignore_errors=True)
    os.makedirs(control)
    for etiqueta, t in momentos:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{max(0.0, t):.2f}", "-i", video, "-frames:v", "1",
                        "-vf", "scale=540:-1", "-q:v", "4", os.path.join(control, f"{etiqueta}.jpg")], check=True)


def resumen_musica(mus):
    return {"estilo": mus["estilo"], "bpm": mus["bpm"], "tono": mus["tono"], "origen": "generada por código (sin licencias de terceros)"}


def generar(c, slugs, reel=True, historias=True, subir=False, solo=None):
    for app in apps_pedidas(c, slugs):
        caps = cargar_capturas(app["slug"])
        if len(caps) != len(app["pasos"]):
            raise SystemExit(f"{app['slug']}: {len(caps)} capturas y {len(app['pasos'])} pasos")
        base = f"{app['numero']}_{app['slug'].replace('-', '_')}"
        comun = {"app": app["nombre"], "publico": app["publico"], "fuentes": [FUENTES_TXT.format(n=app["nombre"])],
                 "origen": "herramientas/demo_app.py"}
        # carrusel (imágenes: la API no permite música en carruseles)
        nom = base + "_carrusel"
        if not ya_publicado(nom) and (not solo or nom in solo):
            carpeta = os.path.join(COLA, nom)
            os.makedirs(carpeta, exist_ok=True)
            n = carrusel(app, caps, carpeta)
            escribir_post(carpeta, dict(tipo="carrusel", texto=app["texto_carrusel"], cuando=app["cuando_carrusel"],
                                        renderizado="no aplica (carrusel)", diapositivas=n, **comun))
            print(f"{nom}: carrusel de {n} diapositivas")
        # historias en vídeo con música
        for k, h in enumerate(app["historias"], 1):
            nom = f"{base}_historia{k}"
            if not historias or ya_publicado(nom) or (solo and nom not in solo):
                continue
            carpeta = os.path.join(COLA, nom)
            os.makedirs(carpeta, exist_ok=True)
            trabajo = os.path.join("/tmp", "demo_" + nom)
            shutil.rmtree(trabajo, ignore_errors=True)
            os.makedirs(trabajo)
            mus = musica_de(**h["musica"])
            video = os.path.join(trabajo, nom + ".mp4")
            total = video_historia(app, caps, h, k, video, trabajo, mus)
            audio = medir(video)
            fotogramas_control(video, carpeta, (("entrada", 0.6), ("completa", total - 1.0)))
            shutil.rmtree(os.path.join(carpeta, "slides"), ignore_errors=True)
            print(f"{nom}: historia «{h['tipo']}» en vídeo de {total:.1f} s, {mus['estilo']} {mus['bpm']:.0f} BPM, "
                  f"{audio['lufs_integrados']} LUFS / {audio['pico_real_dbtp']} dBTP")
            if subir:
                subir_release(video)
                escribir_post(carpeta, dict(tipo="historia", texto="", cuando=h["cuando"],
                                            renderizado=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                            asset=nom + ".mp4", medio="video", duracion_s=round(total, 1),
                                            formato=h["tipo"], musica=resumen_musica(mus), audio=audio, **comun))
            else:
                shutil.copy(video, os.path.join("/tmp", nom + ".mp4"))
        # reel de presentación
        nom = base + "_reel"
        if reel and not ya_publicado(nom) and (not solo or nom in solo):
            trabajo = os.path.join("/tmp", "demo_" + nom)
            shutil.rmtree(trabajo, ignore_errors=True)
            os.makedirs(trabajo)
            mus = musica_de(**app["musica"])
            video = os.path.join(trabajo, nom + ".mp4")
            total, dur = render_video(app, caps, video, trabajo, mus)
            audio = medir(video)
            fotogramas_control(video, os.path.join(COLA, nom), (("gancho", dur["gancho"] * 0.7),
                                                               ("paso", dur["gancho"] + dur["paso"] * 1.6),
                                                               ("cierre", total - 1.0)))
            print(f"{nom}: reel de {total:.1f} s, {mus['estilo']} {mus['bpm']:.0f} BPM, "
                  f"{audio['lufs_integrados']} LUFS / {audio['pico_real_dbtp']} dBTP")
            if subir:
                subir_release(video)
                escribir_post(os.path.join(COLA, nom), dict(
                    tipo="reel", texto=app["texto_reel"], cuando=app["cuando_reel"],
                    renderizado=datetime.now(timezone.utc).isoformat(timespec="seconds"), asset=nom + ".mp4",
                    portada_ms=int(dur["gancho"] * 700), compartir_en_feed=True, duracion_s=round(total, 1),
                    formato="presentación (capturas reales con Ken Burns, música en primer plano y efectos; sin voz)",
                    musica=resumen_musica(mus), audio=audio, **comun))
            else:
                shutil.copy(video, os.path.join("/tmp", nom + ".mp4"))


def leer_post(carpeta):
    for base in ("cola", "publicados"):
        p = os.path.join(BASE, base, carpeta, "post.json")
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                return json.load(f)
    return {}


def reels_carrusel(c, carpetas, subir=False):
    """Versión reel (con música) de carruseles ya aprobados: sus diapositivas animadas, sin cambiar el contenido."""
    for item in c.get("reels_carrusel", []):
        if carpetas and carpetas != ["todos"] and item["carpeta"] not in carpetas:
            continue
        nom = item["carpeta"] + "_reel"
        if ya_publicado(nom):
            continue
        slides = slides_de(item["carpeta"])
        # 10/11/2026: cierre «Prueba gratuita · sin tarjeta · sin compromiso» también en las diapositivas antiguas
        slides[-1] = corregir_cierre(slides[-1], item.get("cierre_sub"))
        post_car = leer_post(item["carpeta"])
        post_reel = leer_post(nom)   # el texto del reel que ya esté en cola (con el cierre de la directiva) manda
        trabajo = os.path.join("/tmp", "demo_" + nom)
        shutil.rmtree(trabajo, ignore_errors=True)
        os.makedirs(trabajo)
        mus = musica_de(**item["musica"])
        video = os.path.join(trabajo, nom + ".mp4")
        total = video_carrusel(slides, video, trabajo, mus)
        audio = medir(video)
        carpeta = os.path.join(COLA, nom)
        os.makedirs(carpeta, exist_ok=True)
        beat = 60.0 / mus["bpm"]
        fotogramas_control(video, carpeta, (("gancho", 1.6), ("medio", total / 2 + 0.6), ("cierre", total - 1.0)))
        print(f"{nom}: reel de {total:.1f} s ({len(slides)} diapositivas), {mus['estilo']} {mus['bpm']:.0f} BPM, "
              f"{audio['lufs_integrados']} LUFS / {audio['pico_real_dbtp']} dBTP")
        if subir:
            subir_release(video)
            escribir_post(carpeta, dict(
                tipo="reel", texto=item.get("texto") or post_reel.get("texto") or post_car.get("texto", ""),
                cuando=post_reel.get("cuando") or item["cuando"],
                renderizado=datetime.now(timezone.utc).isoformat(timespec="seconds"), asset=nom + ".mp4",
                portada_ms=1500, compartir_en_feed=True, duracion_s=round(total, 1),
                formato="versión reel del carrusel (diapositivas animadas, música en primer plano y efectos; sin voz)",
                app=post_car.get("app"), publico=post_car.get("publico"),
                fuentes=[f"Diapositivas del carrusel {item['carpeta']} (aprobado por Calidad); mismo contenido."] +
                        list(post_car.get("fuentes") or []),
                carrusel=item["carpeta"], musica=resumen_musica(mus), audio=audio, origen="herramientas/demo_app.py"))
        else:
            shutil.copy(video, os.path.join("/tmp", nom + ".mp4"))


CIERRE_POST = "Pide tu prueba gratuita: sin tarjeta, sin datos bancarios y sin compromiso. Enlace en el perfil."


def cierres_carruseles(c, carpetas):
    """Carruseles de cola/ con el cierre antiguo cocido en la última diapositiva y en el texto del post: repinta la caja
    (y el subtítulo si el item de reels_carrusel lleva «cierre_sub») y pone el cierre de la directiva del 10/11 en post.json."""
    subs = {it["carpeta"]: it.get("cierre_sub") for it in c.get("reels_carrusel", [])}
    for car in carpetas:
        d = os.path.join(COLA, car)
        sl = sorted(f for f in os.listdir(os.path.join(d, "slides")) if f.endswith(".jpg"))
        ruta = os.path.join(d, "slides", sl[-1])
        corregir_cierre(Image.open(ruta), subs.get(car)).save(ruta, quality=88, subsampling=2, optimize=True)
        pj = os.path.join(d, "post.json")
        post = json.load(open(pj, encoding="utf-8"))
        t = post.get("texto", "")
        t = re.sub(r"(Pide la demo en el enlace del perfil\.\s*)?(¿Lo quieres para tu negocio\?|¿Y una app a medida para tu negocio\?)?\s*"
                   r"Escríbeme IDEA por privado\.?", " " + CIERRE_POST, t)
        t = re.sub(r"\n[ \t]+" + re.escape(CIERRE_POST), "\n" + CIERRE_POST, t)
        post["texto"] = t
        json.dump(post, open(pj, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"{car}: última diapositiva {sl[-1]} y texto del post con el cierre de la directiva")


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
        solo = {x for o in opciones if o.startswith("--solo=") for x in o[7:].replace(",", " ").split() if x}
        generar(c, slugs, reel="--sin-reel" not in opciones, historias="--sin-historias" not in opciones,
                subir="--subir" in opciones, solo=solo or None)
    elif orden == "reels_carrusel":
        reels_carrusel(c, slugs, subir="--subir" in opciones)
    elif orden == "cierres":
        cierres_carruseles(c, slugs)
    else:
        sys.exit(f"orden desconocida: {orden}")


if __name__ == "__main__":
    main()
