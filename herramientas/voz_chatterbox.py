#!/usr/bin/env python3
"""Locución con Chatterbox de Resemble AI (código y pesos MIT: uso comercial sin atribución obligatoria).

Uso: python3 voz_chatterbox.py lote.json
  lote.json = {"modelo": "es-es" | "multilingue", "idioma": "es",
               "exageracion": 0.6, "cfg": 0.35, "temperatura": 0.75, "referencia": "/ruta/voz_ref.wav" | null,
               "ganancia": 1.0, "semilla": 1518, "theta": "" | "griego" | "griego_sin_inicial",
               "frases": [{"texto": "...", "salida": "/ruta/voz0.wav"}, ...]}

- "modelo": "es-es" carga el afinado para español de España (Hugging Face ResembleAI/Chatterbox-Multilingual-es-es,
  MIT) sobre el modelo multilingüe; si no se puede, usa el multilingüe (ResembleAI/chatterbox, MIT) con
  language_id="es" y lo deja dicho en el JSON de salida ("modelo_usado").
- "referencia": wav de 5-15 s cuya voz se imita. SOLO la voz del propio usuario (voces/referencia_usuario.wav) o
  una voz de referencia con licencia libre (p. ej. generada con Kokoro, Apache 2.0). Nunca la de otra persona real.
  Si no hay referencia se usa la voz integrada del modelo (conds.pt, parte de la publicación MIT).
- Funciona en CPU (lento: cuenta ~1 min por cada 10 s de voz en el runner de GitHub). El modelo se carga UNA vez.
- Expresividad: "exageracion" (0,25 plano … 0,5 normal … 0,7+ muy expresivo) y "cfg" (0,5 normal; 0,3 más
  expresivo y más lento). Las pausas se escriben en el texto: comas, puntos y puntos suspensivos.
Escribe en stdout un JSON con tiempos. Código de salida != 0 si algo falla: publicar_gh.py pasa al motor de respaldo.
"""
import json
import os
import re
import sys
import time
import wave

import numpy as np

REPO_ES = "ResembleAI/Chatterbox-Multilingual-es-es"


def a_theta(t, modo):
    """Contra el seseo (7/11/2026): Chatterbox dice «s» donde España dice «z» / «c» ante e, i. Escribiendo esa letra
    como la griega θ el modelo (su tokenizador incluye el griego) sí pronuncia la θ. modo "griego": todas;
    "griego_sin_inicial": se deja la «c» al principio de palabra (cerveza, cinco), que sale como «t»."""
    if not modo:
        return t
    ini = "(?<=[\\wáéíóúñ])" if modo == "griego_sin_inicial" else ""
    t = re.sub(ini + "c(?=[eiéí])", "θ", t)
    t = re.sub(ini + "C(?=[eiéí])", "Θ", t)
    return t.replace("z", "θ").replace("Z", "Θ")


def cargar(modelo_pedido, device="cpu"):
    """Devuelve (modelo, nombre_usado). Primero el afinado es-es; si falla, el multilingüe v3; si falla, el v2."""
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    avisos = []
    try:
        m = ChatterboxMultilingualTTS.from_pretrained(device=device, t3_model="v3")
        base = "multilingue-v3"
    except TypeError:
        m = ChatterboxMultilingualTTS.from_pretrained(device=device)
        base = "multilingue"
    if modelo_pedido != "es-es":
        return m, base, avisos
    try:
        import torch
        from huggingface_hub import hf_hub_download
        from safetensors.torch import load_file
        t3_path = hf_hub_download(repo_id=REPO_ES, filename="t3_es_es.safetensors")
        sd = load_file(t3_path)
        if "model" in sd and isinstance(sd["model"], (list, tuple)):
            sd = sd["model"][0]
        propias = set(m.t3.state_dict().keys())
        if not (set(sd) & propias):  # claves con prefijo (module., t3., model.): se quita
            for pref in ("module.", "t3.", "model."):
                cand = {k[len(pref):]: v for k, v in sd.items() if k.startswith(pref)}
                if set(cand) & propias:
                    sd = cand
                    break
        faltan, sobran = m.t3.load_state_dict(sd, strict=False)
        if faltan or sobran:
            # distinto tamaño de vocabulario u otra arquitectura: no se mezcla, se queda el multilingüe
            raise RuntimeError(f"t3_es_es no encaja (faltan {len(faltan)}, sobran {len(sobran)})")
        try:
            s3_path = hf_hub_download(repo_id=REPO_ES, filename="s3gen_v3.safetensors")
            m.s3gen.load_state_dict(load_file(s3_path), strict=False)
        except Exception as e:  # el decodificador del paquete es opcional
            avisos.append(f"s3gen_v3 no cargado: {str(e)[-120:]}")
        m.t3.eval(); m.s3gen.eval()
        return m, "es-es", avisos
    except Exception as e:
        avisos.append(f"afinado es-es no disponible ({str(e)[-160:]}); se usa el multilingüe")
        return m, base, avisos


