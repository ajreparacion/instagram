#!/usr/bin/env python3
"""Rejilla de parámetros de MeloTTS ES (13/11/2026; la lanza .github/workflows/rejilla_melo.yml, a mano; no publica nada).
Rejilla: sdp_ratio x noise_scale x noise_scale_w (velocidad 1,1, semilla 7) sobre la frase de prueba y las frases con voz de cola/508.
Mide por combinación: expresividad (desviación típica de F0 en semitonos, librosa.pyin, quitando la mediana de cada frase),
estabilidad (clics = picos aislados de alta frecuencia, caídas = huecos de <=60 ms en mitad de voz, recortes; por minuto de voz)
e inteligibilidad (WER de faster-whisper small contra el texto). Elige expresiva / equilibrada / estable, revisa la cadena de voz
(presencia/cuerpo sin subir la sibilancia de 5-9 kHz más de 1 dB ni el suelo de ruido) y genera frase y reel 508 de cada una.
Salida en /tmp/melo/salida: melo_v2_<opcion>_<reel|frase>.mp3 y melo_v2_resultados.json
"""
import copy, itertools, json, os, re, shutil, subprocess, sys, time, unicodedata
import numpy as np
from scipy.signal import resample_poly, butter, sosfilt, medfilt

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE); sys.path.insert(0, os.path.join(BASE, "herramientas"))
import audicion_voces_v2 as a2      # noqa: E402
import publicar_gh as pg            # noqa: E402
import wave                         # noqa: E402

SAL = "/tmp/melo/salida"
GUION = os.path.join(BASE, "cola", "508_jambo_app_gastos_fijos", "guion.json")
GRID = list(itertools.product((0.2, 0.4, 0.6), (0.6, 0.75, 0.9), (0.8, 1.0)))
VEL, SEMILLA = 1.1, 7


def textos_508():
    g = json.load(open(GUION, encoding="utf-8"))
    return [re.sub(r"\s+", " ", e["voz"].replace("*", "")).strip() for e in g["escenas"] if str(e.get("voz") or "").strip()]


def leer(ruta):
    with wave.open(ruta) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        return x, w.getframerate()


def norm(t):
    t = "".join(c for c in unicodedata.normalize("NFD", t.lower()) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9ñ ]", " ", t).split()


def wer(ref, hip):
    r, h = norm(ref), norm(hip)
    d = list(range(len(h) + 1))
    for i in range(1, len(r) + 1):
        p, d[0] = d[0], i
        for j in range(1, len(h) + 1):
            p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (r[i - 1] != h[j - 1]))
    return d[len(h)] / max(len(r), 1)


def f0_st(x, sr):
    import librosa
    y = resample_poly(x, 16000, sr).astype(np.float32)
    f0, vf, _ = librosa.pyin(y, fmin=65, fmax=400, sr=16000, frame_length=1024, hop_length=256)
    f = f0[vf & ~np.isnan(f0)]
    if f.size < 10:
        return np.array([])
    st = 12 * np.log2(f / np.median(f))
    return st


def glitches(x, sr):
    """(clics, caídas, recortes) en una frase."""
    hop = int(sr * 0.005)
    n = len(x) // hop
    if n < 20:
        return 0, 0, 0
    f = x[:n * hop].reshape(n, hop)
    rms = 20 * np.log10(np.sqrt((f ** 2).mean(1)) + 1e-9)
    hf = sosfilt(butter(4, 6000, "hp", fs=sr, output="sos"), x)[:n * hop].reshape(n, hop)
    e = 20 * np.log10(np.sqrt((hf ** 2).mean(1)) + 1e-9)
    med = medfilt(e, 17)
    flag = (e > med + 15) & (e > -50)
    clics = int(np.sum(flag[1:] & ~flag[:-1]) + (1 if flag[0] else 0)) if flag.any() else 0
    # solo cuentan los picos cortos (<=3 tramos de 5 ms); las eses largas no son clics
    clics = 0
    i = 0
    while i < n:
        if flag[i]:
            j = i
            while j < n and flag[j]:
                j += 1
            clics += 1 if (j - i) <= 3 else 0
            i = j
        else:
            i += 1
    pico = np.percentile(rms, 95)
    voz = rms > pico - 20
    caidas = 0
    i = 1
    while i < n - 1:
        if rms[i] < pico - 40 and not voz[i]:
            j = i
            while j < n and rms[j] < pico - 40:
                j += 1
            ancho = j - i
            if 1 <= ancho <= 12 and voz[max(0, i - 3):i].all() and voz[j:j + 3].all() and j + 3 <= n and i >= 3:
                caidas += 1
            i = j
        else:
            i += 1
    recortes = int(np.sum(np.abs(x) >= 0.999))
    return clics, caidas, recortes


