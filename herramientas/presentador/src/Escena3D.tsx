// Capa 3D: presentadora + Bit + cámara. Todo se calcula a partir del número de fotograma (Remotion puede
// renderizar los fotogramas en cualquier orden y en varias pestañas a la vez), como en claude-animated-shorts.
import React, { useMemo } from "react";
import * as THREE from "three";
import { useCurrentFrame } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { useThree } from "@react-three/fiber";
import { Plan, Escena, escenaEn, clamp, suave, salidaAtras, azar, pulso } from "./plan";
import { Presentadora, EstadoPresentadora } from "./personajes/presentadora";
import { Bit, EstadoBit } from "./personajes/bit";

const FOV = 30;
const TAN = Math.tan((FOV / 2) * (Math.PI / 180));
const PLANOS: Record<string, { mira: [number, number, number]; alto: number }> = {
  medio: { mira: [0, 1.63, 0], alto: 0.8 },
  primer: { mira: [0, 1.74, 0], alto: 0.55 },
  abajo: { mira: [0, 2.25, 0], alto: 0.78 },
  lejos: { mira: [0, 1.45, 0], alto: 1.05 },
};

const parpadeoEn = (tg: number, semilla: number) => {
  const per = 2.9;
  const k = Math.floor(tg / per);
  for (const kk of [k, k - 1]) {
    const ini = kk * per + azar(kk * 7.3 + semilla) * 1.6;
    const d = (tg - ini) * 30;
    if (d >= 0 && d < 5) return [0.5, 1, 1, 0.6, 0.2][Math.floor(d)];
  }
  return 0;
};

const ritmoEn = (e: Escena, f: number) => {
  let r = 0;
  for (const w of e.palabras) if (w.clave) r = Math.max(r, pulso(f, w.a - 2, 9));
  return r;
};

function estadoPresentadora(plan: Plan, f: number): EstadoPresentadora {
  const i = escenaEn(plan, f);
  const e = plan.escenas[i];
  const prev = i > 0 ? plan.escenas[i - 1] : { ...e, presentador: "manos" };
  const t = (f - e.a) / 30;
  const tg = f / 30;
  const boca = plan.boca[f] ?? 0;
  let mirar: [number, number] = [0.08 * Math.sin(tg * 0.7), 0.05 * Math.sin(tg * 0.5)];
  if (e.presentador === "senala" || e.presentador === "senala_arriba") mirar = [e.lado * 0.7, 0.25];
  else if (e.presentador === "movil") mirar = [0, -0.7];
  else if (e.presentador === "piensa") mirar = [-e.lado * 0.6, 0.75];
  else if (e.elemento && e.plano === "abajo") {
    // mira la maqueta cuando aparece y vuelve a cámara
    const fe = e.elemento.f;
    const k = clamp((f - fe) / 6) * (1 - clamp((f - fe - 30) / 8));
    mirar = [0.15 * k, 0.85 * k];
  }
  const bocaS = ((plan.boca[f - 1] ?? 0) + boca * 2 + (plan.boca[f + 1] ?? 0)) / 4;
  return {
    poseA: prev.presentador,
    poseB: e.presentador,
    mezcla: salidaAtras(clamp((f - e.a) / 9), 1.4),
    ladoA: prev.lado || 1,
    lado: e.lado || 1,
    t,
    tg,
    expresion: e.expresion || "habla",
    boca,
    parpadeo: parpadeoEn(tg, 1),
    mirar,
    cabeceo: bocaS * 0.5 - 0.15 + ritmoEn(e, f) * 0.6,
    ritmo: ritmoEn(e, f),
  };
}

const CARA_BIT: Record<string, string> = {
  entra: "feliz", sorpresa: "sorpresa", celebra: "estrella", asiente: "feliz", corazon: "corazon", piensa: "piensa",
  saluda: "feliz", senala: "normal", salta: "risa", gira: "feliz", asoma: "guino", flota: "normal", habla: "habla",
};

