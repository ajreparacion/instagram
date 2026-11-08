// Maquetas del modo presentador: captura real de la app en un móvil, b-roll a pantalla completa, terminal que
// escribe, móvil con chat, tarjeta resumen con checks y pegatina «guárdalo», y cierre con el logo de Neogest Lab.
import React from "react";
import { AbsoluteFill, Img, staticFile } from "remotion";
import { Plan, Escena, Elemento, clamp, salidaAtras, suave } from "../plan";

const TITULAR = "Anton, 'Montserrat', sans-serif";
const TEXTO = "Montserrat, 'DejaVu Sans', sans-serif";
const MONO = "'DejaVu Sans Mono', 'Liberation Mono', monospace";

const entrada = (f: number, f0: number, d = 10, k = 1.8) => salidaAtras(clamp((f - f0) / d), k);

const MarcoMovil: React.FC<{ w: number; h: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ w, h, children, style }) => (
  <div
    style={{
      width: w,
      height: h,
      borderRadius: w * 0.13,
      background: "#14121b",
      padding: w * 0.035,
      boxShadow: "0 30px 60px rgba(0,0,0,0.35), 0 0 0 5px #2c2836 inset",
      border: "5px solid #17141f",
      position: "relative",
      ...style,
    }}
  >
    <div style={{ width: "100%", height: "100%", borderRadius: w * 0.1, overflow: "hidden", position: "relative", background: "#fff" }}>
      {children}
      <div style={{ position: "absolute", top: w * 0.025, left: "50%", width: w * 0.28, height: w * 0.065, marginLeft: -w * 0.14, borderRadius: 40, background: "#14121b" }} />
    </div>
  </div>
);

const Etiqueta: React.FC<{ texto: string }> = ({ texto }) => (
  <div style={{ fontFamily: TEXTO, fontWeight: 700, fontSize: 30, color: "#17141f", background: "#ffffff", borderRadius: 40, padding: "6px 20px", border: "3px solid #17141f" }}>
    {texto}
  </div>
);

const Captura: React.FC<{ el: Elemento; e: Escena; f: number; conTitular: boolean }> = ({ el, e, f, conTitular }) => {
  const k = entrada(f, el.f, 11, 1.6);
  const dur = Math.max(1, e.b - el.f);
  const z = el.zoom ?? [0.5, 0.3, 1.18];
  const p = suave((f - el.f - 8) / Math.max(8, dur - 8));
  const esc = 1 + (z[2] - 1) * p;
  const top = conTitular ? 300 : 150;
  const h = conTitular ? 760 : 900;
  const w = Math.round(h * 0.49);
  return (
    <div style={{ position: "absolute", top, left: 0, right: 0, display: "flex", flexDirection: "column", alignItems: "center", gap: 14, transform: `translateY(${(1 - k) * 900}px) rotate(${(1 - k) * 8 + 1.5 * Math.sin(f / 20)}deg)` }}>
      <MarcoMovil w={w} h={h}>
        {el.src ? (
          <Img
            src={staticFile(el.src)}
            style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "top", transform: `scale(${esc})`, transformOrigin: `${z[0] * 100}% ${z[1] * 100}%` }}
          />
        ) : null}
      </MarcoMovil>
      {el.etiqueta ? <Etiqueta texto={el.etiqueta} /> : null}
    </div>
  );
};

const BRoll: React.FC<{ el: Elemento; e: Escena; f: number }> = ({ el, e, f }) => {
  const dur = Math.max(1, e.b - e.a);
  const p = (f - e.a) / dur;
  const z = el.zoom ?? [0.5, 0.25, 1.12];
  const k = entrada(f, el.f, 8, 1.3);
  if (!el.src) return null;
  return (
    <AbsoluteFill>
      <Img src={staticFile(el.src)} style={{ position: "absolute", inset: -80, width: 1240, height: 2080, objectFit: "cover", filter: "blur(36px) brightness(0.55) saturate(1.3)" }} />
      <div style={{ position: "absolute", top: 150, left: 0, right: 0, display: "flex", flexDirection: "column", alignItems: "center", gap: 18, transform: `scale(${0.85 + 0.15 * k})` }}>
        <MarcoMovil w={620} h={1250}>
          <Img src={staticFile(el.src)} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "top", transform: `scale(${1 + (z[2] - 1) * suave(p)})`, transformOrigin: `${z[0] * 100}% ${z[1] * 100}%` }} />
        </MarcoMovil>
        {el.etiqueta ? <Etiqueta texto={el.etiqueta} /> : null}
      </div>
    </AbsoluteFill>
  );
};

