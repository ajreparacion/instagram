#!/usr/bin/env python3
"""Ciclo automático de @nosabesloquehasvisto en GitHub Actions (sin ningún dispositivo encendido).

Lo ejecuta .github/workflows/ciclo.yml varias veces al día. En cada pasada:
  1. Renderiza los reels nuevos de cola/ (guion.json -> hacer_reel.py, remaster.json -> remaster.py),
     les pone la voz (Chatterbox, Kokoro, Kyutai Pocket TTS o Piper, según equipo/voz.json "motor" y "respaldo")
     y guarda el vídeo como archivo de la release "cola" (no en el historial de git).
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
VOZ_CHATTERBOX = os.path.join(BASE, "herramientas", "voz_chatterbox.py")
VOZ_KOKORO = os.path.join(BASE, "herramientas", "voz_kokoro.py")
# Chatterbox va en su propio entorno virtual (fija torch 2.6 y transformers 4.46): ciclo.yml exporta PYTHON_CHATTERBOX
PYTHON_CHATTERBOX = os.environ.get("PYTHON_CHATTERBOX") or sys.executable
ATRIBUCION_POCKET = "Voz: Kyutai Pocket TTS (CC BY 4.0)"
# Chatterbox (MIT) y Kokoro (Apache 2.0) no exigen atribución, pero Meta pide marcar el audio realista generado:
ATRIBUCION_IA = "Voz generada por IA"
ATRIBUCIONES = {"pocket": ATRIBUCION_POCKET, "chatterbox": ATRIBUCION_IA, "kokoro": ATRIBUCION_IA}
MAX_RENDERS = 2
GRACIA_SIN_CALIDAD = timedelta(hours=3)  # ya no se usa (7/11/2026)
NOTA_MINIMA = 90  # nota mínima de Calidad para publicar (7/11/2026)


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


# ---------------------------------------------------------------- voz (Chatterbox / Kokoro / Pocket TTS / Piper)
MOTORES = ("chatterbox", "kokoro", "pocket", "piper")


def ajustes_voz():
    base = {"motor": "piper", "respaldo": ["pocket", "piper"],
            "modelo": "es/es_ES/davefx/medium/es_ES-davefx-medium", "lentitud": 1.08,
            "volumen_voz": 1.25, "umbral_duck": 0.04, "ratio_duck": 3, "limite": 0.7, "variacion": 0.667,
            "ruido": 0.8, "cadena_voz": "",
            "pocket": {"idioma": "spanish", "voz": "lola", "temperatura": None, "ganancia": 1.0, "max_s": 600},
            "chatterbox": {"modelo": "es-es", "idioma": "es", "exageracion": 0.6, "cfg": 0.35, "temperatura": 0.75,
                           "referencia": "voces/referencia_usuario.wav", "referencia_kokoro": None,
                           "ganancia": 1.0, "semilla": 7, "max_s": 1500},
            "kokoro": {"voz": "em_alex", "velocidad": 0.95, "ganancia": 1.0, "max_s": 300}}
    base.update(leer_json(AJUSTES_VOZ, {}) or {})
    return base


def cadena_motores(aj):
    """Motor principal y después los de respaldo, sin repetir y solo los conocidos. Piper siempre cierra la lista."""
    orden = [str(aj.get("motor", "piper")).lower()] + [str(m).lower() for m in (aj.get("respaldo") or [])] + ["piper"]
    vistos = []
    for m in orden:
        if m in MOTORES and m not in vistos:
            vistos.append(m)
    return vistos


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


def _sintetizar_lote(nombre, script, python, lote_datos, textos, salidas, trabajo, max_s, extras=None):
    """Todas las frases en un solo proceso (el modelo se carga una vez). Lanza ErrorAPI si algo falla.
    Devuelve el JSON que imprime el script (tiempos, modelo usado...).
    extras: lista opcional (una por frase) de dicts con ajustes propios de esa frase (p. ej. "exageracion")."""
    lote = os.path.join(trabajo, "lote_" + "".join(c if c.isalnum() else "_" for c in nombre.lower()) + ".json")
    lote_datos = dict(lote_datos)
    lote_datos["frases"] = [dict((extras[i] if extras and i < len(extras) and extras[i] else {}), texto=t, salida=s)
                            for i, (t, s) in enumerate(zip(textos, salidas))]
    escribir_json(lote, lote_datos)
    t0 = time.time()
    try:
        r = subprocess.run([python, script, lote], capture_output=True, text=True, timeout=float(max_s))
    except subprocess.TimeoutExpired:
        raise ErrorAPI(f"{nombre} tardó más de {max_s} s")
    if r.returncode != 0 or not all(os.path.exists(s) and os.path.getsize(s) > 1000 for s in salidas):
        lineas = [l.strip() for l in ((r.stderr or "") + "\n" + (r.stdout or "")).splitlines() if l.strip()]
        raise ErrorAPI(f"{nombre} falló: {' | '.join(lineas[-2:])[-300:]}")
    try:
        info = json.loads((r.stdout or "").strip().splitlines()[-1])
    except Exception:
        info = {}
    info["_segundos"] = round(time.time() - t0)
    return info


def ajustes_por_estilo(cfg_motor, estilos, claves):
    """Ajustes por frase según el estilo de su escena (equipo/voz.json <motor>.por_estilo, p. ej.
    {"gancho": {"exageracion": 0.85, "cfg": 0.3}}). 6/11/2026: el gancho y el giro con más intensidad (énfasis)."""
    pe = cfg_motor.get("por_estilo") or {}
    if not estilos or not isinstance(pe, dict):
        return None
    out = []
    for e in estilos:
        d = pe.get(str(e or ""), {}) if isinstance(pe.get(str(e or "")), dict) else {}
        out.append({k: d[k] for k in claves if k in d})
    return out if any(out) else None


def sintetizar_pocket(textos, salidas, trabajo, aj, estilos=None):
    pk = dict(aj.get("pocket") or {})
    info = _sintetizar_lote("Pocket TTS", VOZ_POCKET, sys.executable,
                            {"idioma": pk.get("idioma", "spanish"), "voz": pk.get("voz", "lola"),
                             "temperatura": pk.get("temperatura"), "ganancia": pk.get("ganancia", 1.0)},
                            textos, salidas, trabajo, pk.get("max_s", 600))
    log(f"Voz con Pocket TTS ({pk.get('idioma', 'spanish')}/{pk.get('voz', 'lola')}): "
        f"{len(textos)} frases en {info['_segundos']} s")


def sintetizar_chatterbox(textos, salidas, trabajo, aj, estilos=None):
    """Chatterbox (Resemble AI, MIT). Referencia de voz: solo la del usuario (voces/referencia_usuario.wav)
    o una con licencia libre; si el archivo no existe se usa la voz integrada del modelo."""
    cb = dict(aj.get("chatterbox") or {})
    ref = cb.get("referencia")
    if ref and not os.path.isabs(ref):
        ref = os.path.join(BASE, ref)
    if ref and os.path.exists(ref) and cb.get("eq_referencia"):
        ref = referencia_con_eq(ref, str(cb["eq_referencia"]))
    if not (ref and os.path.exists(ref)) and cb.get("referencia_kokoro"):
        # Sin voz del usuario: referencia sintética con licencia libre (Kokoro, Apache 2.0), generada aquí mismo
        # y guardada en la caché. No es la voz de ninguna persona real.
        ref = referencia_kokoro(str(cb["referencia_kokoro"]), aj, trabajo)
    info = _sintetizar_lote("Chatterbox", VOZ_CHATTERBOX, PYTHON_CHATTERBOX,
                            {"modelo": cb.get("modelo", "es-es"), "idioma": cb.get("idioma", "es"),
                             "exageracion": cb.get("exageracion", 0.5), "cfg": cb.get("cfg", 0.5),
                             "temperatura": cb.get("temperatura", 0.8), "referencia": ref if ref and os.path.exists(ref) else None,
                             "ganancia": cb.get("ganancia", 1.0), "semilla": cb.get("semilla"),
                             "theta": cb.get("theta") or ""},
                            textos, salidas, trabajo, cb.get("max_s", 1500),
                            extras=ajustes_por_estilo(cb, estilos, ("exageracion", "cfg", "temperatura")))
    log(f"Voz con Chatterbox ({info.get('modelo_usado', '?')}, referencia={'sí' if info.get('referencia') else 'integrada'}, "
        f"exageración {cb.get('exageracion', 0.5)}, cfg {cb.get('cfg', 0.5)}): {len(textos)} frases en {info['_segundos']} s"
        + (f"; avisos: {info['avisos']}" if info.get("avisos") else ""))


def referencia_con_eq(ref, filtros):
    """Copia de la referencia de voz con una ecualización (ffmpeg, p. ej. realce de agudos si la grabación suena
    apagada, como una nota de voz de móvil o una voz separada de la música). Con caché; si falla, la original."""
    try:
        import hashlib
        clave = hashlib.md5((os.path.abspath(ref) + "|" + filtros + "|" + str(os.path.getmtime(ref))).encode()).hexdigest()[:12]
        destino = os.path.join(CACHE, "voces", f"ref_eq_{clave}.wav")
        if os.path.exists(destino) and os.path.getsize(destino) > 20000:
            return destino
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", ref, "-af", filtros + ",alimiter=limit=0.85:level=false",
                            "-ar", "24000", "-ac", "1", destino], capture_output=True, timeout=120)
        if r.returncode != 0 or not os.path.exists(destino):
            raise ErrorAPI(r.stderr.decode(errors="replace")[-160:])
        return destino
    except Exception as e:
        log(f"EQ de la referencia no aplicada ({str(e)[-120:]}); se usa la referencia tal cual")
        return ref


TEXTO_REFERENCIA = ("A ver, te cuento una cosa que me pasó el otro día. Estaba en casa, tranquilo, y de repente… "
                    "oigo un ruido en la cocina. Nada, pensé. Pero no. Ojo, que esto se pone bueno.")


def referencia_kokoro(voz, aj, trabajo):
    """Clip de referencia (~10 s, español) generado con Kokoro para que Chatterbox imite su timbre. Con caché."""
    destino = os.path.join(CACHE, "voces", f"referencia_kokoro_{voz}.wav")
    if os.path.exists(destino) and os.path.getsize(destino) > 20000:
        return destino
    try:
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        tmp = os.path.join(trabajo, "ref_kokoro.wav")
        _sintetizar_lote("Kokoro (referencia)", VOZ_KOKORO, sys.executable,
                         {"voz": voz, "velocidad": 1.0, "ganancia": 1.0}, [TEXTO_REFERENCIA], [tmp], trabajo, 300)
        shutil.copy(tmp, destino)
        return destino
    except Exception as e:
        log(f"Referencia Kokoro no disponible ({str(e)[-160:]}); Chatterbox usa su voz integrada")
        return None


def sintetizar_kokoro(textos, salidas, trabajo, aj, estilos=None):
    kk = dict(aj.get("kokoro") or {})
    info = _sintetizar_lote("Kokoro", VOZ_KOKORO, sys.executable,
                            {"voz": kk.get("voz", "em_alex"), "velocidad": kk.get("velocidad", 1.0),
                             "ganancia": kk.get("ganancia", 1.0)},
                            textos, salidas, trabajo, kk.get("max_s", 300),
                            extras=ajustes_por_estilo(kk, estilos, ("velocidad",)))
    log(f"Voz con Kokoro ({kk.get('voz', 'em_alex')}): {len(textos)} frases en {info['_segundos']} s")


def sintetizar_piper(textos, salidas, trabajo, aj, estilos=None):
    for t, s in zip(textos, salidas):
        sintetizar(t, s)


SINTETIZADORES = {"chatterbox": sintetizar_chatterbox, "kokoro": sintetizar_kokoro,
                  "pocket": sintetizar_pocket, "piper": sintetizar_piper}


def generar_locucion(textos, trabajo, aj=None, estilos=None):
    """Devuelve (lista de wav, motor usado). Se prueba el motor de equipo/voz.json y, si falla, los de "respaldo"
    en orden (Piper siempre el último). Toda la locución sale del mismo motor: no se mezclan voces.
    estilos: estilo de la escena de cada frase (gancho, giro...) para los ajustes por estilo del motor."""
    aj = aj or ajustes_voz()
    salidas = [os.path.join(trabajo, f"voz{i}.wav") for i in range(len(textos))]
    motores = cadena_motores(aj)
    ultimo = None
    for motor in motores:
        try:
            SINTETIZADORES[motor](textos, salidas, trabajo, aj, estilos=estilos)
            return salidas, motor
        except Exception as e:
            ultimo = e
            if motor != motores[-1]:
                log(f"Voz {motor} no disponible en este render ({str(e)[-200:]}); se prueba el siguiente")
            for s in salidas:
                if os.path.exists(s):
                    os.remove(s)
    raise ErrorAPI(f"Ningún motor de voz funcionó ({motores}): {str(ultimo)[-200:]}")


def con_atribucion(texto, motor):
    """Pocket TTS (CC BY 4.0) exige atribución; con Chatterbox/Kokoro se marca que la voz es generada.
    Se añade al final del texto del post (una sola vez)."""
    linea = ATRIBUCIONES.get(str(motor or "").lower())
    if not linea or linea in (texto or "") or "Voz generada" in (texto or "") or "Voz: generada" in (texto or ""):
        return texto
    return (texto or "").rstrip() + "\n\n" + linea


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


def preparar_voz(locucion, trabajo):
    """Genera y recorta la voz de cada tramo de locucion.json. Devuelve (tramos, [(wav, duración)], motor, ajustes)."""
    tramos = [t for t in (leer_json(locucion, []) or []) if t.get("texto", "").strip()]
    if not tramos:
        return tramos, [], None, None
    aj = ajustes_voz()
    rutas, motor = generar_locucion([t["texto"] for t in tramos], trabajo, aj, estilos=[t.get("estilo") for t in tramos])
    recortes = [recortar_silencios(w, aj.get("recorte")) for w in rutas]
    if any(recortes):
        log(f"Voz: silencios recortados por frase (s): {[r or 0 for r in recortes]}")
    # Alineación palabra a palabra (faster-whisper) → subtítulos clavados a la voz y énfasis en las palabras marcadas
    palabras = alinear_palabras(rutas, [t["texto"] for t in tramos], trabajo, aj)
    for t, w, p in zip(tramos, rutas, palabras):
        if p:
            t["palabras"] = p
            if t.get("enfasis"):
                aplicar_enfasis(w, p, t["enfasis"], aj)
    return tramos, [(w, duracion_wav(w)) for w in rutas], motor, aj


VOZ_ALINEAR = os.path.join(BASE, "herramientas", "alinear_voz.py")


def alinear_palabras(rutas, textos, trabajo, aj):
    """[(inicio, fin) por palabra] para cada frase, o None por frase si no se pudo. Nunca lanza: si falta
    faster-whisper o falla, se sigue con la estimación (subtítulos a ritmo estimado, sin realce de énfasis)."""
    cfg = aj.get("alineacion") if isinstance(aj.get("alineacion"), dict) else {}
    if cfg.get("activo") is False:
        return [None] * len(rutas)
    lote = os.path.join(trabajo, "lote_alineacion.json")
    escribir_json(lote, {"modelo": cfg.get("modelo", "small"),
                         "frases": [{"wav": w, "texto": t} for w, t in zip(rutas, textos)]})
    try:
        r = subprocess.run([sys.executable, VOZ_ALINEAR, lote], capture_output=True, text=True,
                           timeout=float(cfg.get("max_s", 420)))
        if r.returncode != 0:
            raise ErrorAPI((r.stderr or r.stdout)[-200:])
        info = json.loads((r.stdout or "").strip().splitlines()[-1])
        res = list(info.get("frases") or [])
        res += [None] * (len(rutas) - len(res))
        log(f"Voz: alineación palabra a palabra ({info.get('modelo')}, {info.get('segundos')} s): "
            f"{sum(1 for x in res if x)}/{len(rutas)} frases")
        return res[:len(rutas)]
    except Exception as e:
        log(f"Voz: sin alineación por palabra ({str(e)[-160:]}); subtítulos a ritmo estimado")
        return [None] * len(rutas)


def aplicar_enfasis(wav, palabras, indices, aj):
    """Énfasis de las palabras marcadas con *asteriscos* en el guion, parte 1 (sobre el wav, antes de la cadena):
    mete un respiro de `pausa_ms` (90 ms) antes de la primera palabra de cada grupo, como quien recalca algo, y
    un realce previo opcional `db_previo` (0 por defecto; el compresor de la cadena lo aplastaría). La subida de
    volumen de verdad (`db`, +3,5 dB) se aplica DESPUÉS de la cadena, en la mezcla (_mezclar_voz). Nunca lanza."""
    cfg = aj.get("enfasis") if isinstance(aj.get("enfasis"), dict) else {}
    if cfg.get("activo") is False or not indices:
        return False
    db = float(cfg.get("db_previo", 0.0)); pausa = float(cfg.get("pausa_ms", 90)) / 1000.0
    try:
        import numpy as np
        import wave
        with wave.open(wav, "rb") as f:
            sr, nch, sw, n = f.getframerate(), f.getnchannels(), f.getsampwidth(), f.getnframes()
            raw = f.readframes(n)
        if sw != 2:
            return False
        x = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
        if nch > 1:
            x = x.reshape(-1, nch).mean(1)
        g = np.ones(len(x), np.float32)
        ramp = max(1, int(sr * 0.025))
        idx = sorted(set(int(i) for i in indices if 0 <= int(i) < len(palabras)))
        inserts = []   # (posición, nº de muestras de silencio) antes de la primera palabra de cada grupo
        for i in idx:
            a, b = palabras[i]
            i0, i1 = int(a * sr), int(b * sr)
            i0 = max(0, min(i0, len(x))); i1 = max(i0, min(i1, len(x)))
            amp = 10 ** (db / 20)
            seg = np.full(i1 - i0, amp, np.float32)
            k = min(ramp, len(seg) // 2)
            if k > 0:
                seg[:k] = np.linspace(1.0, amp, k); seg[-k:] = np.linspace(amp, 1.0, k)
            g[i0:i1] = np.maximum(g[i0:i1], seg)
            if (i - 1) not in idx and i > 0 and pausa > 0:
                inserts.append((i0, int(pausa * sr)))
        y = x * g
        # respiro antes del énfasis: se inserta silencio con fundidos de 15 ms a cada lado (sin chasquido ni corte seco)
        fd = int(sr * 0.015)
        for pos, m in sorted(inserts, reverse=True):
            antes, despues = y[:pos].copy(), y[pos:].copy()
            if len(antes) > fd: antes[-fd:] *= np.linspace(1.0, 0.0, fd, dtype=np.float32)
            if len(despues) > fd: despues[:fd] *= np.linspace(0.0, 1.0, fd, dtype=np.float32)
            y = np.concatenate([antes, np.zeros(m, np.float32), despues])
        pk = float(np.abs(y).max()) if y.size else 0.0
        if pk > 0.97:
            y *= 0.97 / pk
        with wave.open(wav, "wb") as f:
            f.setnchannels(1); f.setsampwidth(2); f.setframerate(sr)
            f.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())
        # los tiempos de las palabras posteriores a cada respiro se desplazan
        if inserts:   # (la palabra enfatizada también se desplaza: el silencio va delante de ella)
            for j, (a, b) in enumerate(palabras):
                desplaza = sum(m for pos, m in inserts if pos <= int(a * sr)) / sr
                palabras[j] = [round(a + desplaza, 3), round(b + desplaza, 3)]
        return True
    except Exception as e:
        log(f"Voz: énfasis no aplicado ({str(e)[-120:]})")
        return False


def anadir_voz(video, locucion, trabajo):
    tramos, wavs, motor, aj = preparar_voz(locucion, trabajo)
    if not tramos:
        return
    mezclar_voz(video, tramos, wavs, aj, trabajo)
    return motor


def mezclar_voz(video, tramos, wavs, aj, trabajo):
    cadena = (aj.get("cadena_voz") or "").strip().strip(",")
    try:
        _mezclar_voz(video, tramos, wavs, aj, cadena, trabajo)
    except ErrorAPI as e:
        if not cadena:
            raise
        # Si la cadena de voz de equipo/voz.json da problemas, se mezcla sin ella en vez de no publicar.
        log(f"Cadena de voz descartada en este render ({str(e)[-160:]}); se mezcla sin procesar la voz")
        _mezclar_voz(video, tramos, wavs, aj, "", trabajo)


def resolver_videos_guion(cfg, guion, trabajo):
    """Clips de video REAL del propio usuario en un guion en modo humano (6/11/2026, humanizar).
    En "imagenes" una entrada puede llevar {"original_id": "<id del reel antiguo de la cuenta>", "inicio": s, ...}:
    aquí se descarga ese reel (media_url de la API) a la carpeta de trabajo y se escribe una copia del guion con
    "video": <ruta local> para hacer_reel.py. Si un original no se puede bajar, la entrada queda como estaba
    (hacer_reel.py la ignora y usa la foto "url" si la hay, o el fondo neutro) y se anota en registro.log.
    Devuelve la ruta del guion que hay que renderizar (el original si no había nada que resolver)."""
    g = leer_json(guion, None)
    if not isinstance(g, dict):
        return guion
    cambiado = False
    bajados = {}
    for esc in g.get("escenas") or []:
        for im in (esc.get("imagenes") or []) if isinstance(esc, dict) else []:
            if not isinstance(im, dict):
                continue
            v = str(im.get("video") or "").strip()
            if v and not v.startswith("http") and not os.path.isabs(v):   # ruta relativa a la carpeta del guion
                im["video"] = os.path.join(os.path.dirname(os.path.abspath(guion)), v)
                cambiado = True
            oid = str(im.get("original_id") or "").strip()
            if not oid or im.get("video"):
                continue
            if oid not in bajados:
                destino = os.path.join(trabajo, f"original_{oid}.mp4")
                try:
                    url = api(cfg, oid, fields="media_url").get("media_url")
                    if not url:
                        raise ErrorAPI("Instagram no da media_url (¿música con licencia?)")
                    descargar(url, destino)
                    bajados[oid] = destino
                except Exception as e:
                    bajados[oid] = None
                    log(f"Clip propio {oid} no disponible ({str(e)[-160:]}); la escena usa su foto o el fondo neutro")
            if bajados.get(oid):
                im["video"] = bajados[oid]
                cambiado = True
    if not cambiado:
        return guion
    copia = os.path.join(trabajo, "guion_resuelto.json")
    escribir_json(copia, g)
    return copia


def grabar_pantalla_guion(guion, trabajo):
    """Plantilla de grabación de pantalla (7/11/2026, directiva «mismo patrón que @claudeai»): si junto al guion hay un
    grabacion.json, herramientas/grabar_pantalla.py abre la página REAL con Playwright (móvil/portátil sobre fondo plano,
    cursor, zoom) y escribe trabajo/grabacion.mp4; devuelve una copia del guion con "video" apuntando a él. Sin
    grabacion.json o si falla, devuelve el guion tal cual (hacer_reel.py ya se detiene si no encuentra el vídeo)."""
    carpeta = os.path.dirname(os.path.abspath(guion))
    spec = os.path.join(carpeta, "grabacion.json")
    if not os.path.exists(spec):
        return guion
    g = leer_json(guion, None)
    if not isinstance(g, dict) or str(g.get("modo", "")).lower() != "app":
        return guion
    salida = os.path.join(trabajo, "grabacion.mp4")
    r = subprocess.run([sys.executable, os.path.join(HERR_REEL, "grabar_pantalla.py"), spec, salida],
                       capture_output=True, text=True, timeout=900, cwd=HERR_REEL)
    if r.returncode != 0 or not os.path.exists(salida):
        raise ErrorAPI(f"La grabación de pantalla falló: {(r.stderr or r.stdout)[-400:]}")
    log("Grabación de pantalla: " + (r.stdout.strip().splitlines() or [""])[-1][:160])
    g["video"] = salida
    g.setdefault("plantilla", True)
    copia = os.path.join(trabajo, "guion_grabado.json")
    escribir_json(copia, g)
    return copia


def envolvente_voz(ruta, fps=30):
    """Envolvente de la voz de una frase (wav 16 bits) a `fps` valores por segundo, 0-1 (normalizada al percentil 95,
    suavizada): hacer_reel.py mueve la boca de Bit y Paco con ella (labios sincronizados con la voz real).
    Si algo falla devuelve None y el render alterna la boca con las palabras, como antes."""
    try:
        import numpy as np
        with wave.open(ruta) as w:
            sr, ch, sw = w.getframerate(), w.getnchannels(), w.getsampwidth()
            raw = w.readframes(w.getnframes())
        if sw != 2 or not raw:
            return None
        x = np.frombuffer(raw, "<i2").astype(np.float32).reshape(-1, ch).mean(axis=1) / 32768.0
        hop = max(1, int(sr / fps))
        nv = len(x) // hop
        if nv < 2:
            return None
        rms = np.sqrt((x[:nv * hop].reshape(nv, hop) ** 2).mean(axis=1))
        ref = max(float(np.percentile(rms, 95)), 1e-4)
        e = np.clip(rms / ref, 0.0, 1.0)
        e = np.convolve(e, [0.25, 0.5, 0.25], mode="same")   # suaviza (sin aleteo entre fotogramas)
        e = np.where(e < 0.06, 0.0, e)                       # el ruido de fondo no abre la boca
        return [round(float(v), 2) for v in e]
    except Exception:
        return None


def renderizar_guion(guion, video, trabajo):
    """Reel nuevo con la VOZ PRIMERO (6/11/2026, humanizar): 1) hacer_reel.py --solo-locucion escribe los tramos;
    2) se genera y recorta la voz; 3) hacer_reel.py --tiempos renderiza con cada escena alargada a la duración real
    de su frase (sin acelerar la voz) y los subtítulos al ritmo real; 4) se mezcla. Devuelve el motor de voz usado.
    Si el paso 1 falla (generador antiguo), se hace como antes: render y después la voz acelerada para que quepa."""
    locucion = os.path.splitext(video)[0] + ".locucion.json"
    r = subprocess.run([sys.executable, os.path.join(HERR_REEL, "hacer_reel.py"), guion, video, "--solo-locucion"],
                       capture_output=True, text=True, timeout=300, cwd=HERR_REEL)
    tramos, wavs, motor, aj = (None, None, None, None)
    if r.returncode == 0 and os.path.exists(locucion):
        tramos, wavs, motor, aj = preparar_voz(locucion, trabajo)
    else:
        log(f"Voz primero no disponible ({(r.stderr or r.stdout)[-160:]}); se renderiza como antes")
    cmd = [sys.executable, os.path.join(HERR_REEL, "hacer_reel.py"), guion, video]
    if tramos:
        tiempos = os.path.join(trabajo, "tiempos_voz.json")
        escribir_json(tiempos, {str(t.get("escena", i)): {"dur": round(d, 3), "palabras": t.get("palabras"),
                                                          "env": envolvente_voz(wav)}   # boca sincronizada con la voz
                                for i, (t, (wav, d)) in enumerate(zip(tramos, wavs))})
        cmd += ["--tiempos", tiempos]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1200, cwd=HERR_REEL)
    if r.returncode != 0 or not os.path.exists(video):
        raise ErrorAPI(f"El generador falló: {(r.stderr or r.stdout)[-500:]}")
    if not os.path.exists(locucion):
        return None
    if tramos:
        nuevos = [t for t in (leer_json(locucion, []) or []) if t.get("texto", "").strip()]
        if len(nuevos) == len(tramos) and all(a["texto"] == b["texto"] for a, b in zip(nuevos, tramos)):
            for a, b in zip(nuevos, tramos):   # los tiempos por palabra (alineación) viven en los tramos viejos
                if b.get("palabras"):
                    a["palabras"] = b["palabras"]
            mezclar_voz(video, nuevos, wavs, aj, trabajo)
            return motor
        log("Voz primero: los tramos cambiaron entre pasadas; se vuelve a generar la voz")
    return anadir_voz(video, locucion, trabajo)


def realce_enfasis(tramo, aj):
    """Filtros ffmpeg 'volume' con línea de tiempo para subir `enfasis.db` las palabras marcadas (grupos de
    palabras seguidas en un solo filtro, 20 ms de margen a cada lado). Cadena vacía si no hay énfasis o tiempos."""
    cfg = aj.get("enfasis") if isinstance(aj.get("enfasis"), dict) else {}
    pal = tramo.get("palabras"); idx = sorted(set(int(i) for i in (tramo.get("enfasis") or [])))
    if cfg.get("activo") is False or not pal or not idx:
        return ""
    db = float(cfg.get("db", 3.5))
    if db <= 0:
        return ""
    grupos, cur = [], None
    for i in idx:
        if i < 0 or i >= len(pal):
            continue
        if cur and i == cur[1] + 1:
            cur[1] = i
        else:
            if cur: grupos.append(cur)
            cur = [i, i]
    if cur: grupos.append(cur)
    # Ganancia con RAMPAS suaves (`rampa_ms`, 60 ms) a cada lado, no un escalón: un cambio brusco de nivel se oye
    # como un corte (queja del usuario 6/11). La expresión se evalúa por fotograma de audio (~23 ms).
    r = max(0.01, float(cfg.get("rampa_ms", 60)) / 1000.0)
    g = 10 ** (db / 20)
    out = "asetnsamples=n=256:p=0,"   # fotogramas de audio de 256 muestras (~6 ms) para que la rampa sea fina
    for a, b in grupos:
        t0 = max(r, float(pal[a][0]) - 0.01); t1 = float(pal[b][1]) + 0.01
        expr = (f"if(between(t,{t0:.3f},{t1:.3f}),{g:.4f},"
                f"if(between(t,{t0 - r:.3f},{t0:.3f}),1+({g:.4f}-1)*(t-{t0 - r:.3f})/{r:.3f},"
                f"if(between(t,{t1:.3f},{t1 + r:.3f}),{g:.4f}-({g:.4f}-1)*(t-{t1:.3f})/{r:.3f},1)))")
        out += f"volume=volume='{expr}':eval=frame,"
    return out


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
        proc += realce_enfasis(t, aj)   # énfasis (+dB en las palabras marcadas), después de la cadena
        filtros.append(f"[{i + 1}:a]aresample=44100,{proc}atempo={tempo:.3f},adelay={ms}|{ms},volume={aj['volumen_voz']}[v{i}]")
        etiquetas.append(f"[v{i}]")
    filtros.append(f"{''.join(etiquetas)}amix=inputs={len(etiquetas)}:normalize=0,pan=stereo|c0=c0|c1=c0,apad,asplit=2[vox][key]")
    filtros.append(f"[0:a][key]sidechaincompress=threshold={aj['umbral_duck']}:ratio={aj['ratio_duck']}:attack=15:release=350[fondo]")
    filtros.append(f"[fondo][vox]amix=inputs=2:duration=first:normalize=0,alimiter=limit={aj['limite']}:level=false[a]")
    salida = os.path.join(trabajo, "con_voz.mp4")
    r = subprocess.run(["ffmpeg", "-y", *entradas, "-filter_complex", ";".join(filtros),
                        "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                        "-movflags", "+faststart", "-shortest", salida], capture_output=True, timeout=600)
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
        cmd = None  # reel nuevo: voz primero y después el render ajustado a la voz (renderizar_guion)
    else:
        raise ErrorAPI("Falta guion.json o remaster.json")
    locucion = os.path.join(trabajo, "video.locucion.json")
    if cmd is None:
        guion = grabar_pantalla_guion(os.path.join(carpeta, "guion.json"), trabajo)
        guion = resolver_videos_guion(cfg, guion, trabajo)
        motor = renderizar_guion(guion, video, trabajo)
        if os.path.exists(locucion):
            shutil.copy(locucion, os.path.join(carpeta, "locucion.json"))
        if motor:
            post["motor_voz"] = motor
    else:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=1200, cwd=HERR_REEL)
        if r.returncode != 0 or not os.path.exists(video):
            raise ErrorAPI(f"El generador falló: {(r.stderr or r.stdout)[-500:]}")
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
        if post.get("renderizado") or post.get("tipo") in ("carrusel", "imagen", "historia") or hechos >= MAX_RENDERS:
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


def subir_y_esperar(cfg, cid, video, uri=None):
    uri = uri or f"https://rupload.facebook.com/ig-api-upload/{cfg['version']}/{cid}"
    with open(video, "rb") as f:
        datos = f.read()
    peticion(uri, "POST", cuerpo=datos, timeout=600, cabeceras={
        "Authorization": f"OAuth {cfg['page_token']}", "offset": "0", "file_size": str(len(datos)),
        "Content-Type": "application/octet-stream"})
    esperar_contenedor(cfg, cid)


class _SinRedireccion(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def url_directa_release(nombre):
    """URL directa (firmada, sin redirección) del asset de la release 'cola'. Solo funciona con el repo PÚBLICO.
    Instagram descarga el vídeo desde ahí con video_url. La firma dura minutos: se pide justo antes de usarla."""
    repo = os.environ.get("GITHUB_REPOSITORY", "ajreparacion/instagram")
    url = f"https://github.com/{repo}/releases/download/{RELEASE}/{urllib.parse.quote(nombre)}"
    opener = urllib.request.build_opener(_SinRedireccion)
    try:
        opener.open(urllib.request.Request(url, method="HEAD"), timeout=60)
        return url
    except urllib.error.HTTPError as e:
        if e.code in (301, 302, 303, 307, 308) and e.headers.get("Location"):
            return e.headers["Location"]
        raise ErrorAPI(f"el vídeo no es descargable desde la release ({e.code}); ¿el repositorio es privado?")


def crear_contenedor_url(cfg, params, video):
    p = {k: v for k, v in params.items() if k != "upload_type"}
    p["video_url"] = url_directa_release(os.path.basename(video))
    r = api(cfg, f"{cfg['ig_user_id']}/media", "POST", **p)
    esperar_contenedor(cfg, r["id"])
    return r["id"]


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
    try:
        subir_y_esperar(cfg, cid, video, r.get("uri"))
    except ErrorAPI as e:
        if "trial_params" not in params:
            # 7/11/2026: en la nube la subida «resumable» falla siempre con ProcessingFailedError (010 y 014).
            # Plan B: Instagram descarga el vídeo él mismo desde la release (video_url; necesita repo público).
            log(f"subida directa fallida ({str(e)[-120:]}); se reintenta con video_url desde la release")
            cid = crear_contenedor_url(cfg, params, video)
            mid = api(cfg, f"{cfg['ig_user_id']}/media_publish", "POST", creation_id=cid)["id"]
            enlace = ""
            try:
                enlace = api(cfg, mid, fields="permalink").get("permalink", "")
            except ErrorAPI:
                pass
            return {"media_id": mid, "enlace": enlace, "prueba_no_seguidores": False, "metodo": "video_url"}
        # 6/11/2026: el 010 (reel de prueba) falló en la subida con «ProcessingFailedError: Request processing
        # failed». Si el contenedor de prueba no procesa el vídeo, se reintenta al momento como reel normal.
        log(f"reel de prueba: fallo al subir/procesar ({str(e)[-160:]}); se publica como reel normal")
        params.pop("trial_params")
        prueba = None
        try:
            r = api(cfg, f"{cfg['ig_user_id']}/media", "POST", **params)
            cid = r["id"]
            subir_y_esperar(cfg, cid, video, r.get("uri"))
        except ErrorAPI as e2:
            log(f"subida directa fallida ({str(e2)[-120:]}); se reintenta con video_url desde la release")
            cid = crear_contenedor_url(cfg, params, video)
    mid = api(cfg, f"{cfg['ig_user_id']}/media_publish", "POST", creation_id=cid)["id"]
    enlace = ""
    try:
        enlace = api(cfg, mid, fields="permalink").get("permalink", "")
    except ErrorAPI:
        pass
    return {"media_id": mid, "enlace": enlace, "prueba_no_seguidores": bool(prueba)}


def aprobado(carpeta, cuando, ahora):
    # 7/11/2026 (orden del dueño: «hay que pasar todo por calidad, subir mucho más el listón»):
    # nada sale sin el visto bueno explícito de Calidad y con nota mínima. Se acabó la gracia de 3 h.
    cal = leer_json(os.path.join(carpeta, "calidad.json"))
    if cal is None:
        return False
    try:
        nota = float(cal.get("nota", 0))
    except (TypeError, ValueError):
        nota = 0
    return bool(cal.get("aprobado")) and nota >= NOTA_MINIMA


def publicar_carrusel(cfg, carpeta, post):
    """Publica una imagen o un carrusel (2-10 imágenes JPG en <carpeta>/slides/, en orden alfabético).
    Instagram descarga cada imagen desde raw.githubusercontent.com (el repo es público)."""
    repo = os.environ.get("GITHUB_REPOSITORY", "ajreparacion/instagram")
    rama = os.environ.get("GITHUB_REF_NAME", "main")
    carpeta_rel = os.path.relpath(carpeta, os.path.dirname(os.path.abspath(__file__)))
    imgs = sorted(f for f in os.listdir(os.path.join(carpeta, "slides")) if f.lower().endswith((".jpg", ".jpeg")))[:10]
    if not imgs:
        raise ErrorAPI("el carrusel no tiene imágenes en slides/")
    # raw.githubusercontent no le vale a Instagram («Only photo or video can be accepted»): se usa la CDN
    # pública jsDelivr del repo público, fijada al commit del ciclo para que no sirva una versión vieja.
    ref = os.environ.get("GITHUB_SHA") or rama
    urls = [f"https://cdn.jsdelivr.net/gh/{repo}@{ref}/{urllib.parse.quote(carpeta_rel)}/slides/{urllib.parse.quote(f)}" for f in imgs]
    if len(urls) == 1:
        r = api(cfg, f"{cfg['ig_user_id']}/media", "POST", image_url=urls[0], caption=post.get("texto", ""))
        cid = r["id"]
    else:
        hijos = []
        for u in urls:
            h = api(cfg, f"{cfg['ig_user_id']}/media", "POST", image_url=u, is_carousel_item="true")["id"]
            esperar_contenedor(cfg, h, max_seg=300)
            hijos.append(h)
        cid = api(cfg, f"{cfg['ig_user_id']}/media", "POST", media_type="CAROUSEL",
                  children=",".join(hijos), caption=post.get("texto", ""))["id"]
    esperar_contenedor(cfg, cid, max_seg=300)
    mid = api(cfg, f"{cfg['ig_user_id']}/media_publish", "POST", creation_id=cid)["id"]
    enlace = ""
    try:
        enlace = api(cfg, mid, fields="permalink").get("permalink", "")
    except ErrorAPI:
        pass
    return {"media_id": mid, "enlace": enlace, "tipo": "carrusel" if len(urls) > 1 else "imagen", "imagenes": len(urls)}


def publicar_historia(cfg, carpeta, post):
    """Historia (8/11/2026): "tipo": "historia". Imagen = primer JPG de <carpeta>/slides/ (servido por jsDelivr fijado
    al commit, como los carruseles); vídeo = post["asset"] de la release 'cola' (video_url). Instagram no admite texto
    en las historias por API: el texto va dentro de la imagen."""
    repo = os.environ.get("GITHUB_REPOSITORY", "ajreparacion/instagram")
    ref = os.environ.get("GITHUB_SHA") or os.environ.get("GITHUB_REF_NAME", "main")
    carpeta_rel = os.path.relpath(carpeta, os.path.dirname(os.path.abspath(__file__)))
    sl = os.path.join(carpeta, "slides")
    imgs = sorted(f for f in os.listdir(sl) if f.lower().endswith((".jpg", ".jpeg"))) if os.path.isdir(sl) else []
    if imgs:
        url = f"https://cdn.jsdelivr.net/gh/{repo}@{ref}/{urllib.parse.quote(carpeta_rel)}/slides/{urllib.parse.quote(imgs[0])}"
        r = api(cfg, f"{cfg['ig_user_id']}/media", "POST", media_type="STORIES", image_url=url)
        esperar_contenedor(cfg, r["id"], max_seg=300)
    elif post.get("asset"):
        r = api(cfg, f"{cfg['ig_user_id']}/media", "POST", media_type="STORIES",
                video_url=url_directa_release(post["asset"]))
        esperar_contenedor(cfg, r["id"])
    else:
        raise ErrorAPI("la historia no tiene imagen en slides/ ni 'asset' de vídeo")
    mid = api(cfg, f"{cfg['ig_user_id']}/media_publish", "POST", creation_id=r["id"])["id"]
    if post.get("asset") and not imgs:
        gh("release", "delete-asset", RELEASE, post["asset"], "-y", check=False)
    return {"media_id": mid, "tipo": "historia", "medio": "imagen" if imgs else "video"}


def publicar_pendientes(cfg):
    ahora = datetime.now(timezone.utc)
    for cuando, carpeta, post in carpetas_cola():
        if cuando > ahora or not (post.get("renderizado") or post.get("tipo") in ("carrusel", "imagen", "historia")):
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
        if post.get("tipo") == "historia":
            # Las historias no cuentan para el límite de una publicación por pasada ni bloquean la cola.
            try:
                res = publicar_historia(cfg, carpeta, post)
                res["publicado"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
                mover(carpeta, PUBLICADOS, res)
                log(f"{nombre}: historia publicada ({res.get('media_id')})")
            except Exception as e:
                intentos = post.get("_intentos", 0) + 1
                post["_intentos"] = intentos
                escribir_json(os.path.join(carpeta, "post.json"), post)
                log(f"{nombre}: fallo al publicar la historia {intentos}/3: {e}")
                if intentos >= 3:
                    mover(carpeta, ERRORES, {"error": str(e), "intentos": intentos})
            finally:
                shutil.rmtree(trabajo, ignore_errors=True)
            continue
        try:
            if post.get("tipo") in ("carrusel", "imagen"):
                res = publicar_carrusel(cfg, carpeta, post)
                res["publicado"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
                mover(carpeta, PUBLICADOS, res)
                log(f"{nombre}: publicado {res.get('enlace')}")
                continue
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
