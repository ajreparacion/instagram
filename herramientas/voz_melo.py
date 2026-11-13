#!/usr/bin/env python3
"""Locución con MeloTTS (MyShell, MIT: uso comercial sin atribución obligatoria), español de España. Voz genérica del modelo,
no clonada de nadie. Sale a 44,1 kHz (la frecuencia del modelo) y NO se remuestrea aquí.

Uso: python3 voz_melo.py lote.json     (se ejecuta con el python del venv de Melo: PYTHON_MELO)
  lote.json = {"idioma": "ES", "speaker": "ES", "velocidad": 1.15, "ganancia": 1.0,
               "pronunciacion": {"Neogest Lab": "Neogés Lab"}, "semilla": 7,
               "sdp_ratio": 0.2, "noise_scale": 0.6, "noise_scale_w": 0.8,   # opcionales; también por frase   # solo cambia el texto que va al modelo, no los subtítulos
               "frases": [{"texto": "...", "salida": "/ruta/voz0.wav", "velocidad": 1.2}, ...]}
Escribe en stdout un JSON con tiempos y la frecuencia. Código de salida != 0 si algo falla: publicar_gh.py pasa al respaldo.
"""
import json, re, sys, time, wave
import numpy as np


def pronunciar(texto, dic):
    """Sustituye palabras o frases (sin distinguir mayúsculas, en palabra completa) por su grafía de pronunciación."""
    for k in sorted((dic or {}), key=len, reverse=True):
        texto = re.sub(r"(?<![\wáéíóúüñ])" + re.escape(k) + r"(?![\wáéíóúüñ])", str(dic[k]), texto, flags=re.IGNORECASE)
    return texto


def main():
    comprobar = sys.argv[1] == "--comprobar"
    lote = {} if comprobar else json.load(open(sys.argv[1], encoding="utf-8"))
    t0 = time.time()
    try:
        from melo.api import TTS
    except Exception:   # solo necesitamos ES: el módulo japonés exige el diccionario unidic (~500 MB); se sustituye por uno vacío
        import types
        for k in [k for k in sys.modules if k == "melo" or k.startswith("melo.")]:
            del sys.modules[k]
        sys.modules["melo.text.japanese"] = types.ModuleType("melo.text.japanese")
        from melo.api import TTS
    if comprobar:
        print("MeloTTS OK"); return
    m = TTS(language=str(lote.get("idioma") or "ES"), device="cpu")
    spk = m.hps.data.spk2id[str(lote.get("speaker") or "ES")]
    sr = int(m.hps.data.sampling_rate)
    vel0 = float(lote.get("velocidad", 1.0))
    gan = float(lote.get("ganancia", 1.0))
    carga = time.time() - t0
    for f in lote["frases"]:
        vel = float(f["velocidad"]) if f.get("velocidad") is not None else vel0
        txt = pronunciar(f["texto"], lote.get("pronunciacion"))
        if lote.get("semilla") is not None:   # misma semilla = misma salida (Melo es estocástico): comparaciones y reels repetibles
            import torch
            torch.manual_seed(int(lote["semilla"]))
        g = lambda k, d: float(f[k]) if f.get(k) is not None else float(lote.get(k, d))
        x = m.tts_to_file(txt, spk, None, sdp_ratio=g("sdp_ratio", 0.2), noise_scale=g("noise_scale", 0.6),
                          noise_scale_w=g("noise_scale_w", 0.8), speed=vel, quiet=True)
        x = np.asarray(x, np.float32).reshape(-1)
        if x.size < sr * 0.2 or not np.isfinite(x).all():
            raise SystemExit(f"Melo devolvió audio vacío o inválido para: {f['texto'][:60]}")
        x = np.clip(x * gan, -1.0, 1.0)
        with wave.open(f["salida"], "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
            w.writeframes((x * 32767).astype(np.int16).tobytes())
    print(json.dumps({"modelo_usado": "MeloTTS " + str(lote.get("idioma") or "ES"), "sr": sr, "carga_s": round(carga, 1),
                      "total_s": round(time.time() - t0, 1)}))


if __name__ == "__main__":
    main()
