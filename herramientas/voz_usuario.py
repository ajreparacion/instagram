#!/usr/bin/env python3
"""Referencia de voz del DUEÑO de la cuenta para clonarla con Chatterbox (la lanza .github/workflows/voz_usuario.yml).

Autorización: el dueño de la cuenta ha dicho por escrito (6/11/2026) que todos los vídeos subidos son suyos, que él es el
protagonista de los reels de Mr. Empírico y que se clone su voz de esos vídeos. Solo se usa SU voz y solo para esta
cuenta (ver equipo/pendiente_usuario.md, punto 0). Nunca se clona la voz de otra persona.

Uso:
  python3 herramientas/voz_usuario.py extraer [id1,id2,...]
      Descarga los reels del podcast Empírico (por defecto, los 10 más vistos de equipo/historico.json; o los ids que se
      pasen), separa la voz de la música (Demucs), transcribe (faster-whisper), agrupa los tramos por hablante (Resemblyzer,
      GE2E) y se queda con el hablante que más habla (el protagonista). Elige los tramos más limpios y escribe:
        voces/referencia_usuario.wav        ~10-14 s, 24 kHz mono, -20 LUFS (la que usa Chatterbox)
        voces/referencia_usuario_larga.wav  ~30 s (para pruebas futuras)
        voces/referencia_hablante_2.wav     si hay un 2.º hablante con bastante voz (por si el protagonista es ese)
      y el informe equipo/pruebas/voz_usuario.json (sin audio: ids, tiempos, texto, hablantes).
  python3 herramientas/voz_usuario.py similitud
      Compara (coseno de Resemblyzer) la referencia con las voces sintetizadas de /tmp/prueba_voz/salida/voz_*.mp3 y lo añade
      al informe. Orientativo con Resemblyzer: > 0,80 suele ser la misma voz; < 0,65, otra persona.
Los audios NUNCA van al historial de git (voces/ está en .gitignore): el workflow los sube a la release «voces».
"""
import json
import os
import shutil
import subprocess
import sys
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
import publicar_gh as pg  # noqa: E402

DIR = "/tmp/voz_usuario"
VOCES = os.path.join(BASE, "voces")
INFORME = os.path.join(BASE, "equipo", "pruebas", "voz_usuario.json")
SR = 16000


def sh(*cmd, **kw):
    return subprocess.run(list(cmd), check=True, capture_output=True, text=True, **kw)


def cargar_audio(ruta, sr=SR):
    import numpy as np
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", ruta, "-vn", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype=np.float32).copy()


def ids_por_defecto(n=10):
    h = pg.leer_json(os.path.join(BASE, "equipo", "historico.json"), {}) or {}
    posts = [p for p in h.get("posts", []) if str(p.get("serie", "")).startswith("Podcast Empírico")
             and "Sara" not in str(p.get("serie", "")) and p.get("views")]
    posts.sort(key=lambda p: -p["views"])
    return [str(p["id"]) for p in posts[:n]]


_ENC = None


def codificador():
    """Resemblyzer (MIT, GE2E; los pesos vienen dentro del paquete, sin Hugging Face)."""
    global _ENC
    if _ENC is None:
        from resemblyzer import VoiceEncoder
        _ENC = VoiceEncoder("cpu", verbose=False)
    return _ENC


def embedding(x):
    import numpy as np
    from resemblyzer import preprocess_wav
    w = preprocess_wav(x.astype(np.float32), source_sr=SR)
    if len(w) < SR * 0.5:
        w = x.astype(np.float32)
    e = codificador().embed_utterance(w)
    return e / (np.linalg.norm(e) + 1e-9)


def db(x):
    import numpy as np
    return float(20 * np.log10(np.sqrt(np.mean(np.square(x))) + 1e-9))


def separar(wav, salida):
    """Demucs (htdemucs, MIT): devuelve (voz, resto) en 16 kHz. Si falla, (original, silencio)."""
    import numpy as np
    try:
        sh(sys.executable, "-m", "demucs", "-n", "htdemucs", "--two-stems", "vocals", "-o", salida, wav)
        nombre = os.path.splitext(os.path.basename(wav))[0]
        d = os.path.join(salida, "htdemucs", nombre)
        return cargar_audio(os.path.join(d, "vocals.wav")), cargar_audio(os.path.join(d, "no_vocals.wav")), \
            os.path.join(d, "vocals.wav")
    except Exception as e:
        print("Demucs no disponible:", str(e)[-200:])
        x = cargar_audio(wav)
        return x, np.zeros_like(x), None


