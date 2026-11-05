#!/usr/bin/env python3
"""Locución con Kyutai Pocket TTS (código MIT, pesos CC BY 4.0: uso comercial con atribución).

Uso: python3 voz_pocket.py lote.json
  lote.json = {"idioma": "spanish", "voz": "lola", "temperatura": 0.3, "ganancia": 1.0,
               "frases": [{"texto": "...", "salida": "/ruta/voz0.wav"}, ...]}

Carga el modelo UNA vez y genera todas las frases (WAV mono 16 bits a la frecuencia del modelo, 24 kHz).
Escribe en stdout un JSON con los tiempos. Sale con código != 0 si algo falla: publicar_gh.py usa entonces Piper.

Voz «lola»: estado precalculado de kyutai/pocket-tts-without-voice-cloning (CC BY 4.0), hecho a partir de un
clip de Mozilla Common Voice en español (CC0). No se clona la voz de ninguna persona.
"""
import json
import sys
import time
import wave

import numpy as np


def main():
    lote = json.load(open(sys.argv[1], encoding="utf-8"))
    t0 = time.time()
    from pocket_tts import TTSModel  # import tardío: si falta el paquete, falla aquí y se usa Piper

    kw = {"language": lote.get("idioma", "spanish")}
    if lote.get("temperatura") is not None:
        kw["temp"] = float(lote["temperatura"])
    modelo = TTSModel.load_model(**kw)
    estado = modelo.get_state_for_audio_prompt(lote.get("voz", "lola"))
    carga = time.time() - t0
    sr = int(modelo.sample_rate)
    ganancia = float(lote.get("ganancia", 1.0))
    tiempos = []
    for f in lote["frases"]:
        t1 = time.time()
        audio = modelo.generate_audio(estado, f["texto"])
        x = audio.detach().cpu().numpy().astype(np.float32).reshape(-1)
        if x.size < sr * 0.2 or not np.isfinite(x).all():
            raise SystemExit(f"Pocket TTS devolvió audio vacío o inválido para: {f['texto'][:60]}")
        x = np.clip(x * ganancia, -1.0, 1.0)
        with wave.open(f["salida"], "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes((x * 32767).astype("<i2").tobytes())
        tiempos.append(round(time.time() - t1, 2))
    print(json.dumps({"carga_s": round(carga, 1), "frases_s": tiempos, "total_s": round(time.time() - t0, 1),
                      "sample_rate": sr}))


if __name__ == "__main__":
    main()
