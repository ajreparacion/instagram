#!/usr/bin/env python3
"""Música «viral» sintetizada con numpy (sin muestras ni licencias de terceros): hace de sustituto de la música de
ascensor anterior (colchón de sierras + arpegio de caja de música + bombo solo en los tiempos 1 y 3).

Qué cambia respecto a lo anterior (10/11/2026, queja del dueño: «parece de ascensor, tiene que destacar y ser viral»):
  - GANCHO MELÓDICO FIJO: un motivo de 5-6 notas sincopadas (pentatónica menor) que se repite cada compás y varía cada
    4 compases; suena desde el segundo 0 (nada de intros lentas).
  - Ritmo de géneros que funcionan en reels: «dembow» (reguetón), «phonk» (cencerro + 808 distorsionado + redobles de
    charles) y «house» (bombo en los 4 tiempos, stabs de acordes, palmas).
  - Bombo en TODOS los tiempos, 808 con deslizamiento, caja/palmas en capas, charles a semicorcheas, bombeo (sidechain)
    del bajo y la melodía con el bombo, saturación y sin reverberación larga.
  - Golpes en los cortes: crash + bombo extra en cada corte de escena, subida de caja antes del último tramo y cada
    4 compases, hueco de bajo («stop-time») en el último tiempo de cada 4 compases.

generar(n, sr, beat, fase, cortes, seed, estilo) -> (L, R, info). `beat` en segundos, `fase` = desplazamiento de la rejilla,
`cortes` = instantes de los cortes de escena (s). Devuelve señales float de longitud n (pico ≈ 0,9)."""
import math

import numpy as np

ESTILOS = ("dembow", "phonk", "house")
ALIAS = {"house": "house", "disco": "house", "pop": "house", "dembow": "dembow", "trap": "phonk", "funk": "phonk",
         "phonk": "phonk"}
PENTA = [0, 3, 5, 7, 10]


def _lp(x, fc, sr, orden=2):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1.0 / sr)
    X *= 1.0 / np.sqrt(1.0 + (f / fc) ** (2 * orden))
    return np.fft.irfft(X, len(x))


def _hp(x, fc, sr, orden=2):
    return x - _lp(x, fc, sr, orden)


def _hz(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


def _poner(buf, sig, t0, sr, g=1.0):
    i = int(round(t0 * sr))
    if i >= len(buf) or i + len(sig) <= 0:
        return
    a, b = max(0, i), min(len(buf), i + len(sig))
    buf[a:b] += sig[a - i:b - i] * g


def _saw(f, n, sr, ph=0.0):
    t = np.arange(n) / sr
    return 2.0 * ((t * f + ph) % 1.0) - 1.0


def _sq(f, n, sr):
    return np.sign(np.sin(2 * np.pi * f * np.arange(n) / sr))


# ------------------------------------------------------------------ sonidos
def _bombo(sr, rng, dur=0.42):
    t = np.arange(int(dur * sr)) / sr
    fase = 2 * np.pi * np.cumsum(46 + 170 * np.exp(-t / 0.022)) / sr
    k = np.sin(fase) * np.exp(-t / 0.20)
    k[:int(0.004 * sr)] += rng.uniform(-0.6, 0.6, int(0.004 * sr))
    return np.tanh(k * 2.6) * np.minimum(1, t / 0.0015)


def _caja(sr, rng):
    t = np.arange(int(0.28 * sr)) / sr
    r = _hp(_lp(rng.uniform(-1, 1, len(t)), 9000, sr), 1600, sr) * np.exp(-t / 0.10)
    return np.tanh((r * 1.0 + np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.05) * 0.7) * 1.8)


def _palmas(sr, rng):
    out = np.zeros(int(0.35 * sr))
    for k, d0 in enumerate((0.0, 0.010, 0.021)):
        n = int(0.3 * sr)
        seg = _hp(_lp(rng.uniform(-1, 1, n), 4200, sr), 900, sr) * np.exp(-np.arange(n) / sr / (0.012 if k < 2 else 0.12))
        _poner(out, seg, d0, sr)
    return np.tanh(out * 1.6)


