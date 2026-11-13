#!/usr/bin/env python3
"""Colas de ATRASOS para Facebook y YouTube — orden del dueño 12/11/2026 17:50.

  python3 herramientas/atrasos.py construir   # regenera atrasos/facebook.json y atrasos/youtube.json (sin tocar lo ya publicado)
  python3 herramientas/atrasos.py pausar   # aplica atrasos/politica.json (escaparates pausados, DIRECTIVA §14) a las colas guardadas
  python3 herramientas/atrasos.py publicar facebook|youtube   # publica la siguiente pieza si toca (lo llama el ciclo)

Qué entra: publicados/ con calidad.json nota ≥ 90 (reels y carruseles; las historias caducan y no se reciclan) y los vídeos del
Centro (Base44 appId 6ae5244d4e2b32702f0a3cd6 → VideoMezcla) con estado «aprobado» (se añaden con `centro_videos.json`, ver abajo).
Orden: nota y retención (alcance medido en Instagram) de mayor a menor.
Límites por canal: 6 al día entre las 09:00 y las 22:00 (Madrid), separadas ≥ 100 min, sin repetir texto. YouTube: cuota ≈ 6
subidas/día CONTANDO las del ciclo. Los mp4 de reels ya publicados se borraron de la release: si no se pueden recuperar se saltan y
quedan apuntados en "saltados" de la cola. Los carruseles se recuperan de git (el commit anterior a quitar_imagenes).
"""
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

try:
    from zoneinfo import ZoneInfo
    MADRID = ZoneInfo("Europe/Madrid")
except Exception:  # pragma: no cover
    MADRID = timezone(timedelta(hours=1))

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "herramientas"))
CENTRO = "https://centro-de-contenido-apps-2f0a3cd6.base44.app"
# 12/11/2026 (dueño: «en Facebook se pueden subir reels de forma masiva»): Facebook hasta 12 al día; YouTube sigue en 6 por la cuota.
MAX_POR_CANAL = {"facebook": 12, "youtube": 6}
MAX_DIA, HORA_INI, HORA_FIN, SEPARACION_MIN, NOTA_MIN = 6, 9, 22, 60, 90
COLAS = {c: os.path.join(RAIZ, "atrasos", f"{c}.json") for c in ("facebook", "youtube")}


POLITICA = os.path.join(RAIZ, "atrasos", "politica.json")


def es_humor_personaje(p):
    """Pieza de humor con personaje de la serie (El Jambo, la Jupillo, la Pelota, el Bola, la Trámites o «Las IAs de la oficina»)."""
    pol = _json(POLITICA, {})
    t = " ".join(str(p.get(k) or "") for k in ("texto", "id", "serie", "personaje")).lower()
    return any(w in t for w in pol.get("palabras_personaje", []))


def es_escaparate(p):
    """Escaparate de app o web: vídeo del Centro, o pieza con app / enlace /solicitar?app= en el texto (DIRECTIVA §14)."""
    if p.get("tipo") == "video_centro" or p.get("app"):
        return True
    t = str(p.get("texto") or "").lower()
    return "solicitar?app=" in t or "ajreparacion.com" in t


def aplicar_pausa(cola):
    """Marca como «pausado» (nunca borra) lo pendiente que es escaparate sin personaje mientras la política lo pida; si la
    política se desactiva, devuelve a «pendiente» lo que ella pausó. Devuelve el número de piezas cambiadas."""
    pol = _json(POLITICA, {})
    activa = bool(pol.get("pausa_escaparates"))
    n = 0
    for p in cola.get("piezas", []):
        if activa and p.get("estado") == "pendiente" and es_escaparate(p) and not es_humor_personaje(p):
            p["estado"] = "pausado"
            p["motivo_pausa"] = "escaparate de app/web sin personaje: pausado por DIRECTIVA §14 (13/11/2026) hasta nuevo dato"
            n += 1
        elif not activa and p.get("estado") == "pausado" and p.get("motivo_pausa"):
            p["estado"] = "pendiente"
            p.pop("motivo_pausa", None)
            n += 1
    return n


def pausar():
    """Aplica la política a las dos colas ya guardadas, sin reconstruirlas."""
    for c, ruta in COLAS.items():
        cola = _json(ruta, None)
        if not cola:
            continue
        n = aplicar_pausa(cola)
        if n:
            _guardar(ruta, cola)
        est = {}
        for p in cola["piezas"]:
            est[p.get("estado")] = est.get(p.get("estado"), 0) + 1
        print(c, "cambiadas:", n, est)


def _json(ruta, defecto):
    try:
        return json.load(open(ruta, encoding="utf-8"))
    except Exception:
        return defecto


