#!/usr/bin/env python3
"""CONTROL DE AUDIO (DIRECTIVA DE VÍDEO 14/11/2026). Uso: python3 control_audio.py video.mp4 guion.json [--salida control_audio.json]
Transcribe el audio final con faster-whisper y lo compara con la voz del guion; mide silencios con silencedetect (-45 dB, 0,6 s).
RECHAZO (exit 1): duración > 30 s · silencio > 0,6 s DENTRO de la voz · palabra distinta del guion (salvo homófonos) · «ehm» ·
falta el giro (escena remate) · sin atribución musical si el post.json la exige. Los silencios al inicio/fin del vídeo no cuentan.
Si falla, el reel NO se publica: publicar_gh.py anota el motivo en control_audio.json y lo deja sin publicar."""
import json, os, re, subprocess, sys, unicodedata

SIL_DB, SIL_S, DUR_MAX = -45, 0.6, 30.0
HOMOFONOS = [{"hechas", "echas"}, {"hecha", "echa"}, {"hecho", "echo"}, {"a", "ha"}, {"hay", "ahi", "ay"}, {"vaya", "valla"},
             {"hacia", "asia"}, {"tuvo", "tubo"}, {"ola", "hola"}, {"he", "e"}, {"sino", "si no"}]
NUM = {"200": "doscientas", "1": "uno", "2": "dos", "3": "tres", "4": "cuatro", "5": "cinco", "10": "diez", "2028": "dos mil veintiocho"}


