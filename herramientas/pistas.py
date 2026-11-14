#!/usr/bin/env python3
"""Biblioteca de pistas SIN DERECHOS (carpeta musica/ del repo) para meterlas en el video como musica base.
10/11/2026 (orden del dueno: «pon musica de librerias sin derechos»).

Reglas:
- Solo se usan los ficheros de musica/ que figuren en musica/pistas.json con su licencia (CC0, Pixabay Content License,
  Uppbeat, YouTube Audio Library, etc.). Sin ficha = no se usa (queda constancia de donde sale cada pista).
- musica/pistas.json: [{"archivo": "x.mp3", "titulo": "...", "autor": "...", "licencia": "CC0|Pixabay|CC-BY 4.0|...",
  "url": "pagina de origen", "atribucion": "texto a poner en el post (solo si la licencia lo exige)", "bpm": 120 (opcional),
  "salto_s": 0.0 (opcional: segundo donde empieza el primer golpe)}]
- El pulso (bpm y fase) se detecta solo con la envolvente de onsets si la ficha no lo trae.
API: hay_pistas(), elegir(nombre) -> ficha, segmento(ficha, n, sr, cortes, total) -> (L, R, info)."""
import hashlib
import json
import os
import subprocess

import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.environ.get("MUSICA_DIR") or os.path.join(BASE, "musica")
EXT = (".mp3", ".wav", ".ogg", ".m4a", ".flac", ".opus")
# 14/11/2026 (directiva de vídeo): pistas de Kevin MacLeod (incompetech.com, CC BY 4.0). La ficha puede traer "descarga" (URL):
# si el archivo no está en musica/, se baja una vez a la caché (no se commitea el mp3). Sin red = esa pista no se usa.
CACHE = os.environ.get("MUSICA_CACHE") or os.path.join(os.path.expanduser("~"), ".cache", "musica_incompetech")


def _ruta(f):
    """Ruta local de la pista de la ficha f (musica/ o caché; la baja de f["descarga"] si falta). None si no se puede."""
    a = f.get("archivo", "")
    for d in (DIR, CACHE):
        r = os.path.join(d, a)
        if os.path.exists(r) and os.path.getsize(r) > 50000:
            return r
    url = f.get("descarga")
    if not url:
        return None
    try:
        import urllib.request
        os.makedirs(CACHE, exist_ok=True)
        r = os.path.join(CACHE, a)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp, open(r + ".tmp", "wb") as out:
            out.write(resp.read())
        if os.path.getsize(r + ".tmp") < 50000:
            raise ValueError("descarga demasiado pequena")
        os.replace(r + ".tmp", r)
        return r
    except Exception as e:
        print("pista %s no disponible (%s)" % (a, str(e)[:120]))
        return None


def fichas():
    try:
        datos = json.load(open(os.path.join(DIR, "pistas.json"), encoding="utf-8"))
    except Exception:
        return []
    salida = []
    for f in datos if isinstance(datos, list) else []:
        a = f.get("archivo", "")
        if a.lower().endswith(EXT) and f.get("licencia") and _ruta(f):
            salida.append(f)
    return salida


def hay_pistas():
    return bool(fichas())


def elegir(nombre):
    fs = sorted(fichas(), key=lambda f: f["archivo"])
    if not fs:
        return None
    return fs[int(hashlib.md5(nombre.encode()).hexdigest(), 16) % len(fs)]


def _cargar(ruta, sr):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", ruta, "-ac", "2", "-ar", str(sr), "-f", "f32le", "-"],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype=np.float32).reshape(-1, 2).astype(np.float64)


def pulso(x, sr):
    """(bpm, fase_s) por autocorrelacion de la envolvente de onsets (70-170 bpm) y suma de fases."""
    mono = x.mean(axis=1)
    salto = 512
    nf = (len(mono) - 2048) // salto
    if nf < 100:
        return 120.0, 0.0
    ventana = np.hanning(2048)
    mag = np.abs(np.array([np.fft.rfft(mono[i * salto:i * salto + 2048] * ventana) for i in range(nf)]))
    flujo = np.maximum(0, np.diff(np.log1p(mag * 20), axis=0)).sum(axis=1)
    flujo = flujo - np.convolve(flujo, np.ones(43) / 43, mode="same")
    flujo = np.maximum(flujo, 0)
    fps = sr / salto
    ac = np.correlate(flujo, flujo, "full")[len(flujo) - 1:]
    lo, hi = int(fps * 60 / 170), int(fps * 60 / 75)
    mejor, bpm = -1.0, 120.0
    for k in range(lo, hi):
        sc = ac[k] + 0.5 * (ac[2 * k] if 2 * k < len(ac) else 0) + 0.25 * (ac[4 * k] if 4 * k < len(ac) else 0)
        b = 60 * fps / k
        sc *= np.exp(-0.5 * ((np.log2(b / 118.0)) / 0.45) ** 2)    # prior suave hacia 100-140 bpm
        if sc > mejor:
            mejor, bpm = sc, b
    per = fps * 60 / bpm
    fases = [flujo[int(f)::max(1, int(round(per)))].sum() for f in np.arange(0, per, 1.0)]
    fase = float(np.argmax(fases)) / fps
    return float(bpm), fase


def segmento(ficha, n, sr, cortes=None, total=None):
    """n muestras de la pista (L, R en [-1, 1]), empezando en un golpe y con el primer corte (si lo hay) cerca de otro."""
    x = _cargar(_ruta(ficha), sr)
    if ficha.get("bpm"):
        bpm, fase = float(ficha["bpm"]), float(ficha.get("salto_s", 0.0))
    else:
        bpm, fase = pulso(x, sr)
    beat = 60.0 / bpm
    dur = n / sr
    # arranque: el primer golpe al principio (se salta la intro suave si la pista es larga y hay sitio)
    ini = fase
    if len(x) / sr > dur + 40:
        ini = fase + beat * 4 * 4          # 4 compases dentro (ya con el bajo y la bateria)
    if ini * sr + n > len(x):              # pista corta: se repite entera
        x = np.tile(x, (int(np.ceil((ini * sr + n) / len(x))) + 1, 1))
    seg = x[int(ini * sr):int(ini * sr) + n]
    pk = max(1e-9, float(np.abs(seg).max()))
    seg = seg / pk * 0.9
    f_in, f_out = int(0.3 * sr), int(min(1.2, dur * 0.2) * sr)   # directiva 14/11: entrada 0,3 s, salida 1,2 s
    seg[:f_in] *= np.linspace(0, 1, f_in)[:, None]
    seg[-f_out:] *= np.linspace(1, 0, f_out)[:, None]
    return seg[:, 0], seg[:, 1], dict(motor="pistas", archivo=ficha["archivo"], titulo=ficha.get("titulo"), autor=ficha.get("autor"),
                                      licencia=ficha.get("licencia"), bpm=round(bpm, 1), fase_ms=round(fase * 1000))
