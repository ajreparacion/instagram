#!/usr/bin/env python3
"""Explora una web pública SOLO LEYENDO (nunca envía formularios): para cada ruta guarda título, texto visible,
botones/enlaces, campos y una captura. Lo usa Mejora para preparar la grabación de un recorrido (grabacion.json).
Uso: python3 explorar_web.py URL carpeta_salida [ruta1 ruta2 ...]   (sin rutas: portada + enlaces internos del menú)"""
import sys, os, json, re
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright

def limpiar(s): return re.sub(r"\s+", " ", s or "").strip()

def explorar(pg, url, carpeta, nombre):
    pg.goto(url, wait_until="networkidle", timeout=60000)
    pg.wait_for_timeout(1500)
    for t in ("saltar", "skip", "entrar", "aceptar", "acepto"):   # introducciones y cookies (no envía nada)
        try:
            b = pg.get_by_role("button", name=re.compile(t, re.I)).first
            if b.count() and b.is_visible():
                b.click(timeout=1500); pg.wait_for_timeout(600); break
        except Exception: pass
    datos = {"url": pg.url, "titulo": pg.title(), "meta": (pg.locator("meta[name=description]").first.get_attribute("content") if pg.locator("meta[name=description]").count() else None)}
    datos["texto"] = limpiar(pg.inner_text("body"))[:2500]
    datos["encabezados"] = [limpiar(x) for x in pg.eval_on_selector_all("h1,h2,h3", "e=>e.map(x=>x.innerText)")][:40]
    datos["botones"] = [limpiar(x) for x in pg.eval_on_selector_all("button,[role=button]", "e=>e.map(x=>x.innerText||x.getAttribute('aria-label')||'')") if limpiar(x)][:40]
    datos["enlaces"] = [[limpiar(t), h] for t, h in pg.eval_on_selector_all("a", "e=>e.map(x=>[x.innerText,x.getAttribute('href')])") if h][:60]
    datos["campos"] = pg.eval_on_selector_all("input,textarea,select", "e=>e.map(x=>({tag:x.tagName,tipo:x.type||'',ph:x.placeholder||'',nombre:x.name||x.id||''}))")[:30]
    datos["alto_pagina"] = pg.evaluate("document.documentElement.scrollHeight")
    pg.screenshot(path=os.path.join(carpeta, nombre + ".png"), full_page=True)
    return datos

def main():
    base, carpeta = sys.argv[1], sys.argv[2]
    rutas = sys.argv[3:]
    os.makedirs(carpeta, exist_ok=True)
    out = {}
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1, locale="es-ES")
        try:
            out["portada"] = explorar(pg, base, carpeta, "portada")
        except Exception as e:
            out["portada"] = {"error": str(e)[:300]}
        if not rutas and "enlaces" in out["portada"]:
            host = urlparse(base).netloc
            vistos = set()
            for _, h in out["portada"]["enlaces"]:
                u = urljoin(base, h)
                if urlparse(u).netloc == host and "#" not in u and u.rstrip("/") not in vistos and u.rstrip("/") != base.rstrip("/") and not u.startswith("mailto"):
                    vistos.add(u.rstrip("/")); rutas.append(u)
            rutas = rutas[:12]
        for i, r in enumerate(rutas):
            u = urljoin(base, r)
            try:
                out[u] = explorar(pg, u, carpeta, f"p{i + 1:02d}")
            except Exception as e:
                out[u] = {"error": str(e)[:300]}
        b.close()
    json.dump(out, open(os.path.join(carpeta, "explorar.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("OK", len(out), "páginas")

if __name__ == "__main__":
    main()
