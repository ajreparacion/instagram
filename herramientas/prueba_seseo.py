#!/usr/bin/env python3
"""Prueba de SESEO (la lanza .github/workflows/prueba_seseo.yml, a mano). No publica nada.

Compara formas de tener la voz del dueño con «c/z» de España (θ), sin seseo:
  cb_actual     Chatterbox es-es con la voz del dueño (lo que hay en producción) = control con seseo.
  cb_griego     lo mismo, escribiendo θ (letra griega) donde España dice θ.
  cb_theta      lo mismo, pero el texto se escribe con «th» donde España dice θ (hace→hathe, gracias→grathias).
  kokoro        Kokoro em_alex (espeak-ng «es» = castellano) tal cual.
  kokoro_ov     Kokoro → OpenVoice V2 (timbre del dueño).
  piper         Piper davefx (voz de España, robótica) = control positivo de θ.
  piper_ov      Piper → OpenVoice V2 (timbre del dueño).
Mide en cada una: θ en palabras con c/z (reconocedor de fonemas wav2vec2-espeak sobre 8 palabras sueltas),
parecido con el dueño (Resemblyzer, coseno), palabras mal reconocidas (Whisper small, WER) y variación de tono.
Salida: equipo/pruebas/prueba_seseo.json y, en /tmp/prueba_seseo/salida/, mp3 con las frases (voz_<variante>.mp3)
y con las palabras sueltas (palabras_<variante>.mp3) para subirlos a la release «pruebas».
"""
import json
import os
import re
import shutil
import subprocess
import sys
import time
import unicodedata

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = "/tmp/prueba_seseo"
SALIDA = os.path.join(DIR, "salida")
INFORME = os.path.join(BASE, "equipo", "pruebas", "prueba_seseo.json")
REF = os.path.join(BASE, "voz_dueno", "referencia_usuario.wav")
REF_LARGA = os.path.join(BASE, "voz_dueno", "referencia_usuario_larga.wav")
PY_CB = os.environ.get("PYTHON_CHATTERBOX") or ""
PY_OV = os.environ.get("PYTHON_OPENVOICE") or ""
CACHE = os.path.expanduser("~/.cache/expedientes")

FRASES = [
    "¿Sabías que puedes hacer un resumen de cien correos en cinco minutos?",
    "Gracias a la inteligencia artificial, esto ya no cuesta nada.",
    "Pídele a Claude que ordene tus facturas y te diga cuáles hay que pagar hoy.",
    "Cerveza, zapatos, azúcar… da igual lo que busques: lo encuentra al instante.",
    "Y lo mejor: no necesitas saber programar, solo escribir con calma lo que quieres.",
    "Comenta la palabra CLAUDE y te mando la guía completa.",
]
# palabra → número de «θ» esperadas
PALABRAS = {"hace": 1, "gracias": 1, "cerveza": 2, "zapato": 1, "cielo": 1, "plaza": 1, "cinco": 1, "azúcar": 1}
PORTADOR = "Mira, {}."


def a_theta(t, modo="th"):
    """Escribe de otra forma lo que en España suena θ (c ante e/i y z), para modelos que sesean.
    modo "th": con «th» (hace → hathe). Medido el 7/11: WER 15 %, «gratias», «terveta»: no vale.
    modo "griego": con la letra griega θ (hace → haθe); el tokenizador multilingüe de Chatterbox incluye el griego."""
    t1, t2 = ("th", "Th") if modo == "th" else ("θ", "Θ")
    if modo == "griego_sin_inicial":   # el 7/11 se oyó «cerveza» → «terveza», «cinco» → «tinco»: la c inicial se deja
        t = re.sub(r"(?<=[\wáéíóúñ])c(?=[eiéí])", t1, t)
        t = re.sub(r"(?<=[\wáéíóúñ])C(?=[eiéí])", t2, t)
    else:
        t = re.sub(r"c(?=[eiéí])", t1, t)
        t = re.sub(r"C(?=[eiéí])", t2, t)
    t = t.replace("z", t1).replace("Z", t2)
    return t


