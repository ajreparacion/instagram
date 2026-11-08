// Composición principal del modo presentador: fondo plano saturado (cambia en cada corte), capa 3D (Nea y Bit),
// maquetas (móvil, terminal, tarjeta, capturas reales), titular enorme y subtítulos palabra a palabra.
import React, { useEffect, useState } from "react";
import { AbsoluteFill, continueRender, delayRender, staticFile, useCurrentFrame } from "remotion";
import { Plan, Escena, escenaEn, colorFondo, clamp, salidaAtras } from "./plan";
import { Escena3D } from "./Escena3D";
import { ElementoVista } from "./ui/Elementos";

export const TITULAR = "Anton, 'Montserrat', 'Arial Narrow', sans-serif";
export const TEXTO = "Montserrat, 'DejaVu Sans', sans-serif";

const useFuentes = () => {
  const [h] = useState(() => delayRender("fuentes"));
  useEffect(() => {
    const fuentes = [
      new FontFace("Anton", `url(${staticFile("fonts/Anton-Regular.ttf")})`),
      new FontFace("Montserrat", `url(${staticFile("fonts/Montserrat-VF.ttf")})`, { weight: "100 900" }),
    ];
    Promise.all(fuentes.map((ff) => ff.load().then((x) => { document.fonts.add(x); }).catch(() => null)))
      .then(() => continueRender(h));
  }, [h]);
};

const aclarar = (hex: string, k: number) => {
  const n = parseInt(hex.slice(1), 16);
  const r = (n >> 16) & 255, g = (n >> 8) & 255, b = n & 255;
  const f = (c: number) => Math.round(k >= 0 ? c + (255 - c) * k : c * (1 + k));
  return `rgb(${f(r)},${f(g)},${f(b)})`;
};

