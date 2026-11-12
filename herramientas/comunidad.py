#!/usr/bin/env python3
"""Comunidad: comentarios de Facebook y YouTube — orden del dueño 12/11/2026 17:50.

  python3 herramientas/comunidad.py recoger   # añade comentarios nuevos a comunidad/pendientes.json (nombre público, texto, id, fecha)
  python3 herramientas/comunidad.py responder # publica comunidad/respuestas.json y marca lo respondido

comunidad/respuestas.json (lo escribe el agente «Redes · Comunidad y monetización»):
  [{"canal": "facebook"|"youtube", "id": "<id del comentario>", "accion": "responder"|"ocultar"|"spam", "texto": "..."}]
Facebook: POST /{comment-id}/comments; ocultar/spam → is_hidden=true. YouTube: comments.insert (alcance youtube; si el token no
lo tiene, queda en comunidad/sin_publicar.json y se avisa en el resumen). Lo ya hecho va a comunidad/hechos.json.
Tokens solo por variables de entorno (FACEBOOK_PAGE_TOKEN, YOUTUBE_*); nunca se registran.
"""
import json
import os
import sys
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "herramientas"))
D = os.path.join(RAIZ, "comunidad")
PEND, RESP, HECHOS, SIN = (os.path.join(D, f) for f in ("pendientes.json", "respuestas.json", "hechos.json", "sin_publicar.json"))
MAX_RESPUESTAS = 30


def _j(r, d):
    try:
        return json.load(open(r, encoding="utf-8"))
    except Exception:
        return d


def _w(r, d):
    os.makedirs(D, exist_ok=True)
    json.dump(d, open(r, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def comentarios_youtube(maximo=50):
    import youtube
    api = youtube.API
    if youtube.credenciales_listas():
        tok = {"Authorization": f"Bearer {youtube.token_acceso()}"}
        canal = youtube.comprobar()["canal_id"]
        url = f"{api}/commentThreads?part=snippet&allThreadsRelatedToChannelId={canal}&maxResults={maximo}&order=time"
        cab = tok
    elif os.environ.get("YOUTUBE_API_KEY"):
        return []   # con solo la clave de API no se puede localizar el canal propio sin su ID; se necesita OAuth
    else:
        return []
    _, _, cuerpo = youtube._peticion(url, cabeceras=cab)
    sal = []
    for it in json.loads(cuerpo).get("items", []):
        c = it["snippet"]["topLevelComment"]
        s = c["snippet"]
        if s.get("authorChannelId", {}).get("value") == canal:
            continue
        sal.append({"canal": "youtube", "id": c["id"], "post": it["snippet"].get("videoId", ""), "nombre": s.get("authorDisplayName", ""),
                    "texto": s.get("textDisplay", ""), "fecha": s.get("publishedAt", "")})
    return sal


def recoger():
    pend = {(c["canal"], c["id"]): c for c in _j(PEND, [])}
    hechos = set(_j(HECHOS, []))
    nuevos, avisos = 0, []
    fuentes = []
    try:
        import facebook
        if facebook.credenciales_listas():
            fuentes.append(("facebook", facebook.comentarios_nuevos))
    except Exception as e:
        avisos.append(f"facebook: {e}")
    fuentes.append(("youtube", comentarios_youtube))
    for nombre, fn in fuentes:
        try:
            for c in fn():
                k = (c["canal"], c["id"])
                if k not in pend and f"{c['canal']}:{c['id']}" not in hechos:
                    pend[k] = c
                    nuevos += 1
        except Exception as e:
            avisos.append(f"{nombre}: {str(e)[-200:]}")
    _w(PEND, sorted(pend.values(), key=lambda c: c.get("fecha", ""))[-300:])
    print(json.dumps({"nuevos": nuevos, "pendientes": len(pend), "avisos": avisos}, ensure_ascii=False))


def _yt_responder(padre, texto):
    import youtube
    cuerpo = json.dumps({"snippet": {"parentId": padre, "textOriginal": texto}}).encode()
    youtube._peticion(f"{youtube.API}/comments?part=snippet", cuerpo,
                      {"Authorization": f"Bearer {youtube.token_acceso()}", "Content-Type": "application/json"}, "POST")


def _yt_ocultar(cid):
    import youtube
    # moderationStatus=rejected: lo retira de la vista pública (sin banear al autor)
    youtube._peticion(f"{youtube.API}/comments/setModerationStatus?id={cid}&moderationStatus=rejected", b"",
                      {"Authorization": f"Bearer {youtube.token_acceso()}", "Content-Length": "0"}, "POST")


def responder():
    resp = _j(RESP, [])
    hechos = set(_j(HECHOS, []))
    sin = _j(SIN, [])
    resto, n = [], 0
    for r in resp:
        clave = f"{r.get('canal')}:{r.get('id')}"
        if clave in hechos:
            continue
        if n >= MAX_RESPUESTAS:
            resto.append(r)
            continue
        acc = r.get("accion", "responder")
        try:
            if r["canal"] == "facebook":
                import facebook
                if acc == "responder":
                    facebook.responder(r["id"], r["texto"])
                else:
                    facebook.ocultar(r["id"])
            elif r["canal"] == "youtube":
                if acc == "responder":
                    _yt_responder(r["id"], r["texto"])
                else:
                    _yt_ocultar(r["id"])
            else:
                continue
            hechos.add(clave)
            n += 1
            time.sleep(2)
        except Exception as e:
            msg = str(e)[-200:]
            if "insufficient" in msg.lower() or "forbidden" in msg.lower() or "403" in msg:
                sin.append({**r, "motivo": msg})   # falta alcance/permiso: acción del dueño (ver pendiente_usuario.md)
                hechos.add(clave)
            else:
                resto.append({**r, "error": msg})
    _w(RESP, resto)
    _w(HECHOS, sorted(hechos))
    _w(SIN, sin)
    pend = [c for c in _j(PEND, []) if f"{c['canal']}:{c['id']}" not in hechos]
    _w(PEND, pend)
    print(json.dumps({"hechas": n, "reintentar": len(resto), "sin_publicar": len(sin)}, ensure_ascii=False))


if __name__ == "__main__":
    o = sys.argv[1] if len(sys.argv) > 1 else ""
    if o == "recoger":
        recoger()
    elif o == "responder":
        responder()
    else:
        sys.exit(__doc__)