const Terminal: React.FC<{ el: Elemento; f: number; conTitular: boolean }> = ({ el, f, conTitular }) => {
  const k = entrada(f, el.f, 9, 1.5);
  const lineas = el.lineas ?? [];
  const total = lineas.reduce((a, l) => a + l.length, 0);
  const [t0, t1] = el.tipeo ?? [el.f + 6, el.f + 6 + total];
  const n = Math.floor(total * clamp((f - t0) / Math.max(1, t1 - t0)));
  let resto = n;
  const cursor = Math.floor(f / 8) % 2 === 0;
  return (
    <div style={{ position: "absolute", top: conTitular ? 330 : 200, left: 70, right: 70, transform: `translateY(${(1 - k) * -700}px)` }}>
      <div style={{ background: "#0e0c14", borderRadius: 26, border: "5px solid #f2f0f7", boxShadow: "0 24px 50px rgba(0,0,0,0.4)", padding: "18px 30px 34px", minHeight: 360 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 18 }}>
          {["#ff5f57", "#febc2e", "#28c840"].map((c) => <div key={c} style={{ width: 20, height: 20, borderRadius: 10, background: c }} />)}
          <div style={{ flex: 1, textAlign: "center", fontFamily: TEXTO, fontWeight: 600, color: "#8d8a99", fontSize: 26, marginRight: 64 }}>{el.titulo || "Terminal"}</div>
        </div>
        {lineas.map((l, i) => {
          const vis = l.slice(0, Math.max(0, resto));
          const activa = resto > 0 && resto <= l.length;
          resto -= l.length;
          if (!vis.length && i > 0) return null;
          return (
            <div key={i} style={{ fontFamily: MONO, fontSize: 46, lineHeight: 1.3, color: "#f4f2fa", wordBreak: "break-all" }}>
              <span style={{ color: "#3ee07a" }}>$ </span>
              {vis}
              {(activa || (i === lineas.length - 1 && resto >= 0)) && cursor ? <span style={{ background: "#3ee07a", color: "#3ee07a" }}>_</span> : null}
            </div>
          );
        })}
      </div>
    </div>
  );
};

const Chat: React.FC<{ el: Elemento; f: number; conTitular: boolean }> = ({ el, f, conTitular }) => {
  const k = entrada(f, el.f, 11, 1.6);
  const h = conTitular ? 760 : 900;
  const w = Math.round(h * 0.49);
  return (
    <div style={{ position: "absolute", top: conTitular ? 300 : 150, left: 0, right: 0, display: "flex", justifyContent: "center", transform: `translateY(${(1 - k) * 900}px) rotate(${(1 - k) * -8 - 1.2}deg)` }}>
      <MarcoMovil w={w} h={h}>
        <div style={{ position: "absolute", inset: 0, background: "#efe7dc", display: "flex", flexDirection: "column" }}>
          <div style={{ background: "#128c7e", color: "#fff", fontFamily: TEXTO, fontWeight: 700, fontSize: 30, padding: "74px 24px 20px" }}>{el.titulo || "Chat"}</div>
          <div style={{ flex: 1, padding: 18, display: "flex", flexDirection: "column", gap: 14, justifyContent: "flex-end" }}>
            {(el.mensajes ?? []).map((m, i) => {
              const d = f - m.f;
              if (d < 0) return null;
              const s = salidaAtras(clamp(d / 6), 2.2);
              const yo = m.de === "yo";
              return (
                <div key={i} style={{ alignSelf: yo ? "flex-end" : "flex-start", maxWidth: "84%", background: yo ? "#d9fdd3" : "#ffffff", borderRadius: 22, padding: "12px 18px", fontFamily: TEXTO, fontWeight: 600, fontSize: 30, lineHeight: 1.2, color: "#17141f", transform: `scale(${s})`, transformOrigin: yo ? "right bottom" : "left bottom", boxShadow: "0 2px 0 rgba(0,0,0,0.12)" }}>
                  {m.texto}
                </div>
              );
            })}
          </div>
        </div>
      </MarcoMovil>
    </div>
  );
};

const Check: React.FC<{ s: number }> = ({ s }) => (
  <div style={{ width: 52, height: 52, borderRadius: 10, background: "#ffe81a", border: "4px solid #17141f", display: "flex", alignItems: "center", justifyContent: "center", transform: `scale(${s})`, flex: "0 0 auto" }}>
    <svg width="34" height="34" viewBox="0 0 24 24"><path d="M4 12.5l5 5L20 6.5" fill="none" stroke="#17141f" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" /></svg>
  </div>
);

