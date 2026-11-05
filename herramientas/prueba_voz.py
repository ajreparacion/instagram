#!/usr/bin/env python3
"""Prueba comparativa de motores de voz (la lanza .github/workflows/prueba_voz.yml, a mano).

Renderiza herramientas/ejemplo_guion.json una vez y le pone la voz con cada motor:
  piper (voz actual), pocket (Kyutai Pocket TTS, spanish/lola) y pocket_24l (spanish_24l/lola, más grande).
Mide para cada uno: tiempo de síntesis en la CPU del runner, duración de las frases frente al hueco de su
escena (atempo necesario), sonoridad final (LUFS, pico real), inteligibilidad (Whisper → % de palabras mal
reconocidas, WER) y naturalidad estimada (UTMOS22, escala 1-5, predictor de MOS para voz sintética).
Escribe equipo/pruebas/prueba_voz.json y deja los vídeos en /tmp/prueba_voz/salida/ (el workflow los sube
a la release "pruebas"; nunca al historial de git).
"""
import copy
import json
import os
import re
import shutil
import subprocess
import sys
import time
import unicodedata

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
import publicar_gh as pg  # noqa: E402

DIR = "/tmp/prueba_voz"
SALIDA = os.path.join(DIR, "salida")
INFORME = os.path.join(BASE, "equipo", "pruebas", "prueba_voz.json")
VARIANTES = [
    ("piper", {"motor": "piper"}),
    ("pocket", {"motor": "pocket", "pocket": {"idioma": "spanish", "voz": "lola"}}),
    ("pocket_24l", {"motor": "pocket", "pocket": {"idioma": "spanish_24l", "voz": "lola"}}),
]


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


def sonoridad(ruta):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", ruta, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    txt = r.stderr
    lufs = re.findall(r"I:\s+(-?[\d.]+) LUFS", txt)
    pico = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", txt)
    return (float(lufs[-1]) if lufs else None), (float(pico[-1]) if pico else None)


def transcribir(modelo, ruta):
    segs, _ = modelo.transcribe(ruta, language="es", beam_size=5, vad_filter=False)
    return " ".join(s.text.strip() for s in segs)


def main():
    shutil.rmtree(DIR, ignore_errors=True)
    os.makedirs(SALIDA)
    base = os.path.join(DIR, "base.mp4")
    t0 = time.time()
    subprocess.run([sys.executable, os.path.join(pg.HERR_REEL, "hacer_reel.py"),
                    os.path.join(pg.HERR_REEL, "ejemplo_guion.json"), base], check=True, cwd=pg.HERR_REEL)
    render_s = round(time.time() - t0, 1)
    locucion = os.path.join(DIR, "base.locucion.json")
    tramos = [t for t in pg.leer_json(locucion, []) if t.get("texto", "").strip()]
    referencia = " ".join(t["texto"] for t in tramos)
    original = pg.ajustes_voz()
    informe = {"fecha": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), "render_video_s": render_s,
               "frases": len(tramos), "referencia": referencia, "variantes": {}}

    try:
        from faster_whisper import WhisperModel
        asr = WhisperModel("small", device="cpu", compute_type="int8")
    except Exception as e:
        asr = None
        informe["aviso_asr"] = str(e)[-200:]
    try:
        import torch
        import torchaudio
        utmos = torch.hub.load("tarepan/SpeechMOS:v1.2.0", "utmos22_strong", trust_repo=True)
    except Exception as e:
        utmos = None
        informe["aviso_utmos"] = str(e)[-200:]

    for nombre, cambios in VARIANTES:
        aj = copy.deepcopy(original)
        for k, v in cambios.items():
            if isinstance(v, dict):
                aj[k] = {**(aj.get(k) or {}), **v}
            else:
                aj[k] = v
        trabajo = os.path.join(DIR, nombre)
        os.makedirs(trabajo)
        video = os.path.join(trabajo, "video.mp4")
        shutil.copy(base, video)
        pg.ajustes_voz = lambda aj=aj: aj
        res = {"ajustes": {k: aj.get(k) for k in ("motor", "modelo", "pocket")}}
        tiempos = {}
        gen_original = pg.generar_locucion if not hasattr(pg, "_gen_orig") else pg._gen_orig
        pg._gen_orig = gen_original

        def cronometrado(textos, trabajo_, aj_=None, _t=tiempos):
            t1 = time.time()
            out = gen_original(textos, trabajo_, aj_)
            _t["sintesis_s"] = round(time.time() - t1, 1)
            return out

        pg.generar_locucion = cronometrado
        try:
            motor = pg.anadir_voz(video, locucion, trabajo)
        except Exception as e:
            res["error"] = str(e)[-300:]
            informe["variantes"][nombre] = res
            continue
        res["motor_usado"] = motor
        res.update(tiempos)
        frases = []
        voz_total = 0.0
        for i, t in enumerate(tramos):
            w = os.path.join(trabajo, f"voz{i}.wav")
            d = pg.duracion_wav(w)
            voz_total += d
            hueco = max(float(t.get("duracion", d)) - 0.15, 0.5)
            frases.append({"dur_s": round(d, 2), "hueco_s": round(hueco, 2), "atempo": round(max(d / hueco, 1.0), 2)})
        res["frases"] = frases
        res["voz_total_s"] = round(voz_total, 1)
        res["veces_tiempo_real"] = round(voz_total / max(res.get("sintesis_s", 0.01), 0.01), 2)
        res["frases_que_no_caben"] = sum(1 for f in frases if f["atempo"] > 1.35)
        res["lufs"], res["pico_real_dbfs"] = sonoridad(video)
        # voz sola (sin música) para la naturalidad y la inteligibilidad pura
        lista = os.path.join(trabajo, "lista.txt")
        with open(lista, "w") as f:
            for i in range(len(tramos)):
                f.write(f"file '{os.path.join(trabajo, f'voz{i}.wav')}'\n")
        solo = os.path.join(trabajo, "voz_sola_16k.wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista,
                        "-ar", "16000", "-ac", "1", solo], check=True)
        if asr:
            try:
                res["transcripcion_mezcla"] = transcribir(asr, video)
                res["wer_mezcla"] = wer(referencia, res["transcripcion_mezcla"])
                res["wer_voz_sola"] = wer(referencia, transcribir(asr, solo))
            except Exception as e:
                res["aviso_asr"] = str(e)[-200:]
        if utmos:
            try:
                notas = []
                for i in range(len(tramos)):
                    x, sr = torchaudio.load(os.path.join(trabajo, f"voz{i}.wav"))
                    x = torchaudio.functional.resample(x.mean(0, keepdim=True), sr, 16000)
                    with torch.no_grad():
                        notas.append(float(utmos(x, 16000).mean()))
                res["utmos_medio"] = round(sum(notas) / len(notas), 2)
                res["utmos_frases"] = [round(n, 2) for n in notas]
            except Exception as e:
                res["aviso_utmos"] = str(e)[-200:]
        shutil.copy(video, os.path.join(SALIDA, f"prueba_voz_{nombre}.mp4"))
        informe["variantes"][nombre] = res
        print(json.dumps({nombre: res}, ensure_ascii=False), flush=True)

    os.makedirs(os.path.dirname(INFORME), exist_ok=True)
    pg.escribir_json(INFORME, informe)
    print(json.dumps(informe, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
