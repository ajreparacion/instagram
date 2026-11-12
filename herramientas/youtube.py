#!/usr/bin/env python3
"""Subida de Shorts a YouTube (canal NeogestLab @neogestlab) — orden del dueño 12/11/2026.

Solo biblioteca estándar. Credenciales SOLO por variables de entorno (secretos de GitHub Actions),
nunca en el repo, que es público:
  YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN  → subir (OAuth, alcance youtube)
  YOUTUBE_API_KEY                                                   → solo lectura (búsquedas, estadísticas públicas)

Uso:
  python3 herramientas/youtube.py comprobar          # dice a qué canal da acceso el token (no sube nada)
  python3 herramientas/youtube.py subir video.mp4 cola/XXX/post.json   # sube un Short y escribe el resultado en JSON

Desde publicar_gh.py se llama a subir_short(video, post) justo después de publicar el reel en Instagram,
antes de borrar el vídeo de la release. Si falla, Instagram no se ve afectado: el error queda en resultado.json.
Cuota de la API: cada subida gasta 1.600 de 10.000 unidades diarias → máx. ~6 subidas al día.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
API = "https://www.googleapis.com/youtube/v3"
CENTRO = "https://centro-de-contenido-apps-2f0a3cd6.base44.app"


def credenciales_listas():
    return all(os.environ.get(k) for k in ("YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN"))


def _peticion(url, datos=None, cabeceras=None, metodo=None, timeout=120):
    req = urllib.request.Request(url, data=datos, headers=cabeceras or {}, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        cuerpo = e.read().decode("utf-8", "replace")
        raise RuntimeError(f"YouTube HTTP {e.code}: {cuerpo[:400]}") from None


def token_acceso():
    datos = urllib.parse.urlencode({
        "client_id": os.environ["YOUTUBE_CLIENT_ID"],
        "client_secret": os.environ["YOUTUBE_CLIENT_SECRET"],
        "refresh_token": os.environ["YOUTUBE_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    }).encode()
    _, _, cuerpo = _peticion(TOKEN_URL, datos, {"Content-Type": "application/x-www-form-urlencoded"})
    return json.loads(cuerpo)["access_token"]


def comprobar():
    tok = token_acceso()
    _, _, cuerpo = _peticion(f"{API}/channels?part=snippet,statistics&mine=true",
                             cabeceras={"Authorization": f"Bearer {tok}"})
    items = json.loads(cuerpo).get("items", [])
    if not items:
        raise RuntimeError("El token no da acceso a ningún canal")
    c = items[0]
    return {"canal_id": c["id"], "titulo": c["snippet"]["title"],
            "handle": c["snippet"].get("customUrl", ""), "suscriptores": c.get("statistics", {}).get("subscriberCount")}


def _limpiar(texto, maximo):
    texto = re.sub(r"[<>]", "", texto or "").strip()
    return texto[:maximo]


def metadatos(post):
    """Título y descripción: bloque post["youtube"] si existe (lo escribe el Creador); si no, se derivan del texto del post."""
    yt = post.get("youtube") or {}
    texto = post.get("texto", "")
    primera = texto.split("\n", 1)[0].strip()
    titulo = yt.get("titulo") or primera
    if not yt.get("largo") and "#shorts" not in titulo.lower():
        titulo = titulo[:91].rstrip() + " #Shorts"
    app = post.get("app")
    enlace = f"{CENTRO}/solicitar?{'app=' + app + '&' if app else ''}src=youtube"
    if yt.get("descripcion"):
        desc = yt["descripcion"]
    else:
        desc = texto.replace("src=instagram", "src=youtube")
        desc = desc.replace("Enlace en el perfil.", f"Pídela aquí: {enlace}").replace("Enlace en el perfil", f"Pídela aquí: {enlace}")
        if enlace not in desc and "ajreparacion.com" not in desc:
            desc += f"\n\n{enlace}"
    if "By Neogest Lab" not in desc:
        desc += "\n\nBy Neogest Lab"
    etiquetas = yt.get("etiquetas") or re.findall(r"#(\w+)", texto)
    return {
        "snippet": {
            "title": _limpiar(titulo, 100),
            "description": _limpiar(desc, 4900),
            "tags": [t for t in etiquetas if t.lower() != "shorts"][:15],
            "categoryId": str(yt.get("categoria", "28")),  # 28 = Ciencia y tecnología
            "defaultLanguage": "es", "defaultAudioLanguage": "es",
        },
        "status": {
            "privacyStatus": yt.get("privacidad", "public"),
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": True,  # voz generada por IA: se declara siempre
        },
    }


def subir_short(video, post):
    if not credenciales_listas():
        return {"estado": "sin_credenciales"}
    tok = token_acceso()
    meta = json.dumps(metadatos(post)).encode()
    tam = os.path.getsize(video)
    _, cab, _ = _peticion(UPLOAD_URL, meta, {
        "Authorization": f"Bearer {tok}", "Content-Type": "application/json; charset=UTF-8",
        "X-Upload-Content-Type": "video/mp4", "X-Upload-Content-Length": str(tam)}, metodo="POST")
    destino = cab.get("Location") or cab.get("location")
    if not destino:
        raise RuntimeError("YouTube no devolvió la URL de subida")
    with open(video, "rb") as f:
        _, _, cuerpo = _peticion(destino, f.read(), {"Authorization": f"Bearer {tok}", "Content-Type": "video/mp4",
                                                      "Content-Length": str(tam)}, metodo="PUT", timeout=900)
    vid = json.loads(cuerpo)["id"]
    return {"estado": "publicado", "video_id": vid, "enlace": f"https://youtube.com/shorts/{vid}",
            "titulo": json.loads(meta)["snippet"]["title"]}


if __name__ == "__main__":
    orden = sys.argv[1] if len(sys.argv) > 1 else "comprobar"
    if orden == "comprobar":
        print(json.dumps(comprobar(), ensure_ascii=False))
    elif orden == "subir":
        print(json.dumps(subir_short(sys.argv[2], json.load(open(sys.argv[3]))), ensure_ascii=False))
    else:
        sys.exit(__doc__)