def extraer(ids):
    import numpy as np
    from faster_whisper import WhisperModel
    cfg = pg.cargar_config()
    shutil.rmtree(DIR, ignore_errors=True)
    os.makedirs(DIR)
    os.makedirs(VOCES, exist_ok=True)
    whisper = WhisperModel("small", device="cpu", compute_type="int8")
    tramos, videos = [], []
    for oid in ids:
        info = {"id": oid}
        videos.append(info)
        try:
            url = pg.api(cfg, oid, fields="media_url").get("media_url")
            if not url:
                info["error"] = "Instagram no da el vídeo (música con licencia o borrado)"
                continue
            mp4 = os.path.join(DIR, f"{oid}.mp4")
            pg.descargar(url, mp4)
            wav = os.path.join(DIR, f"{oid}.wav")
            r = subprocess.run(["ffmpeg", "-hide_banner", "-y", "-i", mp4, "-vn", "-ac", "1", "-ar", "44100", wav],
                               capture_output=True, text=True)
            if r.returncode != 0:
                p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name",
                                    "-of", "csv=p=0", mp4], capture_output=True, text=True)
                info["tamano"] = os.path.getsize(mp4)
                info["error"] = f"ffmpeg: {r.stderr.strip()[-250:]} | flujos: {p.stdout.strip() or p.stderr.strip()[-120:]}"
                continue
            original = cargar_audio(wav)
            voz, resto, ruta_voz = separar(wav, os.path.join(DIR, "sep"))
            n = min(len(voz), len(resto), len(original))
            voz, resto, original = voz[:n], resto[:n], original[:n]
            info["duracion_s"] = round(n / SR, 1)
            info["musica_db_rel"] = round(db(resto) - db(voz), 1)
            segs, _ = whisper.transcribe(voz, language="es", beam_size=5, vad_filter=True)
            for s in segs:
                a, b = int(s.start * SR), int(s.end * SR)
                if b - a < int(1.5 * SR):
                    continue
                xv, xr, xo = voz[a:b], resto[a:b], original[a:b]
                tramos.append({"id": oid, "inicio": round(s.start, 2), "fin": round(s.end, 2),
                               "dur": round(s.end - s.start, 2), "texto": s.text.strip(),
                               "logprob": round(s.avg_logprob, 3), "no_voz": round(s.no_speech_prob, 3),
                               "musica_db_rel": round(db(xr) - db(xv), 1), "pico": round(float(np.abs(xo).max()), 3),
                               "_voz": xv, "_orig": xo, "_emb": embedding(xv)})
            info["tramos"] = sum(1 for t in tramos if t["id"] == oid)
        except Exception as e:
            info["error"] = str(e)[-300:]
        print(json.dumps({k: v for k, v in info.items()}, ensure_ascii=False))
    if not tramos:
        raise SystemExit("No se ha podido sacar ningún tramo de voz de los vídeos.")

    # Agrupar por hablante (coseno, enlace medio) y quedarse con el que más habla
    from sklearn.cluster import AgglomerativeClustering
    E = np.stack([t["_emb"] for t in tramos])
    if len(tramos) >= 2:
        etiquetas = AgglomerativeClustering(n_clusters=None, metric="cosine", linkage="average",
                                            distance_threshold=0.25).fit_predict(E)
    else:
        etiquetas = np.zeros(1, dtype=int)
    for t, e in zip(tramos, etiquetas):
        t["hablante"] = int(e)
    dur = {}
    for t in tramos:
        dur[t["hablante"]] = dur.get(t["hablante"], 0) + t["dur"]
    orden = sorted(dur, key=lambda k: -dur[k])
    renombre = {k: i + 1 for i, k in enumerate(orden)}
    for t in tramos:
        t["hablante"] = renombre[t["hablante"]]
    hablantes = []
    for k in orden:
        i = renombre[k]
        ts = [t for t in tramos if t["hablante"] == i]
        cen = np.mean([t["_emb"] for t in ts], axis=0)
        cen /= np.linalg.norm(cen) + 1e-9
        for t in ts:
            t["sim_hablante"] = round(float(t["_emb"] @ cen), 3)
        hablantes.append({"hablante": i, "segundos": round(dur[k], 1), "tramos": len(ts),
                          "videos": sorted({t["id"] for t in ts}), "_cen": cen,
                          "ejemplos": [t["texto"][:80] for t in sorted(ts, key=lambda t: -t["dur"])[:3]]})
    sim12 = round(float(hablantes[0]["_cen"] @ hablantes[1]["_cen"]), 3) if len(hablantes) > 1 else None

    def puntuar(t):
        # limpio = poca música debajo, transcripción segura, voz típica de su hablante, sin saturar
        return (t["logprob"] * 2 - t["no_voz"] * 2 - max(t["musica_db_rel"] + 30, 0) * 0.05
                + t["sim_hablante"] * 2 - (1 if t["pico"] > 0.99 else 0) + min(t["dur"], 8) * 0.05)

    def construir(hablante, objetivo, nombre):
        ts = [t for t in tramos if t["hablante"] == hablante and t["logprob"] > -0.8 and t["no_voz"] < 0.5
              and t["dur"] <= 14]
        if not ts:
            return None
        # mismo vídeo en lo posible (acústica homogénea): el vídeo con más voz buena de ese hablante
        por_video = {}
        for t in ts:
            por_video.setdefault(t["id"], []).append(t)
        vid = max(por_video, key=lambda v: sum(puntuar(t) + 3 for t in por_video[v] if puntuar(t) > -3))
        elegidos, total = [], 0.0
        for t in sorted(por_video[vid], key=puntuar, reverse=True) + sorted(
                [t for t in ts if t["id"] != vid], key=puntuar, reverse=True):
            if total >= objetivo:
                break
            elegidos.append(t)
            total += t["dur"]
        elegidos.sort(key=lambda t: (t["id"] != vid, t["id"], t["inicio"]))
        # Con poca música debajo se usa el audio original (más natural); si no, la voz separada por Demucs
        usar_original = all(t["musica_db_rel"] < -22 for t in elegidos)
        hueco = np.zeros(int(0.3 * SR), dtype=np.float32)
        x = np.concatenate([np.concatenate([t["_orig"] if usar_original else t["_voz"], hueco]) for t in elegidos])
        bruto = os.path.join(DIR, nombre + "_bruto.wav")
        import wave
        with wave.open(bruto, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())
        destino = os.path.join(VOCES, nombre + ".wav")
        sh("ffmpeg", "-loglevel", "error", "-y", "-i", bruto, "-af",
           "highpass=f=70,loudnorm=I=-20:TP=-2:LRA=11", "-ar", "24000", "-ac", "1", destino)
        return {"archivo": os.path.relpath(destino, BASE), "segundos": round(total, 1),
                "audio": "original" if usar_original else "voz separada (Demucs)",
                "tramos": [{k: t[k] for k in ("id", "inicio", "fin", "texto", "logprob", "musica_db_rel", "sim_hablante")}
                           for t in elegidos]}

    refs = {"referencia_usuario": construir(1, 11.0, "referencia_usuario"),
            "referencia_usuario_larga": construir(1, 30.0, "referencia_usuario_larga")}
    if len(hablantes) > 1 and hablantes[1]["segundos"] >= 12:
        refs["referencia_hablante_2"] = construir(2, 11.0, "referencia_hablante_2")
    informe = {"fecha": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()),
               "autorizacion": "El dueño de la cuenta, 6/11/2026: «los vídeos subidos son todos míos, soy yo el protagonista, "
                               "clona mi voz de esos vídeos de Mr. Empírico».",
               "videos": videos, "similitud_hablante_1_y_2": sim12,
               "nota_hablantes": "Hablante 1 = el que más habla en los vídeos (se toma como el dueño). Si el dueño hacía "
                                 "dos personajes con voces distintas, pueden salir 2 hablantes con similitud alta (> 0,75).",
               "hablantes": [{k: v for k, v in h.items() if not k.startswith("_")} for h in hablantes],
               "referencias": refs}
    os.makedirs(os.path.dirname(INFORME), exist_ok=True)
    with open(INFORME, "w", encoding="utf-8") as f:
        json.dump(informe, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: informe[k] for k in ("similitud_hablante_1_y_2", "hablantes")}, ensure_ascii=False, indent=1))


