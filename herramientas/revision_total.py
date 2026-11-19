#!/usr/bin/env python3
"""Revisión total del repo. Sin argumentos: informa y crea la guardia del logo. Con --aplicar: resetea renders viejos y sube."""
import glob, hashlib, json, os, re, subprocess, sys
from datetime import datetime, timedelta, timezone

APLICAR = "--aplicar" in sys.argv
os.chdir(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip())

def sh(*a):
    r = subprocess.run(a, capture_output=True, text=True)
    return (r.stdout + r.stderr).strip()

def titulo(t):
    print("\n=== %s ===" % t)

def leer(p):
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return None

def fecha(s):
    try:
        d = datetime.fromisoformat(s)
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except Exception:
        return None

# ---------- 0. sincronizar
titulo("0. Sincronizar")
sh("git", "config", "--global", "core.pager", "cat")
print(sh("git", "pull", "--rebase", "--autostash")[-300:])

# ---------- 1. cola y puerta
titulo("1. Cola y puerta de calidad (misma regla que puede_publicar)")
ahora = datetime.now(timezone.utc)
filas = []
for p in sorted(glob.glob("cola/*/post.json")):
    d = leer(p) or {}
    c = leer(p.replace("post.json", "calidad.json")) or {}
    try:
        nota = float(c.get("nota", 0))
    except (TypeError, ValueError):
        nota = 0
    if c.get("aprobado_por") == "dueño":
        est = "PASA (dueño)"
    elif c.get("caducado"):
        est = "BLOQ caducado"
    elif c.get("aprobado") is True and nota >= 90:
        est = "PASA"
    elif c.get("aprobado") is True:
        est = "BLOQ nota %s" % nota
    else:
        est = "BLOQ sin aprobar"
    cu = fecha(d.get("cuando", ""))
    if cu and ahora - cu > timedelta(hours=36):
        est += " + VENCIDO"
    filas.append((d.get("cuando", "?")[:16], os.path.basename(os.path.dirname(p)), est, bool(d.get("renderizado")), cu))
for f in sorted(filas):
    print(f[0], f[1].ljust(38), f[2].ljust(28), "render" if f[3] else "sin render")
prox = [f for f in filas if f[4] and ahora - timedelta(hours=36) < f[4] < ahora + timedelta(days=7)]
print("\nProgramados en los próximos 7 días: %d | pasan la puerta: %d" % (len(prox), sum(1 for f in prox if f[2].startswith("PASA"))))
huecos = (leer("equipo/plan.json") or {}).get("dias", [])
print("Huecos en plan.json: %d | con reel asignado: %d" % (len(huecos), sum(1 for h in huecos if h.get("cola"))))

# ---------- 2. pie de marca
titulo("2. Pie de marca")
src = open("herramientas/hacer_reel.py", encoding="utf-8").read()
print("isotipo_marca presente:", "def isotipo_marca" in src)
print("cuadrado 'NL' dibujado todavía:", bool(re.search(r'"NL"\s*,\s*font', src)))
for n in ("negativo", "color"):
    ruta = "herramientas/recursos/nl2026-isotipo-%s.png" % n
    print(ruta, "->", sh("file", ruta).split(":", 1)[-1].strip())
parche = sh("git", "log", "-1", "--format=%aI", "--grep=isotipo 2026")
fp = fecha(parche)
print("Parche del pie (fecha de autor):", parche or "no encontrado")
viejos, sin_fecha = [], []
for p in sorted(glob.glob("cola/*/post.json")):
    d = leer(p) or {}
    r = d.get("renderizado")
    if not r:
        continue
    fr = fecha(r) if isinstance(r, str) else None
    if fr is None:
        sin_fecha.append(p)
    elif fp and fr < fp:
        viejos.append((p, d))
print("Renderizados ANTES del parche (llevan el 'NL' dibujado):", len(viejos))
for p, d in viejos:
    print("  ", d.get("cuando", "?")[:16], p.split("/")[1])
if sin_fecha:
    print("Renderizados sin fecha legible (revisar a mano):", [p.split("/")[1] for p in sin_fecha])

if APLICAR and viejos:
    limite = ahora + timedelta(days=7)
    tocados = []
    for p, d in viejos:
        cu = fecha(d.get("cuando", ""))
        if not cu or cu > limite or ahora - cu > timedelta(hours=36):
            continue
        s = open(p, encoding="utf-8").read()
        n = re.sub(r'^[ \t]*"renderizado"[ \t]*:[^\n]*\n', "", s, count=1, flags=re.M)
        n = re.sub(r",(\s*})", r"\1", n)
        try:
            json.loads(n)
        except ValueError:
            print("  NO tocado (JSON inválido tras editar):", p)
            continue
        open(p, "w", encoding="utf-8").write(n)
        tocados.append(p)
    if tocados:
        print("Reseteados sin reformatear el JSON:", len(tocados))
        sh("git", "add", *tocados)
        print(sh("git", "commit", "-m", "marca: re-render de reels con pie antiguo (lote)"))

