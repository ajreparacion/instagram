#!/usr/bin/env python3
"""Transcribe con faster-whisper (small, es) los MP3 de una carpeta y anota si dice «Ajota» y «Éxcel». Uso: transcribir_audicion.py carpeta salida.json"""
import json, os, sys, unicodedata
from faster_whisper import WhisperModel

def n(t):
    return "".join(c for c in unicodedata.normalize("NFD", t.lower()) if unicodedata.category(c) != "Mn")

m = WhisperModel("small", device="cpu", compute_type="int8")
res = {}
for f in sorted(os.listdir(sys.argv[1])):
    if not f.endswith(".mp3"):
        continue
    segs, _ = m.transcribe(os.path.join(sys.argv[1], f), language="es", beam_size=5)
    t = " ".join(s.text.strip() for s in segs)
    tn = n(t)
    res[f] = {"texto": t, "ajota": "ajota" in tn, "excel": "excel" in tn}
    print(f, res[f], flush=True)
json.dump(res, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
