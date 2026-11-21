#!/usr/bin/env python3
"""CONTROL DE AUDIO (DIRECTIVA DE VÍDEO 14/11/2026). Uso: python3 control_audio.py video.mp4 guion.json [--salida control_audio.json]
Transcribe el audio final con faster-whisper y lo compara con la voz del guion; mide silencios con silencedetect (-45 dB, 0,6 s).
RECHAZO (exit 1): duración > 30 s · silencio > 0,6 s DENTRO de la voz · palabra distinta del guion (salvo homófonos) · «ehm» ·
falta el giro (escena remate) · sin atribución musical si el post.json la exige. Los silencios al inicio/fin del vídeo no cuentan.
Si falla, el reel NO se publica: publicar_gh.py anota el motivo en control_audio.json y lo deja sin publicar."""
import json, os, re, subprocess, sys, unicodedata

SIL_DB, SIL_S, DUR_MAX = -45, 0.6, 30.0
LEXICO_RUTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lexico_control.json")


def cargar_lexico(ruta=LEXICO_RUTA):
    """Tabla editable (lexico_control.json). Sin el archivo o con un JSON roto el control sigue con la tabla mínima."""
    try:
        return json.load(open(ruta, encoding="utf-8"))
    except Exception:
        return {"homofonos": [["hechas", "echas"], ["a", "ha"], ["uno", "un", "una"], ["tique", "ticket"]],
                "fonetica": {"b_v": True, "h_muda": True, "ll_y": True}, "alias": {}, "contexto_whisper": ""}


_U = "cero uno dos tres cuatro cinco seis siete ocho nueve diez once doce trece catorce quince dieciseis diecisiete dieciocho diecinueve veinte veintiuno veintidos veintitres veinticuatro veinticinco veintiseis veintisiete veintiocho veintinueve".split()
_D = {3: "treinta", 4: "cuarenta", 5: "cincuenta", 6: "sesenta", 7: "setenta", 8: "ochenta", 9: "noventa"}
_C = {1: "ciento", 2: "doscientos", 3: "trescientos", 4: "cuatrocientos", 5: "quinientos", 6: "seiscientos", 7: "setecientos", 8: "ochocientos", 9: "novecientos"}
_ORD = {1: "primero", 2: "segundo", 3: "tercero", 4: "cuarto", 5: "quinto", 6: "sexto", 7: "septimo", 8: "octavo", 9: "noveno", 10: "decimo"}
_NUMW = set(_U) | set(_D.values()) | set(_C.values()) | {"mil", "cien", "millon", "millones"} | {"doscientas", "trescientas", "cuatrocientas", "quinientas", "seiscientas", "setecientas", "ochocientas", "novecientas"}