# ---------- 3. música
titulo("3. Música nueva: licencia")
pistas = leer("musica/pistas.json")
print(json.dumps(pistas, ensure_ascii=False, indent=1)[:1500] if pistas else "sin pistas.json")
print("musica/LICENCIAS.md:", "existe" if os.path.exists("musica/LICENCIAS.md") else "NO existe")
if pistas is not None and "licen" not in json.dumps(pistas).lower():
    print("AVISO: pistas.json no menciona licencia. Si son de Kevin MacLeod (CC BY), el post necesita el crédito. No las uses en vídeos publicados hasta confirmarlo.")

# ---------- 4. ramas
titulo("4. Ramas abiertas: ¿tocan archivos críticos?")
sh("git", "fetch", "--all", "--prune")
for rama in ("fix/336-grabacion-real", "fix/render-pendientes-externo"):
    out = sh("git", "diff", "--stat", "main...origin/" + rama)
    tocan = [l for l in out.splitlines() if re.search(r"hacer_reel|publicar_gh|ciclo\.yml|respuestas_chat", l)]
    print(rama, "->", "TOCA CRÍTICOS" if tocan else "no toca hacer_reel/publicar_gh/ciclo")
    for l in tocan:
        print("    ", l.strip())

# ---------- 5. último ciclo
titulo("5. Último ciclo")
print(sh("gh", "run", "list", "--workflow", "ciclo.yml", "-L", "3"))

# ---------- 6. guardia del logo
titulo("6. Guardia del logo antiguo")
GUARDIA = r'''#!/usr/bin/env python3
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
    sys.exit(1 if malos else 0)

if __name__ == "__main__":
    main()
'''
WORKFLOW = r'''name: Guardia de marca
on:
  push:
  pull_request:
  workflow_dispatch:
permissions:
  contents: read
jobs:
  logo:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4
      - run: python3 herramientas/comprobar_logo.py
'''
open("herramientas/comprobar_logo.py", "w", encoding="utf-8").write(GUARDIA)

# hashes: solo versiones ANTIGUAS de archivos «logo» (sin catálogo ni kit 2026), nunca la versión actual
nombres = set(sh("git", "log", "--all", "--format=", "--name-only").splitlines())
cand = sorted(n for n in nombres if re.search(r"(^|/)[^/]*logo[^/]*\.(png|webp|jpg|jpeg|svg)$", n, re.I)
              and not re.search(r"catalogo|marca-2026|isotipo|icono", n, re.I))
hashes, actuales = set(), []
for n in cand:
    r = subprocess.run(["git", "show", "HEAD:" + n], capture_output=True)
    head = hashlib.sha256(r.stdout).hexdigest() if r.returncode == 0 and r.stdout else None
    if head:
        actuales.append(n)
    for h in sh("git", "log", "--all", "--format=%H", "--", n).split():
        rr = subprocess.run(["git", "show", "%s:%s" % (h, n)], capture_output=True)
        if rr.returncode == 0 and rr.stdout:
            x = hashlib.sha256(rr.stdout).hexdigest()
            if x != head:
                hashes.add(x)
open("equipo/marca_antigua.sha256", "w").write("\n".join(sorted(hashes)) + ("\n" if hashes else ""))
print("Hashes de versiones antiguas guardados:", len(hashes))
print("Logos presentes ahora (MÍRALOS A OJO: ¿'NL' neón o 'N' de circuitos?):")
for n in actuales:
    print("   ", n)

r = subprocess.run([sys.executable, "herramientas/comprobar_logo.py"], capture_output=True, text=True)
print(r.stdout.strip() or "(sin hallazgos)")
limpio = r.returncode == 0
print("GUARDIA:", "LIMPIO" if limpio else "HAY HALLAZGOS, no se sube el workflow")

if limpio:
    os.makedirs(".github/workflows", exist_ok=True)
    open(".github/workflows/guardia_marca.yml", "w", encoding="utf-8").write(WORKFLOW)

# ---------- 7. subir
if APLICAR:
    titulo("7. Subir")
    ficheros = ["herramientas/comprobar_logo.py", "equipo/marca_antigua.sha256"]
    if limpio:
        ficheros.append(".github/workflows/guardia_marca.yml")
    sh("git", "add", *ficheros)
    print(sh("git", "commit", "-m", "marca: guardia contra el logo antiguo"))
    print(sh("git", "pull", "--rebase"))
    print(sh("git", "push"))
else:
    print("\n(Modo informe: nada subido. Para resetear renders viejos y subir: python3 herramientas/revision_total.py --aplicar)")
