#!/usr/bin/env python3
"""Falla (salida 1) si hay logo antiguo NL neón en archivos del repo."""
import hashlib, pathlib, re, subprocess, sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
URL = b"c25965060_neogest-lab-logo"
NOMBRE = re.compile(r"neogest-lab-logo|logo[_-]?nl|nl[_-]?neon", re.I)
SALTAR_DIRS = {"archivo", "descartados"}
SALTAR_FICHEROS = {"DIRECTIVA_VIGENTE.md", "comprobar_logo.py", "marca_2026_LEEME.md", "revision_total.py"}

def hashes_antiguos():
    f = RAIZ / "equipo" / "marca_antigua.sha256"
    if not f.exists():
        return set()
    return {x for x in f.read_text().split() if len(x) == 64}

def main():
    h_old = hashes_antiguos()
    salida = subprocess.run(["git", "ls-files", "-z"], cwd=RAIZ, capture_output=True, text=True).stdout
    malos = []
    for rel in filter(None, salida.split("\0")):
        p = RAIZ / rel
        if not p.is_file() or p.name in SALTAR_FICHEROS:
            continue
        if SALTAR_DIRS & set(p.relative_to(RAIZ).parts[:-1]):
            continue
        if NOMBRE.search(p.name):
            malos.append((rel, "nombre de archivo"))
            continue
        datos = p.read_bytes()
        if hashlib.sha256(datos).hexdigest() in h_old:
            malos.append((rel, "hash de una versión antigua del logo"))
        elif URL in datos:
            malos.append((rel, "URL antigua"))
    for rel, motivo in malos:
        print("LOGO ANTIGUO: %s (%s)" % (rel, motivo))
    if malos:
        sys.exit(1)
    print("LIMPIO")

if __name__ == "__main__":
    main()
