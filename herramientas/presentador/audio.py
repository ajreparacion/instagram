#!/usr/bin/env python3
"""Sonido del modo presentador, todo generado por código (numpy; sin muestras ni licencias de terceros).

- musica(): pista con pegada (bombo a negras, palmas, charles, bajo con bombeo, acordes y arpegio), con un golpe de
  platillo en el destello del gancho y redobles antes de los cambios de bloque.
- Efectos: whoosh en cada corte, pop en titulares y maquetas, ding en los checks, teclas, burbujas de chat, boing
  de Bit, golpe de sello y subida (riser) al final del gancho.
- mezclar(): voz + música (ducking de 5 dB como máximo mientras se habla) + efectos, y máster a -14 LUFS con loudnorm
  de ffmpeg en dos pasadas (pico real <= -1,5 dBTP).

La estructura (tabla de eventos -> efectos sintetizados + música original agachada bajo la voz -> máster por
sonoridad) sigue la de templates/audio de «claude-animated-shorts» (Mr omi, MIT); el código es propio.
"""
import json
import os
import re
import subprocess
import wave

import numpy as np

SR = 48000


def ns(t):
    return int(round(t * SR))


def _rng(seed):
    return np.random.default_rng(seed)


def _lp(x, fc):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (f / max(fc, 1)) ** 4)
    return np.fft.irfft(X, len(x))


def _hp(x, fc):
    return x - _lp(x, fc)


def _bp(x, lo, hi):
    return _hp(_lp(x, hi), lo)


def _hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def _poner(buf, sig, t0, g=1.0):
    i = ns(t0)
    if i >= len(buf) or i + len(sig) <= 0:
        return
    a, b = max(0, i), min(len(buf), i + len(sig))
    buf[a:b] += sig[a - i:b - i] * g


def _env(n, ataque=0.004, caida=0.2):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(ataque, 1e-4)) * np.exp(-t / caida)


def _saw(fr, n, ph=0.0):
    t = np.arange(n) / SR
    return 2 * ((t * fr + ph) % 1) - 1


def _filtro_variable(x, fc):
    """paso bajo de un polo con frecuencia de corte variable (fc: array por muestra)"""
    a = 1 - np.exp(-2 * np.pi * np.asarray(fc) / SR)
    y = np.empty_like(x)
    s = 0.0
    for i in range(len(x)):
        s += a[i] * (x[i] - s)
        y[i] = s
    return y


# ---------------------------------------------------------------- efectos
def whoosh(dur=0.42, pico=0.3, f_lo=300, f_hi=3200, semilla=1):
    r = _rng(semilla)
    n = ns(dur)
    t = np.arange(n) / SR
    k = np.where(t < pico, (t / pico) ** 2, np.exp(-(t - pico) / (dur - pico) * 3.5))
    nz = r.uniform(-1, 1, n)
    y = _filtro_variable(nz, f_lo + (f_hi - f_lo) * k)
    y = _hp(y, 180) * k
    return y / (np.abs(y).max() + 1e-9)


def pop(semilla=2, f0=1150, f1=260):
    n = ns(0.09)
    t = np.arange(n) / SR
    fr = f1 + (f0 - f1) * np.exp(-t / 0.018)
    y = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t / 0.03)
    clic = _rng(semilla).uniform(-1, 1, n) * np.exp(-t / 0.002) * 0.4
    return (y + clic) / 1.2


def ding(nota=88, dur=1.0):
    n = ns(dur)
    t = np.arange(n) / SR
    f = _hz(nota)
    y = np.zeros(n)
    for mult, amp, dec in ((1.0, 1.0, 0.45), (2.0, 0.5, 0.25), (2.76, 0.35, 0.18), (5.4, 0.18, 0.08)):
        y += amp * np.sin(2 * np.pi * f * mult * t) * np.exp(-t / dec)
    y *= np.minimum(1, t / 0.002)
    return y / np.abs(y).max()


