#!/usr/bin/env python3
"""Modo "sketch" de hacer_reel.py: serie «El Jambo que sabe y las IAs» (orden del dueño, 10/11/2026).

Personajes (todos inventados, forma simple + ojos + boca, un acento de color cada uno):
  jambo     El Jambo que sabe: humano desaliñado y poco limpio (pelo revuelto, barba de días, camiseta arrugada y
            manchada, ojeras, zapatillas sucias, moscas). Acciones: presume, delega, desespera, remata.
  jupillo   La Jupillo: la IA que lo acaba haciendo todo; cansada y resignada (ojeras, taza de café, pila de papeles).
  pelota    La Pelota: pelota naranja sabelotodo, siempre muy segura (dedo en alto, gafas redondas).
  bola      El Bola: coach tóxico satírico (gafas de sol, auricular, corbata dorada, bíceps).
  tramites  La Trámites: cuadrado gris con ventanilla, sello y el impreso 27-B.
Escenas (guion "modo": "sketch"): gancho | gag | delega | remate | mensaje | cierre. Gancho «POV: …» desde el fotograma 0,
globo con el nombre de quien habla, contador «Veces que se lo ha pasado a la Jupillo: N» que sube, corte de cámara
cada ~2,7 s (zoom de golpe), efectos de sonido al giro (remate) y fotograma final serio (fondo oscuro, frase, cifra y
fuente pequeña, sin música de chiste).
Se usa desde hacer_reel.py: sketch.bind(modulo_hacer_reel) y después preparar()/render_frame()."""
import math, random, re
import numpy as np
from PIL import Image, ImageDraw

hr = None   # módulo hacer_reel (trazo, circulo, fuentes, Subtitulos...); lo enchufa bind()


def bind(modulo):
    global hr
    hr = modulo


NOMBRES = {"jambo": "El Jambo", "jupillo": "La Jupillo", "pelota": "La Pelota", "bola": "El Bola", "tramites": "La Trámites"}
ACENTO = {"jambo": (214, 150, 30), "jupillo": (112, 96, 205), "pelota": (240, 128, 28),
          "bola": (36, 88, 205), "tramites": (58, 150, 108)}
PERSONAJES = tuple(NOMBRES)
SK_SUELO = 1330            # y del suelo de los personajes
SK_SUB_CY = 1445           # banda de subtítulos (por encima de la interfaz de Instagram)
SK_SEG = 2.7               # segundos entre cortes de cámara dentro de una escena
FONDO_SERIO = (22, 24, 29)
# Primer fotograma (Calidad v8.1, B7; 11/11/2026): fondo plano saturado que corta el feed, primer plano de cara en el
# fotograma 0 con zoom-out de golpe y texto gigante de 3-6 palabras. Se apaga con "fondo": false / "primer_plano": false.
FONDOS = {"amarillo": (255, 214, 10), "cian": (30, 205, 235), "rojo": (240, 70, 60), "naranja": (255, 150, 30)}
ACTIVO_SOBRE_FONDO = (200, 20, 60)   # palabra activa del subtítulo sobre fondo saturado (el cian no se lee sobre amarillo)
PP_ZOOM = 2.0       # zoom de la cara en el fotograma 0
PP_DUR = 0.7        # s que tarda en abrirse al plano normal
GC_FIN = 0.95       # s hasta que el texto gigante se ha ido
PIEL = (236, 194, 158)
SUCIO = (120, 96, 70)



def _T(d, pts, rng, w=9, col=None, amp=2.2, cerrado=False):
    return hr.trazo(d, pts, rng, max(1, int(round(w))), col or hr.TINTA, amp, cerrado)


def _Ci(d, cx, cy, r, rng, w=9, relleno=None, col=None, amp=2.0, ry=None):
    return hr.circulo(d, cx, cy, r, rng, max(1, int(round(w))), relleno, col or hr.TINTA, amp, ry)


def _R(d, x0, y0, x1, y1, rng, w=9, relleno=None, col=None, amp=2.0, radio=0):
    return hr.rect_mano(d, x0, y0, x1, y1, rng, max(1, int(round(w))), relleno, col or hr.TINTA, amp, int(radio))


def _E(d, cx, cy, r, rng, col=None, w=6):
    return hr.estrella(d, cx, cy, r, rng, col or hr.CIAN, int(w))


def _c(col, a=255):
    return tuple(col) + (a,)


# ---------------------------------------------------------------- piezas comunes
def _ojo(d, x, y, r, rng, mirada=(0, 0), parp=False, medio=False, col_iris=None, blanco=(255, 255, 255)):
    """Ojo: blanco + pupila. medio = párpado a medias (cansancio); parp = cerrado."""
    if parp:
        d.line([(x - r, y), (x + r, y)], fill=hr.TINTA, width=6)
        return
    d.ellipse([x - r, y - r * 0.85, x + r, y + r * 0.85], fill=blanco, outline=hr.TINTA, width=4)
    px, py = x + mirada[0] * r * 0.35, y + mirada[1] * r * 0.35
    pr = r * 0.42
    d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=col_iris or hr.TINTA)
    d.ellipse([px - pr * 0.35, py - pr * 0.55, px + pr * 0.05, py - pr * 0.15], fill=(255, 255, 255))
    if medio:   # párpado: tapa la mitad de arriba
        d.polygon([(x - r - 2, y - r * 0.9), (x + r + 2, y - r * 0.9), (x + r + 2, y - r * 0.05), (x - r - 2, y - r * 0.05)],
                  fill=medio if isinstance(medio, tuple) else (225, 188, 150))
        d.line([(x - r, y - r * 0.05), (x + r, y - r * 0.05)], fill=hr.TINTA, width=5)


def _boca(d, x, y, w, hv, rng, tipo="sonrisa", interior=(120, 30, 40), col=None):
    """Boca sincronizada: hv = apertura 0-1 de la voz real. Cerrada, tipo: sonrisa | plana | triste | sonrisa_grande."""
    col = col or hr.TINTA
    if hv > 0.08:
        ab = 8 + 40 * hv
        d.ellipse([x - w * (0.55 + 0.25 * hv), y - ab * 0.35, x + w * (0.55 + 0.25 * hv), y + ab * 0.65], fill=interior, outline=col, width=5)
        if ab > 28:
            d.ellipse([x - w * 0.32, y + ab * 0.22, x + w * 0.32, y + ab * 0.6], fill=(220, 110, 120))
        return
    if tipo == "plana":
        _T(d, [(x - w * 0.5, y), (x + w * 0.5, y + 2)], rng, 6, col, 1.0)
    elif tipo == "triste":
        _T(d, [(x - w * 0.5, y + 8), (x, y - 4), (x + w * 0.5, y + 8)], rng, 6, col, 1.0)
    elif tipo == "sonrisa_grande":
        pts = hr.puntos_elipse(x, y - 8, w * 0.65, 22, 14, 0.15, math.pi - 0.15)
        d.polygon(pts, fill=(255, 255, 255))
        _T(d, pts, rng, 6, col, 1.0, cerrado=True)
    else:
        _T(d, [(x - w * 0.5, y - 2), (x - w * 0.15, y + 8), (x + w * 0.5, y - 8)], rng, 6, col, 1.0)


def _brazo(d, p0, p1, p2, rng, col, w=26, mano=None, rm=15, mano_col=PIEL):
    """Brazo de dos tramos (hombro, codo, mano) con manga de color y mano redonda."""
    _T(d, [p0, p1, p2], rng, w + 8, hr.TINTA, 1.2)
    _T(d, [p0, p1, p2], rng, w, col, 0.8)
    _Ci(d, p2[0], p2[1], rm, rng, 6, relleno=mano_col)


def _pierna(d, x0, y0, x1, y1, rng, col, w=36):
    _T(d, [(x0, y0), (x1, y1)], rng, w + 8, hr.TINTA, 1.0)
    _T(d, [(x0, y0), (x1, y1)], rng, w, col, 0.6)


