#!/usr/bin/env python3
"""Conversión de timbre con OpenVoice V2 (MyShell, licencia MIT: uso comercial permitido; pesos MIT).

Uso (en su propio entorno virtual): python conv_openvoice.py lote.json
  lote.json = {"referencia": "voz_dueno/referencia_usuario.wav", "tau": 0.3,
               "pares": [{"entrada": "/ruta/base.wav", "salida": "/ruta/convertida.wav"}, ...]}
Toma la voz de cada «entrada» (con su acento y su entonación) y le pone el timbre de la «referencia» (la voz del
dueño). El acento y las pausas son los de la entrada: por eso se usa con un TTS que sí hace la «c/z» de España.
Si falta algún módulo del paquete, lo instala y reintenta (OpenVoice arrastra dependencias de chino, japonés, etc.).
Código de salida != 0 si algo falla.
"""
import json
import os
import re
import subprocess
import sys
import time


def importar_openvoice():
    for _ in range(14):
        try:
            from openvoice.api import ToneColorConverter  # noqa: F401
            return ToneColorConverter
        except ModuleNotFoundError as e:
            mod = (e.name or "").split(".")[0]
            if not mod or mod == "openvoice":
                raise
            pip = {"pypinyin": "pypinyin", "cn2an": "cn2an", "jieba": "jieba", "eng_to_ipa": "eng_to_ipa",
                   "inflect": "inflect", "unidecode": "unidecode", "langid": "langid", "pydub": "pydub",
                   "wavmark": "wavmark", "whisper_timestamped": "whisper-timestamped", "g2p_en": "g2p_en",
                   "num2words": "num2words", "anyascii": "anyascii", "jamo": "jamo", "pykakasi": "pykakasi",
                   "fugashi": "fugashi", "cutlet": "cutlet", "mecab": "mecab-python3", "ko_pron": "ko_pron",
                   "indic_transliteration": "indic_transliteration", "gruut": "gruut",
                   "konlpy": "konlpy", "dtw": "dtw-python", "tqdm": "tqdm", "scipy": "scipy",
                   "unidic_lite": "unidic-lite", "librosa": "librosa", "soundfile": "soundfile",
                   "numba": "numba", "pyopenjtalk": "pyopenjtalk"}.get(mod, mod)
            print(f"[openvoice] falta {mod}; pip install {pip}", flush=True)
            r = subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", pip], capture_output=True, text=True)
            if r.returncode != 0:
                print(f"[openvoice] no se pudo instalar {pip}: {r.stderr[-200:]}", flush=True)
                raise
    raise SystemExit("OpenVoice: demasiados módulos que faltan")


def main():
    lote = json.load(open(sys.argv[1], encoding="utf-8"))
    t0 = time.time()
    import torch
    torch.set_num_threads(max(1, os.cpu_count() or 1))
    from huggingface_hub import snapshot_download
    raiz = snapshot_download("myshell-ai/OpenVoiceV2", allow_patterns=["converter/*"])
    cfg = os.path.join(raiz, "converter", "config.json")
    ckpt = os.path.join(raiz, "converter", "checkpoint.pth")
    TCC = importar_openvoice()
    try:
        conv = TCC(cfg, device="cpu", enable_watermark=False)
    except TypeError:
        conv = TCC(cfg, device="cpu")
    conv.load_ckpt(ckpt)
    carga = time.time() - t0
    tgt = conv.extract_se([lote["referencia"]])
    tau = float(lote.get("tau", 0.3))
    tiempos = []
    for p in lote["pares"]:
        t1 = time.time()
        src = conv.extract_se([p["entrada"]])
        conv.convert(audio_src_path=p["entrada"], src_se=src, tgt_se=tgt, output_path=p["salida"], tau=tau,
                     message="")
        if not os.path.exists(p["salida"]) or os.path.getsize(p["salida"]) < 4000:
            raise SystemExit(f"OpenVoice no generó {p['salida']}")
        tiempos.append(round(time.time() - t1, 2))
    print(json.dumps({"carga_s": round(carga, 1), "pares_s": tiempos, "total_s": round(time.time() - t0, 1),
                      "tau": tau}), flush=True)


if __name__ == "__main__":
    main()