def tecla(semilla):
    r = _rng(semilla)
    n = ns(0.03)
    t = np.arange(n) / SR
    y = _bp(r.uniform(-1, 1, n), 1500 + r.uniform(0, 1500), 6000) * np.exp(-t / 0.006)
    y += np.sin(2 * np.pi * (180 + r.uniform(0, 60)) * t) * np.exp(-t / 0.01) * 0.5
    return y / (np.abs(y).max() + 1e-9)


def burbuja():
    n = ns(0.16)
    t = np.arange(n) / SR
    fr = np.where(t < 0.06, 880, 1320)
    y = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-((t % 0.06) / 0.04)) * np.minimum(1, t / 0.003)
    return y


def boing(subida=True):
    n = ns(0.38)
    t = np.arange(n) / SR
    f = (260 + 420 * (t / 0.38)) if subida else (620 - 300 * (t / 0.38))
    f = f * (1 + 0.06 * np.sin(2 * np.pi * 22 * t))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16) * np.minimum(1, t / 0.004)
    return y


def golpe(semilla=3):
    r = _rng(semilla)
    n = ns(0.7)
    t = np.arange(n) / SR
    sub = np.sin(2 * np.pi * np.cumsum(40 + 90 * np.exp(-t / 0.05)) / SR) * np.exp(-t / 0.28)
    ruido = _lp(r.uniform(-1, 1, n), 2500) * np.exp(-t / 0.05)
    y = np.tanh((sub * 1.2 + ruido * 0.8) * 1.6)
    return y / np.abs(y).max()


def platillo(semilla=4, dur=1.6):
    r = _rng(semilla)
    n = ns(dur)
    t = np.arange(n) / SR
    y = _hp(r.uniform(-1, 1, n), 5000) * np.exp(-t / 0.55) * np.minimum(1, t / 0.002)
    return y / (np.abs(y).max() + 1e-9)


def riser(dur=0.9, semilla=5):
    r = _rng(semilla)
    n = ns(dur)
    t = np.arange(n) / SR
    k = (t / dur) ** 2
    y = _filtro_variable(r.uniform(-1, 1, n), 300 + 6000 * k) * k
    y += 0.25 * _saw(220 + 660 * k, n) * k
    return y / (np.abs(y).max() + 1e-9)


# ---------------------------------------------------------------- música
ESTILOS = {
    # bpm, modo, progresiones (grados en semitonos desde la tónica)
    "pop": (118, "M", [0, 7, 9, 5]),
    "house": (124, "m", [0, 8, 3, 10]),
    "funk": (112, "m", [0, 5, 0, 7]),
    "electro": (126, "m", [0, 10, 8, 7]),
}


def _acorde(raiz, grado, modo):
    menores = {9, 2, 4} if modo == "M" else {0, 5, 7}
    r = raiz + grado
    while r > raiz + 6:
        r -= 12
    return [r, r + (3 if (grado % 12) in menores else 4), r + 7]