# ---------------------------------------------------------------- El Jambo (humano, desaliñado)
def dibujar_jambo(d, cx, base, t, rng, accion, hv, s=1.0):
    resp = math.sin(t * 2.0)
    bob = 3 * resp
    sacudida = 0.0
    if accion == "desespera":
        sacudida = 7 * math.sin(t * 22)
    # piernas y zapatillas sucias
    pant = (74, 82, 104)
    for sx in (-1, 1):
        _pierna(d, cx + sx * 30 * s, base - 190 * s, cx + sx * 36 * s, base - 36 * s, rng, pant, 38 * s)
        zx, zy = cx + sx * 44 * s, base - 20 * s
        d.ellipse([zx - 52 * s, zy - 22 * s, zx + 46 * s + (20 * s if sx > 0 else 0), zy + 20 * s], fill=(214, 210, 198), outline=hr.TINTA, width=5)
        d.rectangle([zx - 50 * s, zy + 8 * s, zx + 44 * s, zy + 18 * s], fill=(96, 84, 70))
        d.ellipse([zx - 22 * s, zy - 12 * s, zx + 8 * s, zy + 4 * s], fill=(150, 130, 105, 200))      # mancha de mugre
        _T(d, [(zx - 6 * s, zy - 18 * s), (zx + 10 * s, zy - 8 * s), (zx - 2 * s, zy - 2 * s)], rng, 4, hr.TINTA, 1.0)  # cordón suelto
    ty = base - 395 * s + bob
    sh_r = (cx + 82 * s + sacudida, ty + 22 * s)
    sh_l = (cx - 82 * s + sacudida, ty + 22 * s)
    camisa = (174, 166, 122)
    # torso: camiseta arrugada y con manchas
    tors = [(cx - 84 * s + sacudida, ty), (cx + 84 * s + sacudida, ty), (cx + 96 * s, ty + 205 * s), (cx - 96 * s, ty + 205 * s)]
    d.polygon(tors, fill=camisa)
    _T(d, tors, rng, 8, hr.TINTA, 1.6, cerrado=True)
    for (a, b, c2, e) in [(-40, 60, -6, 70), (20, 120, 56, 112), (-62, 150, -22, 160)]:   # arrugas
        _T(d, [(cx + a * s, ty + b * s), (cx + (a + c2) / 2 * s, ty + (b - 10) * s), (cx + c2 * s, ty + e * s)], rng, 4, (120, 112, 78), 1.0)
    d.ellipse([cx + 14 * s, ty + 100 * s, cx + 58 * s, ty + 134 * s], fill=(196, 62, 44, 235))        # mancha de kétchup
    d.ellipse([cx - 66 * s, ty + 150 * s, cx - 20 * s, ty + 178 * s], fill=SUCIO + (210,))             # mancha de grasa
    d.ellipse([cx - 14 * s, ty + 18 * s, cx + 8 * s, ty + 34 * s], fill=(150, 128, 96, 190))
    # brazos que van detrás del torso según la acción
    if accion == "delega":
        osc = 0.4 * math.sin(t * 7)
        _brazo(d, sh_r, (cx + 150 * s, ty + 50 * s), (cx + 235 * s, ty + 28 * s + 26 * osc * s), rng, camisa, 28 * s, rm=17 * s)
        _brazo(d, sh_l, (cx - 110 * s, ty + 100 * s), (cx - 92 * s, ty + 168 * s), rng, camisa, 28 * s, rm=16 * s)
    elif accion == "desespera":
        _brazo(d, sh_r, (cx + 132 * s, ty - 10 * s), (cx + 62 * s + sacudida, ty - 116 * s), rng, camisa, 28 * s, rm=16 * s)
        _brazo(d, sh_l, (cx - 132 * s, ty - 10 * s), (cx - 62 * s + sacudida, ty - 116 * s), rng, camisa, 28 * s, rm=16 * s)
    elif accion == "remata":
        _brazo(d, sh_r, (cx + 138 * s, ty - 30 * s), (cx + 160 * s, ty - 138 * s - 8 * abs(math.sin(t * 6)) * s), rng, camisa, 28 * s, rm=18 * s)
        _brazo(d, sh_l, (cx - 126 * s, ty + 92 * s), (cx - 60 * s, ty + 150 * s), rng, camisa, 28 * s, rm=16 * s)   # mano en la cadera
    elif accion == "presume":
        _brazo(d, sh_r, (cx + 112 * s, ty + 62 * s), (cx + 26 * s, ty + 70 * s), rng, camisa, 28 * s, rm=16 * s)   # mano en el pecho
        _brazo(d, sh_l, (cx - 126 * s, ty + 92 * s), (cx - 60 * s, ty + 150 * s), rng, camisa, 28 * s, rm=16 * s)
    else:
        _brazo(d, sh_r, (cx + 118 * s, ty + 100 * s), (cx + 108 * s, ty + 176 * s), rng, camisa, 28 * s, rm=16 * s)
        _brazo(d, sh_l, (cx - 118 * s, ty + 100 * s), (cx - 108 * s, ty + 176 * s), rng, camisa, 28 * s, rm=16 * s)
    # cabeza
    hx, hy = cx + sacudida * 0.6, ty - 70 * s + (-6 * s if accion == "presume" else 0)
    r = 74 * s
    if accion == "presume":
        pass
    d.rectangle([hx - 22 * s, hy + r * 0.7, hx + 22 * s, ty + 6 * s], fill=PIEL, outline=hr.TINTA, width=5)   # cuello
    _Ci(d, hx, hy, r, rng, 9, relleno=PIEL)
    # barba de varios días (sombra + puntitos)
    pts = hr.puntos_elipse(hx, hy + 6 * s, r * 0.92, r * 0.9, 18, 0.12 * math.pi, 0.88 * math.pi)
    d.polygon(pts + [(hx, hy + 6 * s)], fill=(96, 88, 84, 120))
    rb = random.Random(5)
    for _ in range(46):
        a = rb.uniform(0.15, 0.85) * math.pi; rr = rb.uniform(0.45, 0.92)
        px, py = hx + math.cos(a) * r * rr, hy + 6 * s + math.sin(a) * r * rr * 0.95
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(60, 52, 48))
    # pelo revuelto (mechones desordenados)
    pelo = (62, 46, 38)
    rh = random.Random(11)
    for k in range(11):
        a = math.pi * (1.08 + 0.86 * k / 10) + rh.uniform(-0.08, 0.08)
        largo = rh.uniform(36, 70) * s
        x0, y0 = hx + math.cos(a) * r * 0.9, hy + math.sin(a) * r * 0.9
        _T(d, [(x0, y0), (x0 + math.cos(a + rh.uniform(-0.5, 0.5)) * largo, y0 + math.sin(a) * largo * 0.9 - 6)], rng, int(11 * s), pelo, 2.5)
    _T(d, [(hx - r * 0.8, hy - r * 0.4), (hx - r * 0.3, hy - r * 0.8), (hx + r * 0.5, hy - r * 0.72), (hx + r * 0.85, hy - r * 0.3)], rng, int(14 * s), pelo, 2.0)
    # ojeras y ojos medio cerrados
    parp = ((t + 0.4) % 3.6) < 0.12
    ey = hy - 10 * s
    for sx in (-1, 1):
        ex = hx + sx * 28 * s
        _ojo(d, ex, ey, 15 * s, rng, mirada=(0.3, 0.1), parp=parp, medio=PIEL)
        _T(d, [(ex - 16 * s, ey + 20 * s), (ex, ey + 27 * s), (ex + 16 * s, ey + 20 * s)], rng, 5, (122, 92, 128), 0.8)   # ojera
    _T(d, [(hx - 46 * s, ey - 28 * s), (hx - 12 * s, ey - 34 * s)], rng, 7, pelo, 1.0)                   # cejas desiguales
    _T(d, [(hx + 12 * s, ey - 40 * s), (hx + 46 * s, ey - 26 * s)], rng, 7, pelo, 1.0)
    _T(d, [(hx - 4 * s, ey + 6 * s), (hx + 8 * s, ey + 26 * s), (hx - 6 * s, ey + 30 * s)], rng, 5, (150, 110, 90), 0.8)   # nariz
    tipo = "sonrisa_grande" if accion in ("presume", "remata") else ("triste" if accion == "desespera" else "sonrisa")
    _boca(d, hx, hy + 44 * s, 38 * s, hv, rng, tipo)
    # lineas de peste y mosca
    for i, dx in enumerate((-1, 0, 1)):
        x = hx + dx * 70 * s + 14 * s * math.sin(t * 2 + i)
        pts = [(x + 10 * s * math.sin(k * 1.3 + t * 3 + i), hy - r - 30 * s - k * 16 * s) for k in range(5)]
        if (dx != 0) or accion in ("presume", "remata"):
            _T(d, pts, rng, 5, (128, 160, 64), 1.0)
    fx, fy = hx + 118 * s * math.cos(t * 4.2), hy - 96 * s + 36 * s * math.sin(t * 5.3)
    d.ellipse([fx - 5, fy - 4, fx + 5, fy + 4], fill=hr.TINTA)
    d.ellipse([fx - 9, fy - 9, fx - 1, fy - 3], fill=(210, 220, 230, 220))
    d.ellipse([fx + 1, fy - 9, fx + 9, fy - 3], fill=(210, 220, 230, 220))


