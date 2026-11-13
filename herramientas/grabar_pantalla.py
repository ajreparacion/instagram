#!/usr/bin/env python3
"""Plantilla de GRABACION DE PANTALLA tipo @claudeai (DIRECTIVA VIGENTE, prioridad 3; "modo":"app" de hacer_reel.py).

Uso: python3 grabar_pantalla.py grabacion.json salida.mp4 [--fps 30]

Abre una pagina REAL con Playwright (una URL, un .html local o una sesion ya iniciada con datos de prueba), hace los
pasos del guion (clics, escribir, scroll, zoom) y compone un video vertical 1080x1920 SIN sonido:
fondo plano de color suave, marco de movil o portatil con sombra, cursor visible con anillo al hacer clic y zoom suave
hacia lo importante. Luego se usa como "video" de un guion con "modo":"app" y "plantilla": true (voz, subtitulos,
musica y gancho los pone hacer_reel.py). Nada se inventa: lo que se ve es lo que hace la pagina.

grabacion.json:
 {"dispositivo": "movil" | "portatil", "fondo": "#DDEBF7", "marco": "oscuro" | "claro",
  "url": "https://...  o ruta .html relativa a este json", "sesion": "storage_state.json (opcional: Gmail, chat...)",
  "viewport": [390, 640], "escala": 2, "idioma": "es-ES", "esperar_carga": 0.8,
  "pasos": [
    {"accion": "esperar", "seg": 1.0},
    {"accion": "clic", "selector": "#boton"}                       (o "x","y" en px del viewport; "doble": true)
    {"accion": "escribir", "selector": "textarea", "texto": "...", "cps": 16}   (el \\n es Intro)
    {"accion": "mover", "selector": "...", "seg": 0.6}
    {"accion": "scroll", "y": 400, "seg": 0.9}                       (desplaza la rueda; y negativo = arriba)
    {"accion": "zoom", "selector": "#resultado", "nivel": 1.5, "seg": 0.8}   (nivel 1.0 = vista completa; con selector
        el nivel se limita para que el elemento entre entero a lo ancho; "forzar": true lo desactiva)
    {"accion": "pulsar", "tecla": "Enter"},  {"accion": "esperar_selector", "selector": "...", "seg": 8},
    {"accion": "ir", "url": "..."}],
  "reemplazos": [{"buscar": " (CaixaBank)", "por": ""}],      (opcional: cambia ese texto en la pagina mientras se graba, p. ej. para
        quitar una marca ajena de los datos de ejemplo; solo texto visible, no toca datos ni cuentas)
  "ocultar": ["#campo_vacio"], "difuminar": [".lista-marcas"],   (opcional, selectores CSS: lo que no debe leerse en pantalla;
        ocultar deja el hueco en blanco, difuminar lo emborrona. No vale para tapar datos reales: esos no se graban.)
  "previos": [{"accion": "clic", "selector": "button:has-text('Saltar')", "opcional": true, "seg": 12},
              {"accion": "esperar_selector", "selector": "#avisos", "seg": 25}, {"accion": "ver", "selector": "#avisos"}]}
        (opcional: pasos que se hacen ANTES de empezar a grabar, sin cursor ni fotogramas: cerrar intros o paneles de
        bienvenida para que el primer fotograma ya sea lo que importa; "opcional": true no falla si el elemento no esta)
La sesion (cookies de una cuenta de PRUEBA ya iniciada) tambien puede venir de la variable PANTALLA_SESION."""
import sys, os, io, re, json, math, time, random, shutil, subprocess, base64
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1080, 1920
FFMPEG = shutil.which("ffmpeg") or "/usr/local/bin/ffmpeg"
HERE = os.path.dirname(os.path.abspath(__file__))
CIAN = (0, 184, 217)

# pantalla (donde va la grabacion) y cuerpo del dispositivo, en el lienzo 1080x1920
DISPOSITIVOS = {
    "movil":   dict(pantalla=(215, 322, 650, 1066), bisel=20, radio_p=44, radio_c=66, viewport=(390, 640), escala=2,
                    movil=True, isla=True),
    "portatil": dict(pantalla=(60, 470, 960, 600), bisel=22, radio_p=10, radio_c=26, viewport=(1280, 800), escala=1.5,
                     movil=False, isla=False),
}

def ease(k):
    k = min(1.0, max(0.0, k)); return k * k * (3 - 2 * k)

