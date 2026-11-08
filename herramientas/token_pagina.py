#!/usr/bin/env python3
"""Devuelve un token de la Página de Facebook a partir de PAGE_TOKEN.
Si PAGE_TOKEN ya es de la página, lo devuelve tal cual. Si es de usuario (p. ej. tras renovarlo
en el Explorador de la API de Graph), pide a Graph el token de esa página. Nunca imprime tokens.
Lo usan los scripts del chat (messenger_profile y me/messages exigen token de página)."""
import json, urllib.error, urllib.request


def _get(token, version, ruta):
    req = urllib.request.Request(f"https://graph.facebook.com/{version}/{ruta}",
                                 headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode(errors="replace"))
        except ValueError:
            return e.code, {}
    except (urllib.error.URLError, TimeoutError, ValueError):
        return 0, {}


def token_de_pagina(token, version, page_id):
    if not page_id:
        return token
    st, yo = _get(token, version, "me?fields=id")
    if st == 200 and str(yo.get("id")) == str(page_id):
        return token
    st, pag = _get(token, version, f"{page_id}?fields=access_token")
    if st == 200 and pag.get("access_token"):
        print(f"PAGE_TOKEN es de usuario: uso el token de la página {page_id} obtenido de Graph (no se imprime).")
        return pag["access_token"]
    st2, cuentas = _get(token, version, "me/accounts?fields=id,access_token&limit=100")
    for c in (cuentas.get("data") or []) if st2 == 200 else []:
        if str(c.get("id")) == str(page_id) and c.get("access_token"):
            print(f"PAGE_TOKEN es de usuario: uso el token de la página {page_id} de me/accounts (no se imprime).")
            return c["access_token"]
    err = (pag.get("error") or {}) if isinstance(pag, dict) else {}
    print(f"AVISO: no se pudo obtener el token de la página {page_id} "
          f"(código {err.get('code')}: {err.get('message')}). Sigo con PAGE_TOKEN tal cual.")
    return token