function estadoBit(plan: Plan, f: number): EstadoBit {
  const i = escenaEn(plan, f);
  const e = plan.escenas[i];
  const t = (f - e.a) / 30;
  const tg = f / 30;
  const accion = e.bit || "flota";
  const plano = PLANOS[e.plano] ? e.plano : "medio";
  const pres = e.presentador;
  const ladoBit = (e.lado > 0 && ["senala", "senala_arriba", "saluda", "presenta", "idea", "pulgar"].includes(pres)) ? -1 : 1;
  const base = new THREE.Vector3(ladoBit * 0.31, 1.9, 0.16);
  if (plano === "primer") base.set(ladoBit * 0.215, 2.03, 0.26);
  if (plano === "lejos") base.set(ladoBit * 0.4, 1.86, 0.12);
  if (plano === "abajo") base.set(ladoBit * 0.31, 1.98, 0.18);
  const est: EstadoBit = {
    visible: accion !== "oculto",
    pos: base.clone(),
    escala: plano === "primer" ? 0.064 : 0.085,
    giroY: -ladoBit * 0.35 + 0.15 * Math.sin(tg * 1.3),
    giroZ: 0.12 * Math.sin(tg * 2.2),
    giroX: 0.05 * Math.sin(tg * 1.7),
    aplasta: 0,
    cara: e.bit_cara || CARA_BIT[accion] || "normal",
    parpadeo: parpadeoEn(tg, 5),
    habla: 0,
    manos: [0, 0],
    t: tg,
  };
  // flotar siempre
  est.pos.y += 0.022 * Math.sin(tg * 2 * Math.PI / 1.7);
  est.pos.x += 0.008 * Math.sin(tg * 1.1);
  const fr = f - e.a;
  switch (accion) {
    case "entra": {
      const k = salidaAtras(clamp(fr / 14), 1.6);
      est.pos.x = base.x + (1 - k) * ladoBit * 1.2;
      est.pos.y += (1 - k) * 0.25;
      est.giroY += (1 - clamp(fr / 16)) * Math.PI * 2 * ladoBit;
      break;
    }
    case "sale": {
      const k = suave((f - (e.b - 14)) / 14);
      est.pos.x = base.x + k * ladoBit * 1.3;
      est.giroY += k * Math.PI * 2;
      break;
    }
    case "salta":
    case "celebra": {
      const ph = (t * 2.4) % 1;
      const n = Math.floor(t * 2.4);
      if (n < 3) {
        est.pos.y += 0.11 * Math.sin(Math.PI * ph);
        est.aplasta = ph < 0.12 ? -0.25 * (1 - ph / 0.12) : 0.12 * Math.sin(Math.PI * ph);
      }
      if (accion === "celebra") { est.giroY += Math.PI * 2 * suave(t / 0.7); est.manos = [0.6, 0.6]; }
      break;
    }
    case "gira":
      est.giroY += Math.PI * 2 * suave(t / 0.6);
      break;
    case "sorpresa": {
      const k = salidaAtras(clamp(fr / 8), 2.2);
      est.pos.y += 0.07 * k;
      est.pos.z -= 0.06 * k;
      est.aplasta = 0.22 * pulso(fr, 0, 10);
      break;
    }
    case "asiente":
      est.giroX += 0.32 * Math.sin(t * 14) * (1 - clamp(t / 1.0));
      break;
    case "senala":
      est.manos = ladoBit > 0 ? [0.45, 0] : [0, 0.45];
      est.giroY = -ladoBit * 0.7;
      break;
    case "saluda":
      est.manos = [0, 0.55 + 0.25 * Math.sin(t * 12)];
      break;
    case "corazon":
      est.escala *= 1 + 0.08 * Math.max(0, Math.sin(t * 9));
      break;
    case "asoma": {
      const k = salidaAtras(clamp(fr / 12), 1.5);
      est.pos.set(0.36, 1.05 + 0.5 * k, 0.4);
      break;
    }
    case "habla":
      est.habla = Math.abs(Math.sin(t * 13));
      break;
  }
  // aparición en el primer corte en que sale (si en la escena anterior estaba oculto)
  const prev = i > 0 ? plan.escenas[i - 1] : null;
  if (accion !== "entra" && accion !== "oculto" && (!prev || prev.bit === "oculto" || prev.bit === "sale")) {
    est.escala *= salidaAtras(clamp(fr / 8), 2);
  }
  return est;
}