def musica(total, estilo="pop", bpm=None, tono=0, semilla=7, golpes=(), cortes=()):
    """golpes: tiempos (s) con platillo y bombo extra (destello del gancho, sello); cortes: cambios de escena"""
    b, modo, prog = ESTILOS.get(estilo, ESTILOS["pop"])
    bpm = float(bpm or b)
    r = _rng(semilla)
    beat = 60.0 / bpm
    bar = 4 * beat
    n = ns(total + 1.5)
    raiz = 57 + int(tono)
    K, S, H, B, C, L, F = (np.zeros(n) for _ in range(7))
    tk = np.arange(ns(0.42)) / SR
    kick = np.sin(2 * np.pi * np.cumsum(48 + 140 * np.exp(-tk / 0.03)) / SR) * np.exp(-tk / 0.22)
    kick[:80] += np.linspace(1, 0, 80) * r.uniform(-0.6, 0.6, 80)
    kick = np.tanh(kick * 2.3)
    nclap = ns(0.3)
    clap = np.zeros(nclap)
    for j, d0 in enumerate((0.0, 0.008, 0.017)):
        seg = _bp(r.uniform(-1, 1, nclap), 900, 4000) * np.exp(-np.arange(nclap) / SR / (0.01 if j < 2 else 0.1))
        _poner(clap, seg, d0)
    hh = _hp(r.uniform(-1, 1, ns(0.05)), 8000) * np.exp(-np.arange(ns(0.05)) / SR / 0.012)
    oh = _hp(r.uniform(-1, 1, ns(0.22)), 7000) * np.exp(-np.arange(ns(0.22)) / SR / 0.08)
    sn = _bp(r.uniform(-1, 1, ns(0.18)), 1500, 7000) * np.exp(-np.arange(ns(0.18)) / SR / 0.06)

    def pluck(m, dur=0.2):
        k = ns(dur)
        t = np.arange(k) / SR
        f = _hz(m)
        return (np.sin(2 * np.pi * f * t) + 0.45 * np.sin(4 * np.pi * f * t) + 0.3 * _saw(f, k) * np.exp(-t / 0.03)) * np.exp(-t / 0.1)

    nb = int(total / bar) + 2
    for c in range(nb):
        t0 = c * bar
        ac = _acorde(raiz, prog[c % len(prog)], modo)
        rb = ac[0] - 24
        for b4 in range(4):
            _poner(K, kick, t0 + b4 * beat, 1.0)
            _poner(H, oh, t0 + (b4 + 0.5) * beat, 0.4)
            for s16 in (0.25, 0.75):
                _poner(H, hh, t0 + (b4 + s16) * beat, 0.28)
        for b4 in (1, 3):
            _poner(S, clap, t0 + b4 * beat, 0.95)
        if estilo == "funk":
            _poner(K, kick, t0 + 2.75 * beat, 0.7)
        if c % 4 == 3:  # redoble al final de cada bloque de 4 compases
            for j in range(8):
                _poner(S, sn, t0 + 3 * beat + j * beat / 8, 0.25 + 0.5 * j / 8)
        # bajo a contratiempo con bombeo
        for e in range(8):
            if e % 2 == 1 or estilo == "funk":
                m = rb + (12 if (e in (3, 7) and estilo != "house") else 0)
                k = ns(0.42 * beat)
                f = _hz(m)
                sig = (_saw(f, k) * 0.55 + np.sin(2 * np.pi * f * np.arange(k) / SR)) * _env(k, 0.003, 0.25 * beat)
                _poner(B, sig, t0 + e * beat / 2, 0.7)
        # acordes: golpes a contratiempo (supersierra)
        for p in (0.5, 1.5, 2.5, 3.5):
            k = ns(0.24)
            s = sum(_saw(_hz(m + 12) * dt, k) for m in ac for dt in (0.994, 1.0, 1.006))
            _poner(C, s * _env(k, 0.002, 0.09), t0 + p * beat, 0.11)
        # arpegio (desde el segundo compás)
        if c >= 1:
            esc = [ac[0] + 24, ac[1] + 24, ac[2] + 24, ac[0] + 36]
            fig = r.permutation(4)
            for e in range(16):
                if e % 4 == 3 and c % 2:
                    continue
                _poner(L, pluck(esc[fig[e % 4]]), t0 + e * beat / 4, 0.14)
    for g in golpes:
        _poner(F, platillo(int(g * 10)), g, 0.55)
        _poner(K, kick, g, 0.9)
    t = np.arange(n) / SR
    bombeo = 1 - 0.55 * np.exp(-(t % beat) / 0.11)
    B = _lp(B, 700)
    C = _lp(C, 3600)
    Lf = _lp(L, 7000)
    mono = K * 1.0 + S * 0.7 + H * 0.45 + B * bombeo * 0.85 + F * 0.6
    ancho = C * bombeo + Lf
    retr = np.roll(ancho, ns(0.012))
    izq = mono + ancho + 0.3 * (retr - ancho)
    der = mono + ancho - 0.3 * (retr - ancho)
    est = np.stack([izq, der], axis=1)[:ns(total)]
    est /= (np.abs(est).max() + 1e-9)
    est = np.tanh(est * 1.5) / np.tanh(1.5)
    caida = ns(0.8)
    est[-caida:] *= np.linspace(1, 0, caida)[:, None] ** 1.4
    return est