const Fondo: React.FC<{ e: Escena }> = ({ e }) => {
  const c = colorFondo(e.fondo);
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse 85% 60% at 50% 42%, ${aclarar(c, 0.16)} 0%, ${c} 52%, ${aclarar(c, -0.32)} 100%)`,
      }}
    />
  );
};

// ---------------------------------------------------------------- titular
const partirTitular = (txt: string) => {
  if (txt.includes("|")) return txt.split("|").map((s) => s.trim());
  const pal = txt.split(/\s+/);
  const lineas: string[] = [];
  let l = "";
  for (const p of pal) {
    if ((l + " " + p).trim().length > 13 && l) { lineas.push(l); l = p; } else l = (l + " " + p).trim();
  }
  if (l) lineas.push(l);
  return lineas;
};

const ESTILOS: Record<string, { fondo: string; color: string; borde?: string }> = {
  amarillo: { fondo: "#ffe81a", color: "#111014" },
  cian: { fondo: "#22e3ff", color: "#0b0b12" },
  rosa: { fondo: "#ff4fa3", color: "#ffffff" },
  blanco: { fondo: "transparent", color: "#ffffff" },
  sello: { fondo: "#ffffff", color: "#e5262e", borde: "#e5262e" },
};

const Titular: React.FC<{ e: Escena; f: number; arriba: boolean }> = ({ e, f, arriba }) => {
  if (!e.titular) return null;
  const est = ESTILOS[e.titular_estilo || "amarillo"] ?? ESTILOS.amarillo;
  const lineas = partirTitular(e.titular.toUpperCase());
  const maxc = Math.max(...lineas.map((l) => l.length));
  const base = arriba ? 118 : 158;
  const fs = Math.min(base, Math.floor(900 / Math.max(4, maxc * 0.56)));
  const f0 = e.titular_f ?? e.a;
  const sello = e.titular_estilo === "sello";
  const top = arriba ? 70 : e.plano === "primer" ? 110 : 150;
  return (
    <div style={{ position: "absolute", top, left: 0, right: 0, display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
      {lineas.map((l, k) => {
        const d = f - f0 - k * 3;
        if (d < 0) return null;
        const s = sello ? 2.3 - 1.3 * salidaAtras(clamp(d / 6), 0.8) : 0.35 + 0.65 * salidaAtras(clamp(d / 7), 2.6);
        const rot = sello ? -6 : -2.2 + (k % 2) * 1.6;
        return (
          <div
            key={k}
            style={{
              fontFamily: TITULAR,
              fontSize: fs,
              lineHeight: 1.0,
              color: est.color,
              background: est.fondo,
              padding: est.fondo === "transparent" ? "0 10px" : sello ? "10px 34px 4px" : "6px 26px 0px",
              border: est.borde ? `10px solid ${est.borde}` : undefined,
              borderRadius: sello ? 14 : 6,
              transform: `rotate(${rot}deg) scale(${s})`,
              opacity: sello ? clamp(d / 2) : 1,
              textShadow: est.fondo === "transparent" ? "0 6px 0 rgba(0,0,0,0.35), 0 0 24px rgba(0,0,0,0.25)" : undefined,
              boxShadow: est.fondo !== "transparent" ? "0 10px 0 rgba(0,0,0,0.22)" : undefined,
              letterSpacing: 1,
              whiteSpace: "nowrap",
            }}
          >
            {l}
          </div>
        );
      })}
    </div>
  );
};

// ---------------------------------------------------------------- subtítulos palabra a palabra
const trozos = (e: Escena) => {
  const out: number[][] = [];
  let cur: number[] = [];
  let chars = 0;
  e.palabras.forEach((w, i) => {
    cur.push(i);
    chars += w.t.length + 1;
    const fin = /[.,;:!?…]$/.test(w.t);
    if (cur.length >= 3 || chars > 17 || fin) { out.push(cur); cur = []; chars = 0; }
  });
  if (cur.length) out.push(cur);
  return out;
};

const Subtitulos: React.FC<{ e: Escena; f: number; acento: string; y: number }> = ({ e, f, acento, y }) => {
  if (!e.palabras.length) return null;
  const tr = trozos(e);
  let activo = -1;
  e.palabras.forEach((w, i) => { if (f >= w.a) activo = i; });
  if (activo < 0) {
    if (f < e.palabras[0].a - 3) return null;
    activo = 0;
  }
  const ti = tr.findIndex((t) => t.includes(activo));
  const t = tr[Math.max(0, ti)];
  const f0 = e.palabras[t[0]].a;
  const pop = 0.86 + 0.14 * salidaAtras(clamp((f - f0 + 3) / 5), 2);
  return (
    <div style={{ position: "absolute", top: y, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
      <div
        style={{
          background: "#ffffff",
          borderRadius: 22,
          border: "4px solid #17141f",
          padding: "10px 28px 12px",
          fontFamily: TEXTO,
          fontWeight: 800,
          fontSize: 64,
          lineHeight: 1.1,
          display: "flex",
          gap: 20,
          transform: `scale(${pop})`,
          boxShadow: "0 8px 0 rgba(0,0,0,0.2)",
          maxWidth: 960,
          flexWrap: "wrap",
          justifyContent: "center",
        }}
      >
        {t.map((i) => {
          const w = e.palabras[i];
          const dicha = f >= w.a;
          const color = !dicha ? "#b9b5c6" : w.clave ? acento : "#17141f";
          const s = i === activo ? 1 + 0.08 * (1 - clamp((f - w.a) / 5)) : 1;
          return (
            <span key={i} style={{ color, display: "inline-block", transform: `scale(${s})`, transformOrigin: "50% 60%" }}>
              {w.t}
            </span>
          );
        })}
      </div>
    </div>
  );
};

const Destello: React.FC<{ e: Escena; f: number }> = ({ e, f }) => {
  if (e.flash === undefined) return null;
  const d = f - e.flash;
  if (d < 0 || d > 3) return null;
  return <AbsoluteFill style={{ background: "#ffffff", opacity: [0.92, 0.6, 0.32, 0.12][d] }} />;
};

export const Reel: React.FC<{ plan: Plan }> = ({ plan }) => {
  useFuentes();
  const f = useCurrentFrame();
  const e = plan.escenas[escenaEn(plan, f)];
  const conElemento = !!e.elemento && e.elemento.tipo !== "cierre";
  const arriba = conElemento && e.elemento!.tipo !== "broll";
  const ySub = e.elemento?.tipo === "broll" ? 1440 : e.plano === "abajo" ? 1150 : e.plano === "primer" ? 1350 : 1170;
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      <Fondo e={e} />
      <Escena3D plan={plan} />
      {e.elemento ? <ElementoVista el={e.elemento} e={e} f={f} plan={plan} conTitular={!!e.titular} /> : null}
      <Titular e={e} f={f} arriba={arriba} />
      <Subtitulos e={e} f={f} acento={plan.acento} y={ySub} />
      <Destello e={e} f={f} />
    </AbsoluteFill>
  );
};
