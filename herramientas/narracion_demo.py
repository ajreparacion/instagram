#!/usr/bin/env python3
"""Narración y música del escaparate /demo (Centro de Contenido Apps). By Neogest Lab.

Uso: python3 herramientas/narracion_demo.py [musica|voz|duraciones|verificar|todo]

- voz: lee herramientas/demo_narracion.json, sintetiza cada clip con voz_chatterbox.py y la configuración vigente de
  equipo/voz.json (desde el 12/11/2026 la voz genérica de España de los reels; la del dueño está prohibida), y deja un mp3 por clip en demo_audio/
  (mono, 44,1 kHz, 112 kbps, -16 LUFS, sin silencios largos al principio ni al final).
- musica: pista de fondo en bucle, GENERADA POR CÓDIGO (numpy), sin material de terceros: sin problemas de licencia.
  ~74 s a 104 bpm (32 compases), -26 LUFS (la voz va a -16: la app además la baja con ducking).
- duraciones: demo_audio/duraciones.json {"clips": {id: segundos}, "musica": segundos}.
- verificar: transcribe 3 clips con faster-whisper y compara con el texto (demo_audio/verificacion.json).
Chatterbox corre con PYTHON_CHATTERBOX (entorno propio); el resto con el Python actual.
"""
import difflib
import json
import os
import re
import subprocess
import sys
import wave

import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(BASE, "demo_audio")
TRABAJO = "/tmp/narracion_demo"
GUION = os.path.join(BASE, "herramientas", "demo_narracion.json")
VOZ_JSON = os.path.join(BASE, "equipo", "voz.json")
VOZ_CB = os.path.join(BASE, "herramientas", "voz_chatterbox.py")
PY_CB = os.environ.get("PYTHON_CHATTERBOX") or sys.executable
REFERENCIA_DEMO = os.path.join(BASE, "voz_dueno", "referencia_demo_8nov_41-54s.wav")
LUFS_VOZ = -16.0
LUFS_MUSICA = -26.0


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def lufs(ruta):
    r = sh(["ffmpeg", "-nostats", "-i", ruta, "-af", "ebur128=peak=true", "-f", "null", "-"])
    m = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    return float(m[-1]) if m else None


def duracion(ruta):
    r = sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", ruta])
    return round(float(r.stdout.strip()), 2)


def normalizar_a_mp3(entrada, salida, objetivo, filtros_previos="", fades=(0.005, 0.03), kbps=112):
    """Mide la sonoridad, aplica la ganancia exacta y un limitador, y codifica mono 44,1 kHz."""
    previo = (filtros_previos + ",") if filtros_previos else ""
    tmp = salida + ".tmp.wav"
    r = sh(["ffmpeg", "-y", "-loglevel", "error", "-i", entrada, "-af", previo + "aresample=44100", "-ac", "1", tmp])
    if r.returncode != 0:
        raise SystemExit("ffmpeg (previo): " + r.stderr[-300:])
    medido = lufs(tmp)
    if medido is None:
        raise SystemExit("no se pudo medir la sonoridad de " + entrada)
    d = duracion(tmp)
    fin = max(0.0, d - fades[1])
    af = f"volume={objetivo - medido:.2f}dB,alimiter=limit=0.89:attack=3:release=50:level=false," \
         f"afade=t=in:d={fades[0]},afade=t=out:st={fin:.3f}:d={fades[1]}"
    r = sh(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-af", af, "-ar", "44100", "-ac", "1",
            "-c:a", "libmp3lame", "-b:a", f"{kbps}k", salida])
    os.remove(tmp)
    if r.returncode != 0:
        raise SystemExit("ffmpeg (mp3): " + r.stderr[-300:])


