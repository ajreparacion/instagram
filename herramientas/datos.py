#!/usr/bin/env python3
"""Modo "datos" de hacer_reel.py: reels verticales explicativos con DATOS VERIFICADOS y gráficos animados
(versión propia de Neogest Lab: ficha de datos -> ganchos y guion -> voz y storyboard -> animación -> control de calidad).

Estética: fondo azul noche (#0A0E1A -> #121A36) con rejilla sutil que se desplaza, grano, acentos neón cian #22E1FF y
magenta #FF2BD6 (estilo del logo NL), texto blanco en Montserrat Bold/Black. El fotograma 0 ya enseña el gancho gigante.
Escenas del guion ("modo": "datos"), clave "grafico" por escena:
  contador    número que sube con easing y rodillo de dígitos, unidad y etiqueta, destello al llegar
  barras      barras horizontales escalonadas con su valor contando; la destacada va en magenta
  linea       línea que se dibuja con punto brillante en la cabeza, área rellena, etiquetas del eje y valor final
  comparar    A frente a B con bloques proporcionales y rótulo «×N veces» si procede
  porcentaje  anillo que se llena con el contador en el centro
  ranking     3-5 filas que entran una a una (la primera del ranking, la última)
  texto       texto cinético grande (gancho, giro, cierre)
Los valores que se pintan SALEN de la ficha "datos" del guion (nunca se teclean dos veces): cada escena con gráfico lleva
"datos": ["d1", ...] con los id de la ficha. Puerta dura: si un dato referenciado no tiene fuente, url, anio, comprobado
o su estado no es "verificado", hacer_reel.py termina con error; solo con --ensayo se salta y se pinta en todos los
fotogramas la marca de agua «ENSAYO · DATOS FICTICIOS».
Cámara: entrada rápida de cada escena (barrido con desenfoque de movimiento o zoom punch, 7 fotogramas), empuje lento
continuo 1.00 -> 1.05 y pequeño temblor en el impacto. Efectos de sonido sintetizados (prefijo dt_: whoosh, tick, pop,
impacto, ding) que se mezclan por la ruta de make_audio de hacer_reel.py. Sin música cocida: la pone Instagram (audio_ig).
Se usa desde hacer_reel.py: datos.bind(modulo_hacer_reel), iniciar(), preparar(), render_frame(), sfx()."""
import math, os, random, re
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

hr = None          # módulo hacer_reel (Subtitulos, parsear_enfasis, W, H, FPS...); lo enchufa bind()
ENSAYO = False     # --ensayo: salta la puerta de la ficha y pinta la marca de agua
AQUI = os.path.dirname(os.path.abspath(__file__))
MONT = os.path.join(AQUI, "fonts", "Montserrat-VF.ttf")

W, H, FPS = 1080, 1920, 30
BG0, BG1 = (10, 14, 26), (18, 26, 54)
CIAN, MAG = (34, 225, 255), (255, 43, 214)
BLANCO = (255, 255, 255)
GRIS = (160, 174, 210)
PANEL = (22, 32, 68)
OSCURO = (8, 12, 28)
SUB_CY = 1445           # banda de subtítulos (encima de la interfaz de Instagram)
PIE_Y = 1306            # y del pie «Fuente: …»
TIPOS = ("contador", "barras", "linea", "comparar", "porcentaje", "ranking", "texto")
CIERRE_PANTALLA = "Prueba gratuita · sin tarjeta · sin compromiso"
FIRMA = "By Neogest Lab"
TRANS = 7               # fotogramas de la transición de entrada


def bind(modulo):
    """Enchufa hacer_reel y le pone Montserrat a los subtítulos (solo en modo datos: un proceso renderiza un modo)."""
    global hr
    hr = modulo
    if not getattr(hr.font, "_datos", False):
        orig = hr.font
        def _font(path, size, _o=orig):
            return F(size, "ExtraBold") if path == MONT else _o(path, size)
        _font._datos = True
        hr.font = _font
    hr.FUENTE_SUB = MONT


# ---------------------------------------------------------------- utilidades
_fc, _tc = {}, {}


def F(size, peso="Bold"):
    k = (int(size), peso)
    if k not in _fc:
        f = ImageFont.truetype(MONT, int(size))
        try:
            f.set_variation_by_name(peso)
        except Exception:
            f.set_variation_by_axes([{"Bold": 700, "ExtraBold": 800, "Black": 900}.get(peso, 700)])
        _fc[k] = f
    return _fc[k]


_probe = ImageDraw.Draw(Image.new("L", (4, 4)))


def anc(texto, f):
    return _probe.textlength(texto, font=f)


def e3(x):
    x = min(1.0, max(0.0, x)); return 1 - (1 - x) ** 3


def eio(x):
    x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)


def eback(x, c1=1.70158):
    x = min(1.0, max(0.0, x)); c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def mezcla(a, b, k):
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


def envolver(texto, f, maxw):
    lin, cur = [], ""
    for w in texto.split():
        t2 = (cur + " " + w).strip()
        if anc(t2, f) <= maxw or not cur:
            cur = t2
        else:
            lin.append(cur); cur = w
    if cur:
        lin.append(cur)
    return lin


def txt(texto, size, peso="Bold", col=BLANCO, maxw=None, maxlin=2, align="center", borde=0):
    """Imagen RGBA de un texto (con ajuste de tamaño y líneas). En caché."""
    key = (texto, size, peso, col, maxw, maxlin, align, borde)
    if key in _tc:
        return _tc[key]
    s = int(size)
    while True:
        f = F(s, peso)
        lin = envolver(texto, f, maxw) if maxw else [texto]
        if not maxw or (len(lin) <= maxlin and all(anc(l, f) <= maxw for l in lin)) or s <= size * 0.55:
            break
        s -= 4
    lin = lin[:maxlin] if maxw else lin
    lh = int(s * 1.22)
    w = int(max(anc(l, f) for l in lin)) + 2 * borde + 8
    im = Image.new("RGBA", (w, lh * len(lin) + 2 * borde + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, l in enumerate(lin):
        lw = anc(l, f)
        x = (w - lw) / 2 if align == "center" else (w - lw if align == "right" else 4 + borde)
        d.text((x, 4 + borde + i * lh), l, font=f, fill=col + (255,), stroke_width=borde, stroke_fill=OSCURO + (255,))
    _tc[key] = im
    return im


def pegar(layer, im, cx, cy, alfa=1.0, esc=1.0):
    """Pega `im` centrada en (cx, cy) con opacidad y escala."""
    if alfa <= 0.01 or esc <= 0.01:
        return
    if esc != 1.0:
        im = im.resize((max(1, int(im.width * esc)), max(1, int(im.height * esc))), Image.BILINEAR)
    if alfa < 0.99:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v, a=alfa: int(v * a)))
    layer.paste(im, (int(cx - im.width / 2), int(cy - im.height / 2)), im)


def ss(w, h, k, fn):
    """Dibuja con supersampling k: fn(draw, k) sobre un lienzo RGBA k veces mayor y lo reduce (bordes suaves)."""
    im = Image.new("RGBA", (int(w * k), int(h * k)), (0, 0, 0, 0))
    fn(ImageDraw.Draw(im), k)
    return im.resize((int(w), int(h)), Image.BOX)


# ---------------------------------------------------------------- formato español
def decimales(vals):
    n = 0
    for v in vals:
        s = ("%.2f" % abs(v)).rstrip("0")
        n = max(n, len(s.split(".")[1]) if "." in s else 0)
    return n


def num_es(v, dec, miles=True):
    s = "{:,.{d}f}".format(v, d=dec)
    s = s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")
    if not miles:
        s = s.replace(".", "")
    return s


