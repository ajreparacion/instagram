#!/usr/bin/env python3
"""Pruebas de MeloTTS ES (13/11/2026). La lanza .github/workflows/prueba_melo.yml, a mano; no publica nada.
Uso: python3 herramientas/prueba_melo.py ajuste | final | reel [guion.json]
  ajuste: velocidades 1.0-1.2 y grafías de «Neogest Lab», «Ajota» y «Éxcel»; transcribe con Whisper (small, es) y mide palabras/s.
  final:  la frase de prueba con equipo/voz.json (melo.velocidad y melo.pronunciacion) -> /tmp/melo/salida/melo_final_frase.mp3
  reel:   render real (publicar_gh.renderizar_guion) de un guion de la cola, sin publicar -> melo_reel_prueba.mp3 (solo audio, 192k) y .mp4
Todo pasa por la cadena_voz y loudnorm -14 LUFS como en producción; MP3 192 kbps a 48 kHz (la voz de Melo nace a 44,1 kHz).
"""
import json, os, subprocess, sys, unicodedata, shutil
import numpy as np
from scipy.signal import welch

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE); sys.path.insert(0, os.path.join(BASE, "herramientas"))
import audicion_voces_v2 as a2          # noqa: E402
import publicar_gh as pg                # noqa: E402

SAL = "/tmp/melo/salida"
FRASE = a2.FRASE
LARGAS = ["Vendes a doce euros y te quedan cuatro con cincuenta y dos. La hizo una IA con este mensaje, y el IVA no es tuyo.",
          "Pide tu prueba gratuita: sin tarjeta, sin datos bancarios y sin compromiso."]


def n(t):
    return "".join(c for c in unicodedata.normalize("NFD", t.lower()) if unicodedata.category(c) != "Mn")


