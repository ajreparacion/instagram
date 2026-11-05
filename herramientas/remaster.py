#!/usr/bin/env python3
"""Remasterizador de reels ya publicados (@nosabesloquehasvisto).
Uso: python3 remaster.py original.mp4 remaster.json salida.mp4
Reutiliza hacer_reel.py (tarjetas, tipografia, HUD, grano, musica). Ver docstring de
main() para el formato del JSON. Escribe tambien <salida_sin_ext>.locucion.json."""
import sys, os, json, math, random, subprocess, tempfile, shutil, time
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hacer_reel as hr
from hacer_reel import W, H, FPS, SR, FFMPEG

FFPROBE = shutil.which("ffprobe") or os.path.join(os.path.dirname(FFMPEG), "ffprobe")
MAX_TRAMO, MAX_TOTAL = 60.0, 75.0

# ---------------------------------------------------------------- utilidades
def probe(path):
    r = subprocess.run([FFPROBE, "-v", "error", "-show_streams", "-show_format", "-of", "json", path],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("ffprobe no puede leer %s: %s" % (path, r.stderr.strip()))
    j = json.loads(r.stdout)
    v = next((s for s in j["streams"] if s["codec_type"] == "video"), None)
    if v is None: sys.exit("el original no tiene pista de video")
    has_a = any(s["codec_type"] == "audio" for s in j["streams"])
    w, h = int(v["width"]), int(v["height"])
    try:
        sn, sd = [float(x) for x in v.get("sample_aspect_ratio", "1:1").split(":")]
        sar = sn / sd if sn > 0 and sd > 0 else 1.0
    except Exception:
        sar = 1.0
    rot = 0
    try: rot = int(float(v.get("tags", {}).get("rotate", 0)))
    except Exception: pass
    for sd_ in v.get("side_data_list", []) or []:
        if "rotation" in sd_:
            rot = int(round(float(sd_["rotation"])))
    if abs(rot) % 180 == 90: w, h = h, int(w)       # ffmpeg autorota
    else: w = int(round(w * sar))
    dur = None
    for src in (v.get("duration"), j.get("format", {}).get("duration")):
        try:
            dur = float(src); break
        except Exception: pass
    if not dur: sys.exit("no se puede determinar la duracion del original")
    return w, h, dur, has_a

def even(x): return max(2, int(x) // 2 * 2)

def n_words(s): return len((s or "").split())

def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, **kw)
    if r.returncode != 0:
        sys.exit("ffmpeg fallo:\n" + r.stderr.decode("utf-8", "replace")[-1500:])
    return r

# ---------------------------------------------------------------- tarjetas
def render_card(path, style, texto, nframes, seed, idx, date_s):
    sc = hr.Scene(idx, {"estilo": style, "texto": texto, "visual": ""}, seed, "", nframes, 0)
    noise = hr.build_noise(seed + idx); rg = random.Random(seed + 99 + idx)
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "10",
           "-pix_fmt", "yuv420p", "-r", str(FPS), "-frames:v", str(nframes), path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(nframes):
        p.stdin.write(hr.render_frame(fi, [sc], noise, date_s, "", rg).tobytes())
    p.stdin.close()
    if p.wait() != 0: sys.exit("ffmpeg fallo al renderizar tarjeta")

def render_cards(path, specs, seed, idx0, date_s):
    """Varias tarjetas seguidas en un solo mp4. specs: [(estilo, texto, nframes), ...]"""
    scenes, start = [], 0
    for k, (style, texto, nf) in enumerate(specs):
        scenes.append(hr.Scene(idx0 + k, {"estilo": style, "texto": texto, "visual": ""}, seed, "", nf, start))
        start += nf
    noise = hr.build_noise(seed + idx0); rg = random.Random(seed + 99 + idx0)
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "10",
           "-pix_fmt", "yuv420p", "-r", str(FPS), "-frames:v", str(start), path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(start):
        p.stdin.write(hr.render_frame(fi, scenes, noise, date_s, "", rg).tobytes())
    p.stdin.close()
    if p.wait() != 0: sys.exit("ffmpeg fallo al renderizar tarjetas del cierre")

# ---------------------------------------------------------------- overlays (HUD + rotulos)
class _Dummy: style = "cierre"

def static_overlay(path):
    """Escaneo + vineta sutil (RGBA)."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    a = np.clip((r - 0.75) / 0.9, 0, 1) ** 1.6 * 110
    a = np.maximum(a, np.where(yy % 4 == 0, 26, 0))
    arr = np.zeros((H, W, 4), np.uint8); arr[..., 3] = a.astype(np.uint8)
    Image.fromarray(arr, "RGBA").save(path, compress_level=1)

def rotulo_layer(texto):
    f, size, lines = hr.wrap_fit(texto, hr.FONT_PATHS["evidencia"], maxw=W - 2 * hr.SAFE_L - 90, maxlines=3, smax=74, smin=40)
    lh = int(size * 1.2); stroke = max(5, size // 14)
    probe_d = ImageDraw.Draw(Image.new("L", (4, 4)))
    tw = max(probe_d.textlength(l, font=f) for l in lines)
    bw, bh = int(tw + 80), len(lines) * lh + 50
    cy = 1290
    top = min(max(cy - bh // 2, 1100), 1450 - bh)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    x0 = (W - bw) // 2
    d.rounded_rectangle([x0, top, x0 + bw, top + bh], 18, fill=(0, 0, 0, 150))
    for i, l in enumerate(lines):
        d.text((W // 2, top + 25 + i * lh + lh // 2 - 2), l, font=f, anchor="mm", fill=(255, 255, 255, 255),
               stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    return layer

def hud_layer(t_abs, date_s):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hr.hud(ImageDraw.Draw(layer, "RGBA"), _Dummy, t_abs, date_s, "")
    al = layer.getchannel("A").point(lambda v: int(v * 0.72))   # sutil
    layer.putalpha(al)
    return layer

def build_overlay_list(tmp, mid_dur, nmid, hook_dur, date_s, rotulos):
    """Secuencia de PNG (concat demuxer) con HUD + rotulo activo. Devuelve ruta de la lista."""
    cuts = {0.0, nmid / FPS}
    k0 = math.ceil(hook_dur * 2 + 1e-9)
    k = k0
    while k / 2 - hook_dur < nmid / FPS - 1e-6:
        cuts.add(round(k / 2 - hook_dur, 6)); k += 1
    for r in rotulos:
        cuts.add(r["i"]); cuts.add(r["f"])
    cuts = sorted(c for c in cuts if 0 <= c <= nmid / FPS + 1e-9)
    cache, lines, last = {}, [], None
    rl = {}
    for a, b in zip(cuts, cuts[1:]):
        if b - a < 1e-4: continue
        mid_t = (a + b) / 2
        ta = hook_dur + mid_t
        act = next((i for i, r in enumerate(rotulos) if r["i"] <= mid_t < r["f"]), -1)
        key = (int(ta * 2), act)
        if key not in cache:
            lay = hud_layer(ta, date_s)
            if act >= 0:
                if act not in rl: rl[act] = rotulo_layer(rotulos[act]["texto"])
                lay = Image.alpha_composite(lay, rl[act])
            p = os.path.join(tmp, "ov_%d_%d.png" % key)
            lay.save(p, compress_level=1); cache[key] = p
        lines.append("file '%s'\nduration %.6f" % (cache[key], b - a)); last = cache[key]
    lines.append("file '%s'" % last)
    lst = os.path.join(tmp, "ov.txt")
    open(lst, "w").write("\n".join(lines) + "\n")
    return lst

# ---------------------------------------------------------------- audio
def hits_track(n, times, seed):
    """Golpe + whoosh (mismo diseno que hacer_reel, variante no-giro) en cada transicion."""
    rg = np.random.default_rng(seed + 3)
    out = np.zeros((n, 2))
    dur = 0.6; m = int(dur * SR); tt = np.arange(m) / SR
    for t0 in times:
        x = rg.standard_normal(m)
        w = hr.lowpass_sweep(x, 0.02, 0.35)
        env = np.sin(np.pi * np.minimum(1, (tt / dur) ** 0.7)) ** 2
        f = 40 + 110 * np.exp(-tt * 12)
        th = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 7)
        sig = w * env * 0.75 * 1.6 + th * 0.6 + th * 0.4
        i0 = int(round(t0 * SR)); i1 = min(n, i0 + m)
        if i0 >= n: continue
        out[i0:i1, 0] += sig[:i1 - i0]; out[i0:i1, 1] += sig[:i1 - i0] * 0.92
    pk = np.abs(out).max()
    if pk > 0: out *= 0.42 / pk
    return out

OBJ_LUFS_ORIGINAL = -15.0   # nivel del tramo original antes de volumen_original (como la voz nueva)
PICO_MAX_ORIGINAL = 0.85    # sin forzar el limitador: la ganancia no pasa de este pico

def gain_original(a):
    """Ganancia para que el tramo original suene parecido al gancho y al cierre (antes podia
    quedar 10-15 dB por debajo si el reel antiguo era flojo, o pegar un salto si era muy fuerte)."""
    if len(a) < int(0.5 * SR): return 1.0
    pk = float(np.abs(a).max())
    if pk < 1e-4: return 1.0
    l = hr.lufs(a)
    if l <= -60: return 1.0
    g = 10 ** ((OBJ_LUFS_ORIGINAL - l) / 20)
    g = min(g, PICO_MAX_ORIGINAL / pk, 10 ** (18 / 20))   # como mucho +18 dB
    return max(g, 10 ** (-20 / 20))

def original_audio(path, inicio, dur, has_a, nsamp, vol):
    out = np.zeros((nsamp, 2))
    if not has_a or vol <= 0: return out
    r = subprocess.run([FFMPEG, "-v", "error", "-ss", "%.3f" % inicio, "-t", "%.3f" % dur, "-i", path, "-vn",
                        "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True)
    a = np.frombuffer(r.stdout, "<f4").reshape(-1, 2).astype(np.float64) if r.stdout else np.zeros((0, 2))
    k = min(len(a), nsamp); a = a[:k]
    a = a * gain_original(a)
    out[:k] = a * vol
    e = int(0.01 * SR)
    if nsamp > 2 * e:
        out[:e] *= np.linspace(0, 1, e)[:, None]; out[-e:] *= np.linspace(1, 0, e)[:, None]
    return out

def build_audio(path_out, orig, inicio, mid_dur, has_a, vol, musica, seed, nh, nm, nc, extra_hits=()):
    total = (nh + nm + nc) / FPS
    n = int(round(total * SR)); t = np.arange(n) / SR
    th, tm = nh / FPS, (nh + nm) / FPS
    st = np.zeros((n, 2))
    i0 = int(round(th * SR)); nm_s = int(round(nm / FPS * SR))
    st[i0:i0 + nm_s] += original_audio(orig, inicio, nm / FPS, has_a, min(nm_s, n - i0), vol)[:n - i0]
    info = None
    if musica:
        mL, mR, cutg, info = hr.make_music([], n, seed, None, th)
        mus = np.stack([mL, mR], 1)
        mus *= 10 ** ((-24 - hr.lufs(mus)) / 20)
        g = np.ones(n) * 10 ** (-6 / 20)       # bajo el original: -30 LUFS aprox.
        ramp = 0.3
        g = np.where(t < th - ramp, 1.0, g) if True else g
        env = np.interp(t, [0, th - ramp, th + ramp, tm - ramp, tm + ramp, total + 1],
                        [1, 1, 10 ** (-6 / 20), 10 ** (-6 / 20), 1, 1])
        st += mus * env[:, None]
    st += hits_track(n, [0.0, th, tm] + list(extra_hits), seed)
    fade = np.minimum(1, np.minimum(t / 0.3, (total - t) / 0.9))
    st *= fade[:, None]
    with open(path_out, "wb") as fh: fh.write(st.astype("<f4").tobytes())
    return total, info

# ---------------------------------------------------------------- principal
def main():
    """remaster.json: semilla, gancho{texto,voz,duracion}, recorte{inicio,fin}, rotulos[{inicio,fin,texto}],
    cierre{texto,voz,duracion} o cierre{partes:[{texto,voz,estilo?,duracion?}, ...]} (varias tarjetas
    seguidas, cada una con su voz: cambio visual cada pocos segundos), musica(bool), volumen_original(float).
    Estilos por defecto de las partes: la primera "giro", las intermedias "evidencia", la ultima "cierre"."""
    if len(sys.argv) < 4:
        print("Uso: python3 remaster.py original.mp4 remaster.json salida.mp4"); sys.exit(1)
    t_start = time.time()
    src, jpath, out = sys.argv[1:4]
    cfg = json.load(open(jpath, encoding="utf-8"))
    seed = int(cfg.get("semilla", 1))
    g = cfg.get("gancho") or {}; c = cfg.get("cierre") or {}
    rec = cfg.get("recorte") or {}
    musica = bool(cfg.get("musica", True)); vol = float(cfg.get("volumen_original", 1.0))
    w, h, dur, has_a = probe(src)

    # --- duraciones
    def card_dur(d, default):
        base = float(d.get("duracion") or default)
        voz = (d.get("voz") or "").strip()
        if voz: base = max(base, n_words(voz) / 2.6 + 0.4)
        return int(math.ceil(base * FPS - 1e-6))
    nh = card_dur(g, 2.5)
    partes = [p for p in (c.get("partes") or []) if (p.get("texto") or p.get("voz") or "").strip()]
    if partes:
        cspecs = []
        for k, p in enumerate(partes):
            est = p.get("estilo") or ("cierre" if k == len(partes) - 1 else ("giro" if k == 0 else "evidencia"))
            cspecs.append((est, p.get("texto", ""), card_dur(p, 2.5), (p.get("voz") or "").strip()))
    else:
        cspecs = [("cierre", c.get("texto", ""), card_dur(c, 3.0), (c.get("voz") or "").strip())]
    nc = sum(s[2] for s in cspecs)
    inicio = max(0.0, float(rec.get("inicio") or 0.0))
    fin = rec.get("fin"); fin = dur if fin is None else min(float(fin), dur)
    mid_dur = min(fin - inicio, MAX_TRAMO, MAX_TOTAL - (nh + nc) / FPS)
    if mid_dur <= 0.2: sys.exit("el recorte queda vacio (inicio=%.2f, duracion original=%.2f)" % (inicio, dur))
    nm = int(round(mid_dur * FPS)); mid_dur = nm / FPS

    rr = random.Random(seed)
    date_s = "%02d/%02d/%d" % (rr.randint(1, 28), rr.randint(1, 12), rr.randint(1994, 2007))
    rotulos = []
    for r in cfg.get("rotulos") or []:
        a, b = float(r.get("inicio", 0)), min(float(r.get("fin", mid_dur)), mid_dur)
        if (r.get("texto") or "").strip() and b - a > 0.05 and a < mid_dur:
            rotulos.append({"i": max(0.0, a), "f": b, "texto": r["texto"].strip()})

    # --- locucion (solo gancho y cierre)
    loc = []
    if (g.get("voz") or "").strip():
        loc.append({"inicio": 0.0, "duracion": round(nh / FPS, 3), "texto": g["voz"].strip()})
    f0, cut_times = nh + nm, []
    for k, (_, _, nf, voz) in enumerate(cspecs):
        if k: cut_times.append(f0 / FPS)
        if voz: loc.append({"inicio": round(f0 / FPS, 3), "duracion": round(nf / FPS, 3), "texto": voz})
        f0 += nf
    with open(os.path.splitext(out)[0] + ".locucion.json", "w", encoding="utf-8") as fh:
        json.dump(loc, fh, ensure_ascii=False, indent=1)

    tmp = tempfile.mkdtemp(prefix="remaster_")
    try:
        t0 = time.time()
        hook_mp4, close_mp4 = os.path.join(tmp, "h.mp4"), os.path.join(tmp, "c.mp4")
        render_card(hook_mp4, "gancho", g.get("texto", ""), nh, seed, 0, date_s)
        render_cards(close_mp4, [(s[0], s[1], s[2]) for s in cspecs], seed, 1, date_s)
        t_cards = time.time() - t0
        sp = os.path.join(tmp, "static.png"); static_overlay(sp)
        lst = build_overlay_list(tmp, mid_dur, nm, nh / FPS, date_s, rotulos)
        wav = os.path.join(tmp, "a.f32")
        ta = time.time()
        total, info = build_audio(wav, src, inicio, mid_dur, has_a, vol, musica, seed, nh, nm, nc, cut_times)
        t_audio = time.time() - ta

        # --- filtro del tramo original
        pre = "[1:v]scale=trunc(iw*sar/2)*2:ih,setsar=1,fps=%d,tpad=stop_mode=clone:stop_duration=1,trim=end_frame=%d,setpts=PTS-STARTPTS,format=yuv420p" % (FPS, nm)
        if w / h <= 0.66:   # vertical (~9:16): llenar y recortar
            base = pre + ",scale=%d:%d:force_original_aspect_ratio=increase:flags=bicubic,crop=%d:%d,setsar=1[base]" % (W, H, W, H)
        else:               # horizontal / cuadrado: centrado sobre si mismo desenfocado
            s = min(W / w, H / h); fw, fh = even(w * s), even(h * s)
            base = (pre + ",split=2[a][b];"
                    "[a]scale=%d:%d:force_original_aspect_ratio=increase,crop=%d:%d,scale=270:480,gblur=sigma=6,"
                    "scale=%d:%d:flags=bicubic,eq=brightness=-0.24:saturation=0.8[bg];"
                    "[b]scale=%d:%d:flags=bicubic,setsar=1[fg];"
                    "[bg][fg]overlay=(W-w)/2:(H-h)/2:format=yuv420[base]") % (W, H, W, H, W, H, fw, fh)
        fc = (base + ";"
              "[3:v]format=rgba[sc];[4:v]fps=%d,format=rgba[ov];"
              "[base][sc]overlay=0:0:format=auto[b1];[b1][ov]overlay=0:0:format=auto,"
              "noise=alls=9:allf=t,format=yuv420p,setsar=1,trim=end_frame=%d,setpts=PTS-STARTPTS[mid];"
              "[0:v]fps=%d,setpts=PTS-STARTPTS,format=yuv420p,setsar=1[hk];"
              "[2:v]fps=%d,setpts=PTS-STARTPTS,format=yuv420p,setsar=1[cl];"
              "[hk][mid][cl]concat=n=3:v=1:a=0[v];"
              "[5:a]alimiter=limit=0.8:level=false:attack=5:release=60,aresample=44100[a]") % (FPS, nm, FPS, FPS)
        cmd = [FFMPEG, "-y", "-loglevel", "error", "-i", hook_mp4,
               "-ss", "%.3f" % inicio, "-t", "%.3f" % (mid_dur + 0.5), "-i", src,
               "-i", close_mp4,
               "-loop", "1", "-framerate", str(FPS), "-t", "%.3f" % (mid_dur + 0.5), "-i", sp,
               "-f", "concat", "-safe", "0", "-i", lst,
               "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", wav,
               "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-maxrate", "5M", "-bufsize", "10M",
               "-pix_fmt", "yuv420p", "-r", str(FPS), "-frames:v", str(nh + nm + nc),
               "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-ac", "2", "-t", "%.3f" % total,
               "-movflags", "+faststart", out]
        tf = time.time()
        run(cmd)
        print("OK %s (%.1fs, gancho %.1fs + tramo %.1fs + cierre %.1fs) | tarjetas %.1fs, audio %.1fs, ffmpeg %.1fs, total %.1fs"
              % (out, total, nh / FPS, mid_dur, nc / FPS, t_cards, t_audio, time.time() - tf, time.time() - t_start))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    main()