def unidad_txt(it):
    u = it["unidad"]
    return ("M " + u).strip() if it.get("escala") == "M" else u


def valor_num(it, v=None):
    v = it["valor"] if v is None else v
    if it.get("escala") == "M":
        v = v / 1e6
    return num_es(v, it["dec"], it.get("miles", True))


def valor_txt(it, v=None):
    u = unidad_txt(it)
    n = valor_num(it, v)
    return n + (" %" if u == "%" else (" " + u if u else ""))


# ---------------------------------------------------------------- ficha de datos y puerta dura
def _num(x):
    try:
        if isinstance(x, bool):
            return None
        return float(x)
    except Exception:
        return None


def problemas_ficha(g):
    """Comprueba la ficha de datos del guion. Devuelve (errores_de_estructura, errores_de_verificacion)."""
    est, ver = [], []
    ficha = g.get("datos")
    if not isinstance(ficha, list) or not ficha:
        return ['falta la ficha de datos: el guion necesita arriba "datos": [{"id", "valor", "unidad", "etiqueta", "fuente", "url", "anio", "estado", "comprobado"}]'], []
    por_id = {}
    for f in ficha:
        if isinstance(f, dict) and f.get("id"):
            por_id[str(f["id"])] = f
    usados = []
    for i, e in enumerate(g.get("escenas") or []):
        gr = e.get("grafico")
        if gr not in TIPOS:
            est.append("escena %d: grafico %r no válido (usa: %s)" % (i, gr, ", ".join(TIPOS)))
            continue
        ids = e.get("datos") or []
        if gr == "texto" and not ids:
            continue
        if not ids:
            est.append('escena %d (%s): falta "datos": ["id", ...] con los datos de la ficha' % (i, gr))
            continue
        for d in ids:
            if str(d) not in por_id:
                est.append("escena %d: el dato %r no existe en la ficha" % (i, d))
            else:
                usados.append((i, str(d)))
    for i, d in usados:
        f = por_id[d]
        falta = []
        serie = f.get("serie")
        if serie:
            if not (isinstance(serie, list) and all(isinstance(s, dict) and _num(s.get("valor")) is not None and str(s.get("etiqueta", "")).strip() for s in serie)):
                est.append('dato %s: "serie" debe ser una lista de {"etiqueta", "valor"}' % d)
        elif _num(f.get("valor")) is None:
            est.append("dato %s: falta el valor numérico" % d)
        if not str(f.get("fuente") or "").strip():
            falta.append("fuente")
        if not str(f.get("url") or "").strip().lower().startswith("http"):
            falta.append("url")
        try:
            a = int(f.get("anio"))
            if not 1900 <= a <= 2100:
                raise ValueError
        except Exception:
            falta.append("anio")
        if not str(f.get("comprobado") or "").strip():
            falta.append("comprobado")
        if falta:
            ver.append("dato %s (escena %d): le falta %s" % (d, i, ", ".join(falta)))
        if str(f.get("estado") or "").strip().lower() != "verificado":
            ver.append('dato %s (escena %d): estado %r (debe ser "verificado" tras abrir la fuente)' % (d, i, f.get("estado")))
    # sin repetir mensajes
    return list(dict.fromkeys(est)), list(dict.fromkeys(ver))


def _items(e, por_id):
    """Elementos que pinta una escena, sacados de la ficha: [{etiqueta, valor, unidad, dec, escala, miles}]."""
    out = []
    for d in e.get("datos") or []:
        f = por_id[str(d)]
        base = {"unidad": str(f.get("unidad") or "").strip(), "escala": str(f.get("escala") or "").strip().upper()}
        if f.get("serie"):
            out += [dict(base, etiqueta=str(s["etiqueta"]), valor=float(s["valor"]), _f=f) for s in f["serie"]]
        else:
            out.append(dict(base, etiqueta=str(f.get("etiqueta") or d), valor=float(f["valor"]), _f=f, id=str(d)))
    dec = decimales([it["valor"] / (1e6 if it.get("escala") == "M" else 1) for it in out])
    for it in out:
        f = it["_f"]
        it["dec"] = int(f["decimales"]) if _num(f.get("decimales")) is not None else dec
        it["miles"] = f.get("separador", True) is not False and not (it["unidad"] == "" and it["valor"] == int(it["valor"]) and 1900 <= it["valor"] <= 2100)
    return out


_MIN = {"contador": 1, "porcentaje": 1, "comparar": 2, "barras": 2, "linea": 2, "ranking": 2}
_MAX = {"contador": 1, "porcentaje": 1, "comparar": 2, "barras": 6, "linea": 9, "ranking": 5}


def iniciar(g, ensayo):
    """Puerta dura + contexto por escena. Termina con error claro en español si algo no cuadra."""
    global ENSAYO
    ENSAYO = bool(ensayo)
    est, ver = problemas_ficha(g)
    por_id = {str(f["id"]): f for f in (g.get("datos") or []) if isinstance(f, dict) and f.get("id")}
    esc = g.get("escenas") or []
    if not est:
        for i, e in enumerate(esc):
            e["_ctx"] = {"items": _items(e, por_id) if e.get("datos") else [], "total": len(esc)}
            gr, n = e.get("grafico"), len(e["_ctx"]["items"])
            if gr in _MIN and not (_MIN[gr] <= n <= _MAX[gr]):
                est.append("escena %d (%s): %d elementos (admite de %d a %d)" % (i, gr, n, _MIN[gr], _MAX[gr]))
            if gr == "porcentaje" and n == 1 and not 0 <= e["_ctx"]["items"][0]["valor"] <= 100:
                est.append("escena %d (porcentaje): el valor %s no está entre 0 y 100" % (i, e["_ctx"]["items"][0]["valor"]))
    if est:
        raise SystemExit("modo datos: el guion no es válido:\n  - " + "\n  - ".join(est))
    if ver and not ENSAYO:
        raise SystemExit("modo datos: la ficha de datos no está completa y verificada (puerta dura, nunca cifras sin fuente):\n  - "
                         + "\n  - ".join(ver) + "\nAbre la fuente oficial, completa fuente, url, anio y comprobado y pon \"estado\": \"verificado\". "
                         "Solo para pruebas con cifras ficticias existe --ensayo (marca de agua; publicar_gh.py nunca lo usa).")
    if ver:
        print("ENSAYO: la ficha no está verificada (%d avisos); se pinta la marca de agua «ENSAYO · DATOS FICTICIOS»" % len(ver))


def fijar_total(scenes, total_f):
    for s in scenes:
        s.total_f = total_f


# ---------------------------------------------------------------- preparación de la escena
_NEED = {"contador": 2.4, "barras": 1.2, "linea": 2.6, "comparar": 2.4, "porcentaje": 2.6, "ranking": 1.0, "texto": 1.0}


def _acento_idx(palabras, cands):
    for i, w in enumerate(palabras):
        if "«" in w or "»" in w or "*" in w:
            return i
    return len(palabras) - 1