# ---------------------------------------------------------------- La Jupillo (IA cansada)
def dibujar_jupillo(d, cx, base, t, rng, accion, hv, s=1.0):
    col = ACENTO["jupillo"]
    oscuro = (76, 64, 150)
    resp = math.sin(t * 1.4)
    cy = base - 205 * s + 3 * resp
    # patitas
    for sx in (-1, 1):
        _R(d, cx + sx * 50 * s - 24 * s, base - 70 * s, cx + sx * 50 * s + 24 * s, base - 14 * s, rng, 7, relleno=oscuro, radio=14 * s)
    # antena caída
    _T(d, [(cx, cy - 138 * s), (cx + 26 * s, cy - 182 * s), (cx + 74 * s, cy - 150 * s + 6 * resp)], rng, 8, hr.TINTA, 1.5)
    _Ci(d, cx + 78 * s, cy - 146 * s, 11 * s, rng, 5, relleno=(150, 150, 170))
    # brazos: taza de café (izq. del personaje) y pila de papeles
    cafe = (cx - 150 * s, cy + 70 * s - 6 * math.sin(t * 2) * s)
    _T(d, [(cx - 92 * s, cy + 30 * s), (cx - 130 * s, cy + 60 * s), cafe], rng, 16, hr.TINTA, 1.0)
    d.rectangle([cafe[0] - 28 * s, cafe[1] - 44 * s, cafe[0] + 28 * s, cafe[1] + 20 * s], fill=(244, 240, 232), outline=hr.TINTA, width=5)
    _T(d, [(cafe[0] + 28 * s, cafe[1] - 30 * s), (cafe[0] + 50 * s, cafe[1] - 18 * s), (cafe[0] + 28 * s, cafe[1] - 2 * s)], rng, 5, hr.TINTA, 0.8)
    for i in range(3):   # vapor
        x = cafe[0] - 14 * s + i * 14 * s
        _T(d, [(x + 4 * math.sin(t * 3 + i + k), cafe[1] - 54 * s - k * 12 * s) for k in range(4)], rng, 4, (160, 160, 170), 0.8)
    pila = (cx + 150 * s, cy + 50 * s)
    _T(d, [(cx + 92 * s, cy + 30 * s), (cx + 130 * s, cy + 52 * s), pila], rng, 16, hr.TINTA, 1.0)
    for i in range(5):
        oy = pila[1] - 8 * s - i * 14 * s
        d.rectangle([pila[0] - 40 * s + (i % 2) * 6 * s, oy - 10 * s, pila[0] + 36 * s + (i % 3) * 5 * s, oy + 4 * s], fill=(250, 250, 246), outline=hr.TINTA, width=3)
    # cuerpo (pastilla)
    pts = hr.puntos_elipse(cx, cy, 108 * s, 136 * s * (1 + 0.01 * resp), 40)
    d.polygon(pts, fill=col)
    _T(d, pts[:-1], rng, 10, hr.TINTA, 2.0, cerrado=True)
    # cara
    ey = cy - 36 * s
    d.rounded_rectangle([cx - 76 * s, ey - 38 * s, cx + 76 * s, ey + 72 * s], radius=int(30 * s), fill=(236, 234, 250), outline=hr.TINTA, width=6)
    parp = ((t + 1.7) % 4.2) < 0.2
    for sx in (-1, 1):
        ex = cx + sx * 36 * s
        _ojo(d, ex, ey + 6 * s, 20 * s, rng, mirada=(0, 0.6), parp=parp, medio=(236, 234, 250))
        d.arc([ex - 22 * s, ey + 18 * s, ex + 22 * s, ey + 50 * s], 20, 160, fill=(96, 72, 150), width=5)   # ojeras
    _T(d, [(cx - 66 * s, ey - 22 * s), (cx - 14 * s, ey - 10 * s)], rng, 6, hr.TINTA, 0.8)      # cejas caídas (resignación)
    _T(d, [(cx + 66 * s, ey - 22 * s), (cx + 14 * s, ey - 10 * s)], rng, 6, hr.TINTA, 0.8)
    _boca(d, cx, ey + 54 * s, 34 * s, hv, rng, "plana" if int(t * 0.5) % 2 == 0 else "triste", col=hr.TINTA)
    # gota de sudor
    gy = ey - 44 * s + 16 * ((t * 0.9) % 1.0) * s
    d.polygon([(cx + 82 * s, gy), (cx + 70 * s, gy + 26 * s), (cx + 94 * s, gy + 26 * s)], fill=(120, 200, 235), outline=hr.TINTA)


# ---------------------------------------------------------------- La Pelota (sabelotodo)
def dibujar_pelota(d, cx, base, t, rng, accion, hv, s=1.0):
    col = ACENTO["pelota"]
    rebote = 16 * abs(math.sin(t * 3.0)) * s if accion != "serio" else 0.0
    cy = base - 150 * s - rebote
    r = 128 * s
    for sx in (-1, 1):   # patas
        _T(d, [(cx + sx * 46 * s, cy + r * 0.85), (cx + sx * 54 * s, base - 14 * s)], rng, 16, hr.TINTA, 1.0)
        d.ellipse([cx + sx * 54 * s - 26 * s, base - 26 * s, cx + sx * 54 * s + 26 * s, base], fill=hr.TINTA)
    # brazos: uno con el dedo en alto
    _brazo(d, (cx + r * 0.92, cy + 10 * s), (cx + r * 1.2, cy - 44 * s), (cx + r * 1.12, cy - 120 * s - 6 * math.sin(t * 6) * s), rng, col, 14 * s, rm=14 * s, mano_col=(255, 255, 255))
    _T(d, [(cx + r * 1.12, cy - 134 * s), (cx + r * 1.12, cy - 168 * s)], rng, 8, hr.TINTA, 0.6)     # dedo índice
    _brazo(d, (cx - r * 0.92, cy + 20 * s), (cx - r * 1.18, cy + 66 * s), (cx - r * 1.0, cy + 112 * s), rng, col, 14 * s, rm=14 * s, mano_col=(255, 255, 255))
    pts = hr.puntos_elipse(cx, cy, r, r, 44)
    d.polygon(pts, fill=col)
    # costuras de la pelota
    _T(d, hr.puntos_elipse(cx - r * 1.05, cy, r * 0.62, r * 1.0, 12, -0.9, 0.9), rng, 5, (150, 70, 10), 1.0)
    _T(d, hr.puntos_elipse(cx + r * 1.05, cy, r * 0.62, r * 1.0, 12, math.pi - 0.9, math.pi + 0.9), rng, 5, (150, 70, 10), 1.0)
    _T(d, [(cx - r * 0.55, cy + r * 0.78), (cx + r * 0.55, cy + r * 0.78)], rng, 5, (150, 70, 10), 1.0)
    _T(d, pts[:-1], rng, 10, hr.TINTA, 2.0, cerrado=True)
    d.ellipse([cx - r * 0.62, cy - r * 0.8, cx - r * 0.18, cy - r * 0.52], fill=(255, 220, 170, 190))      # brillo
    # cara: ojos grandes muy seguros, gafas redondas, sonrisa de listillo
    ey = cy - 18 * s
    parp = ((t + 0.2) % 3.9) < 0.12
    for sx in (-1, 1):
        ex = cx + sx * 44 * s
        _ojo(d, ex, ey, 26 * s, rng, mirada=(0.4 * sx * -1 + 0.2, -0.6), parp=parp)
        _Ci(d, ex, ey, 34 * s, rng, 5, col=hr.TINTA, amp=0.8)                                   # gafas
    _T(d, [(cx - 12 * s, ey), (cx + 12 * s, ey)], rng, 5, hr.TINTA, 0.5)
    _T(d, [(cx - 80 * s, ey - 56 * s), (cx - 24 * s, ey - 68 * s)], rng, 7, hr.TINTA, 1.0)         # ceja arqueada
    _T(d, [(cx + 24 * s, ey - 60 * s), (cx + 80 * s, ey - 52 * s)], rng, 7, hr.TINTA, 1.0)
    _boca(d, cx, cy + 56 * s, 56 * s, hv, rng, "sonrisa_grande")