# ---------------------------------------------------------------- utilidades de ffmpeg
def escribir_wav(ruta, x, sr=SR):
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        x = x[:, None]
    with wave.open(ruta, "wb") as w:
        w.setnchannels(x.shape[1])
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())


def leer_wav(ruta, sr=SR):
    """lee cualquier audio (ffmpeg) como mono float a `sr`"""
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", ruta, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype=np.float32).astype(np.float64)


def lufs(ruta):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", ruta, "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    res = r.stderr[r.stderr.rfind("Summary:"):]
    i = float(re.search(r"I:\s+(-?[\d.]+|-inf) LUFS", res).group(1))
    tp = re.search(r"Peak:\s+(-?[\d.]+|-inf) dBFS", res)
    lra = re.search(r"LRA:\s+(-?[\d.]+) LU", res)
    return {"lufs_integrados": i, "pico_real_dbtp": float(tp.group(1)) if tp else None,
            "lra_lu": float(lra.group(1)) if lra else None, "medido_con": "ffmpeg ebur128=peak=true"}


def _lufs_array(x, trabajo, nombre):
    p = os.path.join(trabajo, f"_med_{nombre}.wav")
    escribir_wav(p, x / max(1.0, np.abs(x).max()))
    v = lufs(p)["lufs_integrados"]
    escala = max(1.0, np.abs(x).max())
    return v + 20 * np.log10(escala)


def master(entrada, salida, objetivo=-14.0, pico=-2.0):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", entrada, "-af",
                        f"loudnorm=I={objetivo}:TP={pico}:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    filtro = (f"loudnorm=I={objetivo}:TP={pico}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
              f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", entrada, "-af", filtro, "-ar", str(SR), salida], check=True)


# ---------------------------------------------------------------- mezcla
def efectos(eventos, total):
    """eventos: [(segundos, tipo, ganancia)] -> pista estéreo"""
    S = np.zeros((ns(total + 1), 2))
    for k, (t, tipo, g) in enumerate(eventos):
        if tipo == "whoosh":
            sig, t0 = whoosh(semilla=k + 11), t - 0.3
        elif tipo == "whoosh_corto":
            sig, t0 = whoosh(0.28, 0.16, 600, 5000, semilla=k + 31), t - 0.16
        elif tipo == "pop":
            sig, t0 = pop(k), t
        elif tipo.startswith("ding"):
            nota = int(tipo[4:] or 88)
            sig, t0 = ding(nota), t
        elif tipo == "tecla":
            sig, t0 = tecla(k), t
        elif tipo == "burbuja":
            sig, t0 = burbuja(), t
        elif tipo == "boing":
            sig, t0 = boing(True), t
        elif tipo == "boing_baja":
            sig, t0 = boing(False), t
        elif tipo == "golpe":
            sig, t0 = golpe(k), t
        elif tipo == "riser":
            sig, t0 = riser(), t - 0.9
        else:
            continue
        pan = 0.5 + 0.25 * np.sin(k * 1.7)
        i = ns(t0)
        a, b = max(0, i), min(len(S), i + len(sig))
        if b > a:
            S[a:b, 0] += sig[a - i:b - i] * g * (1 - pan) * 1.4
            S[a:b, 1] += sig[a - i:b - i] * g * pan * 1.4
    return S[:ns(total)]


