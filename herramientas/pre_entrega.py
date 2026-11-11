#!/usr/bin/env python3
"""PRE-ENTREGA: revisa en segundos, antes de pasar a Calidad, lo que se puede comprobar sin ver el vídeo.
Uso: python3 herramientas/pre_entrega.py [cola/NNN_carpeta ...]   (sin argumentos: toda cola/)
         --stats   ademas escribe equipo/lecciones_calidad.md (aprobacion, motivos de rechazo mas repetidos)
Sale con codigo 1 si hay algun ERROR. Gratis, CPU, sin red. Cubre B1 (gancho > 8 palabras), B6 (cierres antiguos «comenta X»),
B8 (comentario fijado, avance), B9 (marcas ajenas), voz del dueño prohibida, textos repetidos y reels a la misma hora.
Los AVISOS no bloquean; los ERRORES se corrigen antes de entregar. Lo que Calidad rechaza dos veces por el mismo motivo
se convierte aqui en una comprobacion nueva (ver equipo/BUCLE_APRENDIZAJE.md)."""
import sys, os, re, json, glob, unicodedata, collections
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def norm(s): return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")
def cargar(p):
    try: return json.load(open(p, encoding="utf-8"))
    except Exception: return None
def textos(o):
    """Todas las cadenas de un guion o post (texto, voz, subtitulos...), sin las claves que empiezan por _."""
    if isinstance(o, str): yield o
    elif isinstance(o, list):
        for x in o: yield from textos(x)
    elif isinstance(o, dict):
        for k, v in o.items():
            if not str(k).startswith("_"): yield from textos(v)
MARCAS = [norm(m) for m in (cargar(os.path.join(RAIZ, "equipo", "marcas_prohibidas.json")) or {}).get("marcas", [])]
CIERRE_ANTIGUO = re.compile(r"\b(comenta|escr[ií]beme|escribeme)\s+[«\"“]?[A-ZÁÉÍÓÚÑ]{3,}", re.I)

def revisar(carpeta):
    e, a = [], []
    post = cargar(os.path.join(carpeta, "post.json")) or cargar(os.path.join(carpeta, "post.pendiente.json")) or {}
    guion = cargar(os.path.join(carpeta, "guion.json")) or {}
    tipo = post.get("tipo")
    todo = norm(" ".join(textos(post) )) + " " + norm(" ".join(textos(guion)))
    for m in MARCAS:
        if re.search(r"(?<![a-z0-9])" + re.escape(m) + r"(?![a-z0-9])", todo): e.append("B9 marca ajena en texto/guion: «%s»" % m)
    crudo = json.dumps(guion, ensure_ascii=False) + json.dumps(post, ensure_ascii=False)
    for pal in ("voz_dueno", "referencia_usuario", "clon_dueno"):
        if pal in crudo and not pal in json.dumps({k: v for k, v in post.items() if str(k).startswith("_")}, ensure_ascii=False):
            e.append("VOZ del dueño prohibida: aparece «%s»" % pal)
    if tipo == "reel":
        t = post.get("texto", "")
        if CIERRE_ANTIGUO.search(t): e.append("B6 cierre antiguo «comenta/escríbeme X» en el texto del post")
        if any(CIERRE_ANTIGUO.search(x) for x in textos(guion)): e.append("B6 cierre antiguo «comenta/escríbeme X» en la voz o el texto del guion")
        if not post.get("comentario_fijado"): a.append("B8 falta comentario_fijado")
        if not post.get("avance_siguiente"): a.append("B8 falta avance_siguiente")
        esc = guion.get("escenas") or []
        g = next((x for x in esc if x.get("estilo") in ("gancho", None) and x.get("texto")), None)
        txt = (guion.get("gancho_corto") or (g or {}).get("texto") or "")
        n = len(re.sub(r"[*¡!¿?«»]", "", txt).split())
        if txt and n > 8: a.append("B1 gancho de %d palabras (máximo 8): «%s»" % (n, txt[:60]))
        if post.get("app") and "ajreparacion.com" not in t and "prueba gratuita" not in norm(t): a.append("cierre único de prueba gratuita ausente en un reel de app")
    return e, a

def main():
    args = [x for x in sys.argv[1:] if not x.startswith("--")]
    cs = [a.rstrip("/") for a in args] or sorted(glob.glob(os.path.join(RAIZ, "cola", "*")))
    tot_e = 0; primeras = collections.defaultdict(list); cuando = collections.defaultdict(list)
    for c in cs:
        if not os.path.isdir(c): continue
        e, a = revisar(c)
        post = cargar(os.path.join(c, "post.json")) or cargar(os.path.join(c, "post.pendiente.json")) or {}
        if post.get("tipo") == "reel" and post.get("cuando"): cuando[post["cuando"]].append(os.path.basename(c))
        l1 = norm((post.get("texto") or "").split("\n")[0]).strip()
        if l1: primeras[l1].append(os.path.basename(c))
        for m in e: print("ERROR  %s: %s" % (os.path.basename(c), m))
        for m in a: print("AVISO  %s: %s" % (os.path.basename(c), m))
        tot_e += len(e)
    for l1, v in primeras.items():
        if len(v) > 1: print("AVISO  primera línea repetida en %s" % ", ".join(v)); 
    for k, v in cuando.items():
        if len(v) > 1: print("ERROR  reels a la misma hora %s: %s" % (k, ", ".join(v))); tot_e += 1
    print("pre_entrega: %d carpetas, %d errores" % (len(cs), tot_e))
    if "--stats" in sys.argv: stats()
    sys.exit(1 if tot_e else 0)

def stats():
    n = ok = 0; notas = []; motivos = collections.Counter(); ult = []
    for f in sorted(glob.glob(os.path.join(RAIZ, "cola", "*", "calidad.json"))):
        c = cargar(f) or {}; n += 1; ok += bool(c.get("aprobado")); 
        if isinstance(c.get("nota"), (int, float)): notas.append(c["nota"])
        if not c.get("aprobado"):
            for m in c.get("motivos") or []:
                cods = set(re.findall(r"\bB[1-9]\b", m))
                if re.search(r"cierre antiguo|comenta/escr", m, re.I): cods.add("CIERRE (comenta/escríbeme X)")
                if re.search(r"marca (bancaria )?ajena|CaixaBank", m, re.I): cods.add("B9")
                for cod in cods or {"otro"}: motivos[cod] += 1
            ult.append((os.path.basename(os.path.dirname(f)), c.get("nota"), (c.get("motivos") or [""])[0][:140]))
    L = ["# Lecciones de Calidad (generado por herramientas/pre_entrega.py --stats; no editar a mano)", "",
         "Piezas con calidad.json: %d · aprobadas: %d (%.0f %%) · nota media: %.1f" % (n, ok, 100.0 * ok / max(1, n), sum(notas) / max(1, len(notas))), "",
         "## Motivos de rechazo más repetidos (los que no están en pre_entrega.py como comprobación automática, hay que añadirlos)"]
    for k, v in motivos.most_common(): L.append("- %s: %d" % (k, v))
    L += ["", "## Rechazadas ahora mismo"] + ["- %s (%s): %s" % u for u in ult]
    open(os.path.join(RAIZ, "equipo", "lecciones_calidad.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("equipo/lecciones_calidad.md escrito")
if __name__ == "__main__": main()