# ---------------------------------------------------------------- El Bola (coach tóxico)
def dibujar_bola(d, cx, base, t, rng, accion, hv, s=1.0):
    col = ACENTO["bola"]
    oro = (240, 188, 38)
    resp = math.sin(t * 3.4)
    cy = base - 150 * s + 4 * resp - 6 * hv * s
    rx, ry = 150 * s, 128 * s
    for sx in (-1, 1):
        _T(d, [(cx + sx * 58 * s, cy + ry * 0.85), (cx + sx * 66 * s, base - 14 * s)], rng, 18, hr.TINTA, 1.0)
        d.ellipse([cx + sx * 66 * s - 30 * s, base - 28 * s, cx + sx * 66 * s + 34 * s, base], fill=(40, 40, 46))
    # brazo en pose de bíceps (derecha del personaje) y puño al aire (izquierda)
    codo = (cx + rx * 1.12, cy - 10 * s)
    mano = (cx + rx * 0.82, cy - 118 * s - 6 * abs(math.sin(t * 5)) * s)
    _brazo(d, (cx + rx * 0.9, cy + 30 * s), codo, mano, rng, col, 24 * s, rm=18 * s, mano_col=(255, 255, 255))
    _Ci(d, (codo[0] + mano[0]) / 2 + 14 * s, (codo[1] + mano[1]) / 2, 20 * s, rng, 6, relleno=(60, 112, 225))  # bíceps
    _brazo(d, (cx - rx * 0.9, cy + 30 * s), (cx - rx * 1.14, cy - 20 * s), (cx - rx * 1.0, cy - 96 * s - 8 * math.sin(t * 6) * s), rng, col, 24 * s, rm=18 * s, mano_col=(255, 255, 255))
    pts = hr.puntos_elipse(cx, cy, rx, ry, 44)
    d.polygon(pts, fill=col)
    _T(d, pts[:-1], rng, 10, hr.TINTA, 2.0, cerrado=True)
    d.ellipse([cx - rx * 0.7, cy - ry * 0.86, cx - rx * 0.3, cy - ry * 0.6], fill=(150, 190, 255, 160))   # brillo
    # auricular con micro
    _T(d, hr.puntos_elipse(cx, cy - 10 * s, rx * 0.95, ry * 0.95, 14, math.pi * 1.05, math.pi * 1.95), rng, 8, (30, 30, 36), 1.0)
    _T(d, [(cx - rx * 0.86, cy - 6 * s), (cx - rx * 0.78, cy + 52 * s), (cx - 40 * s, cy + 58 * s)], rng, 6, (30, 30, 36), 1.0)
    d.ellipse([cx - 52 * s, cy + 50 * s, cx - 30 * s, cy + 70 * s], fill=(30, 30, 36))
    # gafas de sol
    gy = cy - 22 * s
    _R(d, cx - 110 * s, gy - 28 * s, cx - 12 * s, gy + 30 * s, rng, 6, relleno=(20, 20, 26), radio=14 * s, amp=0.8)
    _R(d, cx + 12 * s, gy - 28 * s, cx + 110 * s, gy + 30 * s, rng, 6, relleno=(20, 20, 26), radio=14 * s, amp=0.8)
    _T(d, [(cx - 12 * s, gy - 8 * s), (cx + 12 * s, gy - 8 * s)], rng, 6, hr.TINTA, 0.5)
    d.line([(cx - 92 * s, gy - 14 * s), (cx - 66 * s, gy - 18 * s)], fill=(255, 255, 255), width=5)
    d.line([(cx + 30 * s, gy - 14 * s), (cx + 56 * s, gy - 18 * s)], fill=(255, 255, 255), width=5)
    # sonrisa de tiburón con dientes
    _boca(d, cx, cy + 56 * s, 84 * s, hv, rng, "sonrisa_grande")
    # corbata dorada y cadena
    d.polygon([(cx - 16 * s, cy + ry * 0.78), (cx + 16 * s, cy + ry * 0.78), (cx + 24 * s, cy + ry * 1.0), (cx, cy + ry * 1.04), (cx - 24 * s, cy + ry * 1.0)], fill=oro, outline=hr.TINTA)
    # destellos de «motivación»
    for i in range(4):
        r2 = random.Random(7 * i + 3)
        ex = cx + r2.uniform(-1, 1) * rx * 1.25; ey = cy - ry - 20 * s - ((t * 55 + i * 40) % 90)
        _E(d, ex, ey, 11 + r2.uniform(0, 6), rng, oro, 5)


# ---------------------------------------------------------------- La Trámites (burócrata con ventanilla)
def dibujar_tramites(d, cx, base, t, rng, accion, hv, s=1.0):
    col = ACENTO["tramites"]
    gris = (170, 174, 182)
    for sx in (-1, 1):
        _R(d, cx + sx * 60 * s - 22 * s, base - 62 * s, cx + sx * 60 * s + 22 * s, base - 10 * s, rng, 7, relleno=(90, 94, 102), radio=10 * s)
    top, bot = base - 372 * s, base - 54 * s
    # cuerpo cuadrado y placa superior
    _R(d, cx - 128 * s, top, cx + 128 * s, bot, rng, 10, relleno=gris, radio=14 * s, amp=1.6)
    _R(d, cx - 96 * s, top - 34 * s, cx + 96 * s, top + 8 * s, rng, 7, relleno=col, radio=8 * s)
    d.text((cx, top - 14 * s), "VENTANILLA 3", font=hr.font(hr.F_DIB_C, int(23 * s)), fill=(255, 255, 255), anchor="mm")
    # ventanilla con cristal y cara detrás
    wx0, wy0, wx1, wy1 = cx - 96 * s, top + 40 * s, cx + 96 * s, top + 168 * s
    _R(d, wx0, wy0, wx1, wy1, rng, 8, relleno=(214, 234, 240), radio=10 * s, amp=1.0)
    parp = ((t + 1.1) % 4.4) < 0.15
    for sx in (-1, 1):
        ex = cx + sx * 36 * s
        _ojo(d, ex, wy0 + 42 * s, 15 * s, rng, mirada=(0.2 * sx, 0.2), parp=parp, medio=(214, 234, 240))
        _Ci(d, ex, wy0 + 42 * s, 22 * s, rng, 4, col=hr.TINTA, amp=0.6)       # gafas
    _T(d, [(cx - 62 * s, wy0 + 14 * s), (cx - 14 * s, wy0 + 20 * s)], rng, 6, hr.TINTA, 0.6)   # cejas serias
    _T(d, [(cx + 62 * s, wy0 + 14 * s), (cx + 14 * s, wy0 + 20 * s)], rng, 6, hr.TINTA, 0.6)
    _boca(d, cx, wy0 + 96 * s, 36 * s, hv, rng, "plana")
    d.line([(wx0 + 14 * s, wy0 + 12 * s), (wx0 + 54 * s, wy0 + 6 * s)], fill=(255, 255, 255), width=6)    # reflejo
    # mostrador con impreso 27-B y sello
    _R(d, cx - 118 * s, wy1 + 10 * s, cx + 118 * s, wy1 + 38 * s, rng, 7, relleno=(150, 112, 78), radio=4 * s)
    d.rectangle([cx - 88 * s, wy1 + 56 * s, cx + 88 * s, wy1 + 150 * s], fill=(252, 252, 246), outline=hr.TINTA, width=4)
    d.text((cx, wy1 + 80 * s), "IMPRESO 27-B", font=hr.font(hr.F_DIB_C, int(24 * s)), fill=hr.TINTA, anchor="mm")
    for k in range(4):
        d.line([(cx - 70 * s, wy1 + 104 * s + k * 14 * s), (cx + 60 * s - (k % 2) * 40 * s, wy1 + 104 * s + k * 14 * s)], fill=(150, 150, 150), width=3)
    # brazo con sello: baja con un golpe cuando habla
    gol = abs(math.sin(t * 3.2)) if hv > 0.08 else 0.0
    sy = wy1 + 20 * s + 24 * gol * s
    _brazo(d, (cx + 126 * s, wy1 + 110 * s), (cx + 182 * s, wy1 + 70 * s), (cx + 138 * s, sy - 26 * s), rng, gris, 20 * s, rm=14 * s, mano_col=(90, 94, 102))
    _R(d, cx + 98 * s, sy - 12 * s, cx + 162 * s, sy + 20 * s, rng, 6, relleno=(180, 50, 50), radio=4 * s)
    if gol > 0.92:
        d.ellipse([cx + 80 * s, sy + 18 * s, cx + 180 * s, sy + 36 * s], fill=(200, 60, 60, 120))


