#!/usr/bin/env python3
"""Remezcla los vídeos del Centro con la cadena de voz nueva y los mete en las colas de atrasos — orden del dueño 12/11/2026.

«La voz suena con eco, lejana y enlatada; mete un compresor» + «a publicar en todas las redes; en Facebook se pueden subir reels
de forma masiva». Para cada vídeo del Centro (videos/pistas/manifest.json) toma sus pistas separadas (vídeo, voz, música), pasa la
voz por equipo/voz.json → cadena_voz, baja la música bajo la voz (sidechain), masteriza a -14 LUFS y sube el mp4 a la release
«centro-v3». Después añade a atrasos/facebook.json (verticales ≤ 90 s, como reel) y atrasos/youtube.json (todos; los horizontales
como vídeo largo) las piezas que aún no estén, con su texto. Uso (en Actions, con GH_TOKEN): python3 herramientas/remezclar_centro.py
"""
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CENTRO = "https://centro-de-contenido-apps-2f0a3cd6.base44.app"
RELEASE = "centro-v3"
REPO = os.environ.get("GITHUB_REPOSITORY", "ajreparacion/instagram")
CIERRE = "Pide tu prueba gratuita: sin tarjeta, sin datos bancarios y sin compromiso."
SEGUIR = "👉 Sigue a Neogest Lab para ver una pieza nueva cada día."

# Textos: solo funciones ya verificadas (hechos_verificados / directiva). Gancho en la primera línea.
TEXTOS = {
    "gestion-integral-7d": ("¿Sigues pasando presupuestos y facturas a mano? 🧾",
                            "Gestión Integral 7D une presupuesto, pedido, albarán y factura: cada paso hereda líneas, IVA y retención.\n"
                            "Facturas en PDF con tus datos fiscales y enlace de pago."),
    "gestion-integral-7d-corto": ("¿Sigues pasando presupuestos y facturas a mano? 🧾",
                                  "Gestión Integral 7D une presupuesto, pedido, albarán y factura sin volver a teclear."),
    "aj-sistema": ("Toda la gestión de un taller en una sola app 🔧",
                   "Órdenes de trabajo, clientes y presupuestos en el mismo sitio. Capturas de la demo con datos de ejemplo."),
    "medicator": ("¿Ya te tomaste la pastilla o no? 💊",
                  "MEDICATOR organiza pastillas y citas médicas con letra grande, pensada para mayores y para quien los cuida.\n"
                  "Organiza; no sustituye a tu médico ni a tu farmacéutico."),
    "studio-beats-pro": ("¿Tienes letras pero no tienes estudio? 🎤",
                         "Studio Beats PRO: eliges estilo y sale la base, grabas tu voz encima y la terminas en un clic. Está en fase de pruebas."),
    "gps-andaluz": ("El GPS que te habla con gracia andaluza 🧭", "GPS Andaluz, de Neogest Lab."),
    "aj-reparacion-web": ("Así es una web a medida hecha por Neogest Lab 💻",
                          "Ejemplo real: ajreparacion.com. ¿Quieres la tuya? Te hacemos una maqueta gratis, sin compromiso."),
}


def sh(*a, check=True):
    r = subprocess.run(a, capture_output=True, text=True)
    if check and r.returncode:
        raise RuntimeError(f"{a[0]} falló: {r.stderr[-400:]}")
    return r


def huella(t):
    return hashlib.sha1(re.sub(r"\W+", " ", t.lower()).strip()[:400].encode()).hexdigest()[:16]


def texto(slug, canal):
    base = slug if slug in TEXTOS else slug.split("-corto")[0]
    gancho, cuerpo = TEXTOS.get(base, (slug, ""))
    app = base.replace("-corto", "")
    enlace = f"{CENTRO}/solicitar?app={app}&src={canal}"
    if app == "aj-reparacion-web":
        cierre = f"Pide tu maqueta gratis: {CENTRO}/solicitar?src={canal}"
    else:
        cierre = f"{CIERRE}\n{enlace}"
    return f"{gancho}\n{cuerpo}\n\n{cierre}\n\n{SEGUIR}\nBy Neogest Lab"


def main():
    cadena = json.load(open(os.path.join(RAIZ, "equipo", "voz.json")))["cadena_voz"].strip().strip(",")
    man = json.load(urllib.request.urlopen(CENTRO + "/videos/pistas/manifest.json"))["videos"]
    trabajo = "/tmp/remezcla"
    os.makedirs(trabajo, exist_ok=True)
    if sh("gh", "release", "view", RELEASE, "-R", REPO, check=False).returncode:
        sh("gh", "release", "create", RELEASE, "-R", REPO, "-t", "Vídeos del Centro con voz nueva (v3)",
           "-n", "Remezclas automáticas con la cadena de voz de equipo/voz.json (12/11/2026).")
    hechos = []
    for v in man:
        if v["formato"] not in ("vertical", "reel", "horizontal"):
            continue
        n = f"{v['slug']}-{v['formato']}"
        rutas = {}
        for k in ("video", "voz", "musica"):
            rutas[k] = os.path.join(trabajo, f"{n}-{k}{os.path.splitext(v[k])[1]}")
            urllib.request.urlretrieve(CENTRO + v[k], rutas[k])
        salida = os.path.join(trabajo, f"{n}-v3.mp4")
        fc = (f"[1:a]aresample=48000,{cadena},asplit=2[vx][key];"
              f"[2:a]aresample=48000,volume=0.9[m];[m][key]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350:makeup=1[md];"
              f"[md][vx]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
        sh("ffmpeg", "-v", "error", "-y", "-i", rutas["video"], "-i", rutas["voz"], "-i", rutas["musica"], "-filter_complex", fc,
           "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest",
           "-movflags", "+faststart", salida)
        sh("gh", "release", "upload", RELEASE, salida, "--clobber", "-R", REPO)
        url = f"https://github.com/{REPO}/releases/download/{RELEASE}/{os.path.basename(salida)}"
        hechos.append({"slug": v["slug"], "formato": v["formato"], "duracion": v["duracion"], "url": url})
        print("remezclado:", n, flush=True)
    for canal in ("facebook", "youtube"):
        ruta = os.path.join(RAIZ, "atrasos", f"{canal}.json")
        cola = json.load(open(ruta, encoding="utf-8"))
        # las piezas del Centro anteriores (voz vieja) que no se han publicado se sustituyen por las nuevas
        cola["piezas"] = [p for p in cola["piezas"] if not (p.get("tipo") == "video_centro" and p.get("estado") != "publicado")]
        ya = {p["id"] for p in cola["piezas"]}
        for h in hechos:
            vertical = h["formato"] in ("vertical", "reel")
            if canal == "facebook" and not (vertical and h["duracion"] <= 90):
                continue
            pid = f"centro_{h['slug']}_{h['formato']}_v3"
            if pid in ya:
                continue
            t = texto(h["slug"], canal)
            cola["piezas"].append({"id": pid, "tipo": "video_centro", "nota": 90, "retencion": 0.0,
                                   "app": h["slug"], "url_mp4": h["url"], "duracion": h["duracion"], "texto": t,
                                   "largo": (not vertical) or h["duracion"] > 59, "huella": huella(t + h["formato"]),
                                   "estado": "pendiente"})
        json.dump(cola, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(canal, "pendientes:", sum(1 for p in cola["piezas"] if p.get("estado") == "pendiente"))


if __name__ == "__main__":
    main()
