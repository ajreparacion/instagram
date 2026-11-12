#!/usr/bin/env python3
"""CONTROL DE CALIDAD AUTOMÁTICO del modo «datos» (equipo/FORMATO_DATOS.md, fase 5).
Uso: python3 herramientas/control_datos.py guion.json video.mp4 [--salida calidad_datos.json]
Escribe y muestra un JSON {aprobado, nota_tecnica, bloqueos[], avisos[], medidas{}} y guarda 3 fotogramas de control
(gancho, medio, cierre) en <carpeta del guion>/control/. Sale con código 1 si hay bloqueos.
BLOQUEOS: ficha incompleta o no verificada · duración fuera de 12-45 s · escena de menos de 1,2 s · gancho de más de 8 palabras ·
tramo estático (freezedetect) de 1,0 s o más · fotogramas negros · pico verdadero por encima de -1 dBTP · sin escena de cierre.
AVISOS: sonoridad integrada fuera de -14 ± 1,5 LUFS (solo aviso: el reel va sin música cocida y la voz se mezcla después) ·
más de 4 palabras por segundo en una escena · cifras en la voz que no salen de la ficha · cierre sin la frase de prueba
gratuita · sin bloque «monetizacion» en post.json. Gratis, solo CPU y ffmpeg; la nota técnica no sustituye a la de Calidad (≥ 90)."""
import json, os, re, subprocess, sys, shutil

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = shutil.which("ffprobe") or "ffprobe"
DUR_MIN, DUR_MAX, ESC_MIN = 12.0, 45.0, 1.2
FREEZE_MAX = 1.0
LUFS_OBJ, LUFS_TOL, PICO_MAX = -14.0, 1.5, -1.0
WPS_MAX = 4.0


def ff(args, stderr=True):
    r = subprocess.run([FFMPEG, "-hide_banner", "-nostats"] + args, capture_output=True, text=True)
    return r.stderr if stderr else r.stdout


def duracion(video):
    r = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", video],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except Exception:
        return 0.0


def tiene_audio(video):
    r = subprocess.run([FFPROBE, "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_type", "-of", "csv=p=0", video],
                       capture_output=True, text=True)
    return "audio" in r.stdout


def limpio(t):
    return re.sub(r"[*«»]", "", str(t or "")).strip()


def palabras(t):
    return len(limpio(t).split())


def numeros(texto):
    return re.findall(r"\d+(?:[.,]\d+)*", texto)


def valores_ficha(g):
    """Cifras que puede mostrar o decir un reel: valores de la ficha, sus series y los años (formatos con coma y punto)."""
    out = set()
    def anota(v):
        try:
            v = float(v)
        except Exception:
            return
        for d in (0, 1, 2):
            s = "%.*f" % (d, v)
            out.add(s.replace(".", ",")); out.add(s)
            if d == 0:
                out.add("{:,}".format(int(round(v))).replace(",", "."))
        if v == int(v):
            out.add(str(int(v)))
    for f in g.get("datos") or []:
        if not isinstance(f, dict):
            continue
        anota(f.get("valor")); anota(f.get("anio"))
        for s in f.get("serie") or []:
            anota(s.get("valor")); out.update(re.findall(r"\d+", str(s.get("etiqueta", ""))))
        if f.get("escala", "").upper() == "M" and _f(f.get("valor")):
            anota(_f(f.get("valor")) / 1e6)
    return out


def _f(x):
    try:
        return float(x)
    except Exception:
        return None


def escenas_dur(g, video):
    """Duración real de cada escena: la de video.locucion.json (voz primero) o, si falta, la del guion."""
    esc = g.get("escenas") or []
    durs = [float(e.get("duracion", 3.0)) for e in esc]
    loc = os.path.splitext(video)[0] + ".locucion.json"
    fuente = "guion"
    try:
        for t in json.load(open(loc, encoding="utf-8")):
            durs[int(t["escena"])] = float(t["duracion"]); fuente = "locucion"
    except Exception:
        pass
    return durs, fuente


