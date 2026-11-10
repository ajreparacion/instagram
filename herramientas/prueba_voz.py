#!/usr/bin/env python3
"""Prueba comparativa de motores de voz (la lanza .github/workflows/prueba_voz.yml, a mano).

Uso: python3 herramientas/prueba_voz.py [guion.json] [variante,variante,...]
  guion.json: por defecto herramientas/ejemplo_guion_humano.json (modo humano, fotos reales).
  variantes: por defecto todas las de VARIANTES.

Renderiza el guion una vez y le pone la voz con cada motor: piper, pocket (Kyutai, lola), kokoro (em_alex / ef_dora)
y chatterbox (Resemble AI; afinado es-es con voz integrada, con referencia Kokoro, y multilingüe).
Mide para cada uno: tiempo de síntesis en la CPU del runner, duración frente al hueco de su escena (atempo),
sonoridad final (LUFS, pico real), inteligibilidad (Whisper → WER), naturalidad estimada (UTMOS22, 1-5) y
PROSODIA (variación del tono en semitonos, proporción de pausas, palabras por segundo): una voz humana contando
algo varía el tono y hace pausas; una voz de locutor sintético es plana y continua.
Escribe equipo/pruebas/prueba_voz.json y deja en /tmp/prueba_voz/salida/ los vídeos (prueba_voz_<variante>.mp4) y
la voz sola en mp3 (voz_<variante>.mp3) para escucharlos; el workflow los sube a la release "pruebas".
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
CB = {"modelo": "es-es", "idioma": "es", "exageracion": 0.6, "cfg": 0.35, "temperatura": 0.75,
      "referencia": None, "referencia_kokoro": None, "semilla": 7, "max_s": 2400}
VARIANTES = [
    # "pocket_antes" = flujo ANTERIOR (render y después la voz acelerada para caber, subtítulos a 2,6 pal/s estimadas).
    # El resto usa el flujo nuevo "voz primero" de publicar_gh.renderizar_guion (escena ajustada a la voz real).
    ("pocket_antes", {"motor": "pocket", "respaldo": [], "pocket": {"idioma": "spanish", "voz": "lola"}, "_flujo": "antiguo"}),
    ("piper", {"motor": "piper", "respaldo": []}),
    ("pocket", {"motor": "pocket", "respaldo": [], "pocket": {"idioma": "spanish", "voz": "lola"}}),
    ("kokoro_alex", {"motor": "kokoro", "respaldo": [], "kokoro": {"voz": "em_alex", "velocidad": 0.95}}),
    ("kokoro_dora", {"motor": "kokoro", "respaldo": [], "kokoro": {"voz": "ef_dora", "velocidad": 0.95}}),
    ("chatterbox_es", {"motor": "chatterbox", "respaldo": [], "chatterbox": dict(CB)}),
    ("chatterbox_es_ref", {"motor": "chatterbox", "respaldo": [], "chatterbox": {**CB, "referencia_kokoro": "em_alex"}}),
    ("chatterbox_mtl", {"motor": "chatterbox", "respaldo": [], "chatterbox": {**CB, "modelo": "multilingue"}}),
    # 10/11/2026: ajustes REALES de equipo/voz.json (cfg, temperatura, θ, por_estilo) con la referencia sintética Kokoro.
    ("chatterbox_prod", {"motor": "chatterbox", "respaldo": [],
                         "chatterbox": {**{k: v for k, v in (json.load(open(os.path.join(BASE, "equipo", "voz.json"))).get("chatterbox") or {}).items()},
                                        "referencia": None, "referencia_kokoro": "em_alex", "max_s": 2400}}),
    # Voz CLONADA del dueño (autorizada por él el 6/11/2026; la saca herramientas/voz_usuario.py de sus reels de
    # Mr. Empírico). Solo funcionan si existe voces/referencia_usuario.wav (workflow voz_usuario.yml).
    ("chatterbox_usuario", {"motor": "chatterbox", "respaldo": [],
                            "chatterbox": {**CB, "referencia": "voces/referencia_usuario.wav"}}),
    ("chatterbox_usuario_suave", {"motor": "chatterbox", "respaldo": [],
                                  "chatterbox": {**CB, "referencia": "voces/referencia_usuario.wav",
                                                 "exageracion": 0.45, "cfg": 0.5}}),
    ("chatterbox_mtl_usuario", {"motor": "chatterbox", "respaldo": [],
                                "chatterbox": {**CB, "modelo": "multilingue", "referencia": "voces/referencia_usuario.wav"}}),
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


def duracion_video(ruta):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", ruta],
                       capture_output=True, text=True)
    try:
        return round(float(r.stdout.strip()), 1)
    except ValueError:
        return None


def audio16k(ruta):
    """Decodifica con ffmpeg a mono 16 kHz float32 (evita PyAV/torchcodec, que fallan según versión)."""
    import numpy as np
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", ruta, "-vn", "-ac", "1", "-ar", "16000",
                        "-f", "f32le", "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype=np.float32).copy()


def transcribir(modelo, ruta):
    segs, _ = modelo.transcribe(audio16k(ruta), language="es", beam_size=5, vad_filter=False)
    return " ".join(s.text.strip() for s in segs)


def prosodia(ruta, n_palabras):
    """Variación del tono (desviación típica y rango 10-90 % en semitonos), proporción de pausas y palabras/s.
    Referencia orientativa: habla conversacional ~2-4 st de desviación y 15-25 % de pausas; lectura plana < 1,5 st."""
    import numpy as np
    try:
        import librosa
    except Exception as e:
        return {"aviso": f"sin librosa: {str(e)[-80:]}"}
    y = audio16k(ruta)
    sr = 16000
    f0, voiced, _ = librosa.pyin(y, fmin=60, fmax=400, sr=sr, frame_length=1024, hop_length=160)
    f0v = f0[np.isfinite(f0) & (voiced == True)]  # noqa: E712
    out = {}
    if f0v.size > 20:
        st = 12 * np.log2(f0v / np.median(f0v))
        out["f0_mediana_hz"] = round(float(np.median(f0v)), 1)
        out["tono_desv_st"] = round(float(np.std(st)), 2)
        out["tono_rango_st"] = round(float(np.percentile(st, 90) - np.percentile(st, 10)), 2)
    rms = librosa.feature.rms(y=y, frame_length=1024, hop_length=160)[0]
    umbral = max(rms.max() * 0.05, 1e-4)
    out["pausas_pct"] = round(float((rms < umbral).mean() * 100), 1)
    dur = len(y) / sr
    out["duracion_s"] = round(dur, 2)
    out["palabras_por_s"] = round(n_palabras / max(dur, 0.1), 2)
    return out


def main():
    guion = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else os.path.join(pg.HERR_REEL, "ejemplo_guion_humano.json")
    guion = os.path.abspath(guion)
    solo = set(sys.argv[2].split(",")) if len(sys.argv) > 2 and sys.argv[2] else None
    variantes = [v for v in VARIANTES if not solo or v[0] in solo]
    shutil.rmtree(DIR, ignore_errors=True)
    os.makedirs(SALIDA)
    base = os.path.join(DIR, "base.mp4")
    t0 = time.time()
    # render del flujo antiguo (una vez; lo comparten las variantes "_flujo": "antiguo")
    subprocess.run([sys.executable, os.path.join(pg.HERR_REEL, "hacer_reel.py"), guion, base], check=True, cwd=pg.HERR_REEL)
    render_s = round(time.time() - t0, 1)
    locucion_base = os.path.join(DIR, "base.locucion.json")
    tramos_base = [t for t in pg.leer_json(locucion_base, []) if t.get("texto", "").strip()]
    referencia = " ".join(t["texto"] for t in tramos_base)
    n_palabras = len(referencia.split())
    original = pg.ajustes_voz()
    informe = {"fecha": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), "guion": os.path.relpath(guion, BASE),
               "render_video_s": render_s, "frases": len(tramos_base), "palabras": n_palabras, "referencia": referencia,
               "cpu": os.cpu_count(), "variantes": {}}

    try:
        from faster_whisper import WhisperModel
        asr = WhisperModel("small", device="cpu", compute_type="int8")
    except Exception as e:
        asr = None
        informe["aviso_asr"] = str(e)[-200:]
    try:
        import torch
        utmos = torch.hub.load("tarepan/SpeechMOS:v1.2.0", "utmos22_strong", trust_repo=True)
    except Exception as e:
        utmos = None
        informe["aviso_utmos"] = str(e)[-200:]

    gen_original = pg.generar_locucion
    for nombre, cambios in variantes:
        aj = copy.deepcopy(original)
        flujo = cambios.get("_flujo", "voz_primero")
        for k, v in cambios.items():
            if k.startswith("_"):
                continue
            if isinstance(v, dict):
                aj[k] = {**(aj.get(k) or {}), **v}
            else:
                aj[k] = v
        trabajo = os.path.join(DIR, nombre)
        os.makedirs(trabajo)
        video = os.path.join(trabajo, "video.mp4")
        locucion = os.path.join(trabajo, "video.locucion.json")
        pg.ajustes_voz = lambda aj=aj: aj
        res = {"flujo": flujo, "ajustes": {k: aj.get(k) for k in ("motor", "modelo", "pocket", "kokoro", "chatterbox") if k in cambios or k == "motor"}}
        tiempos = {}

        def cronometrado(textos, trabajo_, aj_=None, _t=tiempos, **kw):
            t1 = time.time()
            out = gen_original(textos, trabajo_, aj_, **kw)   # kw: estilos (ajustes por estilo: gancho/giro)
            _t["sintesis_s"] = round(time.time() - t1, 1)
            return out

        pg.generar_locucion = cronometrado
        t_var = time.time()
        try:
            if flujo == "antiguo":
                shutil.copy(base, video)
                shutil.copy(locucion_base, locucion)
                motor = pg.anadir_voz(video, locucion, trabajo)
            else:
                motor = pg.renderizar_guion(guion, video, trabajo)
            res["render_total_s"] = round(time.time() - t_var, 1)
            tramos = [t for t in pg.leer_json(locucion, []) if t.get("texto", "").strip()]
            res["duracion_reel_s"] = duracion_video(video)
        except Exception as e:
            res["error"] = str(e)[-300:]
            informe["variantes"][nombre] = res
            print(json.dumps({nombre: res}, ensure_ascii=False), flush=True)
            continue
        finally:
            pg.generar_locucion = gen_original
        res["motor_usado"] = motor
        if motor != aj["motor"]:
            res["error"] = f"el motor {aj['motor']} falló y la voz salió con {motor} (ver registro.log)"
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
        # voz sola (sin música) para la naturalidad, la inteligibilidad pura y la prosodia
        lista = os.path.join(trabajo, "lista.txt")
        with open(lista, "w") as f:
            for i in range(len(tramos)):
                f.write(f"file '{os.path.join(trabajo, f'voz{i}.wav')}'\n")
        solo_wav = os.path.join(trabajo, "voz_sola_16k.wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista,
                        "-ar", "16000", "-ac", "1", solo_wav], check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista,
                        "-ac", "1", "-b:a", "96k", os.path.join(SALIDA, f"voz_{nombre}.mp3")], check=True)
        try:
            res["prosodia"] = prosodia(solo_wav, n_palabras)
        except Exception as e:
            res["aviso_prosodia"] = str(e)[-200:]
        if asr:
            try:
                res["transcripcion_mezcla"] = transcribir(asr, video)
                res["wer_mezcla"] = wer(referencia, res["transcripcion_mezcla"])
                res["transcripcion_voz_sola"] = transcribir(asr, solo_wav)
                res["wer_voz_sola"] = wer(referencia, res["transcripcion_voz_sola"])
            except Exception as e:
                res["aviso_asr"] = str(e)[-200:]
        if utmos:
            try:
                notas = []
                for i in range(len(tramos)):
                    x = torch.from_numpy(audio16k(os.path.join(trabajo, f"voz{i}.wav")))[None]
                    with torch.no_grad():
                        notas.append(float(utmos(x, 16000).mean()))
                res["utmos_medio"] = round(sum(notas) / len(notas), 2)
                res["utmos_frases"] = [round(n, 2) for n in notas]
            except Exception as e:
                res["aviso_utmos"] = str(e)[-200:]
        shutil.copy(video, os.path.join(SALIDA, f"prueba_voz_{nombre}.mp4"))
        informe["variantes"][nombre] = res
        print(json.dumps({nombre: res}, ensure_ascii=False), flush=True)

    informe["registro"] = [l for l in open(pg.REGISTRO, encoding="utf-8", errors="replace").read().splitlines()[-60:]
                           if "Voz" in l or "voz" in l or "Chatterbox" in l or "Kokoro" in l] if os.path.exists(pg.REGISTRO) else []
    os.makedirs(os.path.dirname(INFORME), exist_ok=True)
    pg.escribir_json(INFORME, informe)
    print(json.dumps(informe, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