def _hat(sr, rng, abierto=False):
    d = 0.22 if abierto else 0.05
    t = np.arange(int(d * sr)) / sr
    return _hp(rng.uniform(-1, 1, len(t)), 8000, sr) * np.exp(-t / (0.08 if abierto else 0.013))


def _crash(sr, rng):
    t = np.arange(int(0.9 * sr)) / sr
    return _hp(rng.uniform(-1, 1, len(t)), 5500, sr) * np.exp(-t / 0.28)


def _cencerro(sr, f=587.0):
    t = np.arange(int(0.30 * sr)) / sr
    x = _sq(f, len(t), sr) + _sq(f * 1.504, len(t), sr)
    x = _hp(_lp(x, 3800, sr), 450, sr)
    return np.tanh(x * 1.3) * np.exp(-t / 0.085) * np.minimum(1, t / 0.001)


def _sub808(m, dur, sr, desliza=0.0, drive=2.4):
    n = int(dur * sr)
    t = np.arange(n) / sr
    f = _hz(m) * (1 + desliza * np.exp(-t / 0.05))
    s = np.sin(2 * np.pi * np.cumsum(f) / sr)
    return np.tanh(s * drive) * np.minimum(1, t / 0.004) * np.exp(-t / max(0.2, dur * 0.8)) * np.minimum(1, (n - np.arange(n)) / (0.03 * sr))


def _lead(m, dur, sr, brillo=7500.0):
    n = int(dur * sr)
    f = _hz(m)
    s = sum(_saw(f * 2 ** (c / 1200.0), n, sr, ph) for c, ph in ((-11, 0.0), (0, 0.31), (11, 0.62)))
    s = s / 3.0 + 0.5 * np.sin(2 * np.pi * f * np.arange(n) / sr)
    t = np.arange(n) / sr
    env = np.minimum(1, t / 0.003) * np.exp(-t / max(0.08, dur * 0.55)) * np.minimum(1, (n - np.arange(n)) / (0.02 * sr))
    return np.tanh(_lp(s, brillo, sr) * 2.2) * env


def _stab(notas, sr, dur=0.20):
    n = int(dur * sr)
    s = sum(_saw(_hz(m) * 2 ** (c / 1200.0), n, sr) for m in notas for c in (-9, 9))
    t = np.arange(n) / sr
    return np.tanh(_lp(s / len(notas), 3600, sr) * 1.6) * np.minimum(1, t / 0.002) * np.exp(-t / 0.09)


def _subida(sr, dur, rng):
    n = int(dur * sr)
    p = np.arange(n) / n
    r = _hp(rng.uniform(-1, 1, n), 1800, sr) * p ** 2.2
    return r * 0.9


# ------------------------------------------------------------------ motivo (gancho)
def _motivo(rng, estilo):
    """Devuelve [(paso_16, grado_pentatonica, octava, duracion_en_pasos)] para un compás de 16 semicorcheas."""
    plantillas = {
        "dembow": [[0, 3, 6, 8, 10, 14], [0, 2, 3, 6, 10, 11], [0, 3, 4, 8, 11, 14]],
        "phonk": [[0, 2, 4, 6, 8, 12], [0, 3, 6, 7, 10, 12], [0, 4, 6, 8, 10, 14]],
        "house": [[2, 3, 6, 10, 11, 14], [0, 3, 6, 9, 11, 14], [1, 3, 6, 8, 11, 14]],
    }
    pasos = list(plantillas[estilo][rng.integers(len(plantillas[estilo]))])
    g = int(rng.integers(0, 3))
    notas = []
    for i, p in enumerate(pasos):
        g = int(np.clip(g + rng.choice([-2, -1, -1, 0, 1, 1, 2]), 0, 4))
        # la primera y la última nota tienden a la tónica / quinta para que suene «cerrado»
        if i == 0:
            g = int(rng.choice([0, 2]))
        if i == len(pasos) - 1:
            g = int(rng.choice([0, 2, 3]))
        dur = (pasos[i + 1] - p) if i + 1 < len(pasos) else 16 - p
        notas.append((p, g, 0, max(1, min(dur, 3))))
    return notas


