#!/usr/bin/env python3
"""Diagnóstico de solo lectura: a qué apunta PAGE_TOKEN y qué cuenta de Instagram tiene vinculada la página.
Solo hace GET. El token nunca se imprime ni se guarda."""
import json, os, sys, urllib.request, urllib.error

TOKEN = os.environ.get("PAGE_TOKEN", "")
if not TOKEN:
    sys.exit("Falta el secreto PAGE_TOKEN en el repositorio.")
try:
    CFG = json.load(open("equipo/config_publico.json", encoding="utf-8"))
except (OSError, ValueError):
    CFG = {}
VERSION = CFG.get("version") or "v21.0"
PAGINA = CFG.get("page_id") or "107316837808795"
IG = CFG.get("ig_user_id") or "17841400403112257"
GRAPH = f"https://graph.facebook.com/{VERSION}"


def leer(ruta):
    req = urllib.request.Request(f"{GRAPH}/{ruta}", method="GET", headers={"Authorization": f"Bearer {TOKEN}"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        txt = e.read().decode(errors="replace")
        try:
            return e.code, json.loads(txt)
        except ValueError:
            return e.code, {"raw": txt[:300]}
    except urllib.error.URLError as e:
        return 0, {"raw": str(e.reason)[:300]}


def mostrar(titulo, ruta):
    st, resp = leer(ruta)
    print(f"\n== {titulo}\nGET /{ruta}\n{st} {json.dumps(resp, ensure_ascii=False)}")
    return st, resp


st1, yo = mostrar("1. ¿Quién es /me?", "me?fields=id,name")
st2, pag = mostrar(f"2. Página {PAGINA} y su Instagram vinculado",
                   f"{PAGINA}?fields=name,instagram_business_account,connected_instagram_account")
st3, ig = mostrar(f"3. Cuenta de Instagram {IG}", f"{IG}?fields=username")

print("\n== Resumen")
if st1 == 200:
    print(f"/me = {yo.get('id')} ({yo.get('name')}): "
          + ("ES la página configurada." if str(yo.get("id")) == str(PAGINA) else f"NO es la página {PAGINA}."))
else:
    print("/me no se pudo leer.")
if st2 == 200:
    iba = (pag.get("instagram_business_account") or {}).get("id")
    cia = (pag.get("connected_instagram_account") or {}).get("id")
    print(f"Página {PAGINA}: instagram_business_account={iba or 'ninguna'}, connected_instagram_account={cia or 'ninguna'}"
          + (f"; coincide con {IG}." if IG in (iba, cia) else f"; NO coincide con {IG}."))
else:
    print(f"Página {PAGINA} no se pudo leer.")
print(f"Instagram {IG}: username={ig.get('username')}" if st3 == 200 else f"Instagram {IG} no se pudo leer.")