def preparar(sc, spec, rng):
    ctx = spec.get("_ctx") if isinstance(spec.get("_ctx"), dict) else {"items": []}
    sc.ctx = ctx
    sc.items = ctx.get("items") or []
    sc.graf = spec.get("grafico") if spec.get("grafico") in TIPOS else "texto"
    sc.estilo_d = str(spec.get("estilo") or "dato").strip().lower()
    sc.primero = sc.idx == 0
    sc.total_f = getattr(sc, "total_f", 0)
    sc.golpes = []
    sc.sfx = []
    n = len(sc.items)
    need = _NEED[sc.graf] + (0.3 * n if sc.graf in ("barras", "ranking") else 0)
    sc.sk = min(1.5, max(0.5, (sc.dur - 1.0) / need))     # el reloj de la animación se estira o se comprime según lo que dura la escena
    sc.T0 = 0.2
    voz, enf_voz = hr.parsear_enfasis(spec.get("voz") or "")
    txt_esc, _ = hr.parsear_enfasis(spec.get("texto") or "")
    sc.texto = txt_esc.strip()
    sc.texto_raw = str(spec.get("texto") or "")
    dv = float(spec.get("_voz_dur") or 0)
    tiempos = spec.get("_voz_palabras")
    tiempos = [float(x) + 0.12 for x in tiempos] if (tiempos and len(tiempos) == len(voz.split())) else None
    wps = len(voz.split()) / max(0.3, dv - 0.1) if dv > 0.2 else max(hr.WPS_HUMANO, len(voz.split()) / max(0.3, sc.dur * 0.8))
    estilo = dict(fill=BLANCO, stroke=OSCURO, activo=CIAN, enfasis=MAG, marca=False, cy=SUB_CY, smax=76, smin=54, grosor=14)
    sc.sub = hr.Subtitulos(voz, wps, 0.12, sc.dur, enfasis=enf_voz, tiempos=tiempos, estilo=estilo) if voz else None
    # pie «Fuente: …» (solo si la escena usa datos de la ficha)
    fu = []
    for it in sc.items:
        f = it["_f"]
        s = "%s (%s)" % (str(f.get("fuente") or "").strip(), str(f.get("anio") or "").strip())
        if s not in fu:
            fu.append(s)
    sc.pie = ("Fuente: " + " · ".join(fu)) if fu else ""
    # efectos de sonido (los mezcla make_audio): (tipo, t relativo, duración)
    if sc.idx > 0:
        sc.sfx.append(("dt_whoosh", 0.0, 0.3))
    getattr(sys_mod(), "_prep_" + sc.graf)(sc, spec)
    sc.sfx = [(a, max(0.0, b), c) for a, b, c in sc.sfx if b < sc.dur - 0.05]
    sc.punch = (sc.idx % 2 == 0) or sc.estilo_d == "giro"     # entrada: zoom punch (pares/giro) o barrido (impares)


def sys_mod():
    import sys
    return sys.modules[__name__]


def _t(sc, nominal):
    """Tiempo real (s) de un instante de la animación nominal."""
    return sc.T0 + nominal * sc.sk


def _prep_texto(sc, spec):
    texto = sc.texto_raw.replace("«", "*").replace("»", "*")
    texto, enf = hr.parsear_enfasis(texto)
    texto = " ".join(texto.split())
    if sc.estilo_d in ("gancho", "giro"):
        texto = texto.upper()
    pal = texto.split()
    sc.t_pal = pal
    sc.t_acento = set(enf) if enf else ({len(pal) - 1} if pal else set())
    sc.t_col = MAG if sc.estilo_d == "giro" else CIAN
    maxlin = 3 if sc.estilo_d == "gancho" else 4
    for s in range(150, 66, -4):
        f = F(s, "Black")
        lin = envolver(texto, f, 900)
        if len(lin) <= maxlin and all(anc(l, f) <= 900 for l in lin):
            break
    sc.t_f, sc.t_size, sc.t_lin = f, s, lin
    sc.t_imgs = []   # (imagen de la palabra, x, y de la línea)
    lh = int(s * 1.16)
    k = 0
    for li, l in enumerate(lin):
        ws = l.split()
        x = (W - anc(l, f)) / 2
        for w in ws:
            col = sc.t_col if k in sc.t_acento else BLANCO
            im = Image.new("RGBA", (int(anc(w, f)) + 40, int(s * 1.3) + 30), (0, 0, 0, 0))
            ImageDraw.Draw(im).text((20, 12), w, font=f, fill=col + (255,), stroke_width=7, stroke_fill=OSCURO + (255,))
            sc.t_imgs.append((im, x - 20, li, k))
            x += anc(w + " ", f); k += 1
    sc.t_lh = lh
    sc.t_cy = 780 if sc.estilo_d == "gancho" else (700 if sc.estilo_d == "cierre" else 800)
    if sc.estilo_d == "giro":
        sc.golpes.append(0.25); sc.sfx.append(("dt_impacto", 0.18, 0.7))
    if sc.estilo_d == "cierre":
        sc.sfx.append(("dt_ding", 0.45, 0.8))
    if sc.estilo_d == "gancho":
        sc.sfx.append(("dt_pop", 0.1, 0.12))


def _prep_contador(sc, spec):
    sc.cnt_ini, sc.cnt_dur = 0.15, 1.7
    fin = sc.cnt_ini + sc.cnt_dur
    n = min(12, 6 + len(valor_num(sc.items[0]).replace(".", "").replace(",", "")))
    for k in range(n):   # tick cada vez más espaciado (frecuencia limitada a ~10/s)
        x = (k / n) ** 0.6
        sc.sfx.append(("dt_tick", _t(sc, sc.cnt_ini + x * sc.cnt_dur * 0.97), 0.1))
    sc.sfx.append(("dt_impacto", _t(sc, fin), 0.7))
    sc.golpes.append(_t(sc, fin))


def _prep_barras(sc, spec):
    sc.b_ini, sc.b_paso, sc.b_dur = 0.15, 0.28, 0.75
    for i in range(len(sc.items)):
        sc.sfx.append(("dt_pop", _t(sc, sc.b_ini + i * sc.b_paso + sc.b_dur), 0.12))
    sc.destacar = _destacada(sc, spec)


def _destacada(sc, spec):
    d = spec.get("destacar")
    for i, it in enumerate(sc.items):
        if d is not None and (str(d) == str(it.get("id")) or str(d) == str(i) or str(d) == it["etiqueta"]):
            return i
    return max(range(len(sc.items)), key=lambda i: sc.items[i]["valor"])


def _prep_linea(sc, spec):
    sc.l_ini, sc.l_dur = 0.2, 2.2
    sc.eje_cero = spec.get("eje_cero", True) is not False
    sc.sfx.append(("dt_impacto", _t(sc, sc.l_ini + sc.l_dur), 0.7))
    sc.golpes.append(_t(sc, sc.l_ini + sc.l_dur))
    for i in range(1, len(sc.items)):
        sc.sfx.append(("dt_tick", _t(sc, sc.l_ini + sc.l_dur * i / (len(sc.items) - 1)), 0.1))


def _prep_comparar(sc, spec):
    a, b = sc.items[0]["valor"], sc.items[1]["valor"]
    mn, mx = min(a, b), max(a, b)
    sc.ratio = None
    if spec.get("ratio", True) is not False and mn > 0 and mx / mn >= 1.2:
        r = mx / mn
        r = round(r, 1) if r < 10 else round(r)
        if r > 1.0:
            sc.ratio = r
    sc.c_ini, sc.c_dur = 0.2, 1.0
    sc.sfx.append(("dt_pop", _t(sc, 0.2 + 0.9), 0.12))
    if sc.ratio:
        sc.r_t = 1.5
        sc.sfx.append(("dt_impacto", _t(sc, sc.r_t), 0.7)); sc.golpes.append(_t(sc, sc.r_t))


def _prep_porcentaje(sc, spec):
    sc.p_ini, sc.p_dur = 0.2, 2.0
    sc.sfx.append(("dt_impacto", _t(sc, sc.p_ini + sc.p_dur), 0.7)); sc.golpes.append(_t(sc, sc.p_ini + sc.p_dur))
    for k in range(8):
        sc.sfx.append(("dt_tick", _t(sc, sc.p_ini + ((k / 8) ** 0.6) * sc.p_dur * 0.97), 0.1))
    sc.p_img = None


