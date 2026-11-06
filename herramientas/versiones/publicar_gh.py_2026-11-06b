#!/usr/bin/env python3
"""Ciclo automático de @nosabesloquehasvisto en GitHub Actions (sin ningún dispositivo encendido).

Lo ejecuta .github/workflows/ciclo.yml varias veces al día. En cada pasada:
  1. Renderiza los reels nuevos de cola/ (guion.json -> hacer_reel.py, remaster.json -> remaster.py),
     les pone la voz (Piper o Kyutai Pocket TTS, según equipo/voz.json "motor") y guarda el vídeo como archivo de la release "cola" (no en el historial de git).
  2. Publica en Instagram los que ya tienen su hora y el visto bueno de Calidad (calidad.json).
  3. Responde a los comentarios con la palabra clave de cada reel.
  4. Actualiza estadisticas.json y originales/*.json.

Formato de una carpeta de cola/<NNN_tema>/:
  post.json   {"tipo": "reel", "texto": "...", "cuando": "2026-11-06T20:40:00+01:00",
               "palabra_clave": "BAILE", "respuesta": "...", "original_id": "<solo remaster>", "portada_ms": 2800}
  guion.json  (reel nuevo)   o   remaster.json (reutiliza el reel original_id de la cuenta)
  calidad.json {"aprobado": true, ...}   (lo escribe el agente de Calidad)

Secretos/variables del repositorio: PAGE_TOKEN (secreto). El resto está en equipo/config_publico.json.
Solo usa la librería estándar, Pillow/numpy (para los generadores), ffmpeg, gh, Piper y (opcional) pocket-tts.
"""
import glob
import json
import os
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.error
import urllib.parse
import urllib.request
import wave
from datetime import datetime, timedelta, timezone

BASE = os.path.dirname(os.path.abspath(__file__))
COLA = os.path.join(BASE, "cola")
PUBLICADOS = os.path.join(BASE, "publicados")
REVISION = os.path.join(BASE, "revision")
ERRORES = os.path.join(BASE, "errores")
ORIGINALES = os.path.join(BASE, "originales")
EQUIPO = os.path.join(BASE, "equipo")
ESTADISTICAS = os.path.join(BASE, "estadisticas.json")
REGISTRO = os.path.join(BASE, "registro.log")
RESPONDIDOS = os.path.join(EQUIPO, "respondidos.json")
AJUSTES_VOZ = os.path.join(EQUIPO, "voz.json")
HERR_REEL = os.path.join(BASE, "herramientas")
CACHE = os.path.expanduser(os.environ.get("CACHE_HERRAMIENTAS", "~/.cache/expedientes"))
GRAPH = "https://graph.facebook.com"
RELEASE = "cola"
PIPER_URLS = [
    "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_x86_64.tar.gz",
    "https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz",
]
VOZ_RAIZ = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/"
VOZ_POCKET = os.path.join(BASE, "herramientas", "voz_pocket.py")
ATRIBUCION_POCKET = "Voz: Kyutai Pocket TTS (CC BY 4.0)"
MAX_RENDERS = 2
GRACIA_SIN_CALIDAD = timedelta(hours=3)


# ---------------------------------------------------------------- utilidades
def log(msg):
    hora = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=1))).strftime("%Y-%m-%d %H:%M")
    linea = f"{hora}  {msg}"
    print(linea, flush=True)
    with open(REGISTRO, "a", encoding="utf-8") as f:
        f.write(linea + "\n")


def recortar_registro(max_lineas=600):
    try:
        with open(REGISTRO, encoding="utf-8") as f:
            lineas = f.readlines()
        if len(lineas) > max_lineas:
            with open(REGISTRO, "w", encoding="utf-8") as f:
                f.writelines(lineas[-max_lineas:])
    except OSError:
        pass


class ErrorAPI(Exception):
    pass