DIBUJAR = {"jambo": dibujar_jambo, "jupillo": dibujar_jupillo, "pelota": dibujar_pelota, "bola": dibujar_bola, "tramites": dibujar_tramites}
ALTURA = {"jambo": 545, "jupillo": 400, "pelota": 330, "bola": 300, "tramites": 410}
ESCALA = {"jambo": 1.42, "jupillo": 1.75, "pelota": 1.8, "bola": 1.7, "tramites": 1.5}   # a 1 personaje por escena (x0,78 si hay dos)   # alto aprox. en px a s=1 (para el globo)


# ---------------------------------------------------------------- escena
def _sin_acentos(x):
    return "".join(c for c in x.lower() if c.isalnum())


def preparar(sc, spec, rng):
    """Datos de una escena sketch: hablante, personajes, subtítulos, rótulos, contador, efectos de sonido, cámara."""
    sc.estilo_d = str(spec.get("estilo") or "gag").strip().lower()
    sc.serio = sc.estilo_d in ("mensaje", "cierre")
    dib = spec.get("dibujo") if isinstance(spec.get("dibujo"), dict) else {}
    ctx = spec.get("_ctx") if isinstance(spec.get("_ctx"), dict) else {}
    sc.ctx = ctx
    pers = [str(p).strip().lower() for p in (dib.get("personajes") or [])]
    sc.pers = [p for p in pers if p in PERSONAJES][:2]
    h = str(spec.get("hablante") or "").strip().lower()
    sc.hablante = h if h in PERSONAJES else None
    if sc.hablante and sc.hablante not in sc.pers and not sc.serio:
        sc.pers = ([sc.hablante] + sc.pers)[:2]
    sc.accion = str(dib.get("accion") or ("remata" if sc.estilo_d == "remate" else "habla")).strip().lower()
    ac = dib.get("acciones") if isinstance(dib.get("acciones"), dict) else {}
    sc.acciones = {str(k).strip().lower(): str(v).strip().lower() for k, v in ac.items()}   # accion de cada personaje (si no, la de la escena para quien habla)
    sc.entran = [p for p in sc.pers if p not in hr.DIB_PREV["pers"]]
    sc.primero = sc.idx == 0 and not sc.serio
    if sc.primero:
        sc.entran = []   # fotograma 0: los personajes YA están en escena (antes entraban deslizándose y el primer fotograma era un decorado vacío)
    fo = ctx.get("fondo", "auto")
    if fo in (False, "no", "ninguno"):
        sc.fondo = None
    elif isinstance(fo, (list, tuple)) and len(fo) == 3:
        sc.fondo = tuple(int(x) for x in fo)
    elif isinstance(fo, str) and fo in FONDOS:
        sc.fondo = FONDOS[fo]
    else:
        sc.fondo = FONDOS["amarillo"]
    hr.DIB_PREV["pers"] = set(sc.pers)
    voz, enf_voz = hr.parsear_enfasis(spec.get("voz") or "")
    texto, _ = hr.parsear_enfasis(spec.get("texto") or "")
    sc.texto = texto.strip()
    dv = float(spec.get("_voz_dur") or 0)
    tiempos = spec.get("_voz_palabras")
    tiempos = [float(x) + 0.12 for x in tiempos] if (tiempos and len(tiempos) == len(voz.split())) else None
    if dv > 0.2:
        wps = len(voz.split()) / max(0.3, dv - 0.1)
    else:
        wps = max(hr.WPS_HUMANO, len(voz.split()) / max(0.3, sc.dur * 0.8))
    estilo_sub = dict(fill=hr.TINTA, stroke=(hr.PAPEL if not sc.fondo else (255, 255, 255)), activo=(hr.CIAN if not sc.fondo else ACTIVO_SOBRE_FONDO),
                      enfasis=hr.TINTA, marca=True, cy=SK_SUB_CY, smax=78, smin=52)
    sc.sub = hr.Subtitulos(voz, wps, 0.12, sc.dur, enfasis=enf_voz, tiempos=tiempos, estilo=estilo_sub) if (voz and not sc.serio) else None
    env = spec.get("_voz_env")
    sc.env = [min(1.0, max(0.0, float(x))) for x in env] if isinstance(env, list) and env else None
    # globo: el nombre de quien habla (y el texto solo si añade algo que no dice la voz)
    sc.globo_nombre = NOMBRES.get(sc.hablante) if (sc.hablante and sc.estilo_d in ("gag", "delega", "gancho")) else None
    extra = ""
    if sc.texto and _sin_acentos(sc.texto) not in (_sin_acentos(voz), _sin_acentos(NOMBRES.get(sc.hablante, "")), ""):
        extra = sc.texto
    sc.cartel = str(spec.get("cartel") or "") or (extra if sc.estilo_d == "remate" else "")   # cartel con el chiste (hora, resultado…)
    sc.efecto = str(dib.get("efecto") or "").strip().lower()      # papeles (avalancha sobre El Jambo) | sello (DENEGADO en la cara)
    sc.efecto_t = float(dib.get("efecto_t", 0.9))                 # segundo en que empieza (negativo = ya hecho al empezar la escena)
    sc.efecto_sin_voz = bool(dib.get("sin_voz"))
    sc.sello_texto = str(dib.get("sello_texto") or "DENEGADO").strip().upper()[:16]   # texto del sello (por defecto DENEGADO)
    sc.globo_texto = "" if sc.estilo_d in ("remate", "gancho") else extra
    # gancho y rótulo fijo arriba: «POV: …» desde el fotograma 0
    gancho = str(ctx.get("gancho") or "").strip()
    sc.gancho = hr.rotulo_dibujo(gancho, grande=(sc.estilo_d == "gancho")) if (gancho and not sc.serio) else None
    # texto gigante del fotograma 0 (3-6 palabras); si el guion no lo trae, las últimas 6 palabras del gancho sin «POV:»
    gc = str(ctx.get("gancho_corto") or "").strip()
    if not gc and gancho:
        pal = re.sub(r"^\s*POV\s*:\s*", "", gancho, flags=re.I).split()
        gc = " ".join(pal[-6:])
    sc.gancho_gigante = gc if (sc.primero and gc and ctx.get("primer_plano", True)) else ""
    # contador «Veces que se lo ha pasado a la Jupillo: N» que sube
    cont = ctx.get("contador") if isinstance(ctx.get("contador"), dict) else {}
    sc.cont_texto = str(cont.get("texto") or "")
    sc.cont_ini = int(ctx.get("cont_ini") or 0)
    sc.cont_fin = int(ctx.get("cont_fin") or 0)
    sc.cont_sube = sc.cont_fin > sc.cont_ini
    # efectos de sonido (los mezcla make_audio): (tipo, t relativo, duración)
    sc.sfx = []
    if (sc.idx > 0 or ctx.get("primer_plano", True)) and not sc.serio: sc.sfx.append(("whoosh", 0.0, 0.22))   # el 0,0 s del reel ya suena (B7: sonido en 0,3 s)
    if sc.entran and not sc.serio: sc.sfx.append(("pop", 0.3, 0.09))
    if sc.primero: sc.sfx.append(("pop", 0.1, 0.09))
    if sc.cont_sube:
        for k in range(sc.cont_fin - sc.cont_ini):
            sc.sfx.append(("tick", 0.7 + k * 0.28, 0.12))
    if sc.efecto and sc.efecto_t >= 0:
        sc.sfx.append(("papeles" if sc.efecto == "papeles" else "thud", sc.efecto_t, 1.1 if sc.efecto == "papeles" else 0.35))
        sc.sfx.append(("sting", sc.efecto_t + (1.0 if sc.efecto == "papeles" else 0.3), 0.9))
    elif sc.estilo_d == "remate":
        sc.sfx.append(("sting", 0.14, 0.9))
    if sc.estilo_d == "gag": sc.sfx.append(("boing", 0.45, 0.25))
    # cámara: cortes cada SK_SEG s con encuadre distinto y zoom de golpe
    rc = random.Random(sc.idx * 17 + 3)
    sc.cam = [(rc.choice([1.0, 1.03, 1.06]), rc.uniform(-18, 18), rc.uniform(-12, 12), rc.choice([1, -1])) for _ in range(int(sc.dur / SK_SEG) + 2)]