const Tarjeta: React.FC<{ el: Elemento; f: number; conTitular: boolean }> = ({ el, f, conTitular }) => {
  const k = entrada(f, el.f, 10, 1.6);
  const items = el.items ?? [];
  const checks = el.checks ?? items.map((_, i) => el.f + 10 + i * 12);
  const pf = el.pegatina_f ?? (checks[checks.length - 1] ?? el.f) + 10;
  return (
    <div style={{ position: "absolute", top: conTitular ? 330 : 190, left: 60, right: 60, transform: `translateY(${(1 - k) * -900}px) rotate(${-1.2 + (1 - k) * -6}deg)` }}>
      <div style={{ background: "#ffffff", borderRadius: 30, border: "5px solid #17141f", boxShadow: "0 16px 0 rgba(0,0,0,0.25)", padding: "34px 44px 46px", position: "relative" }}>
        <div style={{ fontFamily: TITULAR, fontSize: 92, lineHeight: 1, color: "#17141f", textTransform: "uppercase" }}>{el.titulo}</div>
        <div style={{ height: 12, background: "#ffe81a", borderRadius: 6, margin: "14px 0 26px" }} />
        {items.map((it, i) => {
          const d = f - checks[i];
          const vis = clamp((d + 4) / 4);
          return (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 22, margin: "16px 0", opacity: vis, transform: `translateX(${(1 - vis) * -40}px)` }}>
              <Check s={d < 0 ? 0.001 : salidaAtras(clamp(d / 6), 3)} />
              <div style={{ fontFamily: TEXTO, fontWeight: 800, fontSize: 46, lineHeight: 1.15, color: "#17141f" }}>{it}</div>
            </div>
          );
        })}
        {el.pegatina && f >= pf ? (
          <div style={{ position: "absolute", right: 30, bottom: -34, fontFamily: TEXTO, fontWeight: 900, fontSize: 40, color: "#fff", background: "#ff2f8e", borderRadius: 40, padding: "8px 30px", border: "4px solid #17141f", transform: `rotate(-8deg) scale(${salidaAtras(clamp((f - pf) / 6), 3)})` }}>
            {el.pegatina}
          </div>
        ) : null}
      </div>
      {el.chip ? (
        <div style={{ display: "flex", justifyContent: "flex-start", marginTop: 54 }}>
          <div style={{ fontFamily: TEXTO, fontWeight: 800, fontSize: 32, color: "#17141f", background: "#ffe81a", borderRadius: 40, padding: "8px 26px", border: "4px solid #17141f", transform: `rotate(-2deg) scale(${salidaAtras(clamp((f - pf - 4) / 6), 2)})` }}>{el.chip}</div>
        </div>
      ) : null}
    </div>
  );
};

const Cierre: React.FC<{ el: Elemento; f: number; plan: Plan; conTitular: boolean }> = ({ el, f, plan, conTitular }) => {
  const k = entrada(f, el.f, 12, 1.7);
  return (
    <div style={{ position: "absolute", top: conTitular ? 430 : 260, left: 0, right: 0, display: "flex", flexDirection: "column", alignItems: "center", gap: 22, transform: `scale(${0.4 + 0.6 * k})`, opacity: clamp((f - el.f) / 3) }}>
      <div style={{ borderRadius: 34, overflow: "hidden", border: "6px solid #ffffff", boxShadow: "0 18px 50px rgba(0,0,0,0.45)", width: 640, height: 349, background: "#e9e9ee" }}>
        <Img src={staticFile(plan.marca.logo)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
      </div>
      <div style={{ fontFamily: TEXTO, fontWeight: 800, fontSize: 48, color: "#ffffff", textShadow: "0 4px 0 rgba(0,0,0,0.35)" }}>{plan.marca.firma}</div>
      {el.chip ? <div style={{ fontFamily: TEXTO, fontWeight: 800, fontSize: 34, color: "#17141f", background: "#ffe81a", borderRadius: 40, padding: "8px 28px", border: "4px solid #17141f", transform: "rotate(-2deg)" }}>{el.chip}</div> : null}
    </div>
  );
};

export const ElementoVista: React.FC<{ el: Elemento; e: Escena; f: number; plan: Plan; conTitular: boolean }> = ({ el, e, f, plan, conTitular }) => {
  if (f < el.f) return null;
  switch (el.tipo) {
    case "captura": return <Captura el={el} e={e} f={f} conTitular={conTitular} />;
    case "broll": return <BRoll el={el} e={e} f={f} />;
    case "terminal": return <Terminal el={el} f={f} conTitular={conTitular} />;
    case "movil": return <Chat el={el} f={f} conTitular={conTitular} />;
    case "tarjeta": return <Tarjeta el={el} f={f} conTitular={conTitular} />;
    case "cierre": return <Cierre el={el} f={f} plan={plan} conTitular={conTitular} />;
    default: return null;
  }
};