def peticion(url, metodo="GET", datos=None, cabeceras=None, cuerpo=None, timeout=120):
    cab = dict(cabeceras or {})
    if datos is not None:
        cuerpo = urllib.parse.urlencode(datos).encode()
        cab.setdefault("Content-Type", "application/x-www-form-urlencoded")
    req = urllib.request.Request(url, data=cuerpo, method=metodo, headers=cab)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        texto = e.read().decode(errors="replace")
        try:
            err = json.loads(texto).get("error", {})
            raise ErrorAPI(f"{err.get('message', texto)} (código {err.get('code')}, subcódigo {err.get('error_subcode')})")
        except (ValueError, AttributeError):
            raise ErrorAPI(f"HTTP {e.code}: {texto[:300]}")
    except urllib.error.URLError as e:
        raise ErrorAPI(f"Sin conexión: {e.reason}")


def leer_json(ruta, defecto=None):
    try:
        with open(ruta, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return defecto


def escribir_json(ruta, datos):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)


def cargar_config():
    cfg = leer_json(os.path.join(EQUIPO, "config_publico.json"), {})
    cfg["page_token"] = os.environ.get("PAGE_TOKEN", "")
    if not cfg["page_token"]:
        raise SystemExit("Falta el secreto PAGE_TOKEN en el repositorio.")
    return cfg


def api(cfg, ruta, metodo="GET", **params):
    params["access_token"] = cfg["page_token"]
    url = f"{GRAPH}/{cfg['version']}/{ruta}"
    if metodo == "GET":
        return peticion(url + "?" + urllib.parse.urlencode(params))
    return peticion(url, metodo, datos=params)


def leer_fecha(texto):
    d = datetime.fromisoformat(texto.strip().replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone(timedelta(hours=1)))


def descargar(url, destino):
    req = urllib.request.Request(url, headers={"User-Agent": "expedientes/1.0"})
    with urllib.request.urlopen(req, timeout=300) as r, open(destino + ".tmp", "wb") as f:
        shutil.copyfileobj(r, f)
    os.replace(destino + ".tmp", destino)


def gh(*args, check=True):
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        raise ErrorAPI(f"gh {' '.join(args[:3])}: {r.stderr.strip()[-300:]}")
    return r


# ---------------------------------------------------------------- voz (Piper / Pocket TTS)
def ajustes_voz():
    base = {"motor": "piper", "modelo": "es/es_ES/davefx/medium/es_ES-davefx-medium", "lentitud": 1.08,
            "volumen_voz": 1.25, "umbral_duck": 0.02, "ratio_duck": 8, "limite": 0.7, "variacion": 0.667,
            "ruido": 0.8, "cadena_voz": "",
            "pocket": {"idioma": "spanish", "voz": "lola", "temperatura": None, "ganancia": 1.0, "max_s": 600}}
    base.update(leer_json(AJUSTES_VOZ, {}) or {})
    return base


def ruta_piper():
    p = os.path.join(CACHE, "piper", "piper")
    if os.path.exists(p):
        return p
    os.makedirs(CACHE, exist_ok=True)
    for url in PIPER_URLS:
        try:
            tgz = os.path.join(CACHE, "piper.tar.gz")
            descargar(url, tgz)
            with tarfile.open(tgz) as t:
                t.extractall(CACHE)
            os.remove(tgz)
            if os.path.exists(p):
                os.chmod(p, 0o755)
                return p
        except Exception as e:
            log(f"Piper: fallo con {url}: {e}")
    raise ErrorAPI("No se pudo descargar Piper")


def modelo_voz():
    rel = ajustes_voz()["modelo"]
    destino = os.path.join(CACHE, "voces", os.path.basename(rel) + ".onnx")
    if not os.path.exists(destino):
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        descargar(VOZ_RAIZ + rel + ".onnx.json", destino + ".json")
        descargar(VOZ_RAIZ + rel + ".onnx", destino)
    return destino


