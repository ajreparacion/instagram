#!/usr/bin/env python3
"""Publicación en la página de Facebook «Neogestlab» (ID 1437632859434095) — orden del dueño 12/11/2026.

Solo biblioteca estándar. El token de página va SOLO por la variable de entorno FACEBOOK_PAGE_TOKEN
(secreto de GitHub Actions): nunca se imprime, registra ni guarda en el repo, que es público.

Uso:
  python3 herramientas/facebook.py comprobar                       # lee el nombre de la página; no publica
  python3 herramientas/facebook.py reel video.mp4 post.json         # publica un reel
  python3 herramientas/facebook.py foto carpeta_con_slides post.json  # foto o carrusel (/photos + /feed)

Desde publicar_gh.py se llama tras publicar en Instagram; si falla, Instagram no se ve afectado.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

PAGINA = "1437632859434095"
GRAPH = "https://graph.facebook.com/v27.0"
GRAPH_VIDEO = "https://rupload.facebook.com/video-upload/v27.0"
CENTRO = "https://centro-de-contenido-apps-2f0a3cd6.base44.app"
SEGUIR = "👉 Sigue la página Neogestlab para ver una pieza nueva cada día."


def credenciales_listas():
    return bool(os.environ.get("FACEBOOK_PAGE_TOKEN"))


_TOKEN_PAGINA = None


def _token():
    """Token de la PÁGINA. Si el secreto guarda un token de usuario (p. ej. ampliado a 60 días), se canjea aquí por el de la página:
    las publicaciones sin publicar (carruseles) exigen publicar como la propia página."""
    global _TOKEN_PAGINA
    if _TOKEN_PAGINA:
        return _TOKEN_PAGINA
    t = os.environ["FACEBOOK_PAGE_TOKEN"]
    try:
        q = urllib.parse.urlencode({"fields": "access_token", "access_token": t})
        with urllib.request.urlopen(f"{GRAPH}/{PAGINA}?{q}", timeout=60) as r:
            _TOKEN_PAGINA = json.loads(r.read()).get("access_token") or t
    except Exception:
        _TOKEN_PAGINA = t
    return _TOKEN_PAGINA


def _limpio(msg):
    """Quita los tokens (secreto y token de página) de cualquier texto antes de registrarlo o devolverlo."""
    s = str(msg)
    for t in (os.environ.get("FACEBOOK_PAGE_TOKEN"), _TOKEN_PAGINA):
        if t:
            s = s.replace(t, "***")
    return s


def _peticion(url, datos=None, cabeceras=None, metodo=None, timeout=120):
    req = urllib.request.Request(url, data=datos, headers=cabeceras or {}, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            cuerpo = r.read()
            return json.loads(cuerpo) if cuerpo else {}
    except urllib.error.HTTPError as e:
        raise RuntimeError(_limpio(f"Facebook HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:400]}")) from None


def graph(ruta, metodo="GET", **params):
    params["access_token"] = _token()
    q = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    if metodo == "GET":
        return _peticion(f"{GRAPH}/{ruta}?{q}")
    return _peticion(f"{GRAPH}/{ruta}", q.encode(), {"Content-Type": "application/x-www-form-urlencoded"}, "POST")


def comprobar():
    d = graph(PAGINA, fields="id,name,fan_count,followers_count")
    return {"pagina_id": d.get("id"), "nombre": d.get("name"), "seguidores": d.get("followers_count", d.get("fan_count"))}


def texto_facebook(post):
    """Texto del post adaptado: bloque post["facebook"]["texto"] si existe; si no, el de Instagram con enlace src=facebook
    y llamada a seguir la página. Sin 'enlace en el perfil' (en Facebook no existe)."""
    fb = post.get("facebook") or {}
    m = re.search(r"solicitar\?app=([\w-]+)", post.get("texto", ""))
    app = post.get("app_slug") or post.get("slug") or (m.group(1) if m else None)
    enlace = f"{CENTRO}/solicitar?{'app=' + app + '&' if app else ''}src=facebook"
    if fb.get("texto"):
        t = fb["texto"]
    else:
        t = post.get("texto", "").replace("src=instagram", "src=facebook").replace("src=youtube", "src=facebook")
        t = re.sub(r"Enlace en el perfil\.?", f"Pídela aquí: {enlace}", t, flags=re.I)
        t = re.sub(r"(?im)^.*(comenta|escríbeme|escribeme).{0,60}por privado.*$", "", t)
        if enlace not in t and "ajreparacion.com" not in t:
            t += f"\n\n{enlace}"
    if SEGUIR not in t:
        t += f"\n\n{SEGUIR}"
    if "By Neogest Lab" not in t:
        t += "\nBy Neogest Lab"
    return re.sub(r"\n{3,}", "\n\n", t).strip()[:60000]


def publicar_reel(video, post):
    """Reel en la página (API de 3 fases: start → subida binaria → finish)."""
    if not credenciales_listas():
        return {"estado": "sin_credenciales"}
    tam = os.path.getsize(video)
    ini = graph(f"{PAGINA}/video_reels", "POST", upload_phase="start")
    vid, destino = ini["video_id"], ini["upload_url"]
    with open(video, "rb") as f:
        _peticion(destino, f.read(), {"Authorization": f"OAuth {_token()}", "offset": "0", "file_size": str(tam),
                                      "Content-Type": "application/octet-stream"}, "POST", timeout=900)
    graph(f"{PAGINA}/video_reels", "POST", upload_phase="finish", video_id=vid, video_state="PUBLISHED",
          description=texto_facebook(post), title=(post.get("texto", "").split("\n", 1)[0])[:100])
    return {"estado": "publicado", "video_id": vid, "enlace": f"https://www.facebook.com/reel/{vid}"}


def _subir_foto(ruta, **extra):
    """Sube una imagen local a /photos (multipart)."""
    lim = "----nl" + os.urandom(8).hex()
    campos = {"access_token": _token(), **{k: v for k, v in extra.items() if v is not None}}
    cuerpo = b""
    for k, v in campos.items():
        cuerpo += f'--{lim}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    cuerpo += (f'--{lim}\r\nContent-Disposition: form-data; name="source"; filename="{os.path.basename(ruta)}"\r\n'
               f'Content-Type: image/jpeg\r\n\r\n').encode() + open(ruta, "rb").read() + f"\r\n--{lim}--\r\n".encode()
    return _peticion(f"{GRAPH}/{PAGINA}/photos", cuerpo, {"Content-Type": f"multipart/form-data; boundary={lim}"}, "POST", 300)


def publicar_foto(carpeta, post):
    """Una imagen → /photos publicada; 2-10 → fotos sin publicar + un /feed con attached_media (carrusel de álbum)."""
    if not credenciales_listas():
        return {"estado": "sin_credenciales"}
    sl = os.path.join(carpeta, "slides")
    imgs = sorted(os.path.join(sl, f) for f in os.listdir(sl) if f.lower().endswith((".jpg", ".jpeg")))[:10]
    if not imgs:
        raise RuntimeError("sin imágenes en slides/")
    texto = texto_facebook(post)
    if len(imgs) == 1:
        d = _subir_foto(imgs[0], caption=texto, published="true")
        return {"estado": "publicado", "post_id": d.get("post_id") or d.get("id"),
                "enlace": f"https://www.facebook.com/{d.get('post_id') or d.get('id')}"}
    ids = [_subir_foto(i, published="false", temporary="true")["id"] for i in imgs]
    d = graph(f"{PAGINA}/feed", "POST", message=texto,
              attached_media=json.dumps([{"media_fbid": i} for i in ids]))
    return {"estado": "publicado", "post_id": d["id"], "enlace": f"https://www.facebook.com/{d['id']}"}


publicar_carrusel = publicar_foto


# ---- comunidad (la usa comunidad.py)
def comentarios_nuevos(limite_posts=25):
    """Comentarios recientes de los últimos posts de la página: solo nombre público, texto, id y fecha."""
    salida = []
    posts = graph(f"{PAGINA}/posts", fields="id,created_time", limit=limite_posts).get("data", [])
    for p in posts:
        for c in graph(f"{p['id']}/comments", fields="id,message,created_time,from{name}", limit=50, order="reverse_chronological").get("data", []):
            salida.append({"canal": "facebook", "id": c["id"], "post": p["id"], "nombre": (c.get("from") or {}).get("name", ""),
                           "texto": c.get("message", ""), "fecha": c.get("created_time", "")})
    return salida


def responder(comment_id, texto):
    return graph(f"{comment_id}/comments", "POST", message=texto)


def ocultar(comment_id):
    return graph(comment_id, "POST", is_hidden="true")


if __name__ == "__main__":
    orden = sys.argv[1] if len(sys.argv) > 1 else "comprobar"
    try:
        if orden == "comprobar":
            print(json.dumps(comprobar(), ensure_ascii=False))
        elif orden == "reel":
            print(json.dumps(publicar_reel(sys.argv[2], json.load(open(sys.argv[3]))), ensure_ascii=False))
        elif orden == "foto":
            print(json.dumps(publicar_foto(sys.argv[2], json.load(open(sys.argv[3]))), ensure_ascii=False))
        else:
            sys.exit(__doc__)
    except Exception as e:
        sys.exit(_limpio(f"ERROR: {e}"))