def num_es(n):
    """Whisper escribe cifras («70», «2028») y el guion letras («setenta»): se pasa todo a letras."""
    if n < 30: return _U[n]
    if n < 100: return _D[n // 10] + ("" if n % 10 == 0 else " y " + _U[n % 10])
    if n == 100: return "cien"
    if n < 1000: return _C[n // 100] + ("" if n % 100 == 0 else " " + num_es(n % 100))
    if n < 1000000:
        m = "mil" if n // 1000 == 1 else num_es(n // 1000) + " mil"
        return m + ("" if n % 1000 == 0 else " " + num_es(n % 1000))
    return str(n)


def _cifras(t):
    """Texto con cifras, siglas y símbolos -> texto «como se dice» (15/11/2026: porcentajes, euros, horas, ordinales, miles, decimales)."""
    t = re.sub(r"\b[Ii]\.?\s*[Aa]\b\.?", "IA", t)                      # Whisper: «I.A.» / «i a» = «IA»
    t = re.sub(r"\b(\d{1,3})(?:\.(\d{3}))+\b", lambda m: m.group().replace(".", ""), t)   # 1.000 / 2.028 = miles
    t = re.sub(r"(\d)\s*[°º]\s*[cC]\b", r"\1 grados", t)                # 27 °C
    t = re.sub(r"(\d+)\s*(?:\.\s*)?([ºª]|er\b)", lambda m: " " + (_ORD[int(m.group(1))] if int(m.group(1)) in _ORD else num_es(int(m.group(1)))) +
               ("a" if m.group(2) == "ª" and int(m.group(1)) in _ORD else "") + " ", t)   # 1.º / 3ª / 1.er
    t = re.sub(r"(\d+),(\d{1,2})\s*€", lambda m: "%d coma %d " % (int(m.group(1)), int(m.group(2))), t)   # 9,90 € (el «euros» final no se oye distinto)
    t = re.sub(r"(\d+)\s*€", r"\1 euros ", t)
    t = re.sub(r"(\d+)\s*\$", r"\1 dolares ", t)
    t = re.sub(r"(\d+),(\d+)", r"\1 coma \2", t)                        # 2,5 -> 2 coma 5 (9,90 -> 9 coma 90)
    t = re.sub(r"(\d)\s*%", r"\1 por ciento", t)
    t = re.sub(r"(\d)\s*h\b", r"\1 horas", t)
    t = re.sub(r"(\d)[:.](\d)", r"\1 \2", t)                            # 23:47 -> 23 47
    t = re.sub(r"(\d)([a-zA-Z])", r"\1 \2", t)                          # 27c -> 27 c
    t = re.sub(r"([a-zA-Z])(\d)", r"\1 \2", t)
    return re.sub(r"\d+", lambda m: num_es(int(m.group())), t)


def _tokens(t):
    t = _cifras(t)
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.findall(r"[a-z0-9]+", t)


def _numerico(toks):
    """«nueve con noventa» (guion) = «9,90» (Whisper): «con»/«coma» entre cifras es lo mismo; «euros» tras el decimal no cuenta."""
    out = []
    for i, w in enumerate(toks):
        if w == "euros" and out and i + 1 < len(toks) and toks[i + 1] in ("con", "coma") and out[-1] in _NUMW:
            continue                                                    # «nueve euros con noventa»
        if w in ("con", "coma") and out and out[-1] in _NUMW and i + 1 < len(toks) and toks[i + 1] in _NUMW:
            w = "coma"
        out.append(w)
    return out


def _alias(toks, lex):
    """Formas conocidas de Whisper (lexico_control.json «alias») -> forma del guion; sobre ambos textos, de varias palabras a una."""
    tabla = {}
    for canon, variantes in (lex.get("alias") or {}).items():
        if canon.startswith("_"): continue
        c = tuple(_tokens(canon))
        for v in variantes:
            tv = tuple(_tokens(v))
            if tv and tv != c: tabla[tv] = c
    if not tabla: return toks
    largo = max(len(k) for k in tabla)
    out, i = [], 0
    while i < len(toks):
        for n in range(min(largo, len(toks) - i), 0, -1):
            c = tabla.get(tuple(toks[i:i + n]))
            if c is not None:
                out += list(c); i += n; break
        else:
            out.append(toks[i]); i += 1
    return out


def norm(t, lex=None):
    lex = lex or LEXICO
    return _alias(_numerico(_tokens(t)), lex)


def _clave(w, lex=None):
    """Forma fonética: b=v, h muda, ll=y (lexico_control.json «fonetica»)."""
    f = (lex or LEXICO).get("fonetica") or {}
    w = w.replace("ch", "ĉ")
    if f.get("ll_y", True): w = w.replace("ll", "y")
    if f.get("b_v", True): w = w.replace("v", "b")
    if f.get("h_muda", True): w = w.replace("h", "")
    return w.replace("ĉ", "ch")


def _grupos(lex):
    return [{_clave(x) for x in g} | set(g) for g in (lex.get("homofonos") or [])]


def _preparar(lex):
    return {"grupos": _grupos(lex)}


LEXICO = cargar_lexico()
_PREP = _preparar(LEXICO)


def igual(a, b):
    if a == b: return True
    if a.endswith(("cientas", "cientos")) and b.endswith(("cientas", "cientos")) and a[:-2] == b[:-2]: return True
    ka, kb = _clave(a), _clave(b)
    return ka == kb or any((a in h or ka in h) and (b in h or kb in h) for h in _PREP["grupos"])


def unir(esp, got):
    """Palabras que Whisper parte o pega («prueba la» = «pruébala», «léelos» = «lee los», «noventa» = «no venta»):
    solo se unen dos palabras si su suma es EXACTAMENTE (en fonética) una palabra del otro texto; nada se inventa."""
    def une(a, b):
        ks = {_clave(x) for x in b}
        out, i = [], 0
        while i < len(a):
            if i + 1 < len(a) and _clave(a[i] + a[i + 1]) in ks and not (_clave(a[i]) in ks and _clave(a[i + 1]) in ks):
                out.append(a[i] + a[i + 1]); i += 2
            else:
                out.append(a[i]); i += 1
        return out
    return une(esp, got), une(got, esp)


def dur(v):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", v], capture_output=True, text=True)
    return float(r.stdout.strip())


def silencios(v):
    r = subprocess.run(["ffmpeg", "-nostats", "-i", v, "-vn", "-af", f"silencedetect=n={SIL_DB}dB:d={SIL_S}", "-f", "null", "-"],
                       capture_output=True, text=True)
    ini = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", r.stderr)]
    fin = [(float(a), float(b)) for a, b in re.findall(r"silence_end: ([\d.]+) \| silence_duration: ([\d.]+)", r.stderr)]
    return [(max(0, e - d), e, d) for e, d in fin]


def transcribir(v, lex=None):
    """[(palabra, inicio, fin)] con faster-whisper. Se le pasan como contexto los nombres de personaje y de las apps
    (lexico_control.json «contexto_whisper»; hotwords si la versión lo admite, si no initial_prompt): solo nombres, nunca el guion."""
    import inspect
    from faster_whisper import WhisperModel
    m = WhisperModel("small", device="cpu", compute_type="int8")
    ctx = str((lex or LEXICO).get("contexto_whisper") or "").strip()
    kw = {}
    if ctx:
        try:
            kw = {"hotwords": ctx} if "hotwords" in inspect.signature(m.transcribe).parameters else {"initial_prompt": ctx}
        except (TypeError, ValueError):
            kw = {"initial_prompt": ctx}
    seg, _ = m.transcribe(v, language="es", beam_size=5, word_timestamps=True, vad_filter=False, **kw)
    return [(w.word.strip(), w.start, w.end) for s in seg for w in s.words]


def texto_de(pal):
    """Texto de la transcripción. Whisper parte «70%» en «70» y «%» y «9,90» en «9» y «,90»: se pega lo que no empieza por letra."""
    out = ""
    for w, _, _ in pal:
        out += (w if (out and re.match(r"[%,.:€$ºª°)]", w)) else " " + w)
    return out.strip()


def verificar(guion_txt, texto, lex=None):
    """Compara el guion con lo que oyó Whisper (ambos normalizados). Devuelve (faltan, sobran). Se usa en control() y en las pruebas."""
    esp, got = unir(norm(guion_txt, lex), norm(texto, lex))
    return comparar(esp, got)


SIL_PROMO = 1.5          # silencio máximo entre frases en promos de app (DIRECTIVA §5)
TOLERANCIA_VOZ = 0.03    # fracción de palabras sin pareja cercana que se tolera como aviso


def _distancia(a, b):
    """Levenshtein corto (palabras sueltas)."""
    if abs(len(a) - len(b)) > 2: return 3
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def _quitar_cercanas(faltan, sobran):
    """Empareja cada palabra que falta con una sobrante a 1-2 letras (Whisper oye mal, la voz dijo bien la palabra)."""
    f2, s2 = [], list(sobran)
    for w in faltan:
        lim = 1 if len(w) <= 4 else 2
        k = next((i for i, x in enumerate(s2) if _distancia(_clave(w), _clave(x)) <= lim), None)
        if k is None: f2.append(w)
        else: s2.pop(k)
    return f2, s2


def comparar(esp, got):
    """Palabras esperadas que no aparecen (alineación por LCS tolerante) y palabras sobrantes."""
    n, m = len(esp), len(got)
    L = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            L[i][j] = L[i + 1][j + 1] + 1 if igual(esp[i], got[j]) else max(L[i + 1][j], L[i][j + 1])
    i = j = 0; faltan = []; sobran = []
    while i < n and j < m:
        if igual(esp[i], got[j]): i += 1; j += 1
        elif L[i + 1][j] >= L[i][j + 1]: faltan.append(esp[i]); i += 1
        else: sobran.append(got[j]); j += 1
    return faltan + esp[i:], sobran + got[j:]


def huecos_voz(tramos, wavs):
    """Silencios >= 0,6 s (-45 dB) ENTRE frases, sobre la pista de voz sola (frases en su instante): con música cocida el
    silencedetect del vídeo final nunca los ve. tramos: locucion.json; wavs: un wav por tramo. Lista [[ini, fin, dur]]."""
    import wave
    ent, fil, et, fines = [], [], [], []
    for i, (t, w) in enumerate(zip(tramos, wavs)):
        ms = int(float(t["inicio"]) * 1000 + 120)
        ent += ["-i", w]
        fil.append("[%d:a]aresample=48000,adelay=%d|%d[v%d]" % (i, ms, ms, i)); et.append("[v%d]" % i)
        with wave.open(w) as f:
            fines.append((float(t["inicio"]) + 0.12, float(t["inicio"]) + 0.12 + f.getnframes() / float(f.getframerate())))
    fil.append("%samix=inputs=%d:normalize=0,silencedetect=n=%ddB:d=%s" % ("".join(et), len(et), SIL_DB, SIL_S))
    r = subprocess.run(["ffmpeg", "-nostats", *ent, "-filter_complex", ";".join(fil), "-f", "null", "-"], capture_output=True, text=True, timeout=300)
    ini = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", r.stderr)]
    fin = re.findall(r"silence_end: ([\d.]+) \| silence_duration: ([\d.]+)", r.stderr)
    p0, p1 = min(a for a, _ in fines), max(b for _, b in fines)
    return [[round(a, 2), round(float(e), 2), round(float(d), 2)] for a, (e, d) in zip(ini, fin) if a >= p0 - 0.05 and float(e) <= p1 + 0.05]


def control(video, guion, post=None, tramos=None, wavs=None):
    g = json.load(open(guion, encoding="utf-8")) if isinstance(guion, str) else guion
    bloqueos, avisos = [], []
    d = dur(video)
    if d > DUR_MAX: bloqueos.append(f"dura {d:.1f} s (máximo {DUR_MAX:.0f})")
    esc = g.get("escenas", [])
    guion_txt = " ".join(re.sub(r"\*", "", e.get("voz", "")) for e in esc if e.get("voz"))
    pal = transcribir(video)
    texto = texto_de(pal)
    modo = str(g.get("modo") or "").lower()
    sil_max = SIL_S if modo in ("", "sketch", "dibujo") else SIL_PROMO   # 21/11/2026: promos de app admiten 1,5 s (DIRECTIVA §5)
    if esc:
        # Hay escenas (reel generado por el motor de dibujo): se compara la voz con el guion palabra a palabra.
        # 21/11/2026 (Calidad, orden del dueño «sin cuellos de botella»): el giro (escena «remate») solo se exige en la serie
        # de humor (modo sketch); las promos de app (ANTES/DESPUÉS) no tienen «remate» y se bloqueaban todas en falso.
        if modo in ("", "sketch") and not any(e.get("estilo") == "remate" for e in esc):
            bloqueos.append("falta el giro (escena «remate»)")
        faltan, sobran = verificar(guion_txt, texto)
        malas = [w for w in sobran if w in ("ehm", "eh", "em", "mm", "hmm")]
        if malas: bloqueos.append(f"muletillas «ehm» en la voz: {malas}")
        if faltan or sobran:
            # 21/11/2026: diferencias de una o dos letras («tarjeta»/«tarjetas», «apruebas»/«aprueba», «pego»/«fego») son
            # errores típicos de Whisper, no de la voz: cuentan como aviso. Solo bloquea lo que queda sin pareja cercana
            # si pasa del 3 % de las palabras del guion (frase cambiada, palabra inventada o cortada).
            f2, s2 = _quitar_cercanas(faltan, sobran)
            tasa = (len(f2) + len(s2)) / max(1, len(norm(guion_txt)))
            msg = f"voz distinta del guion: faltan {faltan}, sobran {sobran} (rehacer esas frases)"
            (bloqueos if (tasa > TOLERANCIA_VOZ or len(f2) + len(s2) > 3) else avisos).append(msg)
    else:
        # Sin escenas (vídeo externo, p. ej. Neogest Studio): no hay guion con el que comparar la voz ni escenas con estilo
        # «remate», así que exigir el giro o comparar la transcripción contra un guion vacío solo daba falsos bloqueos
        # (toda la transcripción salía como «sobrante»). Se avisa, sin bloquear, y se deja la transcripción para Calidad.
        avisos.append("sin escenas en el guion (vídeo externo): no se exige giro ni se compara la voz con un guion")
    t0 = pal[0][1] if pal else 0.0; t1 = pal[-1][2] if pal else d
    for a, b, s in silencios(video):
        if a >= t0 - 0.05 and b <= t1 + 0.05 and s > sil_max and a > 0.3 and b < d - 0.3:
            bloqueos.append(f"silencio de {s:.2f} s entre {a:.1f} y {b:.1f} s (máximo {sil_max} s)")
    if tramos and wavs:
        try:
            h = [x for x in huecos_voz(tramos, wavs) if x[2] > sil_max]
            if h: bloqueos.append(f"silencios > {sil_max} s entre frases (pista de voz): {h}")
        except Exception as e:
            avisos.append(f"silencedetect de la pista de voz no disponible: {str(e)[-80:]}")
    if isinstance(post, dict) and post.get("musica_atribucion_requerida") and "MacLeod" not in post.get("texto", ""):
        bloqueos.append("falta la atribución musical de Kevin MacLeod en el texto del post")
    return {"aprobado": not bloqueos, "duracion_s": round(d, 2), "bloqueos": bloqueos, "avisos": avisos,
            "transcripcion": texto, "guion": guion_txt}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    sal = sys.argv[sys.argv.index("--salida") + 1] if "--salida" in sys.argv else None
    r = control(sys.argv[1], sys.argv[2])
    if sal: json.dump(r, open(sal, "w"), ensure_ascii=False, indent=1)
    print(json.dumps(r, ensure_ascii=False, indent=1))
    sys.exit(0 if r["aprobado"] else 1)