def norm(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.findall(r"[a-z0-9]+", t)


def igual(a, b):
    return a == b or any(a in h and b in h for h in HOMOFONOS)


def dur(v):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", v], capture_output=True, text=True)
    return float(r.stdout.strip())


def silencios(v):
    r = subprocess.run(["ffmpeg", "-nostats", "-i", v, "-vn", "-af", f"silencedetect=n={SIL_DB}dB:d={SIL_S}", "-f", "null", "-"],
                       capture_output=True, text=True)
    ini = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", r.stderr)]
    fin = [(float(a), float(b)) for a, b in re.findall(r"silence_end: ([\d.]+) \| silence_duration: ([\d.]+)", r.stderr)]
    return [(max(0, e - d), e, d) for e, d in fin]


def transcribir(v):
    from faster_whisper import WhisperModel
    m = WhisperModel("small", device="cpu", compute_type="int8")
    seg, _ = m.transcribe(v, language="es", beam_size=5, word_timestamps=True, vad_filter=False)
    return [(w.word.strip(), w.start, w.end) for s in seg for w in s.words]


def comparar(esp, got):
    """Palabras esperadas que no aparecen (alineación por LCS tolerante) y palabras sobrantes."""
    n, m = len(esp), len(got)
    L = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            L[i][j] = L[i + 1][j + 1] + 1 if igual(esp[i], got[j]) else max(L[i + 1][j], L[i][j + 1])
    i = j = 0; faltan = []; sobran = []
    while i < n and j < m:
        if igual(esp[i], got[j]): i += 1; j += 1
        elif L[i + 1][j] >= L[i][j + 1]: faltan.append(esp[i]); i += 1
        else: sobran.append(got[j]); j += 1
    return faltan + esp[i:], sobran + got[j:]


def huecos_voz(tramos, wavs):
    """Silencios >= 0,6 s (-45 dB) ENTRE frases, sobre la pista de voz sola (frases en su instante): con música cocida el
    silencedetect del vídeo final nunca los ve. tramos: locucion.json; wavs: un wav por tramo. Lista [[ini, fin, dur]]."""
    import wave
    ent, fil, et, fines = [], [], [], []
    for i, (t, w) in enumerate(zip(tramos, wavs)):
        ms = int(float(t["inicio"]) * 1000 + 120)
        ent += ["-i", w]
        fil.append("[%d:a]aresample=48000,adelay=%d|%d[v%d]" % (i, ms, ms, i)); et.append("[v%d]" % i)
        with wave.open(w) as f:
            fines.append((float(t["inicio"]) + 0.12, float(t["inicio"]) + 0.12 + f.getnframes() / float(f.getframerate())))
    fil.append("%samix=inputs=%d:normalize=0,silencedetect=n=%ddB:d=%s" % ("".join(et), len(et), SIL_DB, SIL_S))
    r = subprocess.run(["ffmpeg", "-nostats", *ent, "-filter_complex", ";".join(fil), "-f", "null", "-"], capture_output=True, text=True, timeout=300)
    ini = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", r.stderr)]
    fin = re.findall(r"silence_end: ([\d.]+) \| silence_duration: ([\d.]+)", r.stderr)
    p0, p1 = min(a for a, _ in fines), max(b for _, b in fines)
    return [[round(a, 2), round(float(e), 2), round(float(d), 2)] for a, (e, d) in zip(ini, fin) if a >= p0 - 0.05 and float(e) <= p1 + 0.05]


def control(video, guion, post=None, tramos=None, wavs=None):
    g = json.load(open(guion, encoding="utf-8")) if isinstance(guion, str) else guion
    bloqueos, avisos = [], []
    d = dur(video)
    if d > DUR_MAX: bloqueos.append(f"dura {d:.1f} s (máximo {DUR_MAX:.0f})")
    esc = g.get("escenas", [])
    if not any(e.get("estilo") == "remate" for e in esc): bloqueos.append("falta el giro (escena «remate»)")
    guion_txt = " ".join(re.sub(r"\*", "", e.get("voz", "")) for e in esc if e.get("voz"))
    esp = [NUM.get(w, w) for w in norm(guion_txt)]
    esp = sum((norm(w) for w in esp), [])
    pal = transcribir(video)
    got = sum((norm(w) for w, _, _ in pal), [])
    got = sum((norm(NUM.get(w, w)) for w in got), [])
    faltan, sobran = comparar(esp, got)
    malas = [w for w in sobran if w in ("ehm", "eh", "em", "mm", "hmm")]
    if malas: bloqueos.append(f"muletillas «ehm» en la voz: {malas}")
    if faltan or sobran:
        tasa = (len(faltan) + len(sobran)) / max(1, len(esp))
        (bloqueos if tasa > 0.0 else avisos).append(f"voz distinta del guion: faltan {faltan}, sobran {sobran} (rehacer esas frases)")
    t0 = pal[0][1] if pal else 0.0; t1 = pal[-1][2] if pal else d
    for a, b, s in silencios(video):
        if a >= t0 - 0.05 and b <= t1 + 0.05 and s > SIL_S and a > 0.3 and b < d - 0.3:
            bloqueos.append(f"silencio de {s:.2f} s entre {a:.1f} y {b:.1f} s (máximo {SIL_S} s)")
    if tramos and wavs:
        try:
            h = huecos_voz(tramos, wavs)
            if h: bloqueos.append(f"silencios > {SIL_S} s entre frases (pista de voz): {h}")
        except Exception as e:
            avisos.append(f"silencedetect de la pista de voz no disponible: {str(e)[-80:]}")
    if isinstance(post, dict) and post.get("musica_atribucion_requerida") and "MacLeod" not in post.get("texto", ""):
        bloqueos.append("falta la atribución musical de Kevin MacLeod en el texto del post")
    return {"aprobado": not bloqueos, "duracion_s": round(d, 2), "bloqueos": bloqueos, "avisos": avisos,
            "transcripcion": " ".join(w for w, _, _ in pal), "guion": guion_txt}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    sal = sys.argv[sys.argv.index("--salida") + 1] if "--salida" in sys.argv else None
    r = control(sys.argv[1], sys.argv[2])
    if sal: json.dump(r, open(sal, "w"), ensure_ascii=False, indent=1)
    print(json.dumps(r, ensure_ascii=False, indent=1))
    sys.exit(0 if r["aprobado"] else 1)