def _prep_ranking(sc, spec):
    n = len(sc.items)
    sc.orden = list(range(n))
    if spec.get("orden") != "dado":
        sc.orden = sorted(range(n), key=lambda i: -sc.items[i]["valor"])
    sc.r_ini, sc.r_paso = 0.15, 0.5
    for k in range(n):    # entra primero la última fila y la primera del ranking la última (suspense)
        t = sc.r_ini + k * sc.r_paso
        sc.sfx.append(("dt_impacto" if k == n - 1 else "dt_pop", _t(sc, t + 0.3), 0.7 if k == n - 1 else 0.12))
    sc.golpes.append(_t(sc, sc.r_ini + (n - 1) * sc.r_paso + 0.3))


# ---------------------------------------------------------------- fondo (rejilla que se desplaza + degradado + viñeta)
CELDA = 90
_bg = {}


def _fondo_base():
    if "base" in _bg:
        return
    yy = np.linspace(0, 1, H)[:, None, None]
    base = np.array(BG0)[None, None, :] * (1 - yy) + np.array(BG1)[None, None, :] * yy
    base = np.repeat(base, W, axis=1).astype(np.float32)
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    for (cx, cy, r, col, a) in ((180, 360, 900, CIAN, 0.07), (940, 1560, 950, MAG, 0.07)):
        k = np.clip(1 - np.hypot(xs - cx, ys - cy) / r, 0, 1) ** 2 * a
        base += k[:, :, None] * np.array(col)[None, None, :]
    vig = np.clip(1 - (np.hypot((xs - W / 2) / (W * 0.85), (ys - H / 2) / (H * 0.78))) ** 2 * 0.55, 0.45, 1)
    base *= vig[:, :, None]
    _bg["base"] = np.clip(base, 0, 255).astype(np.int16)
    # rejilla: máscara más alta que la pantalla para desplazarla sin costuras
    m = np.zeros((H + CELDA, W), np.float32)
    m[::CELDA, :] = 1.0
    m[1::CELDA, :] = 0.5
    m[:, ::CELDA] = np.maximum(m[:, ::CELDA], 1.0)
    m[:, 1::CELDA] = np.maximum(m[:, 1::CELDA], 0.5)
    fade = np.clip(1 - (np.hypot((xs - W / 2) / (W * 0.8), (ys - H / 2) / (H * 0.75))) ** 2 * 0.9, 0.15, 1)
    fade = np.vstack([fade, fade[:CELDA]])
    _bg["rej"] = (m * fade * 26.0)[:, :, None] * np.array([0.35, 0.6, 1.0], np.float32)[None, None, :]
    _bg["rej"] = _bg["rej"].astype(np.int16)


def fondo(fi):
    _fondo_base()
    oy = int((fi * 0.9) % CELDA)          # rejilla que sube despacio
    arr = _bg["base"] + _bg["rej"][CELDA - oy:CELDA - oy + H]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


# ---------------------------------------------------------------- piezas comunes de la escena
def decoracion(layer, d, sc, t):
    """Anillos que respiran y partículas que suben: movimiento constante pero discreto, detrás de los gráficos."""
    cx, cy = W / 2, 800
    for k in range(3):
        ph = (t * 0.35 + k / 3.0) % 1.0
        r = 260 + 480 * ph
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(34, 225, 255, int(46 * (1 - ph))), width=3)
    rg = random.Random(sc.idx * 7 + 5)
    for k in range(14):
        x0, v, ph0, r0 = rg.uniform(70, 1010), rg.uniform(30, 90), rg.uniform(0, 1), rg.uniform(3, 7)
        y = H - ((t * v + ph0 * H) % (H + 100)) + 20
        a = int(80 * min(1, y / 300, (H - y) / 300)) if 0 < y < H else 0
        if a > 0:
            col = CIAN if k % 3 else MAG
            d.ellipse([x0 - r0, y - r0, x0 + r0, y + r0], fill=col + (a,))


def cabecera(layer, sc, t):
    """Titular de la escena (arriba, y≈300-440)."""
    if not sc.texto or sc.graf == "texto":
        return
    k = e3((t - 0.12) / 0.32)
    im = txt(sc.texto, 56, "Bold", BLANCO, maxw=900, maxlin=2, borde=5)
    top = 318
    pegar(layer, im, W / 2, top + im.height / 2 + (1 - k) * 36, alfa=k)
    barra = int(140 * k)
    yb = top + im.height + 4
    ImageDraw.Draw(layer).rounded_rectangle([W / 2 - barra / 2, yb, W / 2 + barra / 2, yb + 5], 3, fill=MAG + (255,))


def _glow_ring(d, cx, cy, r, w, col, a):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col + (a,), width=w)