def freeze(video):
    out = ff(["-i", video, "-an", "-vf", "freezedetect=n=-45dB:d=0.4", "-f", "null", "-"])
    tramos, ini = [], None
    for l in out.splitlines():
        m = re.search(r"freeze_start: ([\d.]+)", l)
        if m:
            ini = float(m.group(1))
        m = re.search(r"freeze_duration: ([\d.]+)", l)
        if m:
            tramos.append((ini if ini is not None else 0.0, float(m.group(1))))
    return tramos


def negros(video):
    out = ff(["-i", video, "-an", "-vf", "blackdetect=d=0.1:pix_th=0.02:pic_th=0.98", "-f", "null", "-"])
    return [(float(a), float(b)) for a, b in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", out)]


def sonoridad(video):
    out = ff(["-i", video, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"])
    resumen = out[out.rfind("Summary:"):] if "Summary:" in out else ""
    i = re.search(r"I:\s+(-?[\d.]+) LUFS", resumen)
    p = re.search(r"Peak:\s+(-?[\d.]+) dBFS", resumen)
    return (float(i.group(1)) if i else None, float(p.group(1)) if p else None)


def fotogramas(video, carpeta, dur):
    ctl = os.path.join(carpeta, "control")
    os.makedirs(ctl, exist_ok=True)
    rutas = {}
    for nombre, t in (("gancho", 0.0), ("medio", dur / 2), ("cierre", max(0.0, dur - 0.4))):
        p = os.path.join(ctl, nombre + ".jpg")
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-ss", "%.2f" % t, "-i", video, "-frames:v", "1", "-q:v", "3", p])
        rutas[nombre] = p
    return rutas


def revisar(guion, video):
    g = json.load(open(guion, encoding="utf-8"))
    carpeta = os.path.dirname(os.path.abspath(guion))
    bl, av, med = [], [], {}
    if g.get("modo") != "datos":
        bl.append('el guion no es de modo "datos"')
    # 1. ficha completa y verificada
    import datos
    est, ver = datos.problemas_ficha(g)
    for m in est + ver:
        bl.append("ficha: " + m)
    # 2. duración total y por escena
    dur = duracion(video)
    med["duracion_s"] = round(dur, 2)
    if not DUR_MIN <= dur <= DUR_MAX:
        bl.append("duración %.1f s fuera de %d-%d s" % (dur, DUR_MIN, DUR_MAX))
    esc = g.get("escenas") or []
    durs, fuente = escenas_dur(g, video)
    med["escenas_s"] = [round(d, 2) for d in durs]
    med["escenas_fuente"] = fuente
    for i, d in enumerate(durs):
        if d < ESC_MIN:
            bl.append("escena %d dura %.2f s (mínimo %.1f s)" % (i, d, ESC_MIN))
    # 3. gancho
    gancho = g.get("gancho_corto") or (esc[0].get("texto") if esc else "")
    n = palabras(gancho)
    med["gancho_palabras"] = n
    if not gancho:
        bl.append("sin gancho (texto de la primera escena o gancho_corto)")
    elif n > 8:
        bl.append("gancho de %d palabras (máximo 8): «%s»" % (n, limpio(gancho)))
    # 4. tramos estáticos
    fr = freeze(video)
    med["tramos_estaticos"] = [{"inicio": round(a, 2), "duracion": round(b, 2)} for a, b in fr]
    for a, b in fr:
        if b >= FREEZE_MAX:
            bl.append("tramo estático de %.1f s desde %.1f s" % (b, a))
        else:
            av.append("tramo casi estático de %.1f s desde %.1f s" % (b, a))
    # 5. negros
    ng = negros(video)
    med["fotogramas_negros"] = [{"inicio": a, "fin": b} for a, b in ng]
    for a, b in ng:
        bl.append("fotogramas negros de %.1f s a %.1f s" % (a, b))
    # 6. sonoridad y pico
    if tiene_audio(video):
        li, pico = sonoridad(video)
        med["lufs"], med["pico_dbtp"] = li, pico
        sin_musica = g.get("musica") is False
        if li is not None and abs(li - LUFS_OBJ) > LUFS_TOL:
            m = "sonoridad integrada %.1f LUFS (objetivo %.0f ± %.1f)" % (li, LUFS_OBJ, LUFS_TOL)
            if sin_musica:
                av.append(m + ": va sin música cocida, la voz se mezcla después")
            else:
                bl.append(m)
        if pico is not None and pico > PICO_MAX:
            bl.append("pico verdadero %.1f dBTP (máximo %.0f)" % (pico, PICO_MAX))
    else:
        av.append("el vídeo no tiene audio")
    # 7. texto demasiado largo para leerse
    for i, e in enumerate(esc):
        if i >= len(durs):
            break
        voz, tx = palabras(e.get("voz")), palabras(e.get("texto"))
        if voz / max(0.1, durs[i]) > WPS_MAX:
            av.append("escena %d: %.1f palabras/s de voz (máximo %.0f)" % (i, voz / durs[i], WPS_MAX))
        if tx / max(0.1, durs[i]) > WPS_MAX:
            av.append("escena %d: %.1f palabras/s de texto en pantalla (máximo %.0f)" % (i, tx / durs[i], WPS_MAX))
    # 8. cifras de la voz que no salen de la ficha
    ok = valores_ficha(g)
    for i, e in enumerate(esc):
        for x in numeros(limpio(e.get("voz")) + " " + limpio(e.get("texto"))):
            if x not in ok and x.rstrip(",.") not in ok:
                av.append("escena %d: la cifra «%s» de la voz o el texto no sale de la ficha de datos" % (i, x))
    # 9. cierre
    # 9b. voz y música (12/11/2026: las decide el equipo por reel; nunca las dos fuera a la vez sin canción de Instagram)
    con_voz = any(limpio(e.get("voz")) for e in esc)
    med["voz"], med["musica_cocida"] = con_voz, g.get("musica") is not False
    if not con_voz and g.get("musica") is False:
        av.append("sin voz y sin música cocida: el reel depende de la canción de Instagram (audio_ig); si no se aplica, solo quedan los efectos")
    cierre = next((e for e in reversed(esc) if str(e.get("estilo")) == "cierre"), None)
    if not esc or esc[-1].get("estilo") != "cierre":
        bl.append('la última escena no es el cierre ("estilo": "cierre")')
    elif "prueba gratuita" not in limpio((cierre.get("voz") or "") + " " + (cierre.get("texto") or "")).lower():
        av.append("el cierre no menciona la prueba gratuita")
    elif con_voz and not all(k in limpio(cierre.get("voz") or "").lower() for k in ("sin tarjeta", "sin compromiso")):
        av.append("la voz del cierre debería decir «sin tarjeta, sin datos bancarios y sin compromiso»")
    # 10. monetización del post
    post = None
    for nom in ("post.json", "post.pendiente.json"):
        if os.path.exists(os.path.join(carpeta, nom)):
            try:
                post = json.load(open(os.path.join(carpeta, nom), encoding="utf-8")); break
            except Exception:
                pass
    if post is not None and not post.get("monetizacion"):
        av.append("falta el bloque «monetizacion» en post.json")
    # fotogramas de control
    if dur > 0:
        med["fotogramas_control"] = fotogramas(video, carpeta, dur)
    n_bl = len([m for m in bl if not m.startswith("ficha: ")]) + (1 if any(m.startswith("ficha: ") for m in bl) else 0)
    nota = max(0, 100 - 25 * n_bl - 4 * len(av))   # los fallos de la ficha cuentan como un único bloqueo
    return {"aprobado": not bl, "nota_tecnica": nota, "bloqueos": bl, "avisos": av, "medidas": med}


def main():
    a = [x for x in sys.argv[1:]]
    salida = None
    if "--salida" in a:
        i = a.index("--salida"); salida = a[i + 1]; del a[i:i + 2]
    if len(a) != 2:
        print(__doc__); sys.exit(2)
    res = revisar(a[0], a[1])
    txt = json.dumps(res, ensure_ascii=False, indent=2)
    if salida:
        with open(salida, "w", encoding="utf-8") as fh:
            fh.write(txt + "\n")
    print(txt)
    sys.exit(0 if res["aprobado"] else 1)


if __name__ == "__main__":
    main()