# ───────────────────────────── voz ─────────────────────────────
def voz():
    clips = json.load(open(GUION, encoding="utf-8"))["clips"]
    solo = [x.strip() for x in (os.environ.get("SOLO_IDS") or "").split(",") if x.strip()]
    if solo:  # regenerar solo esos clips; el resto se queda como está en demo_audio/
        clips = [c for c in clips if c["id"] in solo]
        print("solo clips:", [c["id"] for c in clips])
    cfg = json.load(open(VOZ_JSON, encoding="utf-8"))
    cb = cfg["chatterbox"]
    if cfg.get("prohibir_voz_dueno", True):
        # Orden del dueño (9/11/2026 23:55): su voz no se usa en ningún audio nuevo (tampoco en la demo del Centro).
        # 12/11/2026 (Mejora): en vez de abortar, la demo se narra con la MISMA voz genérica de España que los reels
        # (publicar_gh.generar_locucion: Chatterbox es-es sin referencia de persona, respaldo Kokoro em_alex), con el mismo
        # recorte, cadena de voz y -16 LUFS. Así el mp3 que queda en demo_audio/ ya no es el de la voz del dueño.
        os.makedirs(TRABAJO, exist_ok=True)
        os.makedirs(SALIDA, exist_ok=True)
        sys.path.insert(0, BASE)
        import publicar_gh as pg
        aj = pg.ajustes_voz()
        rutas, motor = pg.generar_locucion([c["texto"] for c in clips], TRABAJO, aj,
                                           estilos=[pg.ESTILO_VOZ.get(c.get("estilo"), c.get("estilo")) for c in clips])
        print("motor de voz de la demo:", motor, "(genérica de España; nunca la voz del dueño)")
        cadena = (cfg.get("cadena_voz") or "").strip().strip(",")
        recorte = ("silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.06,areverse,"
                   "silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.12,areverse")
        previo = (cadena + "," if cadena else "") + recorte
        for c, wav in zip(clips, rutas):
            normalizar_a_mp3(wav, os.path.join(SALIDA, c["id"] + ".mp3"), LUFS_VOZ, previo)
            print("clip", c["id"], duracion(os.path.join(SALIDA, c["id"] + ".mp3")), "s")
        return
    os.makedirs(TRABAJO, exist_ok=True)
    os.makedirs(SALIDA, exist_ok=True)
    # Referencia propia de la demo (8/11/2026): tramo 41,26-54,13 s (12,9 s, el más limpio y expresivo) de la nota de voz
    # larga voz_dueno/referencia_usuario_8nov.wav (83 s). Si falta, la de equipo/voz.json.
    ref = REFERENCIA_DEMO if os.path.exists(REFERENCIA_DEMO) else cb.get("referencia")
    if ref and not os.path.isabs(ref):
        ref = os.path.join(BASE, ref)
    if not (ref and os.path.exists(ref)):
        raise SystemExit("falta la voz de referencia del dueño: " + str(ref))
    estilos = cb.get("por_estilo") or {}
    frases = []
    for c in clips:
        f = {"texto": c["texto"], "salida": os.path.join(TRABAJO, c["id"] + ".wav")}
        f.update({k: v for k, v in (estilos.get(c.get("estilo")) or {}).items() if k in ("exageracion", "cfg", "temperatura")})
        frases.append(f)
    lote = {"modelo": cb.get("modelo", "es-es"), "idioma": cb.get("idioma", "es"), "exageracion": cb.get("exageracion", 0.5),
            "cfg": cb.get("cfg", 0.5), "temperatura": cb.get("temperatura", 0.8), "referencia": ref,
            "ganancia": cb.get("ganancia", 1.0), "semilla": cb.get("semilla"), "theta": cb.get("theta") or "", "frases": frases}
    ruta_lote = os.path.join(TRABAJO, "lote.json")
    json.dump(lote, open(ruta_lote, "w", encoding="utf-8"), ensure_ascii=False)
    r = subprocess.run([PY_CB, VOZ_CB, ruta_lote], text=True, capture_output=True)
    sys.stdout.write(r.stdout[-1500:])
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-3000:])
        raise SystemExit("Chatterbox falló")
    # cadena de voz vigente (misma que los reels) + recorte de silencios + -16 LUFS
    cadena = (cfg.get("cadena_voz") or "").strip().strip(",")
    recorte = ("silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.06,areverse,"
               "silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.12,areverse")
    previo = (cadena + "," if cadena else "") + recorte
    for c in clips:
        wav = os.path.join(TRABAJO, c["id"] + ".wav")
        normalizar_a_mp3(wav, os.path.join(SALIDA, c["id"] + ".mp3"), LUFS_VOZ, previo)
        print("clip", c["id"], duracion(os.path.join(SALIDA, c["id"] + ".mp3")), "s")


