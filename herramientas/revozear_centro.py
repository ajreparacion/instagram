#!/usr/bin/env python3
"""Rehace la VOZ de un vídeo del Centro con Chatterbox y su voz integrada en español (sin muestra) — orden del dueño 12/11/2026.

«Se oye como si fuera telefónica»: la voz original viene recortada a ~4 kHz porque Chatterbox imitaba una muestra recortada.
Para el vídeo número N de videos/pistas/manifest.json: transcribe su voz por tramos (faster-whisper, mismo texto, nada nuevo),
la vuelve a decir con Chatterbox es-es SIN referencia, coloca cada frase en su sitio (acelerando como mucho un 30 % si no cabe),
le pasa equipo/voz.json → cadena_voz, la mezcla con su música (bajando la música bajo la voz) a -14 LUFS y sustituye el mp4 en la
release «centro-v3» con el MISMO nombre, así las colas de atrasos no cambian. La transcripción queda en atrasos/textos/ para Calidad.
Uso (en Actions): python3 herramientas/revozear_centro.py N
"""
import json
import os
import subprocess
import sys
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CENTRO = "https://centro-de-contenido-apps-2f0a3cd6.base44.app"
RELEASE = "centro-v3"
REPO = os.environ.get("GITHUB_REPOSITORY", "ajreparacion/instagram")
PY_CB = os.environ.get("PYTHON_CHATTERBOX") or sys.executable
VOCAB = ("Neogest Lab, Gestión Integral 7D, MEDICATOR, AJ Sistema, AJ Reparación, ajreparacion.com, Studio Beats PRO, "
         "GPS Andaluz, CIMA, AEMPS, Bizum, Redsys, PDF, IVA, albarán, presupuesto, prueba gratuita.")


def sh(*a):
    r = subprocess.run(a, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"{a[0]} falló: {r.stderr[-500:]}")
    return r.stdout


def dur(f):
    return float(sh("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f).strip())


def main(n):
    voz_cfg = json.load(open(os.path.join(RAIZ, "equipo", "voz.json")))
    cadena = voz_cfg["cadena_voz"].strip().strip(",")
    cb = voz_cfg.get("chatterbox", {})
    man = [v for v in json.load(urllib.request.urlopen(CENTRO + "/videos/pistas/manifest.json"))["videos"]
           if v["formato"] in ("vertical", "reel", "horizontal")]
    if n >= len(man):
        print("nada que hacer", n)
        return
    v = man[n]
    nombre = f"{v['slug']}-{v['formato']}"
    t = f"/tmp/rv_{n}"
    os.makedirs(t, exist_ok=True)
    rutas = {}
    for k in ("video", "voz", "musica", "segmentos"):
        rutas[k] = os.path.join(t, k + os.path.splitext(v[k])[1])
        urllib.request.urlretrieve(CENTRO + v[k], rutas[k])
    tramos = json.load(open(rutas["segmentos"]))["voz"]

    # 1) transcripción por palabra y reparto en tramos
    from faster_whisper import WhisperModel
    m = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(rutas["voz"], language="es", word_timestamps=True, initial_prompt=VOCAB, vad_filter=False)
    palabras = [w for s in segs for w in (s.words or [])]
    textos = []
    for a, b in tramos:
        ws = [w.word.strip() for w in palabras if a - 0.15 <= (w.start + w.end) / 2 <= b + 0.15]
        textos.append(" ".join(x for x in ws if x).strip())
    os.makedirs(os.path.join(RAIZ, "atrasos", "textos"), exist_ok=True)
    json.dump([{"inicio": a, "fin": b, "texto": tx} for (a, b), tx in zip(tramos, textos)],
              open(os.path.join(RAIZ, "atrasos", "textos", f"{nombre}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # 2) voz nueva: Chatterbox es-es con su voz integrada (sin referencia)
    frases = [{"texto": tx, "salida": os.path.join(t, f"f{i}.wav")} for i, tx in enumerate(textos) if tx]
    lote = {"modelo": cb.get("modelo", "es-es"), "idioma": "es", "exageracion": cb.get("exageracion", 0.6),
            "cfg": cb.get("cfg", 0.5), "temperatura": cb.get("temperatura", 0.65), "referencia": None,
            "ganancia": 1.0, "semilla": cb.get("semilla", 7), "theta": "", "frases": frases}
    json.dump(lote, open(os.path.join(t, "lote.json"), "w"), ensure_ascii=False)
    print(sh(PY_CB, os.path.join(RAIZ, "herramientas", "voz_chatterbox.py"), os.path.join(t, "lote.json"))[-400:])

    # 3) colocar cada frase en su tramo
    entradas, filtros, etiquetas = [], [], []
    k = 0
    for i, ((a, b), tx) in enumerate(zip(tramos, textos)):
        if not tx:
            continue
        w = os.path.join(t, f"f{i}.wav")
        sig = tramos[i + 1][0] if i + 1 < len(tramos) else v["duracion"]
        hueco = max(sig - a - 0.08, 0.5)
        tempo = min(max(dur(w) / hueco, 1.0), 1.3)
        entradas += ["-i", w]
        ms = int(a * 1000)
        filtros.append(f"[{k}:a]aresample=48000,atempo={tempo:.3f},adelay={ms}|{ms}[v{k}]")
        etiquetas.append(f"[v{k}]")
        k += 1
    filtros.append(f"{''.join(etiquetas)}amix=inputs={k}:normalize=0,apad,atrim=0:{v['duracion']:.3f}[vz]")
    vozn = os.path.join(t, "voz_nueva.wav")
    sh("ffmpeg", "-v", "error", "-y", *entradas, "-filter_complex", ";".join(filtros), "-map", "[vz]", vozn)

    # 4) cadena + mezcla con la música + máster, y sustituir en la release con el mismo nombre
    salida = os.path.join(t, f"{nombre}-v3.mp4")
    fc = (f"[1:a]aresample=48000,{cadena},asplit=2[vx][key];"
          f"[2:a]aresample=48000,volume=0.9[m];[m][key]sidechaincompress=threshold=0.03:ratio=6:attack=15:release=350:makeup=1[md];"
          f"[md][vx]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    sh("ffmpeg", "-v", "error", "-y", "-i", rutas["video"], "-i", vozn, "-i", rutas["musica"], "-filter_complex", fc,
       "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest",
       "-movflags", "+faststart", salida)
    sh("gh", "release", "upload", RELEASE, salida, "--clobber", "-R", REPO)
    print("rehecho:", nombre, f"{k} frases")


if __name__ == "__main__":
    main(int(sys.argv[1]))