def bandas(wav48):
    """dB de bandas respecto a 150-400 Hz, suelo de ruido (percentil 10 de tramos de 20 ms) y LUFS de un archivo."""
    x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", wav48, "-f", "f32le", "-ac", "1", "-ar", "48000", "-"], capture_output=True).stdout, np.float32)
    from scipy.signal import welch
    fr, P = welch(x, 48000, nperseg=4096)
    b = lambda lo, hi: 10 * np.log10(max(1e-20, P[(fr >= lo) & (fr < hi)].sum()))
    ref = b(150, 400)
    h = 960
    nn = len(x) // h
    suelo = float(np.percentile(20 * np.log10(np.sqrt((x[:nn * h].reshape(nn, h) ** 2).mean(1)) + 1e-9), 10))
    m = subprocess.run(["ffmpeg", "-v", "info", "-i", wav48, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    lufs = float([l for l in m.splitlines() if "I:" in l and "LUFS" in l][-1].split("I:")[1].split("LUFS")[0])
    return {"presencia_2.5-4.5k": round(float(b(2500, 4500) - ref), 1), "sibilancia_5-9k": round(float(b(5000, 9000) - ref), 1),
            "aire_9-12k": round(float(b(9000, 12000) - ref), 1), "suelo_dBFS": round(suelo, 1), "LUFS": lufs}


def melo_lote(frases, nombre, extra=None):
    lote = {"idioma": "ES", "speaker": "ES", "velocidad": VEL, "ganancia": 1.0, "semilla": SEMILLA,
            "pronunciacion": pg.ajustes_voz()["melo"].get("pronunciacion") or {}, "frases": frases}
    lote.update(extra or {})
    j = f"{a2.RAW}/{nombre}.json"
    json.dump(lote, open(j, "w"), ensure_ascii=False)
    r = subprocess.run([os.environ.get("PYTHON_MELO") or sys.executable, os.path.join(BASE, "herramientas", "voz_melo.py"), j], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit("melo falló: " + (r.stderr or r.stdout)[-400:])


def main():
    os.makedirs(a2.RAW, exist_ok=True); os.makedirs(SAL, exist_ok=True); a2.SAL = SAL
    textos = [a2.FRASE] + textos_508()
    nombre = lambda c: "s%.1f_n%.2f_w%.1f" % c
    frases = []
    for c in GRID:
        for i, t in enumerate(textos):
            frases.append({"texto": t, "salida": f"{a2.RAW}/g_{nombre(c)}_{i}.wav", "sdp_ratio": c[0], "noise_scale": c[1], "noise_scale_w": c[2]})
    t0 = time.time()
    melo_lote(frases, "rejilla")
    print(f"síntesis de {len(frases)} frases: {time.time() - t0:.0f} s", flush=True)
    from faster_whisper import WhisperModel
    wh = WhisperModel("small", device="cpu", compute_type="int8")
    res = {}
    for c in GRID:
        st, gl, minutos, errores, palabras = [], [0, 0, 0], 0.0, 0.0, 0
        for i, t in enumerate(textos):
            x, sr = leer(f"{a2.RAW}/g_{nombre(c)}_{i}.wav")
            minutos += len(x) / sr / 60
            st.append(f0_st(x, sr))
            for k, v in enumerate(glitches(x, sr)):
                gl[k] += v
            segs, _ = wh.transcribe(resample_poly(x, 16000, sr).astype(np.float32), language="es", beam_size=5)
            hip = " ".join(s.text for s in segs)
            n = len(norm(t)); errores += wer(t, hip) * n; palabras += n
        st = np.concatenate([s for s in st if s.size]) if any(s.size for s in st) else np.array([0.0])
        res[nombre(c)] = {"sdp_ratio": c[0], "noise_scale": c[1], "noise_scale_w": c[2], "f0_std_st": round(float(st.std()), 2),
                          "WER": round(errores / palabras, 3), "clics": gl[0], "caidas": gl[1], "recortes": gl[2],
                          "glitches_min": round((gl[0] + gl[1]) / minutos, 2), "voz_s": round(minutos * 60, 1)}
        print(nombre(c), res[nombre(c)], flush=True)

    # --- elección: expresiva, equilibrada, estable
    ks = list(res)
    wmin = min(res[k]["WER"] for k in ks); gmin = min(res[k]["glitches_min"] for k in ks)
    ok = [k for k in ks if res[k]["WER"] <= wmin + 0.03 and res[k]["glitches_min"] <= gmin + 1.0] or ks
    expresiva = max(ok, key=lambda k: res[k]["f0_std_st"])
    estable = min(ks, key=lambda k: (res[k]["glitches_min"] + res[k]["recortes"], res[k]["WER"], -res[k]["f0_std_st"]))
    z = lambda v, a: (v - np.mean(a)) / (np.std(a) + 1e-9)
    F = [res[k]["f0_std_st"] for k in ks]; W = [res[k]["WER"] for k in ks]; G = [res[k]["glitches_min"] for k in ks]
    punt = {k: z(res[k]["f0_std_st"], F) - z(res[k]["WER"], W) - z(res[k]["glitches_min"], G) for k in ks}
    equilibrada = max([k for k in ks if k not in (expresiva, estable)] or ks, key=lambda k: punt[k])
    elegidas = {"expresiva": expresiva, "equilibrada": equilibrada, "estable": estable}

    # --- cadena: variantes de presencia/cuerpo con la sibilancia de 5-9 kHz limitada (+1 dB) y el suelo de ruido sin subir
    cadena0 = pg.ajustes_voz()["cadena_voz"].strip().strip(",")
    ref = elegidas["equilibrada"]
    lista = [f"{a2.RAW}/g_{ref}_{i}.wav" for i in range(1, len(textos))]
    cat = f"{a2.RAW}/cat_ref.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *sum([["-i", f] for f in lista], []), "-filter_complex",
                    "".join(f"[{i}:a]aresample=48000,apad=pad_dur=0.3[a{i}];" for i in range(len(lista))) + "".join(f"[a{i}]" for i in range(len(lista))) + f"concat=n={len(lista)}:v=0:a=1[o]",
                    "-map", "[o]", "-ac", "1", cat], check=True)
    ins = lambda extra: cadena0.replace(",deesser=", "," + extra + ",deesser=") if extra else cadena0
    variantes = {"A_actual": "", "B_cuerpo+1_pres+1": "equalizer=f=170:t=q:w=0.9:g=1,equalizer=f=2800:t=q:w=1.0:g=1",
                 "C_cuerpo+1.5_pres+2": "equalizer=f=170:t=q:w=0.9:g=1.5,equalizer=f=2800:t=q:w=1.0:g=2",
                 "D_pres+2_sin_cuerpo": "equalizer=f=2800:t=q:w=1.0:g=2",
                 "E_cuerpo+2_pres+1": "equalizer=f=170:t=q:w=0.9:g=2,equalizer=f=2800:t=q:w=1.0:g=1"}
    medidas = {}
    for nm, extra in variantes.items():
        a2.CADENA = ins(extra)
        a2.postprocesar(cat, "cad_" + nm[0])
        medidas[nm] = bandas(f"{a2.SAL}/cad_{nm[0]}.mp3")
        medidas[nm]["cadena_extra"] = extra
        os.remove(f"{a2.SAL}/cad_{nm[0]}.mp3")
        print("cadena", nm, medidas[nm], flush=True)
    A = medidas["A_actual"]
    validas = [nm for nm, m in medidas.items() if m["sibilancia_5-9k"] <= A["sibilancia_5-9k"] + 1.0 and m["suelo_dBFS"] <= A["suelo_dBFS"] + 1.0 and abs(m["LUFS"] + 14) <= 0.6]
    mejor = max(validas, key=lambda nm: (medidas[nm]["presencia_2.5-4.5k"], nm == "A_actual"))
    cadena = ins(variantes[mejor])
    a2.CADENA = cadena
    print("cadena elegida:", mejor, flush=True)

    # --- frase y reel 508 de cada opción (con la cadena elegida)
    base_aj = pg.ajustes_voz()
    salida = {}
    for opc, k in elegidas.items():
        r = res[k]
        extra = {"sdp_ratio": r["sdp_ratio"], "noise_scale": r["noise_scale"], "noise_scale_w": r["noise_scale_w"]}
        melo_lote([{"texto": a2.FRASE, "salida": f"{a2.RAW}/f_{opc}.wav"}], "f_" + opc, extra)
        a2.postprocesar(f"{a2.RAW}/f_{opc}.wav", f"melo_v2_{opc}_frase")
        aj = copy.deepcopy(base_aj)
        aj["cadena_voz"] = cadena
        aj["melo"].update(extra); aj["melo"]["velocidad"] = VEL; aj["melo"]["semilla"] = SEMILLA
        pg.ajustes_voz = lambda aj=aj: aj
        trabajo = f"/tmp/melo/render_{opc}"; shutil.rmtree(trabajo, ignore_errors=True); os.makedirs(trabajo)
        video = os.path.join(trabajo, "video.mp4")
        t1 = time.time()
        motor = pg.renderizar_guion(GUION, video, trabajo)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vn", "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "48000", f"{SAL}/melo_v2_{opc}_reel.mp3"], check=True)
        salida[opc] = {"combinacion": k, "motor": motor, "render_s": round(time.time() - t1, 1), **res[k],
                       "reel": bandas(f"{SAL}/melo_v2_{opc}_reel.mp3")}
        print(opc, salida[opc], flush=True)
    json.dump({"rejilla": res, "elegidas": salida, "cadena": {"elegida": mejor, "cadena_voz": cadena, "medidas": medidas}, "aj_base_cadena": cadena0},
              open(f"{SAL}/melo_v2_resultados.json", "w"), ensure_ascii=False, indent=1, default=float)


if __name__ == "__main__":
    main()