def _globo(img, d, x, y_bajo, nombre, texto, col, k):
    """Globo de diálogo con la etiqueta de color del que habla; la cola apunta a (x, y_bajo)."""
    f1 = hr.font(hr.F_DIB, 44)
    f2 = hr.font(hr.F_DIB_C, 40)
    tw = max(d.textlength(nombre, font=f1), d.textlength(texto, font=f2) if texto else 0) + 64
    th = 64 + (52 if texto else 0)
    x0 = max(40, min(hr.W - 40 - tw, x - tw / 2))
    y1 = y_bajo - 34
    y0 = y1 - th
    pop = hr.ease_out_back(k)
    cx0, cy0 = x0 + tw / 2, y1
    s = max(0.05, pop)
    cap = Image.new("RGBA", (hr.W, hr.H), (0, 0, 0, 0)); dc = ImageDraw.Draw(cap, "RGBA")
    rng = random.Random(len(nombre) * 3 + len(texto))
    _R(dc, x0, y0, x0 + tw, y1, rng, 7, relleno=(255, 255, 255), radio=26, amp=1.4)
    dc.polygon([(x - 20, y1 - 3), (x + 20, y1 - 3), (x + 4, y_bajo + 12)], fill=(255, 255, 255))
    _T(dc, [(x - 20, y1), (x + 4, y_bajo + 12), (x + 20, y1)], rng, 7, hr.TINTA, 1.0)
    dc.rounded_rectangle([x0 + 14, y0 + 12, x0 + tw - 14, y0 + 58], radius=18, fill=_c(col))
    dc.text((x0 + tw / 2, y0 + 35), nombre.upper(), font=f1, fill=(255, 255, 255), anchor="mm")
    if texto:
        dc.text((x0 + tw / 2, y0 + 84), texto, font=f2, fill=hr.TINTA, anchor="mm")
    if s < 1.0:
        cap = hr.capa_escala(cap, s, cx0, cy0)
    img.paste(cap, (0, 0), cap)


def _gancho_gigante(img, texto, t):
    """Texto de 3-6 palabras, gigante y en contraste máximo, en el fotograma 0 (entre y=400 y 800, legible en miniatura):
    entra de golpe con rebote, una palabra en rojo (la que va entre «» o la última) y se va entre 0,55 y GC_FIN s."""
    texto = " ".join(texto.upper().split())
    pal = texto.split()
    f, size, lines = hr.wrap_fit(texto, hr.F_DIB, maxw=hr.W - 120, maxlines=2, smax=140, smin=84)
    if len(" ".join(lines).split()) < len(pal) or size < 90:   # no cabe bien en 2 líneas: 3 líneas, sin perder palabras
        f, size, lines = hr.wrap_fit(texto, hr.F_DIB, maxw=hr.W - 120, maxlines=3, smax=140, smin=84)
    lh = int(size * 1.12)
    y0 = 400
    cap = Image.new("RGBA", (hr.W, hr.H), (0, 0, 0, 0)); dc = ImageDraw.Draw(cap, "RGBA")
    # palabra de acento: la primera dentro de «» (o con asterisco); si no hay, la última
    ac = next((i for i, w in enumerate(pal) if "«" in w or "»" in w or "*" in w), len(pal) - 1)
    idx = 0
    for li, ln in enumerate(lines):
        ws = ln.split()
        wtot = dc.textlength(ln, font=f)
        x = (hr.W - wtot) / 2
        for w in ws:
            col = ACTIVO_SOBRE_FONDO if idx == ac else hr.TINTA
            dc.text((x, y0 + 10 + li * lh), w.replace("*", ""), font=f, fill=col + (255,), stroke_width=12, stroke_fill=(255, 255, 255, 255))
            x += dc.textlength(w + " ", font=f)
            idx += 1
    k = min(1.0, t / 0.16)
    s = (0.8 + 0.2 * hr.ease_out_back(k)) if k < 1 else 1.0   # ya a 80 % en el fotograma 0 y rebota hasta 100 %
    alfa = 1.0 if t < 0.55 else max(0.0, 1 - (t - 0.55) / (GC_FIN - 0.55))
    if alfa < 1.0:
        cap.putalpha(cap.getchannel("A").point(lambda v: int(v * alfa)))
    if s != 1.0:
        cap = hr.capa_escala(cap, s, hr.W / 2, y0 + (lh * len(lines)) / 2)
    img.paste(cap, (0, 0), cap)