def sintetizar(texto, salida):
    a = ajustes_voz()
    piper = ruta_piper()
    r = subprocess.run([piper, "--model", modelo_voz(), "--output_file", salida,
                        "--length_scale", str(a["lentitud"]), "--noise_scale", str(a["variacion"]),
                        "--noise_w", str(a["ruido"])],
                       input=texto.encode(), cwd=os.path.dirname(piper), capture_output=True, timeout=180)
    if r.returncode != 0 or not os.path.exists(salida):
        raise ErrorAPI(f"Piper falló: {r.stderr.decode(errors='replace')[-300:]}")


def sintetizar_pocket(textos, salidas, trabajo, aj):
    """Todas las frases en un solo proceso (el modelo se carga una vez). Lanza ErrorAPI si algo falla."""
    pk = dict(aj.get("pocket") or {})
    lote = os.path.join(trabajo, "lote_pocket.json")
    escribir_json(lote, {"idioma": pk.get("idioma", "spanish"), "voz": pk.get("voz", "lola"),
                         "temperatura": pk.get("temperatura"), "ganancia": pk.get("ganancia", 1.0),
                         "frases": [{"texto": t, "salida": s} for t, s in zip(textos, salidas)]})
    t0 = time.time()
    try:
        r = subprocess.run([sys.executable, VOZ_POCKET, lote], capture_output=True, text=True,
                           timeout=float(pk.get("max_s", 600)))
    except subprocess.TimeoutExpired:
        raise ErrorAPI(f"Pocket TTS tardó más de {pk.get('max_s', 600)} s")
    if r.returncode != 0 or not all(os.path.exists(s) and os.path.getsize(s) > 1000 for s in salidas):
        raise ErrorAPI(f"Pocket TTS falló: {(r.stderr or r.stdout)[-300:]}")
    log(f"Voz con Pocket TTS ({pk.get('idioma', 'spanish')}/{pk.get('voz', 'lola')}): "
        f"{len(textos)} frases en {time.time() - t0:.0f} s")


def generar_locucion(textos, trabajo, aj=None):
    """Devuelve (lista de wav, motor usado). Si Pocket falla, toda la locución se hace con Piper (no se mezclan voces)."""
    aj = aj or ajustes_voz()
    salidas = [os.path.join(trabajo, f"voz{i}.wav") for i in range(len(textos))]
    if str(aj.get("motor", "piper")).lower() == "pocket":
        try:
            sintetizar_pocket(textos, salidas, trabajo, aj)
            return salidas, "pocket"
        except Exception as e:
            log(f"Pocket TTS no disponible en este render ({str(e)[-200:]}); se usa Piper")
            for s in salidas:
                if os.path.exists(s):
                    os.remove(s)
    for t, s in zip(textos, salidas):
        sintetizar(t, s)
    return salidas, "piper"


def con_atribucion(texto, motor):
    """Pocket TTS (CC BY 4.0) exige atribución: se añade al final del texto del post."""
    if motor != "pocket" or ATRIBUCION_POCKET in (texto or ""):
        return texto
    return (texto or "").rstrip() + "\n\n" + ATRIBUCION_POCKET


def duracion_wav(ruta):
    with wave.open(ruta) as w:
        return w.getnframes() / float(w.getframerate())


