#!/usr/bin/env python3
"""Alineación palabra a palabra de la voz generada con su guion (faster-whisper, CPU).

Uso: python3 alinear_voz.py lote.json
  lote.json = {"modelo": "small", "frases": [{"wav": "/ruta/voz0.wav", "texto": "lo que dice la voz"}, ...]}
Escribe en stdout un JSON: {"frases": [[[inicio, fin], ...] | null, ...], "modelo": "small", "segundos": 12.3}
  (una lista por frase con el (inicio, fin) en segundos de CADA palabra del texto del guion, en orden; null si la
  frase no se ha podido alinear con confianza y hay que usar la estimación).

Para qué sirve (6/11/2026, petición del usuario: «falta gancho y énfasis»): con los tiempos reales los subtítulos
van clavados a la voz y las palabras marcadas con *énfasis* se pueden subir de volumen justo cuando suenan.
Cómo: Whisper transcribe con marcas de tiempo por palabra; sus palabras se casan con las del guion con difflib
(las cifras que Whisper escribe en dígitos frente a «mil ochocientos…» se reparten en el mismo tramo).
Código de salida != 0 si falta faster-whisper o falla el modelo: publicar_gh.py sigue sin alineación.
"""
import difflib
import json
import re
import subprocess
import sys
import time
import unicodedata

import numpy as np


def normal(w):
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9ñ]+", "", w)


def audio16k(ruta):
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", ruta, "-vn", "-ac", "1", "-ar", "16000",
                        "-f", "f32le", "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype=np.float32).copy()


def casar(guion, oidas, dur):
    """guion: lista de palabras del guion; oidas: [(palabra, ini, fin)] de Whisper. Devuelve [(ini, fin)] por
    palabra del guion, o None si casan menos de la mitad."""
    g = [normal(w) for w in guion]
    o = [normal(w) for w, _, _ in oidas]
    sm = difflib.SequenceMatcher(a=g, b=o, autojunk=False)
    res = [None] * len(g)
    iguales = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                res[i1 + k] = (oidas[j1 + k][1], oidas[j1 + k][2])
            iguales += i2 - i1
        elif tag == "replace" and j2 > j1:
            # p. ej. «mil ochocientos setenta y dos» ↔ «1872»: se reparten las palabras del guion en el tramo oído
            t0, t1 = oidas[j1][1], oidas[j2 - 1][2]
            n = i2 - i1
            for k in range(n):
                res[i1 + k] = (t0 + (t1 - t0) * k / n, t0 + (t1 - t0) * (k + 1) / n)
            iguales += min(n, j2 - j1) * 0.5
        # delete (palabras del guion que Whisper no oyó) e insert (palabras de más) se resuelven abajo
    if iguales < 0.5 * len(g):
        return None
    # huecos: se interpolan entre el final de la anterior y el principio de la siguiente con tiempos
    i = 0
    while i < len(res):
        if res[i] is not None:
            i += 1; continue
        j = i
        while j < len(res) and res[j] is None: j += 1
        t0 = res[i - 1][1] if i > 0 else 0.0
        t1 = res[j][0] if j < len(res) else dur
        if t1 <= t0: t1 = min(dur, t0 + 0.25 * (j - i))
        n = j - i
        for k in range(n):
            res[i + k] = (t0 + (t1 - t0) * k / n, t0 + (t1 - t0) * (k + 1) / n)
        i = j
    # monotonía y límites
    out = []
    prev = 0.0
    for a, b in res:
        a = max(prev, min(float(a), dur)); b = max(a + 0.02, min(float(b), dur))
        out.append([round(a, 3), round(b, 3)]); prev = a
    return out


def main():
    lote = json.load(open(sys.argv[1], encoding="utf-8"))
    t0 = time.time()
    from faster_whisper import WhisperModel  # import tardío: si falta, código != 0 y se sigue sin alineación
    nombre = str(lote.get("modelo") or "small")
    modelo = WhisperModel(nombre, device="cpu", compute_type="int8")
    salida = []
    for f in lote["frases"]:
        try:
            y = audio16k(f["wav"])
            dur = len(y) / 16000.0
            segs, _ = modelo.transcribe(y, language="es", beam_size=2, word_timestamps=True, vad_filter=False,
                                        initial_prompt=f["texto"][:200], condition_on_previous_text=False)
            oidas = [(w.word.strip(), float(w.start), float(w.end)) for s in segs for w in (s.words or []) if w.word.strip()]
            salida.append(casar(f["texto"].split(), oidas, dur) if oidas else None)
        except Exception as e:
            print("frase sin alinear:", str(e)[-120:], file=sys.stderr)
            salida.append(None)
    print(json.dumps({"frases": salida, "modelo": nombre, "segundos": round(time.time() - t0, 1)}))


if __name__ == "__main__":
    main()