def _cartel(img, texto, col, t):
    """Cartel del remate (el chiste cruel en una línea: hora, resultado…), cae con rebote."""
    f, size, lines = hr.wrap_fit(texto.upper(), hr.F_DIB_C, maxw=860, maxlines=2, smax=84, smin=48)
    lh = int(size * 1.12)
    w = max(int(ImageDraw.Draw(Image.new("L", (4, 4))).textlength(l, font=f)) for l in lines) + 90
    h = lh * len(lines) + 56
    cap = Image.new("RGBA", (w + 24, h + 24), (0, 0, 0, 0)); dc = ImageDraw.Draw(cap, "RGBA")
    rng = random.Random(len(texto))
    _R(dc, 12, 12, w + 12, h + 12, rng, 9, relleno=_c(col), radio=18, amp=2.0)
    for i, ln in enumerate(lines):
        dc.text(((w + 24) // 2, 12 + 28 + lh * i + lh // 2), ln, font=f, fill=(255, 255, 255), anchor="mm")
    cap = cap.rotate(-3, expand=True, resample=Image.BICUBIC)
    k = hr.ease_out_back(min(1.0, max(0.0, (t - 0.18) / 0.3)))
    if t < 0.18:
        return
    cap = cap.resize((max(1, int(cap.width * max(0.1, k))), max(1, int(cap.height * max(0.1, k)))))
    img.paste(cap, (hr.W // 2 - cap.width // 2, 1170 - cap.height // 2), cap)


def _contador(img, texto, valor, valor_prev, t_cambio, t):
    """Contador fijo bajo el gancho: la cifra salta (rebote) cuando sube."""
    d = ImageDraw.Draw(img, "RGBA")
    f = hr.font(hr.F_DIB_C, 36)
    fn = hr.font(hr.F_DIB, 68)
    y0, y1 = 352, 440
    d.rounded_rectangle([60, y0, hr.W - 60, y1], radius=26, fill=(255, 255, 255, 230), outline=hr.TINTA + (255,), width=5)
    d.text((92, (y0 + y1) / 2), texto.upper() + ":", font=f, fill=hr.TINTA, anchor="lm")
    k = max(0.0, min(1.0, (t - t_cambio) / 0.35)) if t_cambio is not None else 1.0
    esc = 1.0 + 0.55 * math.sin(math.pi * k) if (valor != valor_prev and t_cambio is not None) else 1.0
    num = str(valor)
    nf = hr.font(hr.F_DIB, int(68 * esc))
    d.text((hr.W - 100, (y0 + y1) / 2), num, font=nf, fill=ACENTO["jupillo"], anchor="rm")


def _serio(sc, t):
    """Fotograma final serio: fondo oscuro, frase, fuente pequeña. Sin personajes ni música de chiste."""
    img = Image.new("RGB", (hr.W, hr.H), FONDO_SERIO)
    d = ImageDraw.Draw(img, "RGBA")
    ctx = sc.ctx
    fuente = str(ctx.get("fuente") or "")
    k = hr.ease_out(t / 0.35)
    a = int(255 * k)
    blanco = (244, 242, 236, a)
    if sc.estilo_d == "mensaje":
        f, size, lines = hr.wrap_fit(sc.texto, hr.F_DIB, maxw=hr.W - 180, maxlines=5, smax=92, smin=50)
        lh = int(size * 1.22)
        y = 830 - lh * len(lines) // 2
        d.rectangle([110, y - 56, 110 + 150, y - 46], fill=hr.CIAN + (a,))
        for i, ln in enumerate(lines):
            d.text((hr.W // 2, y + i * lh + lh // 2), ln, font=f, fill=blanco, anchor="mm")
    else:
        # cierre: la frase de antes en pequeño (para que el fotograma se pueda guardar entero) y la petición de enviar
        msg = str(ctx.get("mensaje") or "")
        if msg:
            f, size, lines = hr.wrap_fit(msg, hr.F_DIB_C, maxw=hr.W - 200, maxlines=4, smax=58, smin=40)
            lh = int(size * 1.2)
            for i, ln in enumerate(lines):
                d.text((hr.W // 2, 620 + i * lh), ln, font=f, fill=(244, 242, 236, 190), anchor="mm")
        d.rectangle([hr.W // 2 - 75, 905, hr.W // 2 + 75, 915], fill=hr.CIAN + (255,))
        f, size, lines = hr.wrap_fit(sc.texto, hr.F_DIB, maxw=hr.W - 180, maxlines=3, smax=84, smin=48)
        lh = int(size * 1.2)
        for i, ln in enumerate(lines):
            d.text((hr.W // 2, 1040 + i * lh), ln, font=f, fill=(255, 255, 255, a), anchor="mm")
    if fuente:
        ff = hr.font(hr.F_DIB_C, 31)
        f2, s2, l2 = hr.wrap_fit("Fuente: " + fuente, hr.F_DIB_C, maxw=hr.W - 220, maxlines=3, smax=31, smin=26)
        for i, ln in enumerate(l2):
            d.text((hr.W // 2, 1420 + i * 40), ln, font=f2, fill=(190, 190, 186, int(210 * k)), anchor="mm")
    return img


def _hoja(w, h, ang, cx, cy):
    c, sn = math.cos(ang), math.sin(ang)
    return [(cx + x * c - y * sn, cy + x * sn + y * c) for x, y in ((-w, -h), (w, -h), (w, h), (-w, h))]


def _efecto(img, sc, t, x, sj):
    """Gags visuales sobre El Jambo (fórmula del «robot del diablo»: la máquina responde sin palabras con algo desproporcionado).
    papeles: la pila de la Jupillo le cae encima y lo entierra; sale solo un pulgar. sello: un DENEGADO enorme en la cara."""
    d = ImageDraw.Draw(img, "RGBA")
    te = t - sc.efecto_t
    if te < 0:
        return
    alto = ALTURA["jambo"] * sj
    if sc.efecto == "papeles":
        n = 46
        rr = random.Random(77)
        hojas = []
        for i in range(n):
            lj = rr.uniform(-0.08, 0.08)
            hojas.append((i, i / n * 0.9 + lj, x + rr.uniform(-1, 1) * 150 * sj, SK_SUELO - (i / n) ** 0.85 * alto * 1.12 + rr.uniform(-18, 18),
                          rr.uniform(-0.5, 0.5), rr.uniform(0.7, 1.0)))
        for (i, t0, hx, hy, ang, esc) in sorted(hojas, key=lambda z: z[1]):
            k = (te - t0) / 0.38
            if k <= 0:
                continue
            k = min(1.0, k)
            y = -120 + (hy + 120) * k * k                     # cae con aceleración
            a = ang + (1 - k) * 2.2 * (1 if i % 2 else -1)    # y gira al caer
            w, h = 62 * sj * esc, 82 * sj * esc
            pts = _hoja(w, h, a, hx, y)
            d.polygon(pts, fill=(252, 252, 247, 255), outline=hr.TINTA)
            for q in (-0.45, 0.0, 0.45):
                c_, s_ = math.cos(a), math.sin(a)
                p1 = (hx + (-w * 0.7) * c_ - (h * q) * s_, y + (-w * 0.7) * s_ + (h * q) * c_)
                p2 = (hx + (w * 0.7) * c_ - (h * q) * s_, y + (w * 0.7) * s_ + (h * q) * c_)
                d.line([p1, p2], fill=(160, 160, 165, 255), width=3)
        fin = 0.9 + 0.38
        if te > fin:   # un pulgar asoma entre los papeles
            k = hr.ease_out_back(min(1.0, (te - fin) / 0.35))
            ty = SK_SUELO - alto * 1.12 - 56 * sj * k
            _T(d, [(x + 30 * sj, ty + 60 * sj * k), (x + 30 * sj, ty + 8 * sj)], random.Random(3), 26 * sj, PIEL, 0.6)
            _T(d, [(x + 30 * sj, ty + 14 * sj), (x + 30 * sj, ty - 26 * sj * k)], random.Random(4), 12 * sj, PIEL, 0.4)
            d.ellipse([x + 4 * sj, ty + 4 * sj, x + 58 * sj, ty + 62 * sj], outline=hr.TINTA, width=4)
    elif sc.efecto == "sello":
        k = min(1.0, te / 0.12)
        z = 2.6 - 1.6 * k
        txt = getattr(sc, "sello_texto", "") or "DENEGADO"
        f = hr.font(hr.F_DIB, int(88 * sj * z))
        wtxt = int(d.textlength(txt, font=f))
        cx, cy = x, SK_SUELO - 465 * sj
        cap = Image.new("RGBA", (wtxt + 90, int(150 * sj * z)), (0, 0, 0, 0)); dc = ImageDraw.Draw(cap, "RGBA")
        dc.rounded_rectangle([4, 4, cap.width - 5, cap.height - 5], radius=16, outline=(200, 40, 40, 235), width=10)
        dc.text((cap.width // 2, cap.height // 2), txt, font=f, fill=(200, 40, 40, 235), anchor="mm")
        cap = cap.rotate(-9, expand=True, resample=Image.BICUBIC)
        img.paste(cap, (int(cx - cap.width / 2), int(cy - cap.height / 2)), cap)


def render_frame(fi, sc, noise, rg, seed):
    lf = fi - sc.start
    t = lf / hr.FPS
    if sc.serio:
        img = _serio(sc, t)
        a = np.asarray(img, dtype=np.int16).copy()
        a += noise[fi % 8] // 10   # grano muy suave: la imagen se queda quieta, sin cámara
        np.clip(a, 0, 255, out=a)
        return a.astype(np.uint8)
    img = Image.new("RGB", (hr.W, hr.H), sc.fondo) if sc.fondo else hr.papel_img(seed).copy()
    d = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(seed * 31 + sc.idx * 101 + fi // 4)   # temblor del trazo
    # gancho «POV: …» fijo arriba, desde el fotograma 0
    # Durante el zoom de entrada del fotograma 0 (pp > 0) el rótulo y el contador son HUD: se dibujan DESPUÉS del
    # recorte para que no se corten por arriba (11/11/2026, aviso de Creador: «VECES QUE SE LO HA PASA…»).
    hud_tarde = bool(sc.primero and sc.gancho_gigante and t < PP_DUR)
    def _hud(im):
        if sc.gancho is not None:
            im.paste(sc.gancho, (0, 150), sc.gancho)
        if sc.cont_texto:
            tt = t - 0.7
            n = sc.cont_ini + (max(0, min(sc.cont_fin - sc.cont_ini, int(tt / 0.28) + 1)) if tt >= 0 else 0)
            t_cambio = (0.7 + (n - sc.cont_ini - 1) * 0.28) if n > sc.cont_ini else None
            _contador(im, sc.cont_texto, n, n - 1, t_cambio, t)
    if not hud_tarde:
        _hud(img)
    # personajes
    hv = hr.boca(sc, t)
    n = len(sc.pers)
    mult = 1.0 if n == 1 else 0.72
    xs = {sc.pers[0]: 540} if n == 1 else ({sc.pers[0]: 280, sc.pers[1]: 765} if n == 2 else {})
    for p in sc.pers:
        x = xs[p]
        if p in sc.entran:
            x += (1 - hr.ease_out(t / 0.4)) * (-560 if x < 540 else 560)
        acc = sc.acciones.get(p) or (sc.accion if p == (sc.hablante or sc.pers[0]) else "habla")
        DIBUJAR[p](d, x, SK_SUELO, t, rng, acc, hv if p == sc.hablante else 0.0, ESCALA[p] * mult)
    if sc.efecto:
        _efecto(img, sc, t, xs.get("jambo", 540), ESCALA["jambo"] * mult)
    _T(d, [(110, SK_SUELO + 8), (970, SK_SUELO + 3)], rng, 7, hr.TINTA, 1.5)
    # globo con el nombre de quien habla (+ texto si aporta algo)
    if sc.globo_nombre and sc.hablante in xs:
        x = xs[sc.hablante]
        alto = ALTURA[sc.hablante] * ESCALA[sc.hablante] * mult
        _globo(img, d, x, max(560 if not sc.globo_texto else 610, SK_SUELO - alto - 6), sc.globo_nombre, sc.globo_texto, ACENTO[sc.hablante], min(1.0, t / 0.25))
    if sc.cartel:
        _cartel(img, sc.cartel, ACENTO.get(sc.hablante or "jambo", hr.CIAN), t)
    # subtítulos palabra a palabra
    if sc.sub is not None:
        cp = sc.sub.capa(t)
        if cp:
            timg, ty = cp
            img.paste(timg, (0, ty), timg)
    # cámara: corte cada SK_SEG s (punch-in en cada corte); en el remate zoom de golpe al chiste
    seg = min(len(sc.cam) - 1, int(t / SK_SEG)); z0, dx, dy, sg = sc.cam[seg]
    ts = t - seg * SK_SEG
    z = z0 + 0.012 * sg * ts / SK_SEG
    if sc.idx > 0 or seg > 0:
        z *= 1 + 0.06 * (1 - hr.ease_out(ts / 0.25))
    if sc.estilo_d == "remate" and t > 0.14:
        z *= 1 + 0.16 * hr.ease_out((t - 0.14) / 0.12)
        dx += 10 * math.sin((t - 0.14) * 60) * max(0.0, 1 - (t - 0.14) / 0.4)   # temblor del golpe
    pp = 0.0   # primer plano del fotograma 0: 1 -> 0 en PP_DUR s (zoom-out de golpe sobre la cara de quien habla)
    if sc.primero and sc.gancho_gigante and t < PP_DUR:
        pp = 1 - hr.ease_out(t / PP_DUR)
    zt = z * (1 + (PP_ZOOM - 1) * pp)
    cw, ch = int(hr.W / zt), int(hr.H / zt)
    cx = int((hr.W - cw) / 2 + dx * ts / SK_SEG) if sc.estilo_d != "remate" else int((hr.W - cw) / 2 + dx)
    cy = int((hr.H - ch) / 2 + dy * ts / SK_SEG)
    if pp > 0:
        quien = sc.hablante if sc.hablante in xs else (sc.pers[0] if sc.pers else None)
        if quien:
            alto = ALTURA[quien] * ESCALA[quien] * mult
            hx, hy = xs[quien], SK_SUELO - 0.80 * alto          # centro de la cabeza
            cx = int(cx * (1 - pp) + (hx - 540 / zt) * pp)       # la cabeza queda en (540, 1020) de la pantalla
            cy = int(cy * (1 - pp) + (hy - 1020 / zt) * pp)
    cx = max(0, min(hr.W - cw, cx)); cy = max(0, min(hr.H - ch, cy))
    img = img.crop((cx, cy, cx + cw, cy + ch)).resize((hr.W, hr.H), Image.BILINEAR)
    if hud_tarde:
        _hud(img)
    if sc.primero and sc.gancho_gigante and t < GC_FIN:
        _gancho_gigante(img, sc.gancho_gigante, t)
    a = np.asarray(img, dtype=np.int16).copy()
    a += noise[fi % 8] // 6
    if lf < 2 and sc.idx > 0: a -= 10   # micro parpadeo en el corte (nunca en el fotograma 0: B7)
    np.clip(a, 0, 255, out=a)
    return a.astype(np.uint8)


def sfx(tipo, dur, rg, lp_fft):
    """Efectos de sonido propios del sketch (tick del contador, sting del remate, boing del gag). None si no es de aquí."""
    dur = max(0.03, float(dur)); m = int(dur * SR_); tt = np.arange(m) / SR_
    if tipo in ("thud", "papeles", "tick", "sting", "boing") and False:
        return None
    if tipo == "tick":
        return (np.sin(2 * np.pi * 1760 * tt) * np.exp(-tt * 38) + 0.5 * np.sin(2 * np.pi * 880 * tt) * np.exp(-tt * 30)) * 0.26
    if tipo == "sting":   # «uah-uah»: trombón triste (cae el tono), dos notas
        out = np.zeros(m)
        for k, (f0, f1, a0, a1) in enumerate(((330, 300, 0.0, 0.32), (300, 190, 0.34, dur))):
            i0, i1 = int(a0 * SR_), min(m, int(a1 * SR_))
            if i1 <= i0: continue
            n = i1 - i0; u = np.arange(n) / SR_
            f = np.linspace(f0, f1, n)
            ph = 2 * np.pi * np.cumsum(f) / SR_
            saw = 2 * ((ph / (2 * np.pi)) % 1.0) - 1.0
            sig = lp_fft(saw, 1100, 2) * np.minimum(1.0, u / 0.03) * np.exp(-u * (2.2 if k == 0 else 3.0))
            out[i0:i1] += sig * (0.30 if k == 0 else 0.34)
        return out
    if tipo == "thud":   # golpe sordo (sello / caída)
        f = 70 + 140 * np.exp(-tt * 28)
        return (np.sin(2 * np.pi * np.cumsum(f) / SR_) * np.exp(-tt * 9) + 0.5 * lp_fft(rg.standard_normal(m), 900, 2) * np.exp(-tt * 40)) * 0.55
    if tipo == "papeles":   # avalancha de hojas: ráfagas de ruido que se espesan y un golpe sordo al final
        out = np.zeros(m)
        for k in range(40):
            i0 = int((0.05 + 0.75 * k / 40 + rg.uniform(-0.01, 0.01)) * SR_); mm = min(int(rg.uniform(0.03, 0.07) * SR_), m - i0)
            if mm <= 8 or i0 < 0: continue
            u = np.arange(mm) / SR_
            out[i0:i0 + mm] += (lp_fft(rg.standard_normal(mm), 7000, 2) - lp_fft(rg.standard_normal(mm), 1800, 2)) * np.exp(-u * 60) * rg.uniform(0.2, 0.5)
        return out * 0.5
    if tipo == "boing":
        f = 260 + 220 * np.exp(-tt * 18) * np.sin(2 * np.pi * 9 * tt)
        return np.sin(2 * np.pi * np.cumsum(f) / SR_) * np.exp(-tt * 11) * 0.20
    return None


SR_ = 44100