# ───────────────────────────── música ─────────────────────────────
SR = 44100
BPM = 104
COMPASES = 32


def _nota(f):
    return 440.0 * 2 ** ((f - 69) / 12)


def musica():
    """Base electrónica suave: pad + bajo + percusión ligera; compases exactos y cola plegada al inicio (bucle limpio)."""
    rng = np.random.default_rng(11)
    beat = 60.0 / BPM
    comp = 4 * beat
    n = int(round(COMPASES * comp * SR))
    cola = int(2.5 * SR)
    L = np.zeros(n + cola)
    R = np.zeros(n + cola)

    def poner(buf, s, x):
        i = int(round(s * SR))
        e = min(len(buf), i + len(x))
        if e > i:
            buf[i:e] += x[:e - i]

    def t_(d):
        return np.arange(int(d * SR)) / SR

    # acordes (MIDI) Am - F - C - G, un compás cada uno; la segunda mitad sube una inversión para variar
    prog = [([57, 60, 64], 45), ([53, 57, 60], 41), ([48, 52, 55], 48), ([55, 59, 62], 43)]
    for c in range(COMPASES):
        notas, raiz = prog[c % 4]
        if (c // 16) == 1:
            notas = [x + 12 if k == 0 else x for k, x in enumerate(notas)]
        t0 = c * comp
        # pad: tres notas con ligero desafinado, ataque lento, estéreo
        d = comp + 1.2
        t = t_(d)
        env = np.minimum(1, t / 0.6) * np.exp(-np.maximum(0, t - comp) * 2.2)
        for k, m in enumerate(notas):
            for det, pan in ((-0.07, 0.35), (0.07, 0.65)):
                f = _nota(m) * 2 ** (det / 12)
                x = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t + 1.1)) * env * 0.045
                poner(L, t0, x * (1 - pan)); poner(R, t0, x * pan)
        # bajo: corcheas con síncopa, seno + un toque de armónico
        for j, pos in enumerate([0, 0.75, 1.5, 2.5, 3.0, 3.5]):
            tb = t0 + pos * beat
            dd = 0.42 * beat * 2
            t = t_(dd)
            x = (np.sin(2 * np.pi * _nota(raiz) * t) + 0.25 * np.sin(2 * np.pi * 2 * _nota(raiz) * t)) \
                * np.exp(-t * 7) * np.minimum(1, t / 0.006) * (0.20 if j in (0, 3) else 0.13)
            poner(L, tb, x); poner(R, tb, x)
        # arpegio suave en los compases impares a partir del 5
        if c >= 4 and c % 2 == 1:
            for k in range(8):
                tn = t0 + k * 0.5 * beat
                m = (notas[k % 3]) + 12 + (12 if k % 4 == 3 else 0)
                t = t_(0.9)
                x = np.sin(2 * np.pi * _nota(m) * t) * np.exp(-t * 5.5) * np.minimum(1, t / 0.004) * 0.05
                pan = 0.3 + 0.4 * ((k % 4) / 3)
                poner(L, tn, x * (1 - pan)); poner(R, tn, x * pan)
        # percusión ligera
        for b in range(4):
            tb = t0 + b * beat
            if b in (0, 2) and c >= 2:   # bombo
                t = t_(0.28)
                fr = 48 + 90 * np.exp(-t * 28)
                x = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 11) * 0.30
                poner(L, tb, x); poner(R, tb, x)
            if b in (1, 3) and c >= 8:   # palmada suave
                t = t_(0.16)
                x = rng.standard_normal(len(t)) * np.exp(-t * 28)
                x = np.convolve(x, np.ones(6) / 6, mode="same") * 0.06
                poner(L, tb, x * 0.9); poner(R, tb, x * 1.1)
            if c >= 4:                   # hi-hat a corcheas, contratiempo más suave
                for h, v in ((0, 0.018), (0.5, 0.028)):
                    t = t_(0.05)
                    x = np.diff(rng.standard_normal(len(t) + 1)) * np.exp(-t * 90) * v
                    poner(L, tb + h * beat, x * 1.1); poner(R, tb + h * beat, x * 0.9)
    # plegar la cola al principio => bucle sin salto; luego fundidos cortos de 0,25 s (el mp3 añade un hueco de ~25 ms)
    for buf in (L, R):
        buf[:cola] += buf[n:n + cola]
    L, R = L[:n], R[:n]
    # reverb corta barata: eco difuso mezclado al 12 % (también en bucle: np.roll)
    for buf in (L, R):
        for dly, g in ((0.083, 0.10), (0.131, 0.07), (0.197, 0.05)):
            buf += g * np.roll(buf, int(dly * SR))
    m = np.stack([L, R], axis=1)
    m = np.tanh(m * 2.2) / 2.2
    f = int(0.25 * SR)
    m[:f] *= np.linspace(0, 1, f)[:, None]
    m[-f:] *= np.linspace(1, 0, f)[:, None]
    m = m / max(1e-9, np.abs(m).max()) * 0.8
    os.makedirs(TRABAJO, exist_ok=True)
    os.makedirs(SALIDA, exist_ok=True)
    wav = os.path.join(TRABAJO, "musica.wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((m * 32767).astype("<i2").tobytes())
    # mp3 mono (la música va de fondo: mono pesa la mitad y suena igual de bajo)
    normalizar_a_mp3(wav, os.path.join(SALIDA, "musica.mp3"), LUFS_MUSICA, "", fades=(0.0, 0.0), kbps=96)
    print("musica.mp3", duracion(os.path.join(SALIDA, "musica.mp3")), "s", BPM, "bpm")


# ───────────────────────────── duraciones y verificación ─────────────────────────────
def duraciones():
    clips = json.load(open(GUION, encoding="utf-8"))["clips"]
    d = {"clips": {}, "musica": None}
    for c in clips:
        p = os.path.join(SALIDA, c["id"] + ".mp3")
        if os.path.exists(p):
            d["clips"][c["id"]] = duracion(p)
    p = os.path.join(SALIDA, "musica.mp3")
    if os.path.exists(p):
        d["musica"] = duracion(p)
    json.dump(d, open(os.path.join(SALIDA, "duraciones.json"), "w"), indent=1)
    return d


def _norm(t):
    t = t.lower().replace("«", "").replace("»", "")
    return re.sub(r"[^a-záéíóúñü0-9 ]", " ", t).split()


def verificar():
    from faster_whisper import WhisperModel
    clips = json.load(open(GUION, encoding="utf-8"))["clips"]
    por_id = {c["id"]: c["texto"] for c in clips}
    elegidos = [i for i in ("intro", "web_3", "acciones_4", "gestion_3", "final") if i in por_id][:5]
    modelo = WhisperModel("small", device="cpu", compute_type="int8")
    out = {}
    for i in elegidos:
        segs, _ = modelo.transcribe(os.path.join(SALIDA, i + ".mp3"), language="es")
        txt = " ".join(s.text.strip() for s in segs)
        a, b = _norm(por_id[i]), _norm(txt)
        out[i] = {"esperado": por_id[i], "oido": txt, "similitud": round(difflib.SequenceMatcher(None, a, b).ratio(), 3)}
        print(i, out[i])
    json.dump(out, open(os.path.join(SALIDA, "verificacion.json"), "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    pasos = sys.argv[1:] or ["todo"]
    for p in pasos:
        if p in ("musica", "todo"):
            musica()
        if p in ("voz", "todo"):
            voz()
        if p in ("duraciones", "todo"):
            duraciones()
        if p in ("verificar", "todo"):
            verificar()
