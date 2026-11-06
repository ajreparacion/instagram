#!/usr/bin/env python3
"""Locución con Kokoro-82M (Apache 2.0: uso comercial sin atribución obligatoria). Rápido en CPU.

Uso: python3 voz_kokoro.py lote.json
  lote.json = {"voz": "em_alex" | "ef_dora" | "em_santa", "velocidad": 0.95, "ganancia": 1.0,
               "frases": [{"texto": "...", "salida": "/ruta/voz0.wav"}, ...]}

Voces españolas del modelo hexgrad/Kokoro-82M (lang_code "e"): ef_dora (mujer), em_alex y em_santa (hombres).
Son voces del propio modelo, no clonadas de nadie. El G2P del español lo hace espeak-ng (misaki).
Si una frase sale en varios trozos, se unen con 120 ms de silencio. WAV mono 16 bits a 24 kHz.
Código de salida != 0 si algo falla: publicar_gh.py pasa al motor de respaldo.
"""
import json
import sys
import time
import wave

import numpy as np


def a_numpy(a):
    try:
        a = a.detach().cpu().numpy()
    except AttributeError:
        a = np.asarray(a)
    return a.astype(np.float32).reshape(-1)


def main():
    lote = json.load(open(sys.argv[1], encoding="utf-8"))
    t0 = time.time()
    from kokoro import KPipeline  # import tardío: si falta el paquete, falla aquí y se usa el respaldo

    pipeline = KPipeline(lang_code="e", repo_id="hexgrad/Kokoro-82M")
    voz = str(lote.get("voz") or "em_alex")
    velocidad = float(lote.get("velocidad", 1.0))
    ganancia = float(lote.get("ganancia", 1.0))
    sr = 24000
    carga = time.time() - t0
    tiempos = []
    hueco = np.zeros(int(sr * 0.12), np.float32)
    for f in lote["frases"]:
        t1 = time.time()
        trozos = []
        vel = float(f["velocidad"]) if f.get("velocidad") is not None else velocidad   # ajuste por frase (por_estilo)
        for _gs, _ps, audio in pipeline(f["texto"], voice=voz, speed=vel):
            if audio is None:
                continue
            x = a_numpy(audio)
            if x.size:
                trozos.append(x)
                trozos.append(hueco)
        if not trozos:
            raise SystemExit(f"Kokoro no devolvió audio para: {f['texto'][:60]}")
        x = np.concatenate(trozos[:-1])
        if x.size < sr * 0.2 or not np.isfinite(x).all():
            raise SystemExit(f"Kokoro devolvió audio vacío o inválido para: {f['texto'][:60]}")
        x = np.clip(x * ganancia, -1.0, 1.0)
        with wave.open(f["salida"], "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes((x * 32767).astype("<i2").tobytes())
        tiempos.append(round(time.time() - t1, 2))
    print(json.dumps({"voz": voz, "carga_s": round(carga, 1), "frases_s": tiempos,
                      "total_s": round(time.time() - t0, 1), "sample_rate": sr}))


if __name__ == "__main__":
    main()