class Mundo {
  raiz = new THREE.Group();
  nea = new Presentadora();
  bit = new Bit();
  constructor() {
    const hemi = new THREE.HemisphereLight("#ffffff", "#9c8fc0", 1.1);
    const llave = new THREE.DirectionalLight("#fff3e2", 2.6);
    llave.position.set(1.4, 3.0, 3.2);
    const relleno = new THREE.DirectionalLight("#d6e8ff", 0.55);
    relleno.position.set(-2.5, 1.6, 2.0);
    const contra = new THREE.DirectionalLight("#ffffff", 1.2);
    contra.position.set(-0.6, 2.6, -3.0);
    this.raiz.add(hemi, llave, relleno, contra, this.nea.raiz, this.bit.raiz);
  }
  actualizar(plan: Plan, f: number, cam: THREE.PerspectiveCamera) {
    const i = escenaEn(plan, f);
    const e = plan.escenas[i];
    this.nea.raiz.visible = !e.oculto;
    if (!e.oculto) this.nea.actualizar(estadoPresentadora(plan, f));
    this.bit.actualizar(estadoBit(plan, f));
    // cámara: plano por escena + acercamiento lento + golpe de zoom en las palabras clave + sacudidas
    const P = PLANOS[e.plano] ?? PLANOS.medio;
    const dur = Math.max(1, e.b - e.a);
    let dist = P.alto / TAN;
    dist *= 1 - 0.045 * suave((f - e.a) / dur);
    dist *= 1 - 0.04 * ritmoEn(e, f);
    // entrada de cada plano con un pequeño empujón (corte con energía)
    dist *= 1 + 0.035 * (1 - salidaAtras(clamp((f - e.a) / 7), 1.2));
    const mira = new THREE.Vector3(...P.mira);
    let sx = 0, sy = 0;
    for (const g of e.golpes ?? []) {
      const d = f - g;
      if (d >= 0 && d < 8) {
        const a = (1 - d / 8) * 0.018 * (dist / 2.8);
        sx += (d % 2 ? -1 : 1) * a;
        sy += (d % 2 ? 1 : -1) * a * 0.6;
      }
    }
    const giro = e.giro || 0;
    cam.fov = FOV;
    cam.position.set(mira.x + Math.sin(giro) * dist + sx, mira.y + 0.06 + sy, mira.z + Math.cos(giro) * dist);
    cam.lookAt(mira.x + sx, mira.y + sy, mira.z);
    cam.near = 0.05;
    cam.far = 60;
    cam.updateProjectionMatrix();
  }
}

const Contenido: React.FC<{ plan: Plan }> = ({ plan }) => {
  const f = useCurrentFrame();
  const { camera } = useThree();
  const mundo = useMemo(() => new Mundo(), []);
  mundo.actualizar(plan, f, camera as THREE.PerspectiveCamera);
  return <primitive object={mundo.raiz} dispose={null} />;
};

export const Escena3D: React.FC<{ plan: Plan }> = ({ plan }) => (
  <ThreeCanvas
    width={1080}
    height={1920}
    flat
    gl={{ antialias: true, alpha: true, preserveDrawingBuffer: true, powerPreference: "high-performance" }}
    camera={{ fov: FOV, near: 0.05, far: 60, position: [0, 1.66, 2.8] }}
    style={{ position: "absolute", inset: 0 }}
  >
    <Contenido plan={plan} />
  </ThreeCanvas>
);