# ------------------------------------------------------------------ pieza completa
def generar(n, sr, beat, fase, cortes, seed, estilo="dembow", total=None):
    estilo = ALIAS.get(estilo, estilo)
    if estilo not in ESTILOS:
        estilo = "dembow"
    rng = np.random.default_rng(int(seed) * 7919 + 17)
    total = total if total is not None else n / sr
    paso = beat / 4.0
    barra = 4 * beat
    raiz = 33 + int(rng.integers(0, 12))                    # nota MIDI del bajo (La1 ± tono)
    prog = [[0, 8, 3, 10], [0, 10, 8, 7], [0, 5, 8, 7]][int(rng.integers(0, 3))]
    motivo = _motivo(rng, estilo)
    base_lead = raiz + 36 + (0 if estilo != "house" else 0)  # registro de la melodía
    K, S, H, B, M, C, X = (np.zeros(n) for _ in range(7))
    bombo, caja, palmas = _bombo(sr, rng), _caja(sr, rng), _palmas(sr, rng)
    hh, oh, crash, cenc = _hat(sr, rng), _hat(sr, rng, True), _crash(sr, rng), _cencerro(sr)
    cortes_t = [float(c) for c in (cortes or [])[1:]]
    ultimo_corte = cortes_t[-1] if cortes_t else None
    nb = int((total - fase) / barra) + 2
    kicks = []

    def t_(compas, p16):            # tiempo absoluto de un paso de 16 de un compás
        return fase + compas * barra + p16 * paso

    for c in range(nb):
        t0 = t_(c, 0)
        if t0 > total + 0.1:
            break
        ciclo = c % 4
        raiz_c = raiz + prog[c % len(prog)]
        ultimo_tiempo_vacio = (ciclo == 3)
        # ---- batería
        if estilo == "dembow":
            for b4 in range(4):
                _poner(K, bombo, t_(c, b4 * 4), sr, 1.0); kicks.append(t_(c, b4 * 4))
            for p in (3, 6, 11, 14):                         # dembow 3-3-2
                _poner(S, caja, t_(c, p), sr, 0.85)
            for p in (4, 12):
                _poner(S, palmas, t_(c, p), sr, 0.7)
            for p in range(0, 16, 2):
                _poner(H, hh, t_(c, p), sr, 0.45 if p % 4 == 2 else 0.28)
            if ciclo >= 2:
                for p in (1, 5, 9, 13):
                    _poner(H, hh, t_(c, p), sr, 0.2)
        elif estilo == "phonk":
            patron = [0, 6, 10] if ciclo % 2 == 0 else [0, 3, 6, 11]
            for p in patron:
                _poner(K, bombo, t_(c, p), sr, 1.0); kicks.append(t_(c, p))
            for p in (4, 12):
                _poner(S, palmas, t_(c, p), sr, 0.9); _poner(S, caja, t_(c, p), sr, 0.6)
            for p in range(0, 16, 2):
                _poner(H, hh, t_(c, p), sr, 0.4)
            if ciclo in (1, 3):                              # redoble de charles
                for r in range(6):
                    _poner(H, hh, t_(c, 12 + r * 0.667), sr, 0.28 + 0.05 * r)
        else:  # house
            for b4 in range(4):
                _poner(K, bombo, t_(c, b4 * 4), sr, 1.0); kicks.append(t_(c, b4 * 4))
                _poner(H, oh, t_(c, b4 * 4 + 2), sr, 0.5)
            for p in (4, 12):
                _poner(S, palmas, t_(c, p), sr, 0.95)
            for p in (1, 3, 5, 7, 9, 11, 13, 15):
                _poner(H, hh, t_(c, p), sr, 0.22)
        # ---- bajo (808) siguiendo la raíz del acorde; hueco en el último tiempo de cada 4 compases
        if estilo == "dembow":
            for p, d in ((0, 0.9), (6, 0.45), (8, 0.9), (14, 0.45)):
                if ultimo_tiempo_vacio and p >= 12:
                    continue
                _poner(B, _sub808(raiz_c + 12, d * beat, sr, 0.35), t_(c, p), sr, 0.95)
        elif estilo == "phonk":
            for p, d, dm in ((0, 1.4, 0), (6, 0.7, 0), (10, 1.0, 5 if ciclo % 2 else 0)):
                if ultimo_tiempo_vacio and p >= 12:
                    continue
                _poner(B, _sub808(raiz_c + 12 + dm, d * beat, sr, 0.9, 3.2), t_(c, p), sr, 0.95)
        else:
            for b4 in range(4):
                if ultimo_tiempo_vacio and b4 == 3:
                    continue
                _poner(B, _sub808(raiz_c + 12, 0.42 * beat, sr, 0.0, 2.0), t_(c, b4 * 4 + 2), sr, 0.85)
        # ---- gancho (melodía)
        var = (ciclo == 3)
        for (p, g, _oct, d) in motivo:
            g2 = g
            if var and p >= 10:
                g2 = (g + 2) % 5
            nota = base_lead + PENTA[g2] + (12 if (var and p >= 12) else 0)
            if estilo == "phonk":
                _poner(M, _cencerro(sr, _hz(nota)), t_(c, p), sr, 0.9)
            else:
                _poner(M, _lead(nota, d * paso * 1.05 + 0.04, sr), t_(c, p), sr, 0.8)
        if estilo == "house":                                # stabs de acorde en los contratiempos
            acorde = [raiz_c + 36, raiz_c + 36 + 3, raiz_c + 36 + 7]
            for p in (2, 6, 10, 14):
                _poner(C, _stab(acorde, sr), t_(c, p), sr, 0.38)
        if estilo == "dembow":                               # segunda voz: eco del gancho una octava arriba, suave
            pass
    # ---- golpes en los cortes de escena
    for i, tc in enumerate(cortes_t):
        _poner(X, crash, tc, sr, 0.5)
        _poner(K, bombo, tc, sr, 1.0); kicks.append(tc)
        _poner(X, _sub808(raiz, 0.6, sr, 0.0, 1.5), tc, sr, 0.6)
        if tc == ultimo_corte or i % 3 == 2:                 # subida de caja un compás antes (si cabe)
            ini = tc - barra
            if ini > 0.2:
                _poner(X, _subida(sr, barra, rng), ini, sr, 0.5)
                for r in range(8):
                    _poner(S, caja, tc - barra / 2 + r * barra / 16, sr, 0.35 + 0.08 * r)
    # ---- impacto inicial (segundo 0)
    _poner(X, _sub808(raiz, 0.7, sr, 0.0, 1.6), max(0.0, fase), sr, 0.55)
    _poner(X, crash, max(0.0, fase), sr, 0.35)
    # ---- bombeo (sidechain) con todos los bombos
    duck = np.ones(n)
    kd = 1 - 0.62 * np.exp(-np.arange(int(0.22 * sr)) / sr / 0.075)
    for tk in kicks:
        i0 = int(tk * sr)
        if 0 <= i0 < n:
            i1 = min(n, i0 + len(kd))
            duck[i0:i1] = np.minimum(duck[i0:i1], kd[:i1 - i0])
    B = _lp(B, 500, sr) * duck
    M = M * (0.45 + 0.55 * duck)
    C = C * duck
    # ---- eco corto del gancho (da anchura sin reverberación larga) y estéreo
    retardo = int(0.75 * beat * sr)
    eco = np.zeros(n)
    if retardo < n:
        eco[retardo:] = M[:-retardo] * 0.32
    ancho = np.roll(M + C, int(0.012 * sr))
    mono = K * 0.75 + S * 1.05 + H * 0.9 + B * 0.62 + M * 1.35 + C * 1.15 + X * 0.9
    L = mono + eco * 0.9 + 0.22 * (ancho - (M + C))
    R = mono + eco * 0.5 - 0.22 * (ancho - (M + C))
    pico = max(np.max(np.abs(L)), np.max(np.abs(R)), 1e-9)
    L, R = L / pico, R / pico
    L, R = np.tanh(L * 1.7) / np.tanh(1.7), np.tanh(R * 1.7) / np.tanh(1.7)
    L, R = L * 0.92, R * 0.92
    return L, R, dict(estilo=estilo, bpm=round(60.0 / beat, 2), fase_ms=round(fase * 1000), raiz=raiz,
                      motivo_notas=len(motivo), golpes_en_cortes=len(cortes_t))
