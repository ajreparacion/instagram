#!/usr/bin/env python3
"""Modo presentador: de un guion.json de cola/ a un reel MP4 1080x1920 a 30 fps listo para la release «cola».

Uso (lo lanza .github/workflows/presentador.yml):
  python3 herramientas/presentador/preparar.py cola/<carpeta>/guion.json [--sin-voz] [--subir]
      [--solo-plan] [--navegador RUTA] [--concurrencia N] [--escala 1.0]

Pasos: capturas reales del Centro de Contenido Apps -> voz del dueño (tubería de publicar_gh.py: equipo/voz.json,
voz_dueno/, alineación por palabra) -> tiempos de cada escena ajustados a la voz -> música y efectos generados por
código y máster a -14 LUFS (audio.py) -> render de Remotion + three.js en CPU (SwiftShader) -> mezcla final ->
control de calidad (sonoridad, movimiento, fotogramas de control) -> release «cola» + post.json con "renderizado".

Formato del guion: ver equipo/INSTRUCCIONES_EQUIPO.md, «Modo presentador», y los pilotos en cola/30x_*.
Técnica basada en «claude-animated-shorts» de Mr omi (MIT, ver CREDITOS.md).
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import unicodedata
import urllib.request
from datetime import datetime, timezone

import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, AQUI)
import audio  # noqa: E402

FPS = 30
ORIGEN = "https://centro-de-contenido-apps-2f0a3cd6.base44.app"
RELEASE = "cola"
SALIDA = "/tmp/presentador_salida"
GIROS = [0.0, 0.2, -0.16, 0.08, -0.22, 0.14, -0.07, 0.24, -0.12]
SEGUNDO_FONDO = {"magenta": "morado", "verde": "turquesa", "morado": "magenta", "cian": "azul", "rojo": "magenta",
                 "negro": "morado", "azul": "cian", "turquesa": "verde", "naranja": "rojo", "rosa": "morado", "amarillo": "naranja"}
ELEMENTOS_ARRIBA = {"captura", "terminal", "movil", "tarjeta", "cierre"}
EXPRESION_POR_POSE = {"preocupada": "preocupada", "sorpresa": "sorpresa", "celebra": "risa", "piensa": "piensa",
                      "saluda": "feliz", "encoge": "seria", "pulgar": "guino"}


def log(*a):
    print("[presentador]", *a, flush=True)


def leer(ruta, defecto=None):
    try:
        with open(ruta, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return defecto


def escribir(ruta, datos):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)


def normal(w):
    w = unicodedata.normalize("NFD", w.lower())
    w = "".join(c for c in w if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9ñ]+", "", w)


def parsear_enfasis(texto):
    """'*palabra*' marca énfasis (voz más fuerte y palabra en color). Devuelve (texto limpio, índices)."""
    texto = (texto or "").strip()
    idx, out, k, dentro = [], [], 0, False
    for tok in texto.split():
        abre = tok.startswith("*")
        cierra = tok.rstrip(".,;:!?…\"»)").endswith("*") or tok.endswith("*")
        t = tok.replace("*", "")
        if not t:
            continue
        if abre:
            dentro = True
        if dentro:
            idx.append(k)
        if cierra:
            dentro = False
        out.append(t)
        k += 1
    return " ".join(out), idx


# ---------------------------------------------------------------- capturas
def descargar_capturas(guion, publico):
    destino = os.path.join(publico, "capturas")
    os.makedirs(destino, exist_ok=True)
    for i, esc in enumerate(guion["escenas"]):
        el = esc.get("elemento") or {}
        img = el.get("imagen")
        if not img:
            continue
        url = img if img.startswith("http") else ORIGEN + img
        ext = os.path.splitext(img.split("?")[0])[1] or ".png"
        nombre = hashlib.sha1(url.encode()).hexdigest()[:12] + ext
        ruta = os.path.join(destino, nombre)
        if not os.path.exists(ruta):
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (presentador Neogest Lab)"})
            with urllib.request.urlopen(req, timeout=60) as r, open(ruta, "wb") as f:
                f.write(r.read())
            log(f"captura {img} -> {nombre} ({os.path.getsize(ruta) // 1024} KB)")
        el["src"] = f"capturas/{nombre}"


def preparar_publico(publico):
    os.makedirs(os.path.join(publico, "fonts"), exist_ok=True)
    os.makedirs(os.path.join(publico, "marca"), exist_ok=True)
    mont = os.path.join(BASE, "herramientas", "fonts", "Montserrat-VF.ttf")
    if os.path.exists(mont):
        shutil.copy(mont, os.path.join(publico, "fonts", "Montserrat-VF.ttf"))
    logo = os.path.join(BASE, "equipo", "perfil_kit", "logo_neogest_lab_oficial.png")
    shutil.copy(logo, os.path.join(publico, "marca", "logo.png"))


# ---------------------------------------------------------------- voz
def generar_voz(textos, estilos, enfasis, trabajo, avisos):
    """Voz del dueño con la misma tubería que publicar_gh.py. Devuelve (wavs procesados, palabras, motor) o None."""
    sys.path.insert(0, BASE)
    try:
        import publicar_gh as pg
    except Exception as e:
        avisos.append(f"no se pudo cargar publicar_gh: {e}")
        return None
    loc = os.path.join(trabajo, "locucion.json")
    escribir(loc, [{"texto": t, "estilo": s, "enfasis": en} for t, s, en in zip(textos, estilos, enfasis)])
    try:
        tramos, wavs, motor, aj = pg.preparar_voz(loc, trabajo)
    except Exception as e:
        avisos.append(f"voz no disponible: {str(e)[-300:]}")
        return None
    if motor == "piper":
        avisos.append("la voz salió con Piper (respaldo), no con la voz del dueño")
    cadena = aj.get("cadena_voz") or ""
    salida, palabras = [], []
    for i, ((w, _), tr) in enumerate(zip(wavs, tramos)):
        p = os.path.join(trabajo, f"voz_cadena_{i}.wav")
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", w]
        if cadena:
            cmd += ["-af", cadena]
        cmd += ["-ac", "1", "-ar", str(audio.SR), p]
        subprocess.run(cmd, check=True)
        salida.append(p)
        palabras.append(tr.get("palabras"))
    return salida, palabras, motor


def estimar_palabras(texto, dur):
    pal = texto.split()
    pesos = np.array([len(re.sub(r"[^\wáéíóúñü]", "", p)) + 2.0 for p in pal])
    lim = np.concatenate([[0], np.cumsum(pesos)]) / pesos.sum() * dur
    return [[round(lim[i], 3), round(lim[i + 1], 3)] for i in range(len(pal))]


# ---------------------------------------------------------------- plan
def construir_plan(guion, durs_voz, palabras_voz):
    escenas, eventos, golpes_musica = [], [], []
    t = 0.0
    n = len(guion["escenas"])
    for i, esc in enumerate(guion["escenas"]):
        texto, enf = parsear_enfasis(esc.get("voz", ""))
        dv = durs_voz[i]
        pre = 0.0 if i == 0 else 0.06
        post = 0.16 if texto else 0.0
        d = max(float(esc.get("min", 1.3)), pre + dv + post + float(esc.get("extra", 0)))
        ini, fin = t, t + d
        a, b = round(ini * FPS), round(fin * FPS)
        t = fin
        # palabras en fotogramas
        claves = {normal(c) for c in esc.get("clave", [])}
        pals = []
        tiempos = palabras_voz[i] or estimar_palabras(texto, dv)
        for k, (w, (pa, pb)) in enumerate(zip(texto.split(), tiempos)):
            pals.append({"t": w, "a": round((ini + pre + pa) * FPS), "b": round((ini + pre + pb) * FPS),
                         "clave": k in enf or normal(w) in claves})
        # subcorte: en frases largas se cambia de cámara y de fondo a mitad (cortes cada 2-4 s, como la referencia)
        sub_f = None
        tipo_el = (esc.get("elemento") or {}).get("tipo")
        if d > 3.6 and len(pals) >= 4 and esc.get("subcorte", tipo_el not in ("tarjeta", "cierre", "terminal", "movil")):
            medio = (a + b) / 2
            cand = [w["a"] for w in pals[1:] if w["a"] - a > 1.3 * FPS and b - w["a"] > 1.2 * FPS]
            if cand:
                sub_f = min(cand, key=lambda x: abs(x - medio)) - 1
        el_g = esc.get("elemento")
        tipo = (el_g or {}).get("tipo")
        plano = esc.get("plano") or ("abajo" if tipo in ELEMENTOS_ARRIBA else "medio")
        pose = esc.get("presentador", "explica")
        e = {
            "a": a, "b": b, "fondo": esc.get("fondo", "morado"), "presentador": pose,
            "expresion": esc.get("expresion") or EXPRESION_POR_POSE.get(pose, "feliz"),
            "lado": int(esc.get("lado", 1)), "bit": esc.get("bit", "flota"), "plano": plano,
            "giro": float(esc.get("giro", GIROS[i % len(GIROS)])), "palabras": pals, "golpes": [],
        }
        if esc.get("bit_cara"):
            e["bit_cara"] = esc["bit_cara"]
        if sub_f:
            e["sub"] = sub_f
            vecinos = {e["fondo"], guion["escenas"][i + 1].get("fondo", "morado") if i + 1 < n else ""}
            opciones = [SEGUNDO_FONDO.get(e["fondo"], "morado"), "morado", "magenta", "cian", "verde", "azul", "turquesa"]
            e["fondo2"] = esc.get("fondo2") or next(c for c in opciones if c not in vecinos)
            eventos.append((sub_f / FPS, "whoosh", 0.4))
        if tipo == "broll":
            e["oculto"] = True
        # titular
        if esc.get("titular"):
            e["titular"] = esc["titular"]
            e["titular_estilo"] = esc.get("estilo_titular", "amarillo")
            e["titular_f"] = a + (0 if i == 0 else 2)
            nl = len(esc["titular"].split("|")) if "|" in esc["titular"] else max(1, len(esc["titular"]) // 13 + 1)
            if e["titular_estilo"] == "sello":
                e["golpes"].append(e["titular_f"] + 5)
                eventos.append(((e["titular_f"] + 5) / FPS, "golpe", 0.9))
            else:
                for k in range(nl):
                    eventos.append(((e["titular_f"] + 3 * k + 2) / FPS, "pop", 0.75))
        # elemento
        if el_g:
            el = {k: v for k, v in el_g.items() if k not in ("imagen", "entra")}
            el["f"] = a + round(float(el_g.get("entra", 0.1)) * FPS)
            if tipo in ("captura", "movil", "terminal", "tarjeta"):
                eventos.append((el["f"] / FPS, "whoosh_corto", 0.7))
                eventos.append(((el["f"] + 9) / FPS, "pop", 0.6))
            if tipo == "broll":
                eventos.append((el["f"] / FPS, "whoosh_corto", 0.6))
            if tipo == "tarjeta":
                items = el.get("items", [])
                f0 = el["f"] + 10
                gap = max(7, min(16, (b - 14 - f0) // max(1, len(items))))
                el["checks"] = [f0 + k * gap for k in range(len(items))]
                for k, fc in enumerate(el["checks"]):
                    eventos.append((fc / FPS, f"ding{86 + 2 * k}", 0.55))
                if el.get("pegatina"):
                    el["pegatina_f"] = min(b - 4, (el["checks"][-1] if el["checks"] else f0) + 10)
                    eventos.append((el["pegatina_f"] / FPS, "pop", 0.8))
            if tipo == "terminal":
                chars = sum(len(x) for x in el.get("lineas", []))
                t0 = el["f"] + 6
                t1 = min(b - 8, t0 + int(chars * 1.1))
                el["tipeo"] = [t0, t1]
                for fk in range(t0, t1, 2):
                    eventos.append((fk / FPS, "tecla", 0.35))
            if tipo == "movil":
                ms = el.get("mensajes", [])
                gap = max(10, min(30, (b - el["f"] - 20) // max(1, len(ms))))
                for k, m in enumerate(ms):
                    m["f"] = el["f"] + 8 + k * gap
                    eventos.append((m["f"] / FPS, "burbuja", 0.6))
            if tipo == "cierre":
                eventos.append(((el["f"] + 6) / FPS, "ding91", 0.6))
            e["elemento"] = el
        # Bit
        bit = e["bit"]
        if bit == "entra":
            eventos.append(((a + 2) / FPS, "whoosh_corto", 0.6))
        elif bit in ("salta", "celebra"):
            for k in range(3):
                eventos.append(((a + k * 12.5) / FPS, "boing", 0.4))
        elif bit == "sorpresa":
            eventos.append((a / FPS, "boing", 0.45))
        elif bit == "gira":
            eventos.append((a / FPS, "whoosh_corto", 0.45))
        # corte
        if i > 0:
            eventos.append((ini, "whoosh", 0.5))
        escenas.append(e)
        if esc.get("flash") and i + 1 < n:
            golpes_musica.append(fin)
            eventos.append((fin, "golpe", 0.7))
            eventos.append((fin, "riser", 0.45))
    for i, esc in enumerate(guion["escenas"]):
        if esc.get("flash") and i + 1 < len(escenas):
            escenas[i + 1]["flash"] = escenas[i + 1]["a"]
    total = t
    frames = round(total * FPS)
    escenas[-1]["b"] = frames
    plan = {"frames": frames, "fps": FPS, "escenas": escenas, "boca": [], "acento": guion.get("acento", "#1f5bff"),
            "app": guion.get("app", ""), "marca": {"logo": "marca/logo.png", "firma": "By Neogest Lab"}}
    return plan, eventos, golpes_musica, total


def boca_sin_voz(plan):
    """sin voz: la boca se mueve con las palabras (sílabas aproximadas) para que siga pareciendo que habla"""
    b = np.zeros(plan["frames"] + 2)
    for e in plan["escenas"]:
        for w in e["palabras"]:
            for f in range(w["a"], min(w["b"], len(b))):
                b[f] = 0.25 + 0.55 * abs(np.sin((f - w["a"]) * 0.9))
    return b


# ---------------------------------------------------------------- render
def render(plan_ruta, salida, args):
    cmd = ["npx", "remotion", "render", "src/index.ts", "Presentador", salida, f"--props={plan_ruta}",
           "--gl=swangle", f"--concurrency={args.concurrencia or os.cpu_count() or 2}", "--codec=h264", "--crf=17",
           "--pixel-format=yuv420p", "--muted", "--timeout=180000", "--log=info", f"--scale={args.escala}"]
    if args.navegador:
        cmd.append(f"--browser-executable={args.navegador}")
    log(" ".join(cmd))
    t0 = time.time()
    r = subprocess.run(cmd, cwd=AQUI)
    if r.returncode != 0 or not os.path.exists(salida):
        raise SystemExit("El render de Remotion falló")
    return time.time() - t0


def movimiento(video):
    """diferencia media entre fotogramas (10 fps, 108x192, gris): planos congelados y cortes"""
    W, H = 108, 192
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", video, "-vf", f"fps=10,scale={W}:{H},format=gray",
                        "-f", "rawvideo", "-"], capture_output=True, check=True)
    x = np.frombuffer(r.stdout, np.uint8).reshape(-1, H, W).astype(np.float32)
    d = np.abs(np.diff(x, axis=0)).mean(axis=(1, 2))
    quieto = d < 0.35
    racha = maxr = 0
    for q in quieto:
        racha = racha + 1 if q else 0
        maxr = max(maxr, racha)
    return {"diferencia_media": round(float(d.mean()), 2), "fotogramas_quietos_pct": round(100 * float(quieto.mean()), 1),
            "plano_quieto_max_s": round(maxr / 10, 1), "cortes_detectados": int((d > 14).sum()),
            "medido_con": "ffmpeg 10 fps 108x192, |diferencia| media por fotograma"}


def fotogramas_control(video, plan, carpeta_control, hoja):
    os.makedirs(carpeta_control, exist_ok=True)
    for f in os.listdir(carpeta_control):
        os.remove(os.path.join(carpeta_control, f))
    tiempos = [0.4]
    for e in plan["escenas"]:
        tiempos.append(((e["a"] + e["b"]) / 2) / FPS)
    tiempos.append((plan["frames"] - 8) / FPS)
    rutas = []
    for k, t in enumerate(tiempos):
        p = os.path.join(carpeta_control, f"{k:02d}_{t:05.1f}s.jpg")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1",
                        "-vf", "scale=360:640", "-q:v", "4", p], check=True)
        rutas.append(p)
    try:
        from PIL import Image
        ims = [Image.open(p) for p in rutas]
        cols = min(6, len(ims))
        filas = (len(ims) + cols - 1) // cols
        s = Image.new("RGB", (cols * 360, filas * 640), "black")
        for i, im in enumerate(ims):
            s.paste(im, ((i % cols) * 360, (i // cols) * 640))
        s.save(hoja, quality=82)
    except Exception as e:
        log(f"sin hoja de control: {e}")
    return rutas


# ---------------------------------------------------------------- principal
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("guion")
    ap.add_argument("--sin-voz", action="store_true")
    ap.add_argument("--subir", action="store_true")
    ap.add_argument("--solo-plan", action="store_true")
    ap.add_argument("--sin-capturas", action="store_true", help="pruebas locales sin acceso a *.base44.app")
    ap.add_argument("--navegador")
    ap.add_argument("--concurrencia", type=int)
    ap.add_argument("--escala", type=float, default=1.0)
    args = ap.parse_args()
    t_ini = time.time()
    ruta_guion = os.path.abspath(args.guion)
    carpeta = os.path.dirname(ruta_guion)
    nombre = os.path.basename(carpeta)
    guion = leer(ruta_guion)
    if not guion or not guion.get("escenas"):
        raise SystemExit(f"guion vacío o ilegible: {args.guion}")
    trabajo = f"/tmp/presentador_{nombre}"
    shutil.rmtree(trabajo, ignore_errors=True)
    os.makedirs(trabajo)
    os.makedirs(SALIDA, exist_ok=True)
    publico = os.path.join(AQUI, "public")
    preparar_publico(publico)
    avisos = []
    if not args.sin_capturas:
        descargar_capturas(guion, publico)
    else:
        for esc in guion["escenas"]:
            el = esc.get("elemento") or {}
            if el.get("imagen"):
                el["src"] = el.get("src_local", "")
    # voz
    textos, estilos, enfasis = [], [], []
    for i, esc in enumerate(guion["escenas"]):
        tx, en = parsear_enfasis(esc.get("voz", ""))
        textos.append(tx)
        estilos.append(esc.get("estilo_voz") or ("gancho" if i == 0 else "cierre" if i == len(guion["escenas"]) - 1 else ""))
        enfasis.append(en)
    t_voz = time.time()
    voz = None
    if not args.sin_voz and guion.get("voz", True):
        idx = [i for i, t in enumerate(textos) if t]
        res = generar_voz([textos[i] for i in idx], [estilos[i] for i in idx], [enfasis[i] for i in idx], trabajo, avisos)
        if res:
            wavs = [None] * len(textos)
            pals = [None] * len(textos)
            for j, i in enumerate(idx):
                wavs[i], pals[i] = res[0][j], res[1][j]
            voz = (wavs, pals, res[2])
    t_voz = time.time() - t_voz
    if voz:
        datos_voz = [audio.leer_wav(w) if w else np.zeros(0) for w in voz[0]]
        durs = [len(x) / audio.SR for x in datos_voz]
        palabras = voz[1]
    else:
        if not args.sin_voz:
            avisos.append("reel sin voz (titulares y subtítulos); la voz queda para un segundo paso")
        datos_voz = None
        durs = [len(t) / 14.5 + 0.25 if t else 0 for t in textos]
        palabras = [None] * len(textos)
    plan, eventos, golpes_mus, total = construir_plan(guion, durs, palabras)
    log(f"{len(plan['escenas'])} escenas, {total:.1f} s, {plan['frames']} fotogramas")
    if not 25 <= total <= 45:
        avisos.append(f"duración {total:.1f} s fuera de 25-45 s")
    # pista de voz, énfasis (+3 dB en las palabras marcadas) y boca
    n = int(np.ceil(total * audio.SR)) + 1
    v = None
    if datos_voz:
        v = np.zeros(n)
        for i, (x, e) in enumerate(zip(datos_voz, plan["escenas"])):
            if not len(x):
                continue
            pre = 0.0 if i == 0 else 0.06
            i0 = audio.ns(e["a"] / FPS + pre)
            g = np.ones(len(x))
            _, enf = parsear_enfasis(guion["escenas"][i].get("voz", ""))
            if palabras[i]:
                for k in enf:
                    if k < len(palabras[i]):
                        pa, pb = palabras[i][k]
                        g[audio.ns(pa):audio.ns(pb)] = 10 ** (3 / 20)
                g = np.convolve(g, np.ones(480) / 480, mode="same")
            m = min(len(x), n - i0)
            v[i0:i0 + m] += (x * g)[:m]
        boca = audio.envolvente_voz(v, FPS)
    else:
        boca = boca_sin_voz(plan)
    plan["boca"] = [round(float(b), 3) for b in boca[:plan["frames"] + 1]]
    props = os.path.join(trabajo, "props.json")
    escribir(props, {"plan": plan})
    shutil.copy(props, os.path.join(SALIDA, f"{nombre}_props.json"))
    # música, efectos y máster
    mus_cfg = guion.get("musica") or {}
    cortes = [e["a"] / FPS for e in plan["escenas"]]
    mus = audio.musica(total, mus_cfg.get("estilo", "pop"), mus_cfg.get("bpm"), mus_cfg.get("tono", 0),
                       int(guion.get("semilla", 7)), golpes=golpes_mus, cortes=cortes)
    sfx = audio.efectos(sorted(eventos), total)
    wav_final = os.path.join(trabajo, "audio.wav")
    inf_audio = audio.mezclar(v[:len(mus)] if v is not None else None, mus, sfx, trabajo, wav_final)
    log(f"audio: {inf_audio}")
    if args.solo_plan:
        shutil.copy(wav_final, os.path.join(SALIDA, f"{nombre}_audio.wav"))
        log("solo plan: listo en", trabajo)
        return
    # render
    mudo = os.path.join(trabajo, "mudo.mp4")
    t_render = render(props, mudo, args)
    final = os.path.join(SALIDA, f"{nombre}.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mudo, "-i", wav_final, "-map", "0:v:0", "-map", "1:a:0",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", final],
                   check=True)
    med = audio.lufs(final)
    mov = movimiento(final)
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", final],
                               capture_output=True, text=True).stdout.strip())
    fotogramas_control(final, plan, os.path.join(carpeta, "control"), os.path.join(SALIDA, f"{nombre}_hoja.jpg"))
    informe = {
        "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "duracion_s": round(dur, 2), "fotogramas": plan["frames"], "resolucion": "1080x1920", "fps": FPS,
        "tiempo_voz_s": round(t_voz), "tiempo_render_s": round(t_render), "tiempo_total_s": round(time.time() - t_ini),
        "voz": voz[2] if voz else "sin voz", "audio": {**inf_audio, **{"final": med}}, "movimiento": mov,
        "escenas": [{"a_s": round(e["a"] / FPS, 2), "b_s": round(e["b"] / FPS, 2), "fondo": e["fondo"], "plano": e["plano"],
                     "presentador": e["presentador"], "bit": e["bit"], "elemento": (e.get("elemento") or {}).get("tipo")}
                    for e in plan["escenas"]],
        "avisos": avisos,
    }
    escribir(os.path.join(carpeta, "presentador.json"), informe)
    shutil.copy(os.path.join(carpeta, "presentador.json"), os.path.join(SALIDA, f"{nombre}_informe.json"))
    log(json.dumps(informe, ensure_ascii=False)[:1500])
    if args.subir:
        if subprocess.run(["gh", "release", "view", RELEASE], capture_output=True).returncode != 0:
            subprocess.run(["gh", "release", "create", RELEASE, "--title", "Vídeos en cola", "--notes",
                            "Vídeos renderizados pendientes de publicar. Se borran solos al publicarse."], check=True)
        subprocess.run(["gh", "release", "upload", RELEASE, final, "--clobber"], check=True)
        post = dict(guion.get("post") or {})
        post.setdefault("tipo", "reel")
        texto = post.get("texto", "")
        if voz and voz[2] != "piper" and "Voz:" not in texto:
            texto = texto.rstrip() + "\n\nVoz: generada a partir de la voz del autor."
        post.update({
            "texto": texto, "renderizado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "asset": os.path.basename(final), "duracion_s": round(dur, 1),
            "formato": "modo presentador (Nea y Bit en 3D con three.js + Remotion, titulares, subtítulos palabra a palabra, "
                       "capturas reales de la demo, música y efectos generados por código)",
            "musica": {"estilo": mus_cfg.get("estilo", "pop"), "bpm": mus_cfg.get("bpm") or audio.ESTILOS.get(mus_cfg.get("estilo", "pop"), (118,))[0],
                       "tono": mus_cfg.get("tono", 0), "origen": "generada por código (sin licencias de terceros)"},
            "audio": med, "app": guion.get("app"), "publico": guion.get("publico"), "fuentes": guion.get("fuentes", []),
            "origen": "herramientas/presentador", "motor_voz": voz[2] if voz else None,
        })
        escribir(os.path.join(carpeta, "post.json"), post)
        log(f"subido {os.path.basename(final)} a la release '{RELEASE}' y escrito post.json")


if __name__ == "__main__":
    main()