def _guardar(ruta, datos):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    json.dump(datos, open(ruta, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def _git(*a):
    return subprocess.run(["git", "-C", RAIZ, *a], capture_output=True, text=True)


def huella(texto):
    return hashlib.sha1(re.sub(r"\W+", " ", texto.lower()).strip()[:400].encode()).hexdigest()[:16]


def _commit_imagenes(nombre):
    """Último commit que contenía slides/ de la pieza (el anterior al que las quitó); None si no hay."""
    for base in ("cola", "publicados"):
        r = _git("log", "--all", "-n1", "--format=%H", "--", f"{base}/{nombre}/slides")
        if r.stdout.strip():
            c = r.stdout.strip()
            if _git("ls-tree", "-r", "--name-only", c, f"{base}/{nombre}/slides").stdout.strip():
                return c, f"{base}/{nombre}/slides"
            if _git("ls-tree", "-r", "--name-only", c + "^", f"{base}/{nombre}/slides").stdout.strip():
                return c + "^", f"{base}/{nombre}/slides"
    return None


def _retencion():
    est = _json(os.path.join(RAIZ, "estadisticas.json"), {})
    sal = {}
    for p in est.get("posts", []):
        m = p.get("metricas") or {}
        sal[p["id"]] = float(m.get("reach") or 0) if isinstance(m, dict) else 0.0
    return sal


def construir():
    ret = _retencion()
    previo = {c: _json(r, {"piezas": [], "saltados": []}) for c, r in COLAS.items()}
    hechos = {c: {p["id"]: p for p in previo[c]["piezas"] if p.get("estado") == "publicado"} for c in COLAS}
    nuevas = {c: [] for c in COLAS}
    saltados = {c: [] for c in COLAS}
    for carpeta in sorted(glob.glob(os.path.join(RAIZ, "publicados", "*"))):
        nombre = os.path.basename(carpeta)
        cal, post = _json(os.path.join(carpeta, "calidad.json"), {}), _json(os.path.join(carpeta, "post.json"), {})
        res = _json(os.path.join(carpeta, "resultado.json"), {})
        tipo = post.get("tipo")
        if not cal.get("aprobado") or (cal.get("nota") or 0) < NOTA_MIN or tipo not in ("reel", "carrusel", "imagen"):
            continue
        base = {"id": nombre, "tipo": tipo, "nota": cal["nota"], "retencion": ret.get(res.get("media_id"), 0.0),
                "texto": post.get("texto", ""), "app": post.get("app")}
        if tipo == "reel":
            for c in COLAS:
                saltados[c].append({"id": nombre, "motivo": "el mp4 se borró de la release tras publicar y no se conserva en git"})
            continue
        ci = _commit_imagenes(nombre)
        if not ci:
            saltados["facebook"].append({"id": nombre, "motivo": "imágenes no recuperables del historial de git"})
            continue
        nuevas["facebook"].append({**base, "commit": ci[0], "ruta": ci[1]})
        saltados["youtube"].append({"id": nombre, "motivo": "carrusel de imágenes: no es vídeo"})
    for v in _json(os.path.join(RAIZ, "atrasos", "centro_videos.json"), []):
        # lo escribe quien tenga acceso a Base44 (VideoMezcla con estado «aprobado»): {slug, formato, titulo, duracion, mp4}
        if v.get("estado") != "aprobado":
            continue
        enlace = lambda src: f"{CENTRO}/solicitar?app={v['slug']}&src={src}"
        base = {"id": f"centro_{v['slug']}_{v['formato']}", "tipo": "video_centro", "nota": 90, "retencion": 0.0,
                "app": v.get("titulo"), "url_mp4": CENTRO + v["mp4"], "duracion": v.get("duracion"),
                "texto": f"{v['titulo']}\n\nPrueba gratuita: {enlace('{src}')}\nBy Neogest Lab"}
        nuevas["facebook"].append({**base, "texto": base["texto"].replace("{src}", "facebook")})
        if v.get("formato") in ("vertical", "reel"):
            nuevas["youtube"].append({**base, "texto": base["texto"].replace("{src}", "youtube"),
                                      "largo": (v.get("duracion") or 0) > 59})
    for c in COLAS:
        ya = set(hechos[c])
        pend = [p for p in nuevas[c] if p["id"] not in ya]
        pend.sort(key=lambda p: (-p["nota"], -p["retencion"]))
        usados = {}
        for p in pend:
            h = huella(p["texto"])
            p["huella"] = h
            p["estado"] = "pendiente"
            if h in usados:
                saltados[c].append({"id": p["id"], "motivo": "texto repetido de " + usados[h]})
                p["estado"] = "saltado"
            usados.setdefault(h, p["id"])
        pend = [p for p in pend if p["estado"] == "pendiente"]
        cola_nueva = {"canal": c, "generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                      "piezas": list(hechos[c].values()) + pend, "saltados": saltados[c]}
        pausadas = aplicar_pausa(cola_nueva)
        _guardar(COLAS[c], cola_nueva)
        print(c, "pendientes:", len(pend) - pausadas, "pausadas:", pausadas, "publicadas:", len(ya), "saltadas:", len(saltados[c]))


def _publicadas_hoy(canal):
    hoy = datetime.now(MADRID).date()
    n, ultima = 0, None
    for p in _json(COLAS[canal], {}).get("piezas", []):
        if p.get("estado") == "publicado":
            t = datetime.fromisoformat(p["publicado"])
            if t.astimezone(MADRID).date() == hoy:
                n += 1
            ultima = max(ultima, t) if ultima else t
    if canal == "youtube":   # la cuota cuenta también los Shorts del ciclo
        for f in glob.glob(os.path.join(RAIZ, "publicados", "*", "resultado.json")):
            r = _json(f, {})
            if (r.get("youtube") or {}).get("estado") == "publicado" and r.get("publicado"):
                t = datetime.fromisoformat(r["publicado"]).replace(tzinfo=timezone.utc) if "+" not in r["publicado"] else datetime.fromisoformat(r["publicado"])
                if t.astimezone(MADRID).date() == hoy:
                    n += 1
    return n, ultima


def _recuperar_imagenes(p, destino):
    os.makedirs(os.path.join(destino, "slides"), exist_ok=True)
    if _git("cat-file", "-e", p["commit"]).returncode != 0:
        _git("fetch", "--unshallow", "-q")
    nombres = [n for n in _git("ls-tree", "-r", "--name-only", p["commit"], p["ruta"]).stdout.split("\n") if n]
    for n in nombres:
        datos = subprocess.run(["git", "-C", RAIZ, "show", f"{p['commit']}:{n}"], capture_output=True).stdout
        open(os.path.join(destino, "slides", os.path.basename(n)), "wb").write(datos)
    if not nombres:
        raise RuntimeError("no se pudieron recuperar las imágenes de git")


def publicar(canal, ahora=None, simular=False):
    cola = _json(COLAS[canal], None)
    if not cola:
        return {"estado": "sin_cola"}
    ahora = ahora or datetime.now(timezone.utc)
    m = ahora.astimezone(MADRID)
    if not (HORA_INI <= m.hour < HORA_FIN):
        return {"estado": "fuera_de_horario"}
    hoy, ultima = _publicadas_hoy(canal)
    if hoy >= MAX_POR_CANAL.get(canal, MAX_DIA):
        return {"estado": "tope_diario", "hoy": hoy}
    if ultima and ahora - ultima < timedelta(minutes=SEPARACION_MIN):
        return {"estado": "espera_separacion"}
    if aplicar_pausa(cola) and not simular:   # defensa: una cola construida antes de la política no saca escaparates
        _guardar(COLAS[canal], cola)
    vistos = {p["huella"] for p in cola["piezas"] if p.get("estado") == "publicado"}
    for p in cola["piezas"]:
        if p.get("estado") != "pendiente":
            continue
        if p["huella"] in vistos:
            p["estado"] = "saltado"
            continue
        if simular:
            return {"estado": "siguiente", "id": p["id"]}
        import tempfile
        trabajo = tempfile.mkdtemp(prefix="atraso_")
        try:
            post = {"texto": p["texto"], "app": p.get("app"), "tipo": p["tipo"],
                    "youtube": {"largo": p.get("largo", False)}}
            if canal == "facebook":
                import facebook
                if not facebook.credenciales_listas():
                    return {"estado": "sin_credenciales"}
                if p["tipo"] == "video_centro":
                    v = os.path.join(trabajo, "v.mp4")
                    urllib.request.urlretrieve(p["url_mp4"], v)
                    res = facebook.publicar_reel(v, post)
                else:
                    _recuperar_imagenes(p, trabajo)
                    res = facebook.publicar_foto(trabajo, post)
            else:
                import youtube
                if not youtube.credenciales_listas():
                    return {"estado": "sin_credenciales"}
                v = os.path.join(trabajo, "v.mp4")
                urllib.request.urlretrieve(p["url_mp4"], v)
                res = youtube.subir_short(v, post)
            p.update(estado="publicado", publicado=ahora.isoformat(timespec="seconds"), enlace=res.get("enlace", ""))
            _guardar(COLAS[canal], cola)
            return {"estado": "publicado", "id": p["id"], "enlace": p["enlace"]}
        except Exception as e:
            p["errores"] = p.get("errores", 0) + 1
            if p["errores"] >= 3:
                p["estado"] = "error"
            p["ultimo_error"] = str(e)[-200:]
            _guardar(COLAS[canal], cola)
            return {"estado": "error", "id": p["id"], "error": p["ultimo_error"]}
        finally:
            import shutil
            shutil.rmtree(trabajo, ignore_errors=True)
    _guardar(COLAS[canal], cola)
    return {"estado": "cola_vacia"}


if __name__ == "__main__":
    o = sys.argv[1] if len(sys.argv) > 1 else ""
    if o == "construir":
        construir()
    elif o == "pausar":
        pausar()
    elif o == "publicar" and len(sys.argv) > 2 and sys.argv[2] in COLAS:
        print(json.dumps(publicar(sys.argv[2], simular="--simular" in sys.argv), ensure_ascii=False))
    else:
        sys.exit(__doc__)