def envolvente_voz(v, fps=30):
    """apertura de boca por fotograma (0-1) a partir de la voz"""
    hop = SR // fps
    nf = int(np.ceil(len(v) / hop))
    pad = np.zeros(nf * hop)
    pad[:len(v)] = v
    rms = np.sqrt((pad.reshape(nf, hop) ** 2).mean(axis=1) + 1e-12)
    ref = np.percentile(rms[rms > 1e-4], 95) if np.any(rms > 1e-4) else 1.0
    db = 20 * np.log10(rms / ref)
    a = np.clip((db + 28) / 24, 0, 1) ** 0.85
    out = np.zeros_like(a)
    s = 0.0
    for i, x in enumerate(a):
        s = x if x > s else s * 0.55 + x * 0.45  # abre rápido, cierra suave
        out[i] = s
    return out


def mezclar(voz, mus, sfx, trabajo, salida, duck_db=5.0, voz_lufs=-16.0, mus_lufs=-17.0, sfx_rel_db=-3.0):
    """voz: mono (o None); mus, sfx: estéreo. Devuelve informe con las medidas."""
    n = len(mus)
    inf = {}
    if voz is not None and np.abs(voz).max() > 1e-4:
        v = np.zeros(n)
        v[:min(n, len(voz))] = voz[:n]
        gv = 10 ** ((voz_lufs - _lufs_array(v, trabajo, "voz")) / 20)
        v *= gv
        # actividad de la voz (ventanas de 10 ms) suavizada: ataque 40 ms, suelta 350 ms
        hop = SR // 100
        nf = n // hop
        rms = np.sqrt((v[:nf * hop].reshape(nf, hop) ** 2).mean(axis=1) + 1e-12)
        act = (20 * np.log10(rms + 1e-9) > voz_lufs - 26).astype(float)
        sm = np.zeros(nf)
        s = 0.0
        for i, x in enumerate(act):
            s += (x - s) * (0.25 if x > s else 0.03)
            sm[i] = s
        g = np.repeat(sm, hop)
        g = np.concatenate([g, np.full(n - len(g), g[-1] if len(g) else 0)])
        duck = 10 ** (-duck_db * g / 20)
    else:
        v = np.zeros(n)
        duck = np.ones(n)
        g = np.zeros(n)
    m = mus.copy()
    gm = 10 ** ((mus_lufs - _lufs_array(m.mean(axis=1), trabajo, "mus")) / 20)
    m *= gm
    if np.abs(v).max() == 0:
        m *= 10 ** (2.0 / 20)  # sin voz manda la música
    m *= duck[:, None]
    sf = sfx * (10 ** ((mus_lufs + sfx_rel_db - _lufs_array(sfx.mean(axis=1) + 1e-9, trabajo, "sfx")) / 20)) if np.abs(sfx).max() > 0 else sfx
    mezcla = m + sf + v[:, None]
    crudo = os.path.join(trabajo, "mezcla_cruda.wav")
    pk = np.abs(mezcla).max()
    escribir_wav(crudo, mezcla / max(1.0, pk) * 0.98)
    master(crudo, salida)
    # medidas para Calidad: música bajo la voz y entre frases
    hab = g > 0.6
    calla = g < 0.1
    def rms_db(x, mask):
        return float(20 * np.log10(np.sqrt((x[mask] ** 2).mean()) + 1e-12)) if mask.sum() > SR * 0.3 else None
    mm = m.mean(axis=1)
    inf["musica_bajo_voz_db"] = (round(rms_db(mm, hab) - rms_db(v, hab), 1) if rms_db(v, hab) is not None and rms_db(mm, hab) is not None else None)
    inf["ducking_db"] = (round(rms_db(mm, calla) - rms_db(mm, hab), 1) if rms_db(mm, calla) is not None and rms_db(mm, hab) is not None else 0.0)
    inf["ducking_max_db"] = duck_db
    inf.update(lufs(salida))
    return inf