def normal(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9ñ ]+", " ", t).split()


def wer(ref, hip):
    r, h = normal(ref), normal(hip)
    d = list(range(len(h) + 1))
    for i in range(1, len(r) + 1):
        prev, d[0] = d[0], i
        for j in range(1, len(h) + 1):
            cur = d[j]
            d[j] = min(d[j] + 1, d[j - 1] + 1, prev + (r[i - 1] != h[j - 1]))
            prev = cur
    return round(d[len(h)] / max(len(r), 1), 3)


def audio16k(ruta):
    import numpy as np
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", ruta, "-vn", "-ac", "1", "-ar", "16000",
                        "-f", "f32le", "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype=np.float32).copy()


def concatenar(wavs, destino, extra=()):
    lista = destino + ".txt"
    with open(lista, "w") as f:
        for w in wavs:
            f.write(f"file '{w}'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista,
                    "-ar", "22050", "-ac", "1", *extra, destino], check=True)


def correr(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise RuntimeError(f"{os.path.basename(cmd[1] if len(cmd) > 1 else cmd[0])} falló: {(r.stderr or r.stdout)[-400:]}")
    return r.stdout


# ------------------------------------------------------------------ motores
def textos_prueba():
    return list(FRASES) + [PORTADOR.format(p) for p in PALABRAS]


def nombres_wav(carpeta):
    return ([os.path.join(carpeta, f"s{i}.wav") for i in range(len(FRASES))],
            [os.path.join(carpeta, f"p{i}.wav") for i in range(len(PALABRAS))])


TEXTO_REFERENCIA = ("A ver, te cuento una cosa que me pasó el otro día. Estaba en casa, tranquilo, y de repente… "
                    "oigo un ruido en la cocina. Nada, pensé. Pero no. Ojo, que esto se pone bueno.")


def referencia_kokoro_sintetica():
    """Referencia SINTÉTICA (Kokoro em_alex, Apache 2.0; no es ninguna persona real) para Chatterbox."""
    destino = os.path.join(DIR, "ref_kokoro_em_alex.wav")
    if not os.path.exists(destino):
        lote = {"voz": "em_alex", "velocidad": 1.0, "ganancia": 1.0, "frases": [{"texto": TEXTO_REFERENCIA, "salida": destino}]}
        ruta = os.path.join(DIR, "lote_ref.json")
        json.dump(lote, open(ruta, "w"), ensure_ascii=False)
        correr([sys.executable, os.path.join(BASE, "herramientas", "voz_kokoro.py"), ruta], timeout=900)
    return destino


def sintetizar_chatterbox(carpeta, theta, ref=None):
    """theta: False | "th" | "griego" (ver a_theta). ref: wav de referencia (por defecto REF, la del dueño: ya no se usa)."""
    if not PY_CB:
        raise RuntimeError("sin entorno de Chatterbox (PYTHON_CHATTERBOX)")
    sw, pw = nombres_wav(carpeta)
    textos = textos_prueba()
    if theta:
        textos = [a_theta(t, "th" if theta is True else theta) for t in textos]
    lote = {"modelo": "es-es", "idioma": "es", "exageracion": 0.65, "cfg": 0.45, "temperatura": 0.65,
            "referencia": ref or REF, "ganancia": 1.0, "semilla": 7,
            "frases": [{"texto": t, "salida": s} for t, s in zip(textos, sw + pw)]}
    ruta = os.path.join(carpeta, "lote.json")
    json.dump(lote, open(ruta, "w"), ensure_ascii=False)
    out = correr([PY_CB, os.path.join(BASE, "herramientas", "voz_chatterbox.py"), ruta], timeout=3000)
    return json.loads(out.strip().splitlines()[-1]), textos


def sintetizar_kokoro(carpeta):
    sw, pw = nombres_wav(carpeta)
    lote = {"voz": "em_alex", "velocidad": 0.95, "ganancia": 1.0,
            "frases": [{"texto": t, "salida": s} for t, s in zip(textos_prueba(), sw + pw)]}
    ruta = os.path.join(carpeta, "lote.json")
    json.dump(lote, open(ruta, "w"), ensure_ascii=False)
    out = correr([sys.executable, os.path.join(BASE, "herramientas", "voz_kokoro.py"), ruta], timeout=900)
    return json.loads(out.strip().splitlines()[-1]), textos_prueba()


PIPER_URLS = ["https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_x86_64.tar.gz",
              "https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz"]
VOZ_RAIZ = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/"
PIPER_MODELO = "es/es_ES/davefx/medium/es_ES-davefx-medium"


def sintetizar_piper(carpeta, noise_scale="0.667", noise_w="0.8", length="1.05"):
    piper = os.path.join(CACHE, "piper", "piper")
    if not os.path.exists(piper):
        os.makedirs(CACHE, exist_ok=True)
        for url in PIPER_URLS:
            if subprocess.run(["curl", "-sSL", "-f", "-o", os.path.join(CACHE, "piper.tar.gz"), url]).returncode == 0:
                subprocess.run(["tar", "xzf", os.path.join(CACHE, "piper.tar.gz"), "-C", CACHE], check=True)
                break
    modelo = os.path.join(CACHE, "voces", os.path.basename(PIPER_MODELO) + ".onnx")
    if not os.path.exists(modelo):
        os.makedirs(os.path.dirname(modelo), exist_ok=True)
        for ext in (".onnx.json", ".onnx"):
            subprocess.run(["curl", "-sSL", "-f", "-o", modelo.replace(".onnx", "") + ext, VOZ_RAIZ + PIPER_MODELO + ext],
                           check=True)
    sw, pw = nombres_wav(carpeta)
    t0 = time.time()
    for t, s in zip(textos_prueba(), sw + pw):
        r = subprocess.run([piper, "--model", modelo, "--output_file", s, "--length_scale", length,
                            "--noise_scale", noise_scale, "--noise_w", noise_w], input=t.encode(),
                           cwd=os.path.dirname(piper), capture_output=True, timeout=180)
        if r.returncode != 0:
            raise RuntimeError("Piper falló: " + r.stderr.decode(errors="replace")[-300:])
    return {"total_s": round(time.time() - t0, 1)}, textos_prueba()


def convertir_openvoice(origen, destino):
    """Copia las wav de `origen` a `destino` con el timbre del dueño (OpenVoice V2)."""
    if not PY_OV:
        raise RuntimeError("sin entorno de OpenVoice (PYTHON_OPENVOICE)")
    os.makedirs(destino, exist_ok=True)
    sw, pw = nombres_wav(origen)
    sd, pd = nombres_wav(destino)
    lote = {"referencia": REF, "tau": 0.3, "pares": [{"entrada": a, "salida": b} for a, b in zip(sw + pw, sd + pd)]}
    ruta = os.path.join(destino, "lote_ov.json")
    json.dump(lote, open(ruta, "w"))
    out = correr([PY_OV, os.path.join(BASE, "herramientas", "conv_openvoice.py"), ruta], timeout=1800)
    return json.loads(out.strip().splitlines()[-1])


# ------------------------------------------------------------------ medidas
class Medidor:
    def __init__(self):
        self.asr = self.fon = self.enc = None
        self.avisos = {}
        try:
            from faster_whisper import WhisperModel
            self.asr = WhisperModel("small", device="cpu", compute_type="int8")
        except Exception as e:
            self.avisos["asr"] = str(e)[-200:]
        try:
            from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
            nombre = "facebook/wav2vec2-xlsr-53-espeak-cv-ft"
            self.fon = (Wav2Vec2Processor.from_pretrained(nombre), Wav2Vec2ForCTC.from_pretrained(nombre).eval())
        except Exception as e:
            self.avisos["fonemas"] = str(e)[-300:]
        try:
            from resemblyzer import VoiceEncoder
            self.enc = VoiceEncoder("cpu", verbose=False)
        except Exception as e:
            self.avisos["resemblyzer"] = str(e)[-200:]
        # 10/11/2026: la voz del dueño está prohibida: ya no se carga ni se mide parecido con ella.
        self.enc = None
        self.emb_ref = None

    def embedding(self, x):
        import numpy as np
        from resemblyzer import preprocess_wav
        w = preprocess_wav(x.astype(np.float32), source_sr=16000)
        if len(w) < 8000:
            w = x.astype(np.float32)
        e = self.enc.embed_utterance(w)
        return e / (np.linalg.norm(e) + 1e-9)

    def fonemas(self, ruta):
        import torch
        proc, modelo = self.fon
        x = audio16k(ruta)
        ent = proc(x, sampling_rate=16000, return_tensors="pt")
        with torch.no_grad():
            ids = modelo(ent.input_values).logits.argmax(-1)
        return proc.batch_decode(ids)[0]

    def transcribir(self, ruta):
        segs, _ = self.asr.transcribe(audio16k(ruta), language="es", beam_size=5, vad_filter=False)
        return " ".join(s.text.strip() for s in segs)


def prosodia(ruta, n_palabras):
    import numpy as np
    import librosa
    y = audio16k(ruta)
    f0, voiced, _ = librosa.pyin(y, fmin=60, fmax=400, sr=16000, frame_length=1024, hop_length=160)
    f0v = f0[np.isfinite(f0) & (voiced == True)]  # noqa: E712
    out = {}
    if f0v.size > 20:
        st = 12 * np.log2(f0v / np.median(f0v))
        out["f0_mediana_hz"] = round(float(np.median(f0v)), 1)
        out["tono_desv_st"] = round(float(np.std(st)), 2)
        out["tono_rango_st"] = round(float(np.percentile(st, 90) - np.percentile(st, 10)), 2)
    out["duracion_s"] = round(len(y) / 16000, 2)
    return out


def medir(med, carpeta, nombre):
    res = {}
    sw, pw = nombres_wav(carpeta)
    # 1) seseo: θ en las palabras sueltas
    if med.fon:
        palabras = {}
        aciertos = esperadas = 0
        for (p, n_esp), w in zip(PALABRAS.items(), pw):
            try:
                ph = med.fonemas(w)
            except Exception as e:
                palabras[p] = f"error: {str(e)[-80:]}"
                continue
            n_th = ph.count("θ")
            palabras[p] = {"fonemas": ph, "theta": n_th, "esperadas": n_esp}
            aciertos += min(n_th, n_esp)
            esperadas += n_esp
        res["palabras_theta"] = palabras
        res["theta_pct"] = round(100 * aciertos / max(esperadas, 1), 1)
        res["palabras_con_theta"] = sum(1 for v in palabras.values() if isinstance(v, dict) and v["theta"] > 0)
    # 2) frases: audio unido
    voz = os.path.join(carpeta, "frases.wav")
    concatenar(sw, voz)
    n_pal = sum(len(f.split()) for f in FRASES)
    try:
        res["prosodia"] = prosodia(voz, n_pal)
    except Exception as e:
        res["aviso_prosodia"] = str(e)[-200:]
    if med.asr:
        try:
            res["transcripcion"] = med.transcribir(voz)
            res["wer"] = wer(" ".join(FRASES), res["transcripcion"])
        except Exception as e:
            res["aviso_asr"] = str(e)[-200:]
    if med.enc is not None:
        try:
            import numpy as np
            e = med.embedding(audio16k(voz))
            res["parecido_ref"] = round(float(np.dot(e, med.emb_ref[0])), 3)
            res["parecido_larga"] = round(float(np.dot(e, med.emb_ref[1])), 3)
        except Exception as e:
            res["aviso_parecido"] = str(e)[-200:]
    concatenar(sw, os.path.join(SALIDA, f"voz_{nombre}.mp3"), ("-b:a", "96k"))
    concatenar(pw, os.path.join(SALIDA, f"palabras_{nombre}.mp3"), ("-b:a", "96k"))
    return res


def main():
    solo = set(sys.argv[1].split(",")) if len(sys.argv) > 1 and sys.argv[1] else None
    shutil.rmtree(DIR, ignore_errors=True)
    os.makedirs(SALIDA)
    informe = {"fecha": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), "frases": FRASES,
               "palabras": PALABRAS, "variantes": {}}
    med = Medidor()
    informe["avisos_medidor"] = med.avisos
    # Control de referencia: el propio dueño (parecido consigo mismo y variación de tono natural)
    informe["dueno_referencia"] = {"aviso": "omitida: la voz del dueño está prohibida (10/11/2026)"}

    def variante(nombre, fn):
        if solo and nombre not in solo:
            return
        t0 = time.time()
        carpeta = os.path.join(DIR, nombre)
        os.makedirs(carpeta, exist_ok=True)
        res = {}
        try:
            info, textos = fn(carpeta)
            res["sintesis"] = info
            res["textos"] = textos[:len(FRASES)]
            res.update(medir(med, carpeta, nombre))
        except Exception as e:
            res["error"] = str(e)[-500:]
        res["total_s"] = round(time.time() - t0, 1)
        informe["variantes"][nombre] = res
        resumen = {k: res.get(k) for k in ("theta_pct", "palabras_con_theta", "parecido_ref", "parecido_larga", "wer", "error")}
        resumen["tono_desv_st"] = (res.get("prosodia") or {}).get("tono_desv_st")
        print(f"== {nombre}: {json.dumps(resumen, ensure_ascii=False)}", flush=True)
        os.makedirs(os.path.dirname(INFORME), exist_ok=True)
        json.dump(informe, open(INFORME, "w"), ensure_ascii=False, indent=1)

    variante("piper", lambda c: sintetizar_piper(c))
    variante("kokoro", lambda c: sintetizar_kokoro(c))

    def con_ov(nombre_base, origen_fn):
        def f(carpeta):
            base_dir = os.path.join(DIR, nombre_base)
            if not os.path.exists(os.path.join(base_dir, "s0.wav")):
                os.makedirs(base_dir, exist_ok=True)
                origen_fn(base_dir)
            info = convertir_openvoice(base_dir, carpeta)
            return info, textos_prueba()
        return f

    variante("piper_ov", con_ov("piper", sintetizar_piper))
    variante("kokoro_ov", con_ov("kokoro", sintetizar_kokoro))
    variante("cbk_actual", lambda c: sintetizar_chatterbox(c, False, referencia_kokoro_sintetica()))
    variante("cbk_griego2", lambda c: sintetizar_chatterbox(c, "griego_sin_inicial", referencia_kokoro_sintetica()))
    variante("cb_actual", lambda c: sintetizar_chatterbox(c, False))
    variante("cb_theta", lambda c: sintetizar_chatterbox(c, "th"))
    variante("cb_griego", lambda c: sintetizar_chatterbox(c, "griego"))
    variante("cb_griego2", lambda c: sintetizar_chatterbox(c, "griego_sin_inicial"))
    variante("piper2", lambda c: sintetizar_piper(c, "1.0", "1.0", "1.0"))
    variante("piper2_ov", con_ov("piper2", lambda c: sintetizar_piper(c, "1.0", "1.0", "1.0")))

    json.dump(informe, open(INFORME, "w"), ensure_ascii=False, indent=1)
    print(json.dumps({k: {x: v.get(x) for x in ("theta_pct", "parecido_ref", "wer", "error")}
                      for k, v in informe["variantes"].items()}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