def hex_rgb(h, defecto=(221, 235, 247)):
    m = re.fullmatch(r"#?([0-9a-fA-F]{6})", str(h or "").strip())
    return tuple(int(m.group(1)[i:i + 2], 16) for i in (0, 2, 4)) if m else defecto

# ---------------------------------------------------------------- captura (CDP screencast + registro de eventos)
class Registro:
    def __init__(self):
        self.frames = []          # (t, jpeg bytes)
        self.cursor = []          # (t0, t1, (x0, y0), (x1, y1), arco)
        self.clics = []           # t
        self.camara = []          # (t0, dur, cx, cy, nivel)
        self.t0 = None
    def t(self): return time.time() - self.t0

def ajustar_pantalla(disp, vw, vh):
    """Si el viewport pedido no tiene la proporcion de la pantalla del dispositivo, la pantalla se reencaja (centrada en su
    caja, sin salirse) para que la captura no salga estirada. Con el viewport por defecto no cambia nada."""
    sx, sy, sw, sh = disp["pantalla"]
    if abs(sw / sh - vw / vh) < 0.01: return disp
    w, h = sw, int(round(sw * vh / vw))
    if h > sh: h, w = sh, int(round(sh * vw / vh))
    nd = dict(disp); nd["pantalla"] = (sx + (sw - w) // 2, sy + (sh - h) // 2, w, h)
    return nd

def grabar(spec, base_dir, rec):
    from playwright.sync_api import sync_playwright
    disp = DISPOSITIVOS.get(str(spec.get("dispositivo") or "movil").lower())
    if not disp: sys.exit("dispositivo desconocido: %r (movil | portatil)" % spec.get("dispositivo"))
    vw, vh = [int(x) for x in (spec.get("viewport") or disp["viewport"])]
    disp = ajustar_pantalla(disp, vw, vh)
    escala = float(spec.get("escala") or disp["escala"])
    sesion = spec.get("sesion") or os.environ.get("PANTALLA_SESION") or ""
    if sesion and not os.path.isabs(sesion): sesion = os.path.join(base_dir, sesion)
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        ctx = br.new_context(viewport={"width": vw, "height": vh}, device_scale_factor=escala,
                             is_mobile=disp["movil"], has_touch=False, locale=str(spec.get("idioma") or "es-ES"),
                             storage_state=sesion if (sesion and os.path.exists(sesion)) else None)
        page = ctx.new_page()
        cdp = ctx.new_cdp_session(page)
        pend = []
        def on_frame(ev):
            ts = (ev.get("metadata") or {}).get("timestamp")
            ahora = time.time()
            if ts is None or abs(ts - ahora) > 5: ts = ahora
            rec.frames.append((ts, base64.b64decode(ev["data"])))
            pend.append(ev["sessionId"])
        cdp.on("Page.screencastFrame", on_frame)
        def bombear(ms=20):
            page.wait_for_timeout(ms)
            while pend:
                try: cdp.send("Page.screencastFrameAck", {"sessionId": pend.pop(0)})
                except Exception: pass
        def esperar(seg):
            fin = time.time() + seg
            while time.time() < fin: bombear(16)
        cdp.send("Page.startScreencast", {"format": "jpeg", "quality": 92, "maxWidth": int(vw * escala) + 2,
                                           "maxHeight": int(vh * escala) + 2, "everyNthFrame": 1})
        def ir(url):
            if not re.match(r"^[a-z]+://", url):
                p = url if os.path.isabs(url) else os.path.join(base_dir, url)
                url = "file://" + os.path.abspath(p)
            page.goto(url, wait_until="load", timeout=60000)
        reemp = [(str(r.get("buscar") or ""), str(r.get("por") or "")) for r in (spec.get("reemplazos") or []) if r.get("buscar")]
        if reemp:   # cambia texto visible (nodos de texto), tambien el que la app pinta despues
            page.add_init_script("""(() => { const R = %s;
              const fix = n => { let t = n.nodeValue, o = t; for (const [a, b] of R) t = t.split(a).join(b); if (t !== o) n.nodeValue = t; };
              const pasar = root => { const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT); let n; while ((n = w.nextNode())) fix(n); };
              const ini = () => { pasar(document.body); new MutationObserver(ms => { for (const m of ms) { if (m.type === 'characterData') fix(m.target); m.addedNodes.forEach(a => { if (a.nodeType === 3) fix(a); else if (a.nodeType === 1) pasar(a); }); } })
                .observe(document.body, {childList: true, subtree: true, characterData: true}); };
              if (document.body) ini(); else document.addEventListener('DOMContentLoaded', ini); })();""" % json.dumps(reemp, ensure_ascii=False))
        # 12/11/2026 (Calidad, 601 y B9): "ocultar" y "difuminar" = listas de selectores CSS que no deben leerse en la
        # grabacion (campos vacios sin etiqueta, listas con marcas ajenas). ocultar conserva el hueco; difuminar emborrona.
        css = "".join("%s{visibility:hidden !important}" % str(x) for x in (spec.get("ocultar") or []) if str(x).strip()) + \
              "".join("%s{filter:blur(7px) !important}" % str(x) for x in (spec.get("difuminar") or []) if str(x).strip())
        if css:
            page.add_init_script("""(() => { const add = () => { const s = document.createElement('style'); s.textContent = %s;
              (document.head || document.documentElement).appendChild(s); };
              if (document.head) add(); else document.addEventListener('DOMContentLoaded', add); })();""" % json.dumps(css))
        ir(str(spec.get("url") or ""))
        esperar(float(spec.get("esperar_carga", 0.8)))
        for p in spec.get("previos") or []:   # antes de grabar: sin cursor ni fotogramas
            a = str(p.get("accion") or "").lower(); opc = bool(p.get("opcional"))
            try:
                if a == "esperar": esperar(float(p.get("seg", 0.5)))
                elif a == "esperar_selector":
                    page.locator(p["selector"]).first.wait_for(state="visible", timeout=int(float(p.get("seg", 10)) * 1000)); bombear(80)
                elif a == "clic":
                    page.locator(p["selector"]).first.click(timeout=int(float(p.get("seg", 8)) * 1000)); bombear(150)
                elif a == "ver":   # desplaza hasta que el elemento se vea (el primer fotograma ya lo muestra)
                    page.locator(p["selector"]).first.scroll_into_view_if_needed(timeout=int(float(p.get("seg", 8)) * 1000)); bombear(150)
            except Exception as e:
                if not opc: raise
                print("previo opcional omitido:", a, p.get("selector"), str(e)[:60])
        esperar(0.4)
        rec.t0 = time.time()
        pos = [vw / 2, vh * 0.8]   # cursor inicial: abajo, centrado
        rec.cursor.append((0.0, 0.0, tuple(pos), tuple(pos), 0.0))

        def centro(sel):
            loc = page.locator(sel).first
            loc.wait_for(state="visible", timeout=15000)
            loc.scroll_into_view_if_needed(timeout=5000)
            bombear(30)
            bb = loc.bounding_box()
            if not bb: sys.exit("sin caja visible para %r" % sel)
            return bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2, bb

        def mover(x, y, seg=0.55):
            x0, y0 = pos; dist = math.hypot(x - x0, y - y0)
            seg = max(0.18, seg if dist > 4 else 0.1)
            arco = random.uniform(-0.12, 0.12) * dist
            t0 = rec.t(); rec.cursor.append((t0, t0 + seg, (x0, y0), (x, y), arco))
            n = max(2, int(seg * 40))
            for i in range(1, n + 1):
                k = ease(i / n); nx, ny = punto_cursor((x0, y0), (x, y), arco, k)
                page.mouse.move(nx, ny); bombear(max(1, int(seg / n * 1000) - 4))
            pos[0], pos[1] = x, y

        def clic(x, y, doble=False):
            mover(x, y); bombear(60)
            rec.clics.append(rec.t())
            page.mouse.down(); page.mouse.up()
            if doble:
                bombear(90); rec.clics.append(rec.t()); page.mouse.down(); page.mouse.up()
            bombear(120)

        def zoom(cx, cy, nivel, seg):
            rec.camara.append((rec.t(), seg, cx, cy, max(1.0, float(nivel))))

        for p in spec.get("pasos") or []:
            a = str(p.get("accion") or "").lower()
            seg = float(p.get("seg", 0.7))
            if a == "esperar":
                esperar(seg)
            elif a == "esperar_selector":
                page.locator(p["selector"]).first.wait_for(state="visible", timeout=int(float(p.get("seg", 10)) * 1000)); bombear(80)
            elif a == "ir":
                ir(str(p["url"])); esperar(0.6)
            elif a in ("clic", "mover"):
                if p.get("selector"): x, y, _ = centro(p["selector"])
                else: x, y = float(p.get("x", pos[0])), float(p.get("y", pos[1]))
                if a == "clic": clic(x, y, bool(p.get("doble")))
                else: mover(x, y, seg)
            elif a == "escribir":
                if p.get("selector"):
                    x, y, _ = centro(p["selector"]); clic(x, y)
                cps = max(4.0, float(p.get("cps", 15)))
                for ch in str(p.get("texto") or ""):
                    if ch == "\n": page.keyboard.press("Enter")
                    else: page.keyboard.type(ch)
                    esperar(random.uniform(0.6, 1.4) / cps)
                esperar(0.15)
            elif a == "pulsar":
                page.keyboard.press(str(p.get("tecla") or "Enter")); bombear(100)
            elif a == "scroll":
                n = max(2, int(seg * 30)); tot = float(p.get("y", 300)); prev = 0.0
                for i in range(1, n + 1):
                    k = ease(i / n); page.mouse.wheel(0, tot * k - prev); prev = tot * k; bombear(max(1, int(seg / n * 1000) - 4))
                esperar(0.2)
            elif a == "zoom":
                nivel = float(p.get("nivel", 1.0))
                if nivel <= 1.001: cx, cy = vw / 2, vh / 2
                elif p.get("selector"):
                    cx, cy, bb = centro(p["selector"])
                    if not p.get("forzar"):   # nunca cortar el elemento por los lados: el zoom cabe en su ancho (+ margen)
                        nivel = max(1.0, min(nivel, vw / (bb["width"] + 24), vh / (bb["height"] + 24)))
                        # 12/11/2026 (Calidad, 405: «el borde corta Saldo e Ingresos»): tampoco se cortan por los lados
                        # los textos cortos vecinos (etiquetas, cifras, botones); se baja el nivel hasta que entren enteros.
                        pedido = nivel
                        try: cajas = page.evaluate(JS_TEXTOS)
                        except Exception: cajas = []
                        while nivel > 1.001 and textos_cortados(cajas, cx, cy, nivel, vw, vh):
                            nivel = max(1.0, round(nivel - 0.05, 3))
                        if nivel < pedido - 0.001:
                            print("AVISO ENCUADRE: zoom a %s bajado de %.2f a %.2f para no cortar texto por los lados (\"forzar\": true lo impide)"
                                  % (str(p.get("selector"))[:50], pedido, nivel))
                else:
                    cx, cy = float(p.get("x", vw / 2)), float(p.get("y", vh / 2))
                    if not p.get("forzar"):   # 13/11/2026 (Calidad, 406: título y botón cortados): la misma guardia con zoom por coordenadas
                        pedido = nivel
                        try: cajas = page.evaluate(JS_TEXTOS)
                        except Exception: cajas = []
                        while nivel > 1.001 and textos_cortados(cajas, cx, cy, nivel, vw, vh):
                            nivel = max(1.0, round(nivel - 0.02, 3))
                        if nivel < pedido - 0.001:
                            print("AVISO ENCUADRE: zoom a (%d,%d) bajado de %.2f a %.2f para no cortar texto por los lados (\"forzar\": true lo impide)"
                                  % (cx, cy, pedido, nivel))
                zoom(cx, cy, nivel, seg); esperar(seg + 0.1)
            else:
                print("paso desconocido ignorado:", a)
        esperar(0.25)
        duracion = rec.t()
        cdp.send("Page.stopScreencast")
        br.close()
    return duracion, (vw, vh), escala, disp

def punto_cursor(p0, p1, arco, k):
    """Camino del cursor: recta con un pequeno arco (curva de Bezier cuadratica) para que no sea robotico."""
    x = p0[0] + (p1[0] - p0[0]) * k; y = p0[1] + (p1[1] - p0[1]) * k
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]; L = math.hypot(dx, dy) or 1.0
    s = math.sin(math.pi * k) * arco
    return x - dy / L * s, y + dx / L * s