def a_numpy(wav):
    try:
        x = wav.detach().cpu().numpy()
    except AttributeError:
        x = np.asarray(wav)
    return x.astype(np.float32).reshape(-1)


def main():
    lote = json.load(open(sys.argv[1], encoding="utf-8"))
    t0 = time.time()
    import torch
    torch.set_num_threads(max(1, os.cpu_count() or 1))
    if lote.get("semilla") is not None:
        torch.manual_seed(int(lote["semilla"]))
    modelo, usado, avisos = cargar(str(lote.get("modelo") or "es-es"), "cpu")
    carga = time.time() - t0
    sr = int(getattr(modelo, "sr", 24000))
    kw = {"language_id": str(lote.get("idioma") or "es"),
          "exaggeration": float(lote.get("exageracion", 0.5)),
          "cfg_weight": float(lote.get("cfg", 0.5)),
          "temperature": float(lote.get("temperatura", 0.8))}
    ref = lote.get("referencia")
    if ref and os.path.exists(ref) and os.path.getsize(ref) > 20000:
        kw["audio_prompt_path"] = ref
    else:
        ref = None
    ganancia = float(lote.get("ganancia", 1.0))
    tiempos = []
    reintentos = []
    for f in lote["frases"]:
        t1 = time.time()
        # Chatterbox a veces alucina (repite o añade palabras): si la frase dura mucho más de lo que
        # corresponde a sus palabras (~2,2 palabras/s + pausas), se vuelve a generar con otra semilla (máx. 2 veces).
        # (base 1,0 s + 0,5 s por cada punto/signo interno: «Falso. Lo inventamos nosotros.» dura 4,4 s de forma legítima)
        esperado = len(f["texto"].split()) / 2.2 + 1.0 + 0.4 * f["texto"].count("…") \
            + 0.5 * max(0, len(re.findall(r"[.!?;:]\s", f["texto"].strip())))
        kwf = dict(kw)   # ajustes propios de la frase (publicar_gh.py por_estilo: gancho y giro más intensos)
        for k_json, k_cb in (("exageracion", "exaggeration"), ("cfg", "cfg_weight"), ("temperatura", "temperature")):
            if f.get(k_json) is not None:
                kwf[k_cb] = float(f[k_json])
        x = None
        for intento in range(3):
            with torch.inference_mode():
                wav = modelo.generate(a_theta(f["texto"], lote.get("theta")), **kwf)
            x = a_numpy(wav)
            dur = x.size / sr
            if x.size >= sr * 0.2 and np.isfinite(x).all() and dur <= esperado * 1.6:
                break
            reintentos.append({"texto": f["texto"][:40], "dur": round(dur, 2), "esperado": round(esperado, 2)})
            torch.manual_seed(int(lote.get("semilla") or 7) + 101 * (intento + 1))
        if x is None or x.size < sr * 0.2 or not np.isfinite(x).all():
            raise SystemExit(f"Chatterbox devolvió audio vacío o inválido para: {f['texto'][:60]}")
        pico = float(np.abs(x).max())
        if pico > 0.98:  # el modelo a veces roza el techo: se normaliza a -1 dBFS antes del procesado posterior
            x = x * (0.89 / pico)
        x = np.clip(x * ganancia, -1.0, 1.0)
        with wave.open(f["salida"], "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes((x * 32767).astype("<i2").tobytes())
        tiempos.append(round(time.time() - t1, 2))
    if reintentos:
        avisos.append(f"frases regeneradas por duración anómala: {reintentos}")
    print(json.dumps({"modelo_usado": usado, "referencia": bool(ref), "avisos": avisos, "carga_s": round(carga, 1),
                      "frases_s": tiempos, "total_s": round(time.time() - t0, 1), "sample_rate": sr,
                      "theta": lote.get("theta") or None,
                      "ajustes": {k: v for k, v in kw.items() if k != "audio_prompt_path"}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
