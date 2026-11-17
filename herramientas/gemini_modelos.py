#!/usr/bin/env python3
"""Diagnóstico: lista los modelos de Gemini que la clave GEMINI_API_KEY puede usar ahora
mismo para generateContent. Útil cuando guionista_gemini.py se queda sin modelos válidos
en MODELOS (Google cambia el catálogo con cierta frecuencia).
Uso: GEMINI_API_KEY=... python3 herramientas/gemini_modelos.py
"""
import json
import os
import urllib.request

api_key = os.environ["GEMINI_API_KEY"]
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
with urllib.request.urlopen(url, timeout=30) as resp:
    data = json.loads(resp.read().decode("utf-8"))

for m in data.get("models", []):
    metodos = m.get("supportedGenerationMethods", [])
    if "generateContent" in metodos:
        print(m["name"], "·", m.get("displayName", ""))