def melo(frases, velocidad, pron, nombre):
    lote = {"idioma": "ES", "speaker": "ES", "velocidad": velocidad, "ganancia": 1.0, "pronunciacion": pron,
            "frases": [{"texto": t, "salida": f"{a2.RAW}/{nombre}_{i}.wav", **({"velocidad": v} if v else {})} for i, (t, v) in enumerate(frases)]}
    j = f"{a2.RAW}/{nombre}.json"
    json.dump(lote, open(j, "w"), ensure_ascii=False)
    py = os.environ.get("PYTHON_MELO") or sys.executable
    r = subprocess.run([py, os.path.join(BASE, "herramientas", "voz_melo.py"), j], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit("melo falló: " + (r.stderr or r.stdout)[-400:])
    return [f["salida"] for f in lote["frases"]]


def bandas(mp3):
    x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", mp3, "-f", "f32le", "-ac", "1", "-ar", "48000", "-"], capture_output=True).stdout, np.float32)
    fr, P = welch(x, 48000, nperseg=4096)
    b = lambda lo, hi: 10 * np.log10(max(1e-20, P[(fr >= lo) & (fr < hi)].sum()))
    ref = b(150, 400)
    m = subprocess.run(["ffmpeg", "-v", "info", "-i", mp3, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    lufs = [l for l in m.splitlines() if "I:" in l and "LUFS" in l][-1].split("I:")[1].split("LUFS")[0].strip()
    return {"8-12k_dB": float(round(b(8000, 12000) - ref, 1)), "12-16k_dB": float(round(b(12000, 16000) - ref, 1)), "LUFS": float(lufs), "dur_s": float(round(len(x) / 48000, 2))}


def whisper(ruta):
    from faster_whisper import WhisperModel
    global _W
    try: _W
    except NameError: _W = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = _W.transcribe(ruta, language="es", beam_size=5, word_timestamps=True)
    segs = list(segs)
    pal = [w for s in segs for w in s.words]
    texto = " ".join(s.text.strip() for s in segs)
    wps = float(round(len(pal) / max(pal[-1].end - pal[0].start, 0.1), 2)) if pal else 0.0
    return texto, wps


def ajuste():
    res = {}
    grafias = ["Neogest Lab", "Neogest, Lab", "Neogest. Lab", "Neogest... Lab", "Neogés, Lab", "Neojest, Lab", "Neogest, Láb", "Neogest, Leb"]
    ajota = ["Ajota", "Ajóta", "A jota", "Ahota"]
    excel = ["Éxcel", "Eksel", "Ecsel"]
    for v in (1.0, 1.1, 1.15, 1.2):
        nom = f"v{str(v).replace('.', '')}"
        rutas = melo([(FRASE, None)], v, {}, "aj_" + nom)
        a2.postprocesar(rutas[0], f"melo_vel_{nom}")
        t, w = whisper(f"{a2.SAL}/melo_vel_{nom}.mp3")
        res[f"velocidad_{v}"] = {"texto": t, "palabras_s": float(w), **bandas(f"{a2.SAL}/melo_vel_{nom}.mp3")}
        print(nom, res[f"velocidad_{v}"], flush=True)
    for g in grafias:
        frase = FRASE.replace("Neogest Lab", g)
        rutas = melo([(frase, None)], 1.15, {}, "gr")
        a2.postprocesar(rutas[0], "melo_gr")
        t, w = whisper(f"{a2.SAL}/melo_gr.mp3")
        res["grafia_" + g] = {"texto": t, "ok": "neogestlab" in n(t).replace(" ", "")}
        print(g, res["grafia_" + g], flush=True)
    for g in ajota:
        rutas = melo([(FRASE.replace("Ajota", g), None)], 1.15, {}, "ga")
        a2.postprocesar(rutas[0], "melo_ga"); t, _ = whisper(f"{a2.SAL}/melo_ga.mp3")
        res["ajota_" + g] = {"texto": t, "ok": "ajota" in n(t) or "ajsistema" in n(t).replace(" ", "")}; print(g, res["ajota_" + g], flush=True)
    for g in excel:
        rutas = melo([(FRASE.replace("Éxcel", g), None)], 1.15, {}, "ge")
        a2.postprocesar(rutas[0], "melo_ge"); t, _ = whisper(f"{a2.SAL}/melo_ge.mp3")
        res["excel_" + g] = {"texto": t, "ok": "excel" in n(t)}; print(g, res["excel_" + g], flush=True)
    for f in ("melo_gr", "melo_ga", "melo_ge"):
        os.remove(f"{a2.SAL}/{f}.mp3")
    json.dump(res, open(f"{a2.SAL}/melo_ajuste.json", "w"), ensure_ascii=False, indent=1, default=float)


def grafias():
    res = {}
    for g in ["Neogest Láb", "Neogest, Láb", "Neogest Lab", "Neogest Láb", "Neogest, Láb", "Neogest Lab", "Neogest Láb", "Neogest, Láb"]:
        v = 1.1
        rutas = melo([(FRASE.replace("Neogest Lab", g), None)], v, {}, "gx")
        a2.postprocesar(rutas[0], "melo_gx"); t, w = whisper(f"{a2.SAL}/melo_gx.mp3")
        ok = "neogestlab" in n(t).replace(" ", "").replace(",", "")
        res.setdefault(g, []).append({"texto": t, "ok": ok, "palabras_s": w}); print(g, ok, t, flush=True)
    os.remove(f"{a2.SAL}/melo_gx.mp3")
    json.dump(res, open(f"{a2.SAL}/melo_grafias.json", "w"), ensure_ascii=False, indent=1)


def final():
    aj = pg.ajustes_voz()["melo"]
    rutas = melo([(FRASE, None)] + [(t, None) for t in LARGAS], aj.get("velocidad", 1.0), aj.get("pronunciacion") or {}, "final")
    a2.postprocesar(rutas[0], "melo_final_frase")
    res = {}
    t, w = whisper(f"{a2.SAL}/melo_final_frase.mp3")
    res["frase"] = {"texto": t, "palabras_s": float(w), **bandas(f"{a2.SAL}/melo_final_frase.mp3")}
    for i, r in enumerate(rutas[1:]):
        a2.postprocesar(r, f"melo_final_larga{i}")
        t, w = whisper(f"{a2.SAL}/melo_final_larga{i}.mp3")
        res[f"larga{i}"] = {"texto": t, "palabras_s": w}
        os.remove(f"{a2.SAL}/melo_final_larga{i}.mp3")
    print(json.dumps(res, ensure_ascii=False, indent=1, default=float))
    json.dump(res, open(f"{a2.SAL}/melo_final.json", "w"), ensure_ascii=False, indent=1, default=float)


def reel(guion):
    trabajo = "/tmp/melo/render"; shutil.rmtree(trabajo, ignore_errors=True); os.makedirs(trabajo)
    video = os.path.join(trabajo, "video.mp4")
    import time; t0 = time.time()
    motor = pg.renderizar_guion(os.path.abspath(guion), video, trabajo)
    seg = round(time.time() - t0, 1)
    shutil.copy(video, f"{SAL}/melo_reel_prueba.mp4")
    sh = lambda c: subprocess.run(c, check=True, capture_output=True)
    sh(["ffmpeg", "-v", "error", "-y", "-i", video, "-vn", "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "48000", f"{SAL}/melo_reel_prueba.mp3"])
    wavs = sorted(f for f in os.listdir(trabajo) if f.startswith("voz") and f.endswith(".wav"))
    sr = [__import__("wave").open(os.path.join(trabajo, f)).getframerate() for f in wavs]
    t, w = whisper(f"{SAL}/melo_reel_prueba.mp3")
    res = {"motor_usado": motor, "render_s": seg, "sr_wavs_voz": sorted(set(sr)), "texto": t, "palabras_s": w, **bandas(f"{SAL}/melo_reel_prueba.mp3")}
    print(json.dumps(res, ensure_ascii=False, indent=1, default=float))
    json.dump(res, open(f"{SAL}/melo_reel.json", "w"), ensure_ascii=False, indent=1, default=float)


if __name__ == "__main__":
    os.makedirs(a2.RAW, exist_ok=True); os.makedirs(SAL, exist_ok=True)
    a2.SAL = SAL
    modo = sys.argv[1]
    if modo == "ajuste": ajuste()
    elif modo == "final": final()
    elif modo == "grafias": grafias()
    else: reel(sys.argv[2] if len(sys.argv) > 2 else "cola/508_jambo_app_gastos_fijos/guion.json")
