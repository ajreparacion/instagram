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
