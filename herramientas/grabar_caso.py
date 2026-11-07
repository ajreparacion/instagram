#!/usr/bin/env python3
"""Graba con Playwright una herramienta de herramientas/casos/<nombre>.html funcionando de verdad (1080x1920).
Secuencia: [0-3 s] resultado ya hecho (gancho) -> mensaje a la IA tecleado -> herramienta vacia -> se rellena con cursor -> resultado.
Uso: python3 herramientas/grabar_caso.py <nombre> <carpeta_salida>   -> demo.mp4 y marcas.json (segundos de cada fase)."""
import sys, os, json, time, subprocess, glob, shutil, tempfile
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
PROMPTS = json.load(open(os.path.join(HERE, "casos", "prompts.json"), encoding="utf-8"))

def run(nombre, out):
    os.makedirs(out, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="rec_")
    marks = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 1080, "height": 1920}, device_scale_factor=1,
                            record_video_dir=tmp, record_video_size={"width": 1080, "height": 1920})
        t0 = time.time()
        pg = ctx.new_page()
        T = lambda: round(time.time() - t0, 2)
        wait = pg.wait_for_timeout
        pg.goto("file://" + os.path.join(HERE, "casos", nombre + ".html"))
        pg.wait_for_load_state("load"); wait(200)
        def mv(sel, dx=0, dy=0, steps=16):
            bb = pg.locator(sel).first.bounding_box()
            pg.mouse.move(bb["x"] + bb["width"] / 2 + dx, bb["y"] + bb["height"] / 2 + dy, steps=steps)
        def clk(sel, **k):
            mv(sel, **k); wait(90); pg.mouse.down(); wait(60); pg.mouse.up(); wait(160)
        def tipo(sel, txt, d=70):
            clk(sel); pg.keyboard.type(txt, delay=max(18, d // 2)); wait(150)
        pg.evaluate("preset(); showTool()"); marks["hook_ini"] = T(); wait(3400)
        marks["prompt_ini"] = T(); pg.mouse.move(540, 1650)
        pg.evaluate("showPrompt()"); wait(350)
        txt = PROMPTS[nombre]["prompt"]
        pg.evaluate("setPrompt('')")
        n = 0
        step = max(1, len(txt) // 42)
        while n < len(txt):
            n = min(len(txt), n + step); pg.evaluate("setPrompt(%s)" % json.dumps(txt[:n])); wait(55)
        wait(900); clk("#send", steps=16); marks["prompt_fin"] = T()
        pg.evaluate("reset(); showTool()"); wait(700); marks["tool_ini"] = T()
        pg.mouse.move(540, 1650)
        marks.update(globals()["paso_" + nombre](pg, clk, tipo, mv, wait, T))
        marks["fin"] = T(); wait(300)
        ctx.close(); b.close()
    vid = glob.glob(os.path.join(tmp, "*.webm"))[0]
    mp4 = os.path.join(out, "demo.mp4")
    off = marks["hook_ini"] + 0.7   # recorte del arranque en blanco; todas las marcas pasan a ser del mp4
    marks = {k: round(v - off, 2) for k, v in marks.items()}
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "%.2f" % off, "-i", vid, "-r", "30", "-c:v", "libx264", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", mp4], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    json.dump(marks, open(os.path.join(out, "marcas.json"), "w"), indent=1)
    print(nombre, marks)

# ------------------------------------------------------------------ pasos de cada herramienta
def paso_presupuesto(pg, clk, tipo, mv, wait, T):
    m = {}
    L = lambda i, j: ".ln:nth-child(%d) input:nth-child(%d)" % (i, j)
    tipo(L(1, 1), "Cambiar grifo cocina"); tipo(L(1, 2), "1", 90); tipo(L(1, 3), "85")
    tipo(L(2, 1), "Material de fontanería"); tipo(L(2, 2), "1", 90); tipo(L(2, 3), "32")
    m["lineas12"] = T()
    clk("#add"); tipo(L(3, 1), "Desplazamiento"); tipo(L(3, 2), "1", 90); tipo(L(3, 3), "15")
    wait(600); m["total21"] = T(); assert pg.inner_text("#total").replace("\xa0", " ") == "159,72 €", pg.inner_text("#total")
    clk("#iva"); pg.select_option("#iva", "10"); wait(900)
    m["total10"] = T(); assert pg.inner_text("#total") == "145,20 €"; wait(1100)
    return m

def paso_cuenta(pg, clk, tipo, mv, wait, T):
    m = {}
    tipo("#tot", "86,40", 110); wait(400)
    for _ in range(2): clk("#mas", steps=14)
    m["pers4"] = T(); clk('#chips button[data-p="5"]'); wait(900)
    m["res4"] = T(); assert pg.inner_text("#cada") == "22,68 €", pg.inner_text("#cada")
    wait(500); clk("#mas", steps=12); wait(1000)
    m["res5"] = T(); assert pg.inner_text("#cada") == "18,14 €", pg.inner_text("#cada"); wait(1000)
    return m

def paso_suscripciones(pg, clk, tipo, mv, wait, T):
    m = {}
    for n, pr in (("Streaming", "12,99"), ("Música", "10,99"), ("Gimnasio", "29,90")):
        tipo("#nom", n, 55); tipo("#pre", pr, 70); clk("#add", steps=16)
    wait(700); m["tres"] = T(); assert pg.inner_text("#anio") == "646,56 €", pg.inner_text("#anio")
    wait(500); clk(".it:nth-child(3) .ck", steps=20); wait(1100)
    m["quita"] = T(); assert pg.inner_text("#anio") == "287,76 €" and "358,80" in pg.inner_text("#ah"), pg.inner_text("#ah")
    wait(1100)
    return m

def paso_compra(pg, clk, tipo, mv, wait, T):
    m = {}
    tipo("#txt", "leche, papel higiénico, manzanas, pan, detergente, yogures, tomates, arroz, lejía, huevos", 38)
    wait(300); clk("#ord", steps=16); wait(1000); m["ordenada"] = T()
    items = pg.locator(".i")
    txt = [items.nth(k).inner_text().strip().replace("✓","").strip() for k in range(items.count())]
    assert txt[:2] == ["Manzanas", "Tomates"] and "Papel higiénico" in txt and "Lejía" in txt, txt
    clk(".g:nth-child(1) .i:nth-of-type(1)", steps=22); wait(300)
    clk(".g:nth-child(2) .i:nth-of-type(1)", steps=18); wait(300)
    clk(".g:nth-child(2) .i:nth-of-type(2)", steps=14); wait(1100)
    m["tachado"] = T()
    return m

if __name__ == "__main__":
    run(sys.argv[1], sys.argv[2])