# ---------------------------------------------------------------- composicion
def _rr_mask(size, radio, ss=3):
    m = Image.new("L", (size[0] * ss, size[1] * ss), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size[0] * ss - 1, size[1] * ss - 1], radio * ss, fill=255)
    return m.resize(size, Image.LANCZOS)

def fondo_dispositivo(nombre, disp, color, marco):
    """Lienzo base: fondo plano + sombra suave + cuerpo del dispositivo (la pantalla se pega encima en cada fotograma)."""
    sx, sy, sw, sh = disp["pantalla"]; b = disp["bisel"]
    cuerpo = (24, 24, 28) if marco != "claro" else (236, 236, 240)
    img = Image.new("RGB", (W, H), color)
    x0, y0, x1, y1 = sx - b, sy - b, sx + sw + b, sy + sh + b
    if nombre == "portatil": y1 += 0   # la tapa; la base se dibuja aparte
    sombra = Image.new("L", (W, H), 0); ds = ImageDraw.Draw(sombra)
    ds.rounded_rectangle([x0 + 6, y0 + 26, x1 + 6, y1 + 30], disp["radio_c"], fill=110)
    if nombre == "portatil": ds.rounded_rectangle([x0 - 50, y1 + 6, x1 + 50, y1 + 52], 20, fill=110)
    sombra = sombra.filter(ImageFilter.GaussianBlur(26))
    oscuro = Image.new("RGB", (W, H), tuple(int(c * 0.55) for c in color))
    img = Image.composite(oscuro, img, sombra.point(lambda v: int(v * 0.55)))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x0, y0, x1, y1], disp["radio_c"], fill=cuerpo)
    if nombre == "portatil":   # base del portatil bajo la tapa
        base = (205, 207, 214) if marco != "claro" else (222, 223, 228)
        d.rounded_rectangle([x0 - 50, y1 - 2, x1 + 50, y1 + 36], 18, fill=base)
        d.rounded_rectangle([W // 2 - 90, y1 - 2, W // 2 + 90, y1 + 12], 8, fill=tuple(int(c * 0.88) for c in base))
    if disp["isla"]:
        d.rounded_rectangle([W // 2 - 70, sy + 16, W // 2 + 70, sy + 16 + 38], 19, fill=(8, 8, 10))
    return img

def sprite_cursor(alto=46):
    """Flecha de cursor con borde y sombra, dibujada a 4x y reducida (nitida)."""
    ss = 4; w, h = int(alto * 0.72) * ss, alto * ss
    pts = [(0, 0), (0, 0.80), (0.19, 0.63), (0.31, 0.93), (0.43, 0.88), (0.31, 0.58), (0.56, 0.58)]
    P = [(x * w * 1.0, y * h) for x, y in pts]
    im = Image.new("RGBA", (w + 24 * ss, h + 24 * ss), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    off = 8 * ss
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).polygon([(x + off + 3 * ss, y + off + 4 * ss) for x, y in P], fill=(0, 0, 0, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(3 * ss)); im.alpha_composite(sh)
    d.polygon([(x + off, y + off) for x, y in P], fill=(255, 255, 255, 255), outline=(20, 20, 24, 255))
    d.line([(x + off, y + off) for x, y in P + [P[0]]], fill=(20, 20, 24, 255), width=2 * ss, joint="curve")
    return im.resize((im.width // ss, im.height // ss), Image.LANCZOS), (off // ss, off // ss)

JS_TEXTOS = """() => { const out = []; const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n;
  while ((n = w.nextNode())) { if (!n.textContent.trim() || !n.parentElement) continue;
    const st = getComputedStyle(n.parentElement); if (st.visibility === 'hidden' || parseFloat(st.opacity) < 0.1) continue;
    const r = document.createRange(); r.selectNodeContents(n);
    for (const b of r.getClientRects()) { if (b.width > 2 && b.height > 2) out.push([b.left, b.top, b.width, b.height]); } }
  return out; }"""

def textos_cortados(cajas, cx, cy, nivel, vw, vh):
    """Numero de lineas de texto cortas (< 60 % del ancho) que el encuadre del zoom partiria por la izquierda o la derecha."""
    rw, rh = vw / nivel, vh / nivel
    x0 = min(max(cx - rw / 2, 0), vw - rw); y0 = min(max(cy - rh / 2, 0), vh - rh)
    n = 0
    for (x, y, w, h) in cajas:
        if w >= 0.6 * vw or y + h <= y0 + 2 or y >= y0 + rh - 2: continue
        if (x < x0 - 0.5 and x + w > x0 + 3) or (x + w > x0 + rw + 0.5 and x < x0 + rw - 3): n += 1
    return n

def camara_en(t, cams, vw, vh):
    """Rectangulo visible (x0, y0, ancho, alto) del viewport en el instante t, con transiciones suaves entre zooms."""
    cx0, cy0, n0 = vw / 2, vh / 2, 1.0
    for (ti, dur, cx, cy, nivel) in cams:
        if t >= ti + dur: cx0, cy0, n0 = cx, cy, nivel; continue
        k = ease((t - ti) / max(0.05, dur)) if t > ti else 0.0
        cx0, cy0, n0 = cx0 + (cx - cx0) * k, cy0 + (cy - cy0) * k, n0 + (nivel - n0) * k
        break
    rw, rh = vw / n0, vh / n0
    x0 = min(max(cx0 - rw / 2, 0), vw - rw); y0 = min(max(cy0 - rh / 2, 0), vh - rh)
    return x0, y0, rw, rh

def cursor_en(t, segs):
    pos = segs[0][2]
    for (t0, t1, p0, p1, arco) in segs:
        if t < t0: break
        if t >= t1: pos = p1; continue
        pos = punto_cursor(p0, p1, arco, ease((t - t0) / max(0.01, t1 - t0))); break
    return pos

def componer(rec, duracion, vwh, escala, disp, spec, salida, fps):
    vw, vh = vwh
    nombre = str(spec.get("dispositivo") or "movil").lower()
    base = fondo_dispositivo(nombre, disp, hex_rgb(spec.get("fondo")), str(spec.get("marco") or "oscuro"))
    sx, sy, sw, sh = disp["pantalla"]
    mascara = _rr_mask((sw, sh), disp["radio_p"])
    spr, (ox, oy) = sprite_cursor(46)
    frames = sorted(rec.frames, key=lambda f: f[0])
    if not frames: sys.exit("la captura no devolvio ningun fotograma (¿la pagina carga?)")
    n = max(2, int(math.ceil((duracion + 0.3) * fps)))
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H), "-r", str(fps),
           "-i", "-", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", salida]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    idx = -1; cur_img = None; abs0 = rec.t0
    for fi in range(n):
        t = fi / fps
        j = 0
        while j + 1 < len(frames) and frames[j + 1][0] <= abs0 + t: j += 1
        if j != idx:
            idx = j; cur_img = Image.open(io.BytesIO(frames[j][1])).convert("RGB")
            ek = cur_img.width / vw   # escala real de la captura (px por px CSS)
        x0, y0, rw, rh = camara_en(t, rec.camara, vw, vh)
        crop = cur_img.crop((int(x0 * ek), int(y0 * ek), int((x0 + rw) * ek), int((y0 + rh) * ek)))
        scr = crop.resize((sw, sh), Image.LANCZOS)
        img = base.copy(); img.paste(scr, (sx, sy), mascara)
        k = sw / rw   # px de lienzo por px CSS
        px, py = cursor_en(t, rec.cursor)
        cx, cy = sx + (px - x0) * k, sy + (py - y0) * k
        # anillo de clic (cian, 0,5 s)
        d = ImageDraw.Draw(img, "RGBA")
        for tc in rec.clics:
            dt = t - tc
            if 0 <= dt < 0.5 and sx <= cx <= sx + sw and sy <= cy <= sy + sh:
                kk = ease(dt / 0.5); r = 18 + 54 * kk
                d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=CIAN + (int(230 * (1 - kk)),), width=6)
        if sx - 4 <= cx <= sx + sw and sy - 4 <= cy <= sy + sh:
            img.paste(spr, (int(cx - ox), int(cy - oy)), spr)
        pr.stdin.write(np.asarray(img, dtype=np.uint8).tobytes())
    pr.stdin.close()
    if pr.wait() != 0: sys.exit("ffmpeg fallo")
    return n

def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    spec_path, salida = sys.argv[1], sys.argv[2]
    fps = int(sys.argv[sys.argv.index("--fps") + 1]) if "--fps" in sys.argv else 30
    spec = json.load(open(spec_path, encoding="utf-8"))
    random.seed(int(spec.get("semilla", 3)))
    rec = Registro(); t0 = time.time()
    duracion, vwh, escala, disp = grabar(spec, os.path.dirname(os.path.abspath(spec_path)), rec)
    print("captura: %.1f s, %d fotogramas, %d clics (%.1f s)" % (duracion, len(rec.frames), len(rec.clics), time.time() - t0))
    n = componer(rec, duracion, vwh, escala, disp, spec, salida, fps)
    print("OK %s (%d fotogramas, %.1f s, total %.1f s)" % (salida, n, n / fps, time.time() - t0))

if __name__ == "__main__":
    main()