def recortar_silencios(ruta, cfg):
    """Quita el silencio del principio y del final de una frase y acorta las pausas internas largas.

    equipo/voz.json "recorte": {"umbral_db": -40, "margen_ms": 70, "pausa_larga_s": 0.5, "pausa_max_s": 0.35}
    (umbral relativo al pico de la frase; ventanas de 20 ms). Así la voz arranca justo al empezar la escena,
    hace falta menos atempo para que quepa y no quedan huecos muertos dentro de una frase.
    Si algo falla, la frase se queda como estaba (devuelve False)."""
    if not cfg or cfg.get("activo") is False:
        return False
    try:
        import numpy as np
        with wave.open(ruta) as w:
            sr, ch, sw = w.getframerate(), w.getnchannels(), w.getsampwidth()
            raw = w.readframes(w.getnframes())
        if sw != 2:
            return False
        x = np.frombuffer(raw, "<i2").astype(np.float32).reshape(-1, ch)
        mono = np.abs(x).mean(axis=1)
        hop = max(1, int(sr * 0.02))
        nv = len(mono) // hop
        if nv < 10:
            return False
        rms = np.sqrt((mono[:nv * hop].reshape(nv, hop) ** 2).mean(axis=1) + 1e-9)
        pico = rms.max()
        if pico < 30:  # frase casi muda: no se toca
            return False
        habla = 20 * np.log10(rms / pico) > float(cfg.get("umbral_db", -40))
        idx = np.flatnonzero(habla)
        if idx.size == 0:
            return False
        margen = int(float(cfg.get("margen_ms", 70)) / 1000 * sr / hop + 0.5)
        larga = float(cfg.get("pausa_larga_s", 0.5)) * sr / hop
        maxp = float(cfg.get("pausa_max_s", 0.35)) * sr / hop
        # tramos de habla (ventanas) separados por pausas; las pausas > pausa_larga se dejan en pausa_max
        trozos, ini, prev = [], idx[0], idx[0]
        for i in idx[1:]:
            if i - prev - 1 > larga:
                trozos.append((ini, prev)); ini = i
            prev = i
        trozos.append((ini, prev))
        piezas = []
        fade = int(sr * 0.012)
        for k, (a, b) in enumerate(trozos):
            ext_a = margen if k == 0 else int(maxp / 2)
            ext_b = margen if k == len(trozos) - 1 else int(maxp / 2)
            s0 = max(0, (a - ext_a) * hop)
            s1 = min(len(x), (b + 1 + ext_b) * hop)
            seg = x[s0:s1].copy()
            if len(seg) > 2 * fade:  # fundidos cortos para que no haya chasquidos en los cortes
                r = np.linspace(0, 1, fade, dtype=np.float32)[:, None]
                seg[:fade] *= r; seg[-fade:] *= r[::-1]
            piezas.append(seg)
        y = np.concatenate(piezas)
        if len(y) < sr * 0.2 or len(y) > len(x):
            return False
        with wave.open(ruta, "wb") as w:
            w.setnchannels(ch); w.setsampwidth(2); w.setframerate(sr)
            w.writeframes(np.clip(y, -32768, 32767).astype("<i2").tobytes())
        return round((len(x) - len(y)) / sr, 2)
    except Exception as e:
        log(f"Recorte de silencios omitido en {os.path.basename(ruta)}: {str(e)[-120:]}")
        return False


def anadir_voz(video, locucion, trabajo):
    tramos = [t for t in (leer_json(locucion, []) or []) if t.get("texto", "").strip()]
    if not tramos:
        return
    aj = ajustes_voz()
    rutas, motor = generar_locucion([t["texto"] for t in tramos], trabajo, aj)
    recortes = [recortar_silencios(w, aj.get("recorte")) for w in rutas]
    if any(recortes):
        log(f"Voz: silencios recortados por frase (s): {[r or 0 for r in recortes]}")
    wavs = [(w, duracion_wav(w)) for w in rutas]
    cadena = (aj.get("cadena_voz") or "").strip().strip(",")
    try:
        _mezclar_voz(video, tramos, wavs, aj, cadena, trabajo)
    except ErrorAPI as e:
        if not cadena:
            raise
        # Si la cadena de voz de equipo/voz.json da problemas, se mezcla sin ella en vez de no publicar.
        log(f"Cadena de voz descartada en este render ({str(e)[-160:]}); se mezcla sin procesar la voz")
        _mezclar_voz(video, tramos, wavs, aj, "", trabajo)
    return motor


