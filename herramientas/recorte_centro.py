#!/usr/bin/env python3
"""Recorte de una GRABACION REAL del Centro de Contenido Apps para la plantilla "modo":"app" + "plantilla": true.

Uso: python3 recorte_centro.py recorte.json salida.mp4

Para apps sin demo publica ni sesion de prueba (Gestion Integral 7D, MEDICATOR) el Creador no puede grabar con
grabar_pantalla.py. El Centro ya tiene esas apps grabadas de verdad, funcionando con datos de ejemplo
(entidad VideoMezcla, campo "video": /videos/pistas/<slug>-<formato>-video.mp4). Este script NO toca esos mp4: lee la
pista, se queda SOLO con la pantalla del movil (sin los rotulos ni los subtitulos del Centro), ordena los tramos que
pide el guion y los pega en el mismo marco de movil sobre fondo plano que usa grabar_pantalla.py, con zoom suave en los
tramos quietos. Sale un video vertical 1080x1920 sin sonido para usar como "video": "demo.mp4" del guion.
Nada se inventa: cada fotograma es la app real tal y como la grabo el Centro.

recorte.json:
 {"origen": "https://.../videos/pistas/...-video.mp4 (o ruta local)", "fondo": "#DCEBFA", "marco": "oscuro",
  "pantalla_origen": [190, 203, 700, 1512],      (x, y, ancho, alto de la pantalla del movil dentro del video del Centro)
  "segmentos": [{"inicio": 35.2, "fin": 38.2,    (segundos de la pista del Centro)
                 "y": 220,                        (desplazamiento vertical de la ventana dentro de la pantalla; la ventana
                                                   tiene el ancho de la pantalla y la proporcion del movil de la plantilla)
                 "zoom": [1.0, 1.1],              (opcional: nivel al empezar y al acabar el tramo)
                 "foco": [0.5, 0.45],             (opcional: centro del zoom, 0-1 dentro de la ventana)
                 "dur": 2.6}]}                    (opcional: duracion de salida; si es mayor que fin-inicio se queda el ultimo
                                                   fotograma y el zoom sigue: empuje suave sobre una pantalla quieta)"""
import sys, os, json, subprocess, shutil, tempfile, urllib.request
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grabar_pantalla import W, H, FFMPEG, DISPOSITIVOS, fondo_dispositivo, _rr_mask, hex_rgb, ease

FPS = 30


def main():
    if len(sys.argv) < 3: sys.exit(__doc__)
    ruta, salida = sys.argv[1], sys.argv[2]
    spec = json.load(open(ruta, encoding="utf-8"))
    origen = str(spec["origen"])
    tmp = None
    if origen.startswith("http"):
        tmp = tempfile.mkdtemp(prefix="recorte_")
        local = os.path.join(tmp, "pista.mp4")
        with urllib.request.urlopen(origen, timeout=120) as r, open(local, "wb") as f: shutil.copyfileobj(r, f)
    else:
        local = origen if os.path.isabs(origen) else os.path.join(os.path.dirname(os.path.abspath(ruta)), origen)
    disp = DISPOSITIVOS["movil"]
    sx, sy, sw, sh = disp["pantalla"]
    ox, oy, ow, oh = [int(v) for v in spec.get("pantalla_origen") or (190, 203, 700, 1512)]
    vh = int(round(ow * sh / sw)) // 2 * 2          # alto de la ventana con la proporcion del movil de la plantilla
    base = fondo_dispositivo("movil", disp, hex_rgb(spec.get("fondo")), str(spec.get("marco") or "oscuro"))
    mascara = _rr_mask((sw, sh), disp["radio_p"])
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H), "-r", str(FPS),
           "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", salida]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    total = 0; t_out = 0.0
    for s in spec["segmentos"]:
        a, b = float(s["inicio"]), float(s["fin"])
        y = max(0, min(oh - vh, int(s.get("y", 0))))
        z0, z1 = [float(v) for v in (s.get("zoom") or (1.0, 1.0))]
        fx, fy = [float(v) for v in (s.get("foco") or (0.5, 0.5))]
        n = int(round(max(b - a, float(s.get("dur", 0))) * FPS)); tam = ow * vh * 3   # "dur" > fin-inicio: congela el ultimo fotograma
        dec = subprocess.Popen([FFMPEG, "-loglevel", "error", "-ss", "%.3f" % a, "-t", "%.3f" % (b - a + 0.2), "-i", local,
                                "-vf", "crop=%d:%d:%d:%d,fps=%d" % (ow, vh, ox, oy + y, FPS),
                                "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        ultimo = None
        for i in range(n):
            buf = dec.stdout.read(tam)
            if len(buf) == tam: ultimo = Image.frombuffer("RGB", (ow, vh), buf, "raw", "RGB", 0, 1)
            if ultimo is None: sys.exit("la pista no tiene fotogramas en %.1f-%.1f s" % (a, b))
            z = z0 + (z1 - z0) * ease(i / max(1, n - 1))
            cw, ch = ow / z, vh / z
            cx = min(max(fx * ow, cw / 2), ow - cw / 2); cy = min(max(fy * vh, ch / 2), vh - ch / 2)
            scr = ultimo.resize((sw, sh), Image.LANCZOS, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2))
            img = base.copy(); img.paste(scr, (sx, sy), mascara)
            pr.stdin.write(np.asarray(img, dtype=np.uint8).tobytes())
        dec.stdout.close(); dec.kill(); dec.wait()
        print("tramo %.1f-%.1f s del Centro -> %.2f-%.2f s" % (a, b, t_out, t_out + n / FPS))
        t_out += n / FPS; total += n
    pr.stdin.close()
    if pr.wait() != 0: sys.exit("ffmpeg fallo")
    if tmp: shutil.rmtree(tmp, ignore_errors=True)
    print("OK %s (%d fotogramas, %.1f s)" % (salida, total, total / FPS))


if __name__ == "__main__":
    main()
