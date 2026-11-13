#!/usr/bin/env python3
"""Audición de voces v2 (13/11/2026, queja del dueño: voz «telefónica» y «con acento chino»). Misma frase con cada candidato
(voces genéricas con licencia o servicios oficiales; NADIE clonado, ni el dueño). Cada salida pasa por la `cadena_voz` de
equipo/voz.json y por loudnorm a -14 LUFS, MP3 192 kbps a 48 kHz. Un candidato que falla no para a los demás.

Uso (workflow audicion_voces_v2.yml):  python3 herramientas/audicion_voces_v2.py <grupo>
Grupos: melo, kokoro, piper, chatterbox, edge. Sale en /tmp/a2/salida/audicion2_<letra>_<motor>_<voz>.mp3
"""
import asyncio, json, os, subprocess, sys, wave
import numpy as np

FRASE = "Hola, soy de Neogest Lab. Con Ajota Sistema llevas tu negocio al día, sin papeles y sin Éxcel. ¿Te lo enseño en un minuto?"
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
RAW, SAL = "/tmp/a2/raw", "/tmp/a2/salida"
CADENA = None   # si no es None, sustituye a la cadena_voz de voz.json (pruebas de cadena)


def sh(cmd, **k):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **k)


def postprocesar(entrada, nombre):
    """48 kHz mono, pico a -6 dBFS, cadena_voz actual, loudnorm 2 pasadas a -14 LUFS / -1,5 dBTP, MP3 192 kbps 48 kHz."""
    cadena = (CADENA if CADENA is not None else json.load(open(os.path.join(RAIZ, "equipo", "voz.json"), encoding="utf-8")).get("cadena_voz", "")).strip().strip(",")
    w48 = f"{RAW}/{nombre}_48.wav"
    sh(["ffmpeg", "-v", "error", "-y", "-i", entrada, "-ar", "48000", "-ac", "1", w48])
    vd = subprocess.run(["ffmpeg", "-v", "info", "-i", w48, "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True).stderr
    pico = float([l for l in vd.splitlines() if "max_volume" in l][-1].split(":")[1].split()[0])
    pre = f"volume={-6 - pico:.2f}dB" + ("," + cadena if cadena else "")
    ln = "loudnorm=I=-14:TP=-1.5:LRA=11"
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", w48, "-af", pre + "," + ln + ":print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
    ln2 = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
           f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    os.makedirs(SAL, exist_ok=True)
    sh(["ffmpeg", "-v", "error", "-y", "-i", w48, "-af", pre + "," + ln2 + ",aresample=48000", "-ar", "48000", "-ac", "1",
        "-c:a", "libmp3lame", "-b:a", "192k", f"{SAL}/{nombre}.mp3"])
    print("HECHA", nombre, flush=True)


def escribir_wav(x, sr, ruta):
    x = np.clip(np.asarray(x, np.float32).reshape(-1), -1, 1)
    with wave.open(ruta, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def intentar(nombre, f):
    try:
        f()
    except Exception as e:
        print("FALLO", nombre, repr(e)[-400:], flush=True)


def melo():
    from melo.api import TTS
    m = TTS(language="ES", device="cpu")
    spk = m.hps.data.spk2id
    print("MeloTTS speakers:", dict(spk), "sr", m.hps.data.sampling_rate, flush=True)
    for k in spk.keys():
        def uno(k=k):
            ruta = f"{RAW}/a_melo_{k}.wav"
            m.tts_to_file(FRASE, spk[k], ruta, speed=1.0)
            postprocesar(ruta, f"audicion2_a_melo_{k.lower()}")
        intentar(f"melo_{k}", uno)


def kokoro():
    for voz in ("em_alex", "ef_dora", "em_santa"):
        def uno(voz=voz):
            ruta = f"{RAW}/b_kokoro_{voz}.wav"
            lote = {"voz": voz, "velocidad": 0.95, "ganancia": 1.0, "frases": [{"texto": FRASE, "salida": ruta}]}
            j = f"{RAW}/b_{voz}.json"
            json.dump(lote, open(j, "w"), ensure_ascii=False)
            sh([sys.executable, os.path.join(AQUI, "voz_kokoro.py"), j])
            postprocesar(ruta, f"audicion2_b_kokoro_{voz}")
        intentar(f"kokoro_{voz}", uno)


def piper():
    base = "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES"
    for voz, ruta_hf in (("davefx-medium", "davefx/medium/es_ES-davefx-medium"), ("sharvard-medium", "sharvard/medium/es_ES-sharvard-medium"),
                         ("carlfm-x_low", "carlfm/x_low/es_ES-carlfm-x_low")):
        def uno(voz=voz, ruta_hf=ruta_hf):
            modelo = f"{RAW}/{voz}.onnx"
            for ext, dest in ((".onnx", modelo), (".onnx.json", modelo + ".json")):
                sh(["curl", "-fsSL", "-o", dest, f"{base}/{ruta_hf}{ext}"])
            carpeta = ruta_hf.rsplit("/", 1)[0]
            subprocess.run(["curl", "-fsSL", "-o", f"{SAL}/MODEL_CARD_piper_{voz}.txt", f"{base}/{carpeta}/MODEL_CARD"])
            ruta = f"{RAW}/c_piper_{voz}.wav"
            subprocess.run([sys.executable, "-m", "piper", "-m", modelo, "-f", ruta], input=FRASE, text=True, check=True, capture_output=True)
            postprocesar(ruta, f"audicion2_c_piper_{voz}")
        intentar(f"piper_{voz}", uno)


def chatterbox():
    ruta = f"{RAW}/d_chatterbox_mtl_es.wav"
    lote = {"modelo": "multilingue", "idioma": "es", "exageracion": 0.4, "cfg": 0.5, "temperatura": 0.65, "referencia": None,
            "semilla": 7, "theta": "", "frases": [{"texto": FRASE, "salida": ruta}]}
    j = f"{RAW}/d.json"
    json.dump(lote, open(j, "w"), ensure_ascii=False)
    def uno():
        out = sh([sys.executable, os.path.join(AQUI, "voz_chatterbox.py"), j])
        print(out.stdout[-500:], flush=True)
        postprocesar(ruta, "audicion2_d_chatterbox_multilingue-es")
    intentar("chatterbox", uno)


def edge():
    import edge_tts
    voces = asyncio.run(edge_tts.list_voices())
    es = [v for v in voces if v["ShortName"].startswith("es-ES")]
    print("es-ES:", [(v["ShortName"], v.get("Gender")) for v in es], flush=True)
    elegidas = ["es-ES-AlvaroNeural", "es-ES-ElviraNeural"] + [v["ShortName"] for v in es if "Multilingual" in v["ShortName"]]
    for voz in elegidas:
        def uno(voz=voz):
            ruta = f"{RAW}/e_edge_{voz}.mp3"
            asyncio.run(edge_tts.Communicate(FRASE, voz).save(ruta))
            print(voz, sh(["ffprobe", "-v", "error", "-show_entries", "stream=sample_rate,bit_rate", "-of", "csv=p=0", ruta]).stdout.strip(), flush=True)
            postprocesar(ruta, "audicion2_e_edge_" + voz.replace("es-ES-", "").replace("Neural", "").lower())
        intentar(f"edge_{voz}", uno)


GRUPOS = {"melo": melo, "kokoro": kokoro, "piper": piper, "chatterbox": chatterbox, "edge": edge}

if __name__ == "__main__":
    os.makedirs(RAW, exist_ok=True); os.makedirs(SAL, exist_ok=True)
    g = sys.argv[1]
    intentar(g, GRUPOS[g])
    print("ficheros:", sorted(os.listdir(SAL)))
