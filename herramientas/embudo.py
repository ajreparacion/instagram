#!/usr/bin/env python3
"""EMBUDO DE MONETIZACION: del alcance al primer euro. Lee equipo/kpi_buzzfy.json y equipo/leads.json y escribe equipo/embudo.md.
Uso: python3 herramientas/embudo.py        (gratis, sin red). Lo regenera cualquier rol tras actualizar kpi_buzzfy.json o leads.json.
Señala el paso mas debil (donde mas gente se pierde respecto a la referencia) para que sea la prioridad del dia."""
import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
k = json.load(open(os.path.join(R, "equipo", "kpi_buzzfy.json"), encoding="utf-8"))
l = json.load(open(os.path.join(R, "equipo", "leads.json"), encoding="utf-8"))
reg = [x for x in l.get("registros", [])]
def suma(c): 
    v = [x.get(c) for x in reg if isinstance(x.get(c), (int, float))]; return sum(v) if v else None
def pct(a, b): return "n/d" if not b or a is None else "%.1f %%" % (100.0 * a / b)
nsa, vp, ce = k.get("alcance_no_seguidores_total"), k.get("visitas_perfil"), k.get("clics_enlace")
sol, dms, pru, eur = suma("solicitudes_centro"), suma("dms_con_intencion"), suma("pruebas_gratuitas"), suma("ingresos_eur")
pasos = [("Alcance a no seguidores → visita al perfil", vp, nsa, 3.0, "gancho del reel, nombre visible y portada: que el perfil prometa lo que el reel enseñó"),
         ("Visita al perfil → clic en el enlace", ce, vp, 25.0, "nombre visible, bio y enlace (hoy: «IA Fácil…», «Escríbeme IDEA» y /demo en lugar de /solicitar)"),
         ("Clic en el enlace → solicitud en el Centro", sol, ce, 20.0, "página de destino y formulario /solicitar")]
L = ["# Embudo de monetización (generado por herramientas/embudo.py; no editar a mano)", "",
     "Datos Buzzfy: %s · ventana %s días · seguidores netos/día %s" % (k.get("fecha"), k.get("dias"), k.get("seguidores_netos_dia")), "",
     "| Paso | Cifras | Conversión | Referencia | Dónde actuar |", "|---|---|---|---|---|"]
peor = None
for n, a, b, ref, donde in pasos:
    c = None if (a is None or not b) else 100.0 * a / b
    L.append("| %s | %s de %s | %s | ≥ %.0f %% | %s |" % (n, "n/d" if a is None else a, "n/d" if b is None else b, pct(a, b), ref, donde))
    if c is not None:
        brecha = c / ref
        if peor is None or brecha < peor[0]: peor = (brecha, n, donde)
L += ["", "Solicitudes en el Centro: %s · DMs con intención: %s · pruebas gratuitas: %s · **ingresos confirmados: %s €**" % tuple("n/d" if v is None else v for v in (sol, dms, pru, eur)), ""]
if peor: L.append("**Paso más débil hoy: %s.** Prioridad del día: %s." % (peor[1], peor[2]))
if not sol: L.append("**Cero solicitudes registradas**: nada vale más que la primera. Cada pieza y cada cambio de la jornada se justifica por cómo la acerca.")
p = k.get("perfil") or {}
falta = []
if "IA Fácil" in str(p.get("nombre_visible")): falta.append("nombre visible → «Neogest Lab · Apps a medida» (Instagram lo bloquea hasta %s)" % (p.get("nombre_bloqueado_hasta") or "pasar 14 días"))
if "/solicitar" not in str(p.get("enlace")): falta.append("enlace de la bio → https://centro-de-contenido-apps-2f0a3cd6.base44.app/solicitar?src=instagram con título «Pide tu prueba gratuita» (solo desde la app del móvil, Editar perfil → Enlaces)")
if p.get("bio_con_IDEA"): falta.append("bio sin «Escríbeme IDEA»")
if falta: L += ["", "Pendiente del perfil (la API no lo cambia): " + "; ".join(falta) + "."]
open(os.path.join(R, "equipo", "embudo.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))