# ---- texto cinético
def _g_texto(layer, d, sc, t):
    n = len(sc.t_imgs)
    if not n:
        return
    lins = len(sc.t_lin)
    y0 = sc.t_cy - (lins * sc.t_lh) / 2
    for (im, x, li, k) in sc.t_imgs:
        if sc.primero:
            p = (t + 0.22) / 0.2                    # el gancho está entero y legible desde el fotograma 0
        else:
            p = (t - 0.1 - k * 0.09) / 0.24
        if p <= 0:
            continue
        s = 0.55 + 0.45 * eback(p) if p < 1 else 1.0
        a = 1.0 if sc.primero else min(1.0, p * 1.6)
        cy = y0 + li * sc.t_lh + sc.t_lh / 2 + (0 if sc.primero else (1 - e3(p)) * 40)
        pegar(layer, im, x + im.width / 2 + 20 - 20, cy, alfa=a, esc=s)
    if sc.estilo_d == "cierre":
        a = e3((t - 0.6) / 0.35)
        pill = txt(CIERRE_PANTALLA, 40, "Bold", BLANCO, maxw=860, maxlin=1)
        yy = y0 + lins * sc.t_lh + 90 + pill.height / 2
        w, h = pill.width + 70, pill.height + 40
        pl = Image.new("RGBA", (w, h), (0, 0, 0, 0)); dp = ImageDraw.Draw(pl)
        dp.rounded_rectangle([0, 0, w - 1, h - 1], h // 2, fill=PANEL + (235,), outline=CIAN + (255,), width=4)
        pl.alpha_composite(pill, ((w - pill.width) // 2, (h - pill.height) // 2))
        pegar(layer, pl, W / 2, yy, alfa=a, esc=0.9 + 0.1 * eback((t - 0.6) / 0.35))
        pegar(layer, _firma(), W / 2, yy + h / 2 + 120, alfa=e3((t - 0.9) / 0.4))
    if sc.estilo_d == "giro":    # destello al revelar
        a = max(0.0, 1 - (t - 0.2) / 0.45)
        if a > 0:
            d.ellipse([W / 2 - 520, 800 - 520, W / 2 + 520, 800 + 520], fill=MAG + (int(36 * a),))


def _firma():
    if "firma" not in _tc:
        f = F(40, "Bold")
        w = int(anc(FIRMA, f)) + 120
        im = Image.new("RGBA", (w, 100), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([4, 14, 76, 86], 16, outline=CIAN + (255,), width=5, fill=OSCURO + (200,))
        fn = F(34, "Black")
        d.text((26, 50), "N", font=fn, fill=CIAN + (255,), anchor="lm")
        d.text((50, 50), "L", font=fn, fill=MAG + (255,), anchor="lm")
        d.text((100, 50), FIRMA, font=f, fill=BLANCO + (255,), anchor="lm")
        _tc["firma"] = im
    return _tc["firma"]


# ---- contador con rodillo de dígitos
def _columna(dig, sig, s, size, cw, col):
    key = ("col", dig, sig, round(s, 2), size, col)
    if key in _tc:
        return _tc[key]
    f = F(size, "Black")
    h = int(size * 1.0)
    im = Image.new("RGBA", (cw + 6, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    base = int(size * 0.86); step = int(size * 0.95)
    d.text(((cw + 6) / 2, base - s * step), str(dig), font=f, fill=col + (255,), anchor="ms", stroke_width=6, stroke_fill=OSCURO + (255,))
    if s > 0:
        d.text(((cw + 6) / 2, base + (1 - s) * step), str(sig), font=f, fill=col + (255,), anchor="ms", stroke_width=6, stroke_fill=OSCURO + (255,))
    if len(_tc) < 4000:
        _tc[key] = im
    return im


def numero_rodillo(it, v, size, col=BLANCO, final=None):
    """Imagen RGBA del número `v` con rodillo de dígitos. La anchura es la del valor final (no se mueve al contar)."""
    dec = it["dec"]
    esc = 1e6 if it.get("escala") == "M" else 1.0
    fin = final if final is not None else valor_num(it)
    f = F(size, "Black")
    cw = int(anc("0", f)) + 4
    sw = int(anc(",", f)) + 6
    slots = []
    x = 0
    ndig = sum(c.isdigit() for c in fin)
    j = ndig
    for c in fin:
        if c.isdigit():
            j -= 1; slots.append((c, x, j, cw)); x += cw
        else:
            slots.append((c, x, None, sw)); x += sw
    tw = x
    X = round(max(0.0, v / esc) * 10 ** dec, 6)
    lienzo = Image.new("RGBA", (tw + 12, int(size * 1.0)), (0, 0, 0, 0))
    # una coma/punto se ve si hay algún dígito visible a su izquierda
    vis_dig = []
    for (c, x0, jj, w) in slots:
        if jj is not None:
            vis_dig.append(X >= 10 ** jj or jj <= dec)
        else:
            vis_dig.append(None)
    for idx, (c, x0, jj, w) in enumerate(slots):
        if jj is not None:
            if not vis_dig[idx]:
                continue
            dg = int(X // 10 ** jj) % 10
            r = (X / 10 ** jj) % 1.0
            s = r if jj == 0 else max(0.0, min(1.0, (r - 0.9) / 0.1))
            if s < 0.02 or (jj == 0 and abs(X - round(X)) < 1e-6):
                s = 0.0
            else:
                s = round(s, 1)
            col_im = _columna(dg, (dg + 1) % 10, s, size, cw, col)
            lienzo.alpha_composite(col_im, (x0 - 3 + 6, 0))
        else:
            # separador: visible si queda algún dígito visible a su izquierda
            izq = any(vis_dig[k] for k in range(idx) if vis_dig[k] is not None)
            if izq:
                ImageDraw.Draw(lienzo).text((x0 + w / 2 + 6, int(size * 0.86)), c, font=f, fill=col + (255,), anchor="ms", stroke_width=6, stroke_fill=OSCURO + (255,))
    return lienzo


def _g_contador(layer, d, sc, t):
    it = sc.items[0]
    cy = 800
    a_in = e3((t - 0.05) / 0.3)
    ta = (t - sc.T0) / sc.sk
    p = e3((ta - sc.cnt_ini) / sc.cnt_dur)
    v = it["valor"] * p
    fin = valor_num(it)
    unidad = unidad_txt(it)
    corta = len(unidad) <= 3 and unidad != ""
    size = 300
    while size > 120 and (anc("0", F(size, "Black")) + 4) * sum(c.isdigit() for c in fin) + 40 * (len(fin) - sum(c.isdigit() for c in fin)) + (size * 0.7 if corta else 0) > 900:
        size -= 12
    # destello y pop al llegar
    ts = t - _t(sc, sc.cnt_ini + sc.cnt_dur)
    pop = 1 + 0.08 * math.sin(min(1.0, ts / 0.4) * math.pi) if ts > 0 else 1.0
    if 0 < ts < 0.5:
        a = 1 - ts / 0.5
        r = 300 + 260 * (1 - a)
        d.ellipse([W / 2 - r, cy - r, W / 2 + r, cy + r], fill=CIAN + (int(46 * a),))
        for k in range(14):
            ang = k * 2 * math.pi / 14 + 0.2
            r0, r1 = 300 + 140 * ts / 0.5, 380 + 300 * ts / 0.5
            d.line([(W / 2 + r0 * math.cos(ang), cy + r0 * math.sin(ang)), (W / 2 + r1 * math.cos(ang), cy + r1 * math.sin(ang))],
                   fill=(MAG if k % 2 else CIAN) + (int(230 * a),), width=7)
    num = numero_rodillo(it, v, size, BLANCO, final=fin)
    ancho_u = 0
    if corta:
        ui = txt(unidad.replace("%", "%"), int(size * 0.55), "Black", CIAN, borde=5)
        ancho_u = ui.width + 10
    tot = num.width + ancho_u
    x0 = (W - tot) / 2
    glow = Image.new("RGBA", (tot + 40, num.height + 40), (0, 0, 0, 0))
    glow.paste(num, (20, 20), num)
    if corta:
        glow.paste(ui, (20 + num.width + 10, 20 + int(num.height * 0.28)), ui)
    pegar(layer, glow, W / 2, cy, alfa=a_in, esc=pop)
    if not corta and unidad:
        pegar(layer, txt(unidad, 64, "Bold", CIAN, maxw=900, maxlin=1, borde=4), W / 2, cy + size * 0.5 + 40, alfa=e3((ta - 0.5) / 0.4))
    yl = cy + size * 0.5 + (110 if (not corta and unidad) else 60)
    pegar(layer, txt(it["etiqueta"], 50, "Bold", BLANCO, maxw=900, maxlin=2, borde=4), W / 2, yl + 40, alfa=e3((ta - 0.6) / 0.4))
    # barra de progreso hacia el valor (movimiento extra)
    bw = 520 * p
    d.rounded_rectangle([W / 2 - 260, cy - size * 0.5 - 60, W / 2 + 260, cy - size * 0.5 - 50], 5, fill=(255, 255, 255, 30))
    if bw > 2:
        d.rounded_rectangle([W / 2 - 260, cy - size * 0.5 - 60, W / 2 - 260 + bw, cy - size * 0.5 - 50], 5, fill=CIAN + (255,))


# ---- barras horizontales
def _g_barras(layer, d, sc, t):
    n = len(sc.items)
    ta = (t - sc.T0) / sc.sk
    pitch = min(165, 740 / n)
    y0 = 520
    vmax = max(it["valor"] for it in sc.items) or 1
    maxw = 640
    x0 = 90
    d.line([(x0 - 6, y0 - 6), (x0 - 6, y0 + n * pitch - 20)], fill=CIAN + (110,), width=4)
    for i, it in enumerate(sc.items):
        ini = sc.b_ini + i * sc.b_paso
        p = e3((ta - ini) / sc.b_dur)
        ya = e3((ta - ini + 0.2) / 0.3)
        y = y0 + i * pitch
        dest = i == sc.destacar
        col = MAG if dest else CIAN
        lab = txt(it["etiqueta"], 40, "Black" if dest else "Bold", BLANCO if dest else (205, 218, 245), maxw=860, maxlin=1)
        pegar(layer, lab, x0 + lab.width / 2 - 2, y + 20, alfa=ya)
        wbar = max(0.0, maxw * (it["valor"] / vmax) * p)
        if wbar > 2:
            hb = 58
            ww = int(wbar) + 24
            tile = Image.new("RGBA", (ww, hb), (0, 0, 0, 0)); dt = ImageDraw.Draw(tile)
            dt.rounded_rectangle([0, 0, int(wbar) - 1 + 12, hb - 1], 16, fill=col + (235 if dest else 200,))
            ov = Image.new("RGBA", tile.size, (0, 0, 0, 0)); do = ImageDraw.Draw(ov)
            do.rounded_rectangle([8, 7, int(wbar) + 4, 19], 6, fill=(255, 255, 255, 55))
            if p >= 1.0:   # destello que recorre la barra
                sx = ((t * 0.7 + i * 0.23) % 1.6 - 0.3) * (wbar + 80)
                if 0 < sx < wbar:
                    do.polygon([(sx, 0), (sx + 26, 0), (sx + 6, hb), (sx - 20, hb)], fill=(255, 255, 255, 70 if dest else 40))
            tile.alpha_composite(ov)
            mask = Image.new("L", tile.size, 0)
            ImageDraw.Draw(mask).rounded_rectangle([0, 0, int(wbar) - 1 + 12, hb - 1], 16, fill=255)
            tile.putalpha(ImageChops.multiply(tile.getchannel("A"), mask))
            layer.paste(tile, (x0 - 6, int(y + 50)), tile)
        vt = valor_txt(it, it["valor"] * p)
        im = txt(vt, 54, "Black", BLANCO if dest else (222, 232, 250), borde=5)
        sc_ = 1.0 + (0.1 * math.sin(min(1.0, (ta - ini - sc.b_dur) / 0.3) * math.pi) if ta - ini - sc.b_dur > 0 else 0)
        pegar(layer, im, x0 - 6 + wbar + 22 + im.width / 2, y + 79, alfa=ya, esc=sc_)


# ---- línea
def _g_linea(layer, d, sc, t):
    n = len(sc.items)
    ta = (t - sc.T0) / sc.sk
    xa, xb, yt, yb = 130, 960, 600, 1130
    vals = [it["valor"] for it in sc.items]
    vmx = max(vals) * 1.12 or 1
    vmn = 0.0 if (sc.eje_cero and min(vals) >= 0) else (min(vals) - 0.18 * (max(vals) - min(vals) or 1))
    pad = 70
    pw, ph = xb - xa + 2 * pad, yb - yt + 2 * pad
    pts = [(xa + i * (xb - xa) / (n - 1) - (xa - pad), yb - (v - vmn) / (vmx - vmn) * (yb - yt) - (yt - pad)) for i, v in enumerate(vals)]
    prog = eio((ta - sc.l_ini) / sc.l_dur) * (n - 1)
    seg = min(n - 2, int(prog)); fr = prog - seg
    if prog >= n - 1:
        seg, fr = n - 2, 1.0
    head = (pts[seg][0] + (pts[seg + 1][0] - pts[seg][0]) * fr, pts[seg][1] + (pts[seg + 1][1] - pts[seg][1]) * fr)
    vhead = vals[seg] + (vals[seg + 1] - vals[seg]) * fr
    trazo = pts[:seg + 1] + [head]
    pulso = 0.5 + 0.5 * math.sin(t * 6)

    def dib(dd, k):
        for gi in range(5):    # rejilla horizontal
            yy = (pad + (yb - yt) * gi / 4) * k
            dd.line([(pad * k - 20 * k, yy), ((pad + xb - xa) * k + 20 * k, yy)], fill=(120, 150, 220, 40), width=int(2 * k))
        dd.line([(pad * k - 20 * k, (pad + yb - yt) * k), ((pad + xb - xa) * k + 20 * k, (pad + yb - yt) * k)], fill=CIAN + (130,), width=int(3 * k))
        if len(trazo) >= 2:
            area = [(x * k, y * k) for x, y in trazo] + [(trazo[-1][0] * k, (pad + yb - yt) * k), (trazo[0][0] * k, (pad + yb - yt) * k)]
            dd.polygon(area, fill=CIAN + (60,))
            dd.line([(x * k, y * k) for x, y in trazo], fill=CIAN + (255,), width=int(11 * k), joint="curve")
            for (x, y) in trazo:
                dd.ellipse([(x - 5.5) * k, (y - 5.5) * k, (x + 5.5) * k, (y + 5.5) * k], fill=CIAN + (255,))
        for i, (x, y) in enumerate(pts[:seg + 1]):
            dd.ellipse([(x - 12) * k, (y - 12) * k, (x + 12) * k, (y + 12) * k], fill=OSCURO + (255,), outline=BLANCO + (255,), width=int(4 * k))
        r = 15 + 5 * pulso
        dd.ellipse([(head[0] - r - 8) * k, (head[1] - r - 8) * k, (head[0] + r + 8) * k, (head[1] + r + 8) * k], fill=MAG + (70,))
        dd.ellipse([(head[0] - 14) * k, (head[1] - 14) * k, (head[0] + 14) * k, (head[1] + 14) * k], fill=BLANCO + (255,), outline=MAG + (255,), width=int(5 * k))
    chart = ss(pw, ph, 2, dib)
    layer.paste(chart, (int(xa - pad), int(yt - pad)), chart)
    # etiquetas del eje (años) cuando la línea las alcanza
    step = 1 if n <= 6 else 2
    for i, it in enumerate(sc.items):
        if i % step == 0 or i == n - 1:
            a = e3((prog - i + 0.6) / 0.6)
            pegar(layer, txt(it["etiqueta"], 34, "Bold", GRIS, borde=3), xa + i * (xb - xa) / (n - 1), yb + 34, alfa=a)
    # valor en la cabeza (cuenta) y final
    hx = head[0] + (xa - pad)
    hy = head[1] + (yt - pad)
    fin = prog >= n - 1 - 1e-6
    it0 = sc.items[0]
    tsf = t - _t(sc, sc.l_ini + sc.l_dur)
    pop = 1 + 0.12 * math.sin(min(1.0, tsf / 0.4) * math.pi) if fin and tsf > 0 else 1.0
    im = txt(valor_txt(it0, vhead), 66 if not fin else 80, "Black", BLANCO if not fin else CIAN, borde=6)
    px = min(W - 90 - im.width / 2, max(90 + im.width / 2, hx))
    pegar(layer, im, px, max(yt - 30, hy - 66), esc=pop)
    # primer valor, pequeño, a la izquierda
    if n > 2:
        pegar(layer, txt(valor_txt(it0, vals[0]), 36, "Bold", GRIS, borde=3), xa + 20, pts[0][1] + (yt - pad) + 44, alfa=e3((prog + 0.5) / 0.4))


# ---- comparar
def _g_comparar(layer, d, sc, t):
    ta = (t - sc.T0) / sc.sk
    a, b = sc.items
    vmax = max(a["valor"], b["valor"]) or 1
    yb, mh, bw = 1110, 380, 380
    cols = (CIAN, MAG)
    for i, (it, x0) in enumerate(((a, 90), (b, 610))):
        p = eback((ta - sc.c_ini - i * 0.12) / sc.c_dur)
        pc = e3((ta - sc.c_ini - i * 0.12) / sc.c_dur)
        h = max(56, mh * it["valor"] / vmax) * max(0.0, p)
        if h > 3:
            tile = Image.new("RGBA", (bw, int(h) + 2), (0, 0, 0, 0)); dt = ImageDraw.Draw(tile)
            dt.rounded_rectangle([0, 0, bw - 1, int(h)], 26, fill=cols[i] + (225,))
            ov = Image.new("RGBA", tile.size, (0, 0, 0, 0))
            ImageDraw.Draw(ov).rounded_rectangle([16, 16, 60, max(24, int(h) - 14)], 14, fill=(255, 255, 255, 45))
            tile.alpha_composite(ov)
            layer.paste(tile, (x0, int(yb - h)), tile)
        v = it["valor"] * pc
        im = txt(valor_txt(it, v), 76, "Black", BLANCO, maxw=bw + 80, maxlin=1, borde=6)
        pegar(layer, im, x0 + bw / 2, yb - h - 50, alfa=e3((ta - sc.c_ini + 0.1) / 0.3))
        pegar(layer, txt(it["etiqueta"], 40, "Bold", cols[i], maxw=bw + 30, maxlin=2, borde=4), x0 + bw / 2, yb + 62, alfa=e3((ta - 0.4) / 0.4))
    d.line([(60, yb + 3), (1020, yb + 3)], fill=(255, 255, 255, 110), width=4)
    # «VS»
    k = e3((ta - 0.3) / 0.3)
    d.ellipse([540 - 44, yb - 200 - 44, 540 + 44, yb - 200 + 44], fill=OSCURO + (255,), outline=BLANCO + (int(255 * k),), width=4) if k > 0 else None
    if k > 0:
        pegar(layer, txt("VS", 38, "Black", BLANCO), 540, yb - 200, alfa=k)
    if sc.ratio:
        p = (ta - sc.r_t) / 0.35
        if p > 0:
            r = sc.ratio
            s = ("×" + num_es(r, 0 if r >= 10 or r == int(r) else 1) + " veces")
            im = txt(s, 92, "Black", BLANCO, borde=7)
            w, h = im.width + 80, im.height + 36
            pl = Image.new("RGBA", (w, h), (0, 0, 0, 0)); dp = ImageDraw.Draw(pl)
            dp.rounded_rectangle([0, 0, w - 1, h - 1], h // 2, fill=OSCURO + (240,), outline=MAG + (255,), width=6)
            pl.alpha_composite(im, ((w - im.width) // 2, (h - im.height) // 2))
            pegar(layer, pl, 540, 560, alfa=min(1.0, p * 2), esc=0.6 + 0.4 * eback(p))


# ---- porcentaje (anillo)
_anillo = {}


def _anillo_base(R, grosor):
    key = (R, grosor)
    if key in _anillo:
        return _anillo[key]
    k = 2
    S = (R + grosor) * 2 + 40
    ann = Image.new("L", (S * k, S * k), 0)
    da = ImageDraw.Draw(ann)
    c = S * k // 2
    da.ellipse([c - (R + grosor // 2) * k, c - (R + grosor // 2) * k, c + (R + grosor // 2) * k, c + (R + grosor // 2) * k], fill=255)
    da.ellipse([c - (R - grosor // 2) * k, c - (R - grosor // 2) * k, c + (R - grosor // 2) * k, c + (R - grosor // 2) * k], fill=0)
    # degradado cian -> magenta en ángulo
    ys, xs = np.mgrid[0:S * k, 0:S * k].astype(np.float32)
    ang = (np.arctan2(ys - c, xs - c) + math.pi / 2) % (2 * math.pi) / (2 * math.pi)
    col = np.zeros((S * k, S * k, 3), np.float32)
    for ch in range(3):
        col[:, :, ch] = CIAN[ch] + (MAG[ch] - CIAN[ch]) * ang
    rgb = Image.fromarray(col.astype(np.uint8))
    _anillo[key] = (S, k, ann, rgb)
    return _anillo[key]


def _g_porcentaje(layer, d, sc, t):
    it = sc.items[0]
    ta = (t - sc.T0) / sc.sk
    R, G = 265, 66
    cy = 800
    S, k, ann, rgb = _anillo_base(R, G)
    p = e3((ta - sc.p_ini) / sc.p_dur)
    pct = max(0.0, min(100.0, it["valor"])) / 100.0 * p
    # pista
    track = Image.new("RGBA", (S * k, S * k), (0, 0, 0, 0))
    track.paste(Image.new("RGBA", (S * k, S * k), (120, 150, 220, 46)), (0, 0), ann)
    # arco relleno
    mask = Image.new("L", (S * k, S * k), 0)
    if pct > 0.0005:
        ImageDraw.Draw(mask).pieslice([0, 0, S * k - 1, S * k - 1], -90, -90 + 360 * pct, fill=255)
    mk = ImageChops.multiply(mask, ann)
    fill = rgb.convert("RGBA"); fill.putalpha(mk)
    track.alpha_composite(fill)
    track = track.resize((S, S), Image.BOX)
    layer.paste(track, (W // 2 - S // 2, cy - S // 2), track)
    # punta brillante
    if pct > 0.0005:
        a = -math.pi / 2 + 2 * math.pi * pct
        hx, hy = W / 2 + R * math.cos(a), cy + R * math.sin(a)
        d.ellipse([hx - 24, hy - 24, hx + 24, hy + 24], fill=BLANCO + (255,), outline=MAG + (255,), width=5)
    # número en el centro
    unidad = unidad_txt(it)
    v = it["valor"] * p
    ts = t - _t(sc, sc.p_ini + sc.p_dur)
    pop = 1 + 0.08 * math.sin(min(1.0, ts / 0.4) * math.pi) if ts > 0 else 1.0
    fin = valor_num(it)
    size = 200
    num = numero_rodillo(it, v, size, BLANCO, final=fin)
    ui = txt("%" if unidad == "%" else unidad, 100, "Black", CIAN, borde=5)
    tot = num.width + ui.width + 8
    im = Image.new("RGBA", (tot + 40, num.height + 40), (0, 0, 0, 0))
    im.paste(num, (20, 20), num); im.paste(ui, (20 + num.width + 8, 20 + int(num.height * 0.18)), ui)
    pegar(layer, im, W / 2, cy, esc=pop)
    if 0 < ts < 0.5:
        a = 1 - ts / 0.5
        r = R + 40 + 120 * (1 - a)
        d.ellipse([W / 2 - r, cy - r, W / 2 + r, cy + r], outline=MAG + (int(200 * a),), width=6)
    pegar(layer, txt(it["etiqueta"], 46, "Bold", BLANCO, maxw=880, maxlin=2, borde=4), W / 2, cy + R + G // 2 + 68, alfa=e3((ta - 0.5) / 0.4))


# ---- ranking
def _g_ranking(layer, d, sc, t):
    n = len(sc.items)
    ta = (t - sc.T0) / sc.sk
    pitch = min(168, 730 / n)
    rowh = pitch - 18
    y0 = 520
    vmax = max(it["valor"] for it in sc.items) or 1
    for pos, i in enumerate(sc.orden):
        it = sc.items[i]
        k = n - 1 - pos                      # orden de entrada: la última fila primero
        p = (ta - sc.r_ini - k * sc.r_paso) / 0.5
        if p <= 0:
            continue
        s = eback(p)
        dx = (1 - min(1.0, s)) * 700
        y = y0 + pos * pitch
        top = pos == 0
        x0, x1 = 70 + dx, 1010 + dx
        d.rounded_rectangle([x0, y, x1, y + rowh], 28, fill=PANEL + (235,), outline=(MAG if top else CIAN) + (255 if top else 140,), width=5 if top else 3)
        cxb, cyb = x0 + 66, y + rowh / 2
        d.ellipse([cxb - 40, cyb - 40, cxb + 40, cyb + 40], fill=(MAG if top else CIAN) + (255,))
        pegar(layer, txt(str(pos + 1), 54, "Black", OSCURO), cxb, cyb - 1)
        lab = txt(it["etiqueta"], 42, "Black" if top else "Bold", BLANCO, maxw=520, maxlin=1)
        pegar(layer, lab, x0 + 130 + lab.width / 2, y + rowh * 0.38)
        vt = valor_txt(it, it["valor"] * e3(p))
        vi = txt(vt, 54, "Black", BLANCO if top else (215, 228, 250), borde=4)
        pegar(layer, vi, x1 - 28 - vi.width / 2, y + rowh * 0.38)
        bw = (x1 - x0 - 170) * (it["valor"] / vmax) * e3(p)
        if bw > 3:
            d.rounded_rectangle([x0 + 130, y + rowh - 30, x0 + 130 + bw, y + rowh - 16], 7, fill=(MAG if top else CIAN) + (255,))


# ---------------------------------------------------------------- cámara y transición
def _tf(im, z, tx, ty):
    if z == 1.0 and tx == 0 and ty == 0:
        return im
    cx, cy = W / 2, H / 2
    return im.transform((W, H), Image.AFFINE, (1 / z, 0, cx - (cx + tx) / z, 0, 1 / z, cy - (cy + ty) / z), resample=Image.BILINEAR)


def camara(layer, sc, t, lf):
    dur = max(0.5, sc.dur)
    z = 1.0 + 0.05 * min(1.0, t / dur)                      # empuje lento continuo 1.00 -> 1.05
    tx = 6 * math.sin(t * 0.9 + sc.idx)
    ty = 0.0
    for g in sc.golpes:                                     # pequeño temblor en el impacto
        dt = t - g
        if 0 <= dt < 0.45:
            a = 14 * math.exp(-dt * 9)
            tx += a * math.sin(dt * 75); ty += a * 0.6 * math.cos(dt * 61)
            z *= 1 + 0.02 * math.exp(-dt * 12)
    if sc.idx > 0 and lf < TRANS:
        k = (lf + 0.5) / TRANS
        if sc.punch:
            muestras = []
            for s in (-0.5, 0.0, 0.5):
                kk = min(1.0, max(0.0, k + s / TRANS))
                zz = z * (1 + 0.28 * (1 - e3(kk)))
                muestras.append(_tf(layer, zz, tx, ty))
            acc = muestras[0]
            for j, m in enumerate(muestras[1:], 2):
                acc = Image.blend(acc, m, 1.0 / j)
            acc.putalpha(acc.getchannel("A").point(lambda v, a=min(1.0, 0.35 + k): int(v * a)))
            return acc
        off = lambda kk: (1 - e3(kk)) ** 1.5 * W * 0.85
        span = abs(off(k - 0.5 / TRANS) - off(k + 0.5 / TRANS))
        acc = None
        for j, s in enumerate((-0.5, -0.25, 0.0, 0.25, 0.5), 1):
            m = _tf(layer, z, tx + off(k) + s * span, ty)
            acc = m if acc is None else Image.blend(acc, m, 1.0 / j)
        return acc
    return _tf(layer, z, tx, ty)


# ---------------------------------------------------------------- fotograma
def _pie(sc):
    key = ("pie", sc.pie)
    if key not in _tc:
        s = 30
        while s > 22 and anc(sc.pie, F(s, "Bold")) > 900:
            s -= 2
        _tc[key] = txt(sc.pie if anc(sc.pie, F(s, "Bold")) <= 920 else sc.pie[:70] + "…", s, "Bold", (170, 186, 222), borde=3)
    return _tc[key]


def _chrome(img, sc, t, fi):
    """Etiqueta, barra de progreso del reel y marca de agua del ensayo (no se mueven con la cámara)."""
    d = ImageDraw.Draw(img, "RGBA")
    tot = max(1, sc.total_f or (sc.start + sc.nframes))
    d.rounded_rectangle([60, 232, 1020, 236], 2, fill=(255, 255, 255, 40))
    d.rounded_rectangle([60, 232, 60 + 960 * min(1.0, fi / tot), 236], 2, fill=CIAN + (255,))
    pul = 0.5 + 0.5 * math.sin(t * 5)
    d.ellipse([66, 256, 84, 274], fill=MAG + (int(150 + 105 * pul),))
    f = F(30, "Black")
    d.text((98, 265), "DATOS", font=f, fill=BLANCO + (255,), anchor="lm", stroke_width=3, stroke_fill=OSCURO + (255,))
    if ENSAYO:
        im = txt("ENSAYO · DATOS FICTICIOS", 32, "Black", BLANCO)
        w, h = im.width + 36, im.height + 12
        pl = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(pl).rounded_rectangle([0, 0, w - 1, h - 1], h // 2, fill=(210, 20, 90, 235), outline=BLANCO + (255,), width=3)
        pl.alpha_composite(im, (18, 6))
        img.paste(pl, (1020 - w, 258 - h // 2), pl)


def render_frame(fi, sc, noise, rg, seed):
    lf = fi - sc.start
    t = lf / FPS
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    decoracion(layer, d, sc, t)
    cabecera(layer, sc, t)
    getattr(sys_mod(), "_g_" + sc.graf)(layer, d, sc, t)
    cont = camara(layer, sc, t, lf)
    img = fondo(fi)
    img.paste(cont, (0, 0), cont)
    # resplandor neón: el contenido, reducido, desenfocado y sumado
    peq = cont.resize((W // 4, H // 4), Image.BOX)
    base = Image.new("RGBA", peq.size, (0, 0, 0, 255))
    peq = Image.alpha_composite(base, peq).convert("RGB").filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BILINEAR)
    img = ImageChops.add(img, peq.point(lambda v: int(v * 0.5)))
    # pie de fuente y subtítulos (fijos, dentro de la zona segura)
    if sc.pie:
        pi = _pie(sc)
        a = e3((t - 0.3) / 0.3)
        pegar(img, pi, W / 2, PIE_Y, alfa=a) if a < 1 else img.paste(pi, (int(W / 2 - pi.width / 2), int(PIE_Y - pi.height / 2)), pi)
    if sc.sub is not None:
        cp = sc.sub.capa(t)
        if cp:
            timg, ty = cp
            img.paste(timg, (0, ty), timg)
    _chrome(img, sc, t, fi)
    a = np.asarray(img, dtype=np.int16) + noise[fi % 8] // 7
    np.clip(a, 0, 255, out=a)
    return a.astype(np.uint8)


# ---------------------------------------------------------------- efectos de sonido (sintetizados, sin archivos)
def sfx(tipo, dur, rg, lp_fft):
    """Efectos del modo datos (prefijo dt_). Discretos: la voz los hunde en la mezcla. None si no es de aquí."""
    SR = hr.SR
    dur = max(0.03, float(dur)); m = int(dur * SR); tt = np.arange(m) / SR
    if tipo == "dt_whoosh":      # barrido de ruido filtrado que sube
        x = rg.standard_normal(m)
        x = lp_fft(x, 5200, 2) - lp_fft(x, 700, 2)
        env = np.sin(np.pi * np.minimum(1.0, tt / dur)) ** 2 * np.linspace(0.5, 1.0, m)
        return x * env * 0.22
    if tipo == "dt_tick":        # clic suave del contador
        return (np.sin(2 * np.pi * 2400 * tt) * np.exp(-tt * 110) + 0.4 * np.sin(2 * np.pi * 1200 * tt) * np.exp(-tt * 80)) * 0.075
    if tipo == "dt_pop":         # pop de cada barra / fila
        f = 640 - 300 * np.minimum(1.0, tt / 0.1)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 36) * 0.17
    if tipo == "dt_impacto":     # golpe grave de la revelación
        f = 46 + 130 * np.exp(-tt * 24)
        cuerpo = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 6.5)
        golpe = lp_fft(rg.standard_normal(m), 800, 2) * np.exp(-tt * 38)
        return (cuerpo * 0.5 + golpe * 0.28)
    if tipo == "dt_ding":        # campanilla del cierre
        return (np.sin(2 * np.pi * 1318.5 * tt) + 0.35 * np.sin(2 * np.pi * 1975.5 * tt) + 0.2 * np.sin(2 * np.pi * 2637 * tt)) * np.exp(-tt * 5.5) * 0.13
    return None