def _mezclar_voz(video, tramos, wavs, aj, cadena, trabajo):
    # cadena (equipo/voz.json "cadena_voz"): filtros ffmpeg sobre cada frase de la voz, p. ej.
    # paso alto + EQ de presencia + compresor + de-esser. Vacía = voz de Piper sin procesar.
    entradas, filtros, etiquetas = ["-i", video], [], []
    for i, (t, (wav, d)) in enumerate(zip(tramos, wavs)):
        hueco = max(float(t.get("duracion", d)) - 0.15, 0.5)
        tempo = min(max(d / hueco, 1.0), 1.35)
        entradas += ["-i", wav]
        ms = int(float(t["inicio"]) * 1000 + 120)
        proc = f"{cadena}," if cadena else ""
        filtros.append(f"[{i + 1}:a]aresample=44100,{proc}atempo={tempo:.3f},adelay={ms}|{ms},volume={aj['volumen_voz']}[v{i}]")
        etiquetas.append(f"[v{i}]")
    filtros.append(f"{''.join(etiquetas)}amix=inputs={len(etiquetas)}:normalize=0,pan=stereo|c0=c0|c1=c0,apad,asplit=2[vox][key]")
    filtros.append(f"[0:a][key]sidechaincompress=threshold={aj['umbral_duck']}:ratio={aj['ratio_duck']}:attack=15:release=350[fondo]")
    filtros.append(f"[fondo][vox]amix=inputs=2:duration=first:normalize=0,alimiter=limit={aj['limite']}:level=false[a]")
    salida = os.path.join(trabajo, "con_voz.mp4")
    r = subprocess.run(["ffmpeg", "-y", *entradas, "-filter_complex", ";".join(filtros),
                        "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                        "-shortest", salida], capture_output=True, timeout=600)
    if r.returncode != 0:
        raise ErrorAPI(f"ffmpeg falló al mezclar la voz: {r.stderr.decode(errors='replace')[-400:]}")
    os.replace(salida, video)


# ---------------------------------------------------------------- render
def carpetas_cola():
    if not os.path.isdir(COLA):
        return []
    salida = []
    for nombre in sorted(os.listdir(COLA)):
        carpeta = os.path.join(COLA, nombre)
        post = leer_json(os.path.join(carpeta, "post.json"))
        if post is None:
            continue
        try:
            cuando = leer_fecha(post["cuando"])
        except Exception as e:
            log(f"{nombre}: post.json sin 'cuando' válido ({e})")
            continue
        salida.append((cuando, carpeta, post))
    return sorted(salida, key=lambda x: x[0])


def asegurar_release():
    if gh("release", "view", RELEASE, check=False).returncode != 0:
        gh("release", "create", RELEASE, "--title", "Vídeos en cola",
           "--notes", "Vídeos renderizados pendientes de publicar. Se borran solos al publicarse.")


def renderizar(cfg, carpeta, post):
    nombre = os.path.basename(carpeta)
    trabajo = os.path.join("/tmp", "render_" + nombre)
    shutil.rmtree(trabajo, ignore_errors=True)
    os.makedirs(trabajo)
    video = os.path.join(trabajo, "video.mp4")
    if os.path.exists(os.path.join(carpeta, "remaster.json")):
        oid = post.get("original_id")
        if not oid:
            raise ErrorAPI("remaster.json sin 'original_id' en post.json")
        url = api(cfg, str(oid), fields="media_url").get("media_url")
        if not url:
            raise ErrorAPI("Instagram no da el vídeo original (puede tener música con licencia)")
        original = os.path.join(trabajo, "original.mp4")
        descargar(url, original)
        cmd = [sys.executable, os.path.join(HERR_REEL, "remaster.py"), original,
               os.path.join(carpeta, "remaster.json"), video]
    elif os.path.exists(os.path.join(carpeta, "guion.json")):
        cmd = [sys.executable, os.path.join(HERR_REEL, "hacer_reel.py"), os.path.join(carpeta, "guion.json"), video]
    else:
        raise ErrorAPI("Falta guion.json o remaster.json")
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1200, cwd=HERR_REEL)
    if r.returncode != 0 or not os.path.exists(video):
        raise ErrorAPI(f"El generador falló: {(r.stderr or r.stdout)[-500:]}")
    locucion = os.path.join(trabajo, "video.locucion.json")
    if os.path.exists(locucion):
        shutil.copy(locucion, os.path.join(carpeta, "locucion.json"))
        motor = anadir_voz(video, locucion, trabajo)
        if motor:
            post["motor_voz"] = motor
    asset = os.path.join(trabajo, f"{nombre}.mp4")
    os.replace(video, asset)
    asegurar_release()
    gh("release", "upload", RELEASE, asset, "--clobber")
    post["renderizado"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    post["asset"] = f"{nombre}.mp4"
    post.pop("_error_render", None)
    escribir_json(os.path.join(carpeta, "post.json"), post)
    shutil.rmtree(trabajo, ignore_errors=True)
    log(f"{nombre}: renderizado con voz y subido a la release '{RELEASE}'")


def renderizar_pendientes(cfg):
    hechos = 0
    for _, carpeta, post in carpetas_cola():
        if post.get("renderizado") or hechos >= MAX_RENDERS:
            continue
        nombre = os.path.basename(carpeta)
        try:
            renderizar(cfg, carpeta, post)
            hechos += 1
        except Exception as e:
            intentos = post.get("_intentos_render", 0) + 1
            post["_intentos_render"] = intentos
            post["_error_render"] = str(e)[:400]
            escribir_json(os.path.join(carpeta, "post.json"), post)
            log(f"{nombre}: error al renderizar ({intentos}/3): {e}")
            if intentos >= 3:
                mover(carpeta, ERRORES, {"error": f"Render: {e}"})


# ---------------------------------------------------------------- publicar
def mover(carpeta, destino, resultado):
    os.makedirs(destino, exist_ok=True)
    escribir_json(os.path.join(carpeta, "resultado.json"), resultado)
    final = os.path.join(destino, os.path.basename(carpeta))
    if os.path.exists(final):
        final += "_" + datetime.now().strftime("%H%M%S")
    shutil.move(carpeta, final)


def esperar_contenedor(cfg, cid, max_seg=900):
    inicio = time.time()
    while time.time() - inicio < max_seg:
        r = api(cfg, cid, fields="status_code,status")
        estado = r.get("status_code")
        if estado == "FINISHED":
            return
        if estado in ("ERROR", "EXPIRED"):
            raise ErrorAPI(f"Instagram rechazó el vídeo: {r.get('status', estado)}")
        time.sleep(10)
    raise ErrorAPI("Instagram tardó demasiado en procesar el vídeo")


def publicar_reel(cfg, video, post):
    params = {"media_type": "REELS", "upload_type": "resumable",
              "caption": con_atribucion(post.get("texto", ""), post.get("motor_voz")),
              "share_to_feed": "true" if post.get("compartir_en_feed", True) else "false"}
    if post.get("portada_ms") is not None:
        params["thumb_offset"] = str(int(post["portada_ms"]))
    # Reel de prueba (trial reel): Instagram lo enseña primero solo a no seguidores.
    # post.json: "prueba_no_seguidores": true (se gradúa solo si rinde, SS_PERFORMANCE) o "MANUAL".
    prueba = post.get("prueba_no_seguidores")
    if prueba:
        estrategia = "MANUAL" if str(prueba).upper() == "MANUAL" else "SS_PERFORMANCE"
        params["trial_params"] = json.dumps({"graduation_strategy": estrategia})
    try:
        r = api(cfg, f"{cfg['ig_user_id']}/media", "POST", **params)
    except ErrorAPI as e:
        if "trial_params" not in params:
            raise
        log(f"reel de prueba rechazado por la API ({e}); se publica como reel normal")
        params.pop("trial_params")
        prueba = None
        r = api(cfg, f"{cfg['ig_user_id']}/media", "POST", **params)
    cid = r["id"]
    uri = r.get("uri") or f"https://rupload.facebook.com/ig-api-upload/{cfg['version']}/{cid}"
    with open(video, "rb") as f:
        datos = f.read()
    peticion(uri, "POST", cuerpo=datos, timeout=600, cabeceras={
        "Authorization": f"OAuth {cfg['page_token']}", "offset": "0", "file_size": str(len(datos)),
        "Content-Type": "application/octet-stream"})
    esperar_contenedor(cfg, cid)
    mid = api(cfg, f"{cfg['ig_user_id']}/media_publish", "POST", creation_id=cid)["id"]
    enlace = ""
    try:
        enlace = api(cfg, mid, fields="permalink").get("permalink", "")
    except ErrorAPI:
        pass
    return {"media_id": mid, "enlace": enlace, "prueba_no_seguidores": bool(prueba)}


def aprobado(carpeta, cuando, ahora):
    cal = leer_json(os.path.join(carpeta, "calidad.json"))
    if cal is not None:
        return bool(cal.get("aprobado"))
    return ahora - cuando > GRACIA_SIN_CALIDAD  # si Calidad no pudo revisarlo, sale con 3 h de retraso


def publicar_pendientes(cfg):
    ahora = datetime.now(timezone.utc)
    for cuando, carpeta, post in carpetas_cola():
        if cuando > ahora or not post.get("renderizado"):
            continue
        nombre = os.path.basename(carpeta)
        if ahora - cuando > timedelta(hours=36):
            mover(carpeta, ERRORES, {"error": "Caducado: más de 36 h después de su hora"})
            log(f"{nombre}: caducado, movido a errores/")
            continue
        if not aprobado(carpeta, cuando, ahora):
            continue
        log(f"{nombre}: publicando…")
        trabajo = os.path.join("/tmp", "pub_" + nombre)
        shutil.rmtree(trabajo, ignore_errors=True)
        os.makedirs(trabajo)
        try:
            gh("release", "download", RELEASE, "-p", post["asset"], "-D", trabajo, "--clobber")
            res = publicar_reel(cfg, os.path.join(trabajo, post["asset"]), post)
            res["publicado"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            mover(carpeta, PUBLICADOS, res)
            gh("release", "delete-asset", RELEASE, post["asset"], "-y", check=False)
            log(f"{nombre}: publicado {res.get('enlace')}")
        except Exception as e:
            intentos = post.get("_intentos", 0) + 1
            post["_intentos"] = intentos
            escribir_json(os.path.join(carpeta, "post.json"), post)
            log(f"{nombre}: fallo al publicar {intentos}/3: {e}")
            if intentos >= 3:
                mover(carpeta, ERRORES, {"error": str(e), "intentos": intentos})
        finally:
            shutil.rmtree(trabajo, ignore_errors=True)
        break  # como máximo un reel por pasada


# ---------------------------------------------------------------- comentarios
def responder_comentarios(cfg, maximo=15):
    hechos = set(leer_json(RESPONDIDOS, []) or [])
    enviados = 0
    limite = datetime.now(timezone.utc) - timedelta(days=7)
    for carpeta in sorted(glob.glob(os.path.join(PUBLICADOS, "*"))):
        post = leer_json(os.path.join(carpeta, "post.json"), {}) or {}
        res = leer_json(os.path.join(carpeta, "resultado.json"), {}) or {}
        clave = (post.get("palabra_clave") or "").strip().lower()
        respuesta = (post.get("respuesta") or "").strip()
        mid = res.get("media_id")
        if not (clave and respuesta and mid):
            continue
        try:
            if leer_fecha(res.get("publicado", "")) < limite:
                continue
        except Exception:
            pass
        try:
            datos = api(cfg, f"{mid}/comments", fields="id,text,username", limit=50).get("data", [])
        except ErrorAPI as e:
            log(f"{os.path.basename(carpeta)}: no se pudieron leer comentarios: {e}")
            continue
        for c in datos:
            if enviados >= maximo:
                break
            if c["id"] in hechos or c.get("username") == cfg.get("ig_username"):
                continue
            if clave not in (c.get("text") or "").lower():
                continue
            try:
                api(cfg, f"{c['id']}/replies", "POST", message=f"@{c.get('username', '')} {respuesta}".strip())
                hechos.add(c["id"])
                enviados += 1
                time.sleep(3)
            except ErrorAPI as e:
                log(f"No se pudo responder a un comentario: {e}")
                break
    escribir_json(RESPONDIDOS, sorted(hechos))
    if enviados:
        log(f"Comentarios respondidos: {enviados}")


# ---------------------------------------------------------------- estadísticas
METRICAS_REEL = ["reach", "views", "saved", "shares", "comments", "likes", "total_interactions",
                 "ig_reels_avg_watch_time", "ig_reels_video_view_total_time"]
METRICAS_OTRO = ["reach", "views", "saved", "shares", "total_interactions"]


def metricas(cfg, mid, nombres):
    try:
        r = api(cfg, f"{mid}/insights", metric=",".join(nombres))
        return {m["name"]: (m.get("values") or [{}])[0].get("value") for m in r.get("data", [])}
    except ErrorAPI:
        salida = {}
        for n in nombres:
            try:
                r = api(cfg, f"{mid}/insights", metric=n)
                for m in r.get("data", []):
                    salida[m["name"]] = (m.get("values") or [{}])[0].get("value")
            except ErrorAPI:
                salida[n] = None
        return salida


def actualizar_estadisticas(cfg):
    cuenta = api(cfg, cfg["ig_user_id"], fields="username,followers_count,follows_count,media_count")
    medios = api(cfg, f"{cfg['ig_user_id']}/media", limit=30,
                 fields="id,caption,media_type,media_product_type,timestamp,permalink,like_count,comments_count").get("data", [])
    for m in medios:
        m["metricas"] = metricas(cfg, m["id"], METRICAS_REEL if m.get("media_product_type") == "REELS" else METRICAS_OTRO)
        if m.get("media_product_type") == "REELS":
            ruta = os.path.join(ORIGINALES, f"{m['id']}.json")
            if not os.path.exists(ruta):
                escribir_json(ruta, {k: m.get(k) for k in ("id", "caption", "timestamp", "permalink",
                                                          "like_count", "comments_count")})
    historial = (leer_json(ESTADISTICAS, {}) or {}).get("historial_cuenta", [])
    historial.append({"fecha": datetime.now(timezone.utc).isoformat(timespec="minutes"),
                      "seguidores": cuenta.get("followers_count")})
    escribir_json(ESTADISTICAS, {"actualizado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                 "cuenta": cuenta, "posts": medios, "historial_cuenta": historial[-400:]})
    log(f"Estadísticas actualizadas ({len(medios)} posts, {cuenta.get('followers_count')} seguidores)")


def estadisticas_viejas(horas=6):
    datos = leer_json(ESTADISTICAS, {}) or {}
    try:
        return datetime.now(timezone.utc) - leer_fecha(datos["actualizado"]) > timedelta(hours=horas)
    except Exception:
        return True


# ---------------------------------------------------------------- principal
def ciclo():
    cfg = cargar_config()
    for d in (COLA, PUBLICADOS, REVISION, ERRORES, ORIGINALES):
        os.makedirs(d, exist_ok=True)
    pasos = [("renderizar", renderizar_pendientes), ("publicar", publicar_pendientes),
             ("comentarios", responder_comentarios)]
    if estadisticas_viejas() or os.environ.get("FORZAR_ESTADISTICAS"):
        pasos.append(("estadísticas", actualizar_estadisticas))
    for nombre, paso in pasos:
        try:
            paso(cfg)
        except Exception as e:
            log(f"Error en {nombre}: {e}")
    recortar_registro()


def estado():
    cfg = cargar_config()
    r = api(cfg, cfg["ig_user_id"], fields="username,followers_count")
    print(f"Conexión OK: @{r.get('username')} · {r.get('followers_count')} seguidores")
    for cuando, carpeta, post in carpetas_cola():
        print(f"  {cuando.isoformat()}  {os.path.basename(carpeta)}  renderizado={bool(post.get('renderizado'))}")


if __name__ == "__main__":
    orden = sys.argv[1] if len(sys.argv) > 1 else "ciclo"
    {"ciclo": ciclo, "estado": estado}.get(orden, ciclo)()