def similitud():
    informe = pg.leer_json(INFORME, {}) or {}
    ref = os.path.join(VOCES, "referencia_usuario.wav")
    if not os.path.exists(ref):
        raise SystemExit("No hay voces/referencia_usuario.wav")
    er = embedding(cargar_audio(ref))
    otras = {}
    for nombre in ("referencia_usuario_larga", "referencia_hablante_2"):
        p = os.path.join(VOCES, nombre + ".wav")
        if os.path.exists(p):
            otras[nombre] = round(float(embedding(cargar_audio(p)) @ er), 3)
    sal = "/tmp/prueba_voz/salida"
    res = {}
    for f in sorted(os.listdir(sal)) if os.path.isdir(sal) else []:
        if f.startswith("voz_") and f.endswith(".mp3"):
            res[f[4:-4]] = round(float(embedding(cargar_audio(os.path.join(sal, f))) @ er), 3)
    informe["similitud_con_referencia"] = {"referencias": otras, "voces_sintetizadas": res,
                                           "lectura": "Coseno Resemblyzer con voces/referencia_usuario.wav. Orientativo: "
                                                      "> 0,80 misma voz; 0,65-0,80 parecida; < 0,65 otra persona. "
                                                      "Pocket/Piper sirven de control (no son la voz del dueño)."}
    with open(INFORME, "w", encoding="utf-8") as f:
        json.dump(informe, f, ensure_ascii=False, indent=2)
    print(json.dumps(informe["similitud_con_referencia"], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else "extraer"
    if modo == "extraer":
        extraer([i for i in (sys.argv[2] if len(sys.argv) > 2 else "").split(",") if i.strip()] or ids_por_defecto())
    elif modo == "similitud":
        similitud()
    else:
        raise SystemExit(__doc__)
