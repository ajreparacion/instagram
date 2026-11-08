// «Nea», presentadora original de Neogest Lab (no es ninguna persona real): chica de dibujo animado con gafas,
// moño, sudadera amarilla con el monograma NL y cordones cian. Hecha solo con primitivas de three.js, sombreado por
// bandas y contorno de tinta (toon.ts). Brazos con cinemática inversa de dos huesos: cada pose es la posición de la
// muñeca, hacia dónde apunta el codo, hacia dónde mira la palma y cuánto se cierran los dedos.
import * as THREE from "three";
import { conTinta, entre, lerp, malla, plano, toon, v3 } from "./toon";

const PIEL = "#f2c29e";
const PIEL_SOMBRA = "#e4a582";
const PELO = "#3b2219";
const SUDADERA = "#ffbd1f";
const SUDADERA_OSC = "#f0a612";
const VAQUERO = "#2c3c6e";
const CIAN = "#22d3ee";
const GAFAS = "#2a2238";

export type EstadoPresentadora = {
  poseA: string;
  poseB: string;
  mezcla: number;
  ladoA: number;
  lado: number;
  t: number; // segundos dentro de la escena
  tg: number; // segundos globales
  expresion: string;
  boca: number;
  parpadeo: number;
  mirar: [number, number];
  cabeceo: number;
  ritmo: number; // pulso de gesto en las palabras clave
};

type PoseBrazo = { T: THREE.Vector3; polo: THREE.Vector3; palma: THREE.Vector3; dir?: THREE.Vector3; curl: number; indice?: number; pulgar?: number };
type PoseCuerpo = { giro: number; hombros: number; inclina: number; movil: boolean; agacha: number };

const N = (x: number, y: number, z: number) => v3(x, y, z).normalize();

/** pose de un brazo. s = lado del brazo en pantalla (+1 derecha), lider = es la mano que gesticula */
function poseBrazo(nombre: string, s: number, lider: boolean, t: number): PoseBrazo {
  const manos = (): PoseBrazo => ({ T: v3(s * 0.035, 1.06, 0.2), polo: N(s, -0.6, -0.5), palma: N(-s, 0.35, 0.25), curl: 0.6, pulgar: 0.3 });
  const reposo = (): PoseBrazo => ({ T: v3(s * 0.275, 0.99, 0.07), polo: N(s * 0.3, 0, -1), palma: N(-s, 0, 0.25), curl: 0.35, pulgar: 0.5 });
  const barriga = (): PoseBrazo => ({ T: v3(-s * 0.02, 1.1, 0.21), polo: N(s, -0.7, -0.3), palma: N(0, -0.1, -1), dir: N(-s, 0.15, 0.1), curl: 0.25, pulgar: 0.6 });
  switch (nombre) {
    case "reposo":
      return reposo();
    case "explica":
      return lider
        ? { T: v3(s * 0.2, 1.2 + 0.015 * Math.sin(t * 5), 0.3), polo: N(s, -1, -0.3), palma: N(0, 1, 0.3), dir: N(s * 0.35, 0.25, 1), curl: 0.12, pulgar: 0.8 }
        : barriga();
    case "presenta":
      return { T: v3(s * 0.43, 1.2, 0.22), polo: N(s * 0.6, -1, -0.4), palma: N(0, 1, 0.35), dir: N(s, 0.25, 0.4), curl: 0.1, pulgar: 0.9 };
    case "senala":
      return lider
        ? { T: v3(s * 0.5, 1.5 + 0.01 * Math.sin(t * 6), 0.2), polo: N(s * 0.2, -1, -0.4), palma: N(0, -0.6, 0.6), dir: N(s, 0.25, 0.25), curl: 1, indice: 0, pulgar: 0.2 }
        : reposo();
    case "senala_arriba":
      return lider
        ? { T: v3(s * 0.36, 1.66, 0.16), polo: N(s, -1, -0.2), palma: N(0, 0, 1), dir: N(s * 0.35, 1, 0.1), curl: 1, indice: 0, pulgar: 0.2 }
        : reposo();
    case "idea":
      return lider
        ? { T: v3(s * 0.17, 1.5, 0.23), polo: N(s, -1, -0.1), palma: N(-s * 0.2, 0, 1), dir: N(0, 1, 0.12), curl: 1, indice: 0, pulgar: 0.15 }
        : barriga();
    case "saluda": {
      if (!lider) return reposo();
      const w = Math.sin(t * 11) * 0.38;
      return { T: v3(s * 0.34, 1.6, 0.1), polo: N(s, -1, -0.2), palma: N(0, 0, 1), dir: N(s * 0.2 + Math.sin(w) * 0.9, 1, 0), curl: 0.02, pulgar: 1 };
    }
    case "celebra": {
      const b = Math.abs(Math.sin(t * 7 + (s > 0 ? 0.5 : 0))) * 0.04;
      return { T: v3(s * 0.3, 1.84 + b, 0.06), polo: N(s, -0.2, -0.4), palma: N(0, 0, 1), dir: N(s * 0.2, 1, 0), curl: 1, pulgar: 0.2 };
    }
    case "sorpresa":
      return { T: v3(s * 0.28, 1.55, 0.2), polo: N(s, -1, -0.2), palma: N(0, 0, 1), dir: N(s * 0.25, 1, 0.2), curl: 0.0, pulgar: 1 };
    case "encoge":
      return { T: v3(s * 0.36, 1.17, 0.17), polo: N(s * 0.5, -1, -0.5), palma: N(0, 1, 0.25), dir: N(s, 0.2, 0.6), curl: 0.08, pulgar: 0.9 };
    case "pulgar":
      return lider
        ? { T: v3(s * 0.17, 1.3, 0.29), polo: N(s, -1, -0.3), palma: N(-s, 0, 0), dir: N(0, 0.35, 1), curl: 1, pulgar: 1.4 }
        : reposo();
    case "piensa":
      return lider
        ? { T: v3(s * 0.05, 1.53, 0.21), polo: N(s, -1, 0), palma: N(0, 0.2, -1), dir: N(-s * 0.25, 1, 0.3), curl: 0.75, pulgar: 0.5 }
        : { T: v3(s * 0.08, 1.2, 0.21), polo: N(-s, -1, -0.3), palma: N(0, 1, 0), dir: N(-s, 0.1, 0.2), curl: 0.3, pulgar: 0.6 };
    case "preocupada":
      return { T: v3(s * 0.19, 1.665, 0.075), polo: N(s, -1, 0), palma: N(-s, 0, 0.2), dir: N(-s * 0.08, 1, 0.12), curl: 0.12, pulgar: 0.7 };
    case "movil":
      return lider
        ? { T: v3(s * 0.08, 1.33, 0.3), polo: N(s, -1, -0.3), palma: N(0, 0.75, 0.65), dir: N(-s * 0.1, 0.65, -0.75), curl: 0.35, pulgar: 0.4 }
        : { T: v3(-s * 0.0, 1.38, 0.32), polo: N(s, -1, -0.4), palma: N(0, -0.6, -0.4), dir: N(s * 0.3, 0.4, 0.2), curl: 1, indice: 0.1, pulgar: 0.2 };
    case "manos":
    default:
      return manos();
  }
}

function poseCuerpo(nombre: string, lado: number): PoseCuerpo {
  const b: PoseCuerpo = { giro: 0, hombros: 0, inclina: 0, movil: false, agacha: 0 };
  switch (nombre) {
    case "senala": return { ...b, giro: lado * 0.18, inclina: lado * 0.04 };
    case "senala_arriba": return { ...b, giro: lado * 0.1 };
    case "encoge": return { ...b, hombros: 0.035, inclina: 0.06 };
    case "celebra": return { ...b, hombros: 0.02 };
    case "piensa": return { ...b, inclina: -lado * 0.1 };
    case "preocupada": return { ...b, hombros: 0.02, agacha: 0.02 };
    case "movil": return { ...b, movil: true, agacha: 0.03 };
    case "explica": return { ...b, giro: -lado * 0.08 };
    case "presenta": return { ...b, hombros: 0.01 };
    default: return b;
  }
}

const mezclaV = (a: THREE.Vector3, b: THREE.Vector3, k: number) => a.clone().lerp(b, k);
function mezclaBrazo(a: PoseBrazo, b: PoseBrazo, k: number): PoseBrazo {
  const da = a.dir ?? b.dir, db = b.dir ?? a.dir;
  return {
    T: mezclaV(a.T, b.T, k),
    polo: mezclaV(a.polo, b.polo, k).normalize(),
    palma: mezclaV(a.palma, b.palma, k).normalize(),
    dir: da && db ? mezclaV(da, db, k).normalize() : undefined,
    curl: lerp(a.curl, b.curl, k),
    indice: lerp(a.indice ?? a.curl, b.indice ?? b.curl, k),
    pulgar: lerp(a.pulgar ?? 0.5, b.pulgar ?? 0.5, k),
  };
}

// ---------------------------------------------------------------- mano
class Mano {
  raiz = new THREE.Group();
  dedos: THREE.Group[] = [];
  pulgar = new THREE.Group();
  movil = new THREE.Group();
  constructor(private s: number) {
    const piel = toon(PIEL);
    const palma = conTinta(new THREE.SphereGeometry(0.043, 20, 14), piel, 4);
    palma.scale.set(1, 1.1, 0.52);
    palma.position.set(0, 0.045, 0);
    this.raiz.add(palma);
    const dedoGeo = new THREE.CapsuleGeometry(0.0118, 0.032, 4, 10);
    [-0.026, -0.0088, 0.0088, 0.026].forEach((x, i) => {
      const g = new THREE.Group();
      g.position.set(x * 0.95, 0.083, 0.002);
      const d = conTinta(dedoGeo, piel, 3.5);
      const largo = i === 0 || i === 3 ? 0.85 : 1;
      d.scale.set(1, largo, 1);
      d.position.set(0, 0.022 * largo, 0);
      g.add(d);
      this.raiz.add(g);
      this.dedos.push(g);
    });
    // el pulgar va del lado de la mano que mira al centro del cuerpo (ver cálculo de la base en actualizar)
    const p = conTinta(new THREE.CapsuleGeometry(0.0128, 0.03, 4, 10), piel, 3.5);
    p.position.set(0, 0.024, 0);
    this.pulgar.add(p);
    this.pulgar.position.set(-this.s * 0.036, 0.035, 0.012);
    this.raiz.add(this.pulgar);
    // móvil en la mano (pose «movil»)
    const carcasa = conTinta(new THREE.BoxGeometry(0.075, 0.15, 0.011), toon("#1d1b26"), 3);
    const pantalla = new THREE.Mesh(new THREE.PlaneGeometry(0.064, 0.135), plano("#7fe8ff"));
    pantalla.position.z = 0.0062;
    carcasa.add(pantalla);
    carcasa.position.set(0, 0.07, 0.03);
    this.movil.add(carcasa);
    this.movil.visible = false;
    this.raiz.add(this.movil);
  }
  actualizar(curl: number, indice: number, pulgar: number, movil: boolean) {
    this.dedos.forEach((g, i) => {
      const c = i === (this.s > 0 ? 0 : 3) ? indice : curl; // índice = dedo del lado del pulgar
      g.rotation.x = c * 1.75;
    });
    // pulgar: 0 recogido sobre la palma, 1 abierto, >1 estirado hacia arriba (pulgar arriba)
    this.pulgar.rotation.z = this.s * (0.25 + 0.75 * Math.min(1, pulgar) + (pulgar > 1 ? 0.6 * (pulgar - 1) / 0.4 : 0));
    this.pulgar.rotation.x = 0.7 - 0.6 * Math.min(1, pulgar);
    this.movil.visible = movil;
  }
}

// ---------------------------------------------------------------- brazo con IK de dos huesos
const L1 = 0.27, L2 = 0.25;
class Brazo {
  hombro = v3();
  superior: THREE.Mesh;
  antebrazo: THREE.Mesh;
  codo: THREE.Mesh;
  bolaHombro: THREE.Mesh;
  puno: THREE.Mesh;
  mano: Mano;
  grupo = new THREE.Group();
  constructor(public s: number) {
    const tela = toon(SUDADERA);
    this.superior = conTinta(new THREE.CapsuleGeometry(0.05, L1 - 0.04, 6, 14), tela, 5);
    this.antebrazo = conTinta(new THREE.CapsuleGeometry(0.045, L2 - 0.06, 6, 14), tela, 5);
    this.codo = conTinta(new THREE.SphereGeometry(0.048, 16, 12), tela, 0);
    this.bolaHombro = conTinta(new THREE.SphereGeometry(0.058, 18, 12), tela, 5);
    this.puno = conTinta(new THREE.CylinderGeometry(0.041, 0.043, 0.04, 16), toon(SUDADERA_OSC), 4);
    this.mano = new Mano(s);
    this.grupo.add(this.superior, this.antebrazo, this.codo, this.bolaHombro, this.puno, this.mano.raiz);
  }
  actualizar(p: PoseBrazo, hombros: number, movil: boolean) {
    const S = this.hombro.set(this.s * 0.207, 1.405 + hombros, 0);
    const d = p.T.clone().sub(S);
    let dist = d.length();
    const dirU = d.clone().normalize();
    dist = Math.min(Math.max(dist, 0.12), L1 + L2 - 0.002);
    const T = S.clone().addScaledVector(dirU, dist);
    const a = (L1 * L1 - L2 * L2 + dist * dist) / (2 * dist);
    const h = Math.sqrt(Math.max(0, L1 * L1 - a * a));
    const polo = p.polo.clone().addScaledVector(dirU, -p.polo.dot(dirU));
    if (polo.lengthSq() < 1e-6) polo.set(this.s, 0, -1);
    polo.normalize();
    const E = S.clone().addScaledVector(dirU, a).addScaledVector(polo, h);
    entre(this.superior, S, E);
    entre(this.antebrazo, E, T);
    this.codo.position.copy(E);
    this.bolaHombro.position.copy(S).add(v3(this.s * 0.01, -0.005, 0));
    // puño de la manga y mano
    const fore = T.clone().sub(E).normalize();
    this.puno.position.copy(T).addScaledVector(fore, -0.012);
    this.puno.quaternion.setFromUnitVectors(v3(0, 1, 0), fore);
    const Yh = (p.dir ? p.dir.clone() : fore.clone()).normalize();
    const Zh = p.palma.clone().addScaledVector(Yh, -p.palma.dot(Yh));
    if (Zh.lengthSq() < 1e-6) Zh.set(0, 0, 1);
    Zh.normalize();
    const Xh = Yh.clone().cross(Zh).normalize();
    const m = new THREE.Matrix4().makeBasis(Xh, Yh, Zh);
    this.mano.raiz.quaternion.setFromRotationMatrix(m);
    this.mano.raiz.position.copy(T).addScaledVector(fore, 0.006);
    this.mano.actualizar(p.curl, p.indice ?? p.curl, p.pulgar ?? 0.5, movil);
  }
}

// ---------------------------------------------------------------- cara
class Cara {
  raiz = new THREE.Group();
  ojos: THREE.Group[] = [];
  iris: THREE.Group[] = [];
  arcos: THREE.Mesh[] = [];
  cejas: THREE.Mesh[] = [];
  sonrisa: THREE.Mesh;
  bocaAbierta = new THREE.Group();
  hueco: THREE.Mesh;
  dientes: THREE.Mesh;
  lengua: THREE.Mesh;
  constructor() {
    const blanco = toon("#ffffff");
    [-1, 1].forEach((s) => {
      const g = new THREE.Group();
      g.position.set(s * 0.049, 0.142, 0.113);
      g.rotation.y = s * 0.33;
      const esc = conTinta(new THREE.SphereGeometry(0.031, 20, 16), blanco, 3);
      esc.scale.set(0.82, 1.08, 0.45);
      g.add(esc);
      const ir = new THREE.Group();
      const iris = new THREE.Mesh(new THREE.SphereGeometry(0.0185, 18, 14), toon("#4a2a17"));
      iris.scale.set(1, 1.1, 0.42);
      iris.position.z = 0.0105;
      const pupila = new THREE.Mesh(new THREE.SphereGeometry(0.0105, 14, 10), plano("#120a0c"));
      pupila.scale.set(1, 1.1, 0.4);
      pupila.position.z = 0.0145;
      const brillo = new THREE.Mesh(new THREE.SphereGeometry(0.0048, 10, 8), plano("#ffffff"));
      brillo.position.set(0.0065, 0.0075, 0.0175);
      ir.add(iris, pupila, brillo);
      g.add(ir);
      this.raiz.add(g);
      this.ojos.push(g);
      this.iris.push(ir);
      // ojo cerrado contento (∩)
      const arco = new THREE.Mesh(new THREE.TorusGeometry(0.019, 0.0042, 6, 18, Math.PI), plano("#2a1a20"));
      arco.position.set(s * 0.049, 0.137, 0.126);
      arco.rotation.y = s * 0.33;
      arco.visible = false;
      this.raiz.add(arco);
      this.arcos.push(arco);
      const ceja = conTinta(new THREE.CapsuleGeometry(0.0068, 0.032, 4, 10), toon(PELO), 0);
      ceja.position.set(s * 0.052, 0.196, 0.117);
      ceja.rotation.set(0, s * 0.35, Math.PI / 2);
      this.raiz.add(ceja);
      this.cejas.push(ceja);
      // colorete
      const col = new THREE.Mesh(new THREE.CircleGeometry(0.019, 20), plano("#ff8a8a", { transparent: true, opacity: 0.42 }));
      col.position.set(s * 0.079, 0.093, 0.111);
      col.rotation.y = s * 0.62;
      this.raiz.add(col);
    });
    // nariz
    const nariz = conTinta(new THREE.SphereGeometry(0.019, 14, 10), toon(PIEL_SOMBRA), 3);
    nariz.scale.set(1, 0.85, 0.9);
    nariz.position.set(0, 0.106, 0.131);
    this.raiz.add(nariz);
    // boca cerrada (sonrisa: media rosquilla hacia abajo)
    this.sonrisa = new THREE.Mesh(new THREE.TorusGeometry(0.026, 0.0048, 6, 20, Math.PI), plano("#5b1f2a"));
    this.sonrisa.position.set(0, 0.07, 0.125);
    this.sonrisa.rotation.z = Math.PI;
    this.raiz.add(this.sonrisa);
    // boca abierta
    this.hueco = conTinta(new THREE.SphereGeometry(0.027, 20, 14), toon("#6b1a2b"), 3);
    this.hueco.scale.set(1.05, 0.6, 0.36);
    this.dientes = new THREE.Mesh(new THREE.CapsuleGeometry(0.0062, 0.026, 4, 8), plano("#ffffff"));
    this.dientes.rotation.z = Math.PI / 2;
    this.dientes.position.set(0, 0.01, 0.006);
    this.lengua = new THREE.Mesh(new THREE.SphereGeometry(0.016, 14, 10), plano("#ff7d8e"));
    this.lengua.scale.set(1.1, 0.55, 0.5);
    this.lengua.position.set(0, -0.011, 0.005);
    this.bocaAbierta.add(this.hueco, this.dientes, this.lengua);
    this.bocaAbierta.position.set(0, 0.066, 0.115);
    this.raiz.add(this.bocaAbierta);
  }
  actualizar(e: EstadoPresentadora) {
    const ex = e.expresion;
    const contenta = ex === "risa" || ex === "feliz_cerrada";
    // ojos
    this.ojos.forEach((g, i) => {
      const s = i === 0 ? -1 : 1;
      const guino = ex === "guino" && s > 0;
      const grande = ex === "sorpresa" ? 1.18 : 1;
      const cerr = Math.max(e.parpadeo, guino ? 1 : 0);
      g.visible = !contenta && !guino;
      g.scale.set(grande, grande * Math.max(0.08, 1 - cerr * 0.95), grande);
      this.arcos[i].visible = contenta || guino;
      this.iris[i].position.set(e.mirar[0] * 0.0075, e.mirar[1] * 0.007, 0);
    });
    // cejas
    const cejas: Record<string, [number, number, number]> = {
      // subida, giro hacia dentro (+ = frunce), extra ceja derecha
      feliz: [0.006, -0.08, 0], habla: [0.002, 0, 0], sorpresa: [0.02, -0.12, 0], preocupada: [0.01, -0.38, 0],
      piensa: [0.004, 0.1, 0.016], guino: [0.004, -0.05, -0.006], risa: [0.01, -0.1, 0], seria: [-0.004, 0.22, 0],
      feliz_cerrada: [0.008, -0.08, 0],
    };
    const [sub, giro, extra] = cejas[ex] ?? cejas.habla;
    const alza = e.ritmo * 0.006;
    this.cejas.forEach((c, i) => {
      const s = i === 0 ? -1 : 1;
      c.position.y = 0.196 + sub + alza + (s > 0 ? extra : 0);
      c.rotation.z = Math.PI / 2 + s * giro;
    });
    // boca: abierta según la voz; si no habla, la forma de la expresión
    const ab = e.boca;
    const forzada = ex === "sorpresa" ? 0.55 : ex === "risa" ? 0.7 : 0;
    const apertura = Math.max(ab, forzada);
    const abierta = apertura > 0.07;
    this.bocaAbierta.visible = abierta;
    this.sonrisa.visible = !abierta;
    if (abierta) {
      const ancho = ex === "sorpresa" ? 0.75 : ex === "risa" || ex === "feliz" ? 1.12 : 1;
      this.hueco.scale.set(1.05 * ancho, 0.22 + apertura * 0.78, 0.36);
      this.dientes.position.y = 0.006 + apertura * 0.008;
      this.dientes.visible = ex !== "sorpresa";
      this.lengua.position.y = -0.005 - apertura * 0.008;
    } else {
      const triste = ex === "preocupada" || ex === "seria";
      this.sonrisa.rotation.z = triste ? 0 : Math.PI;
      this.sonrisa.position.y = triste ? 0.058 : 0.07;
      const w = ex === "feliz" || ex === "guino" ? 1.12 : ex === "piensa" ? 0.7 : triste ? 0.62 : 0.9;
      this.sonrisa.scale.set(w, triste ? 0.55 : ex === "feliz" ? 1.0 : 0.75, 1);
      this.sonrisa.position.x = ex === "piensa" ? 0.012 : 0;
    }
  }
}

// ---------------------------------------------------------------- personaje completo
export class Presentadora {
  raiz = new THREE.Group();
  torso = new THREE.Group(); // pivota en la cadera
  cabeza = new THREE.Group(); // pivota en el cuello
  brazos: Brazo[];
  cara = new Cara();
  constructor() {
    // piernas (solo se ven en el plano general)
    const vaq = toon(VAQUERO);
    [-1, 1].forEach((s) => {
      const p = conTinta(new THREE.CapsuleGeometry(0.078, 0.8, 6, 14), vaq, 5);
      p.position.set(s * 0.09, 0.48, 0);
      this.raiz.add(p);
    });
    this.torso.position.set(0, 0.9, 0);
    this.raiz.add(this.torso);
    const T = new THREE.Group(); // todo lo del torso, en coordenadas de mundo desplazadas
    T.position.set(0, -0.9, 0);
    this.torso.add(T);
    // sudadera (torno)
    const perfil = [
      [0.0, 0.84], [0.168, 0.85], [0.188, 0.9], [0.193, 1.0], [0.198, 1.12], [0.206, 1.25], [0.212, 1.34], [0.205, 1.4],
      [0.18, 1.45], [0.135, 1.482], [0.075, 1.5], [0.0, 1.505],
    ].map(([r, y]) => new THREE.Vector2(r, y));
    const cuerpo = conTinta(new THREE.LatheGeometry(perfil, 40), toon(SUDADERA), 5);
    cuerpo.scale.set(1.12, 1, 0.72);
    T.add(cuerpo);
    // parche frontal con el monograma NL y el bolsillo canguro (dibujo en canvas, se ciñe al torno)
    const parche = new THREE.Mesh(this.geoParche(perfil, 1.0, 1.42), new THREE.MeshToonMaterial({
      map: this.texturaPecho(), transparent: true, gradientMap: (toon(SUDADERA) as THREE.MeshToonMaterial).gradientMap, depthWrite: false,
    }));
    parche.scale.set(1.12 * 1.006, 1, 0.72 * 1.012);
    T.add(parche);
    // goma inferior
    const goma = conTinta(new THREE.TorusGeometry(0.172, 0.028, 10, 36), toon(SUDADERA_OSC), 5);
    goma.rotation.x = Math.PI / 2;
    goma.scale.set(1.12, 0.72, 1);
    goma.position.y = 0.86;
    T.add(goma);
    // capucha: cuello vuelto y la capucha plegada detrás
    const cuello = conTinta(new THREE.TorusGeometry(0.086, 0.026, 12, 30), toon(SUDADERA_OSC), 5);
    cuello.rotation.x = Math.PI / 2;
    cuello.scale.set(1.12, 0.92, 1);
    cuello.position.set(0, 1.497, -0.003);
    T.add(cuello);
    const capucha = conTinta(new THREE.SphereGeometry(0.13, 20, 14), toon(SUDADERA), 5);
    capucha.scale.set(1.05, 0.62, 0.55);
    capucha.position.set(0, 1.49, -0.11);
    T.add(capucha);
    // cordones cian con herretes
    [-1, 1].forEach((s) => {
      const c = conTinta(new THREE.CylinderGeometry(0.0062, 0.0062, 0.15, 8), toon(CIAN), 3);
      c.position.set(s * 0.04, 1.4, 0.151);
      c.rotation.set(-0.12, 0, s * 0.06);
      const h = conTinta(new THREE.CapsuleGeometry(0.0095, 0.018, 4, 8), toon("#f4f4f4"), 3);
      h.position.set(s * 0.045, 1.318, 0.161);
      T.add(c, h);
    });
    // cuello y cabeza
    const piel = toon(PIEL);
    const cuelloP = conTinta(new THREE.CylinderGeometry(0.048, 0.052, 0.13, 16), piel, 4);
    cuelloP.position.set(0, 1.535, 0);
    T.add(cuelloP);
    this.cabeza.position.set(0, 1.585, 0.005);
    this.cabeza.scale.setScalar(1.2);
    T.add(this.cabeza);
    const craneo = conTinta(new THREE.SphereGeometry(0.135, 36, 28), piel, 5);
    craneo.scale.set(1, 1.06, 0.97);
    craneo.position.set(0, 0.13, 0);
    this.cabeza.add(craneo);
    [-1, 1].forEach((s) => {
      const oreja = conTinta(new THREE.SphereGeometry(0.03, 14, 10), piel, 4);
      oreja.scale.set(0.55, 1, 0.8);
      oreja.position.set(s * 0.133, 0.125, -0.005);
      this.cabeza.add(oreja);
    });
    this.cabeza.add(this.cara.raiz);
    this.gafas();
    this.pelo();
    this.brazos = [new Brazo(-1), new Brazo(1)];
    this.brazos.forEach((b) => T.add(b.grupo));
  }

  /** trozo del torno (frente) para pegar el dibujo del pecho, entre las alturas y0 e y1 */
  geoParche(perfil: THREE.Vector2[], y0: number, y1: number) {
    const pts: THREE.Vector2[] = [];
    const radio = (y: number) => {
      for (let i = 1; i < perfil.length; i++) {
        const a = perfil[i - 1], b = perfil[i];
        if (y >= a.y && y <= b.y) return lerp(a.x, b.x, (y - a.y) / (b.y - a.y));
      }
      return perfil[perfil.length - 1].x;
    };
    const n = 24;
    for (let i = 0; i <= n; i++) {
      const y = lerp(y0, y1, i / n);
      pts.push(new THREE.Vector2(radio(y), y));
    }
    return new THREE.LatheGeometry(pts, 24, -0.62, 1.24);
  }

  texturaPecho() {
    const W = 512, H = 512;
    const c = document.createElement("canvas");
    c.width = W; c.height = H;
    const g = c.getContext("2d")!;
    g.clearRect(0, 0, W, H);
    // el parche cubre de y=1.0 (abajo) a 1.36 (arriba) y 1.24 rad de ancho: 0,36 m de alto y ~0,29 m de ancho
    // bolsillo canguro (abajo)
    g.strokeStyle = "rgba(150,80,0,0.9)";
    g.lineWidth = 7;
    g.lineJoin = "round";
    g.beginPath();
    g.moveTo(W * 0.2, H * 0.99);
    g.lineTo(W * 0.27, H * 0.7);
    g.lineTo(W * 0.73, H * 0.7);
    g.lineTo(W * 0.8, H * 0.99);
    g.stroke();
    // monograma NL con degradado neón (azul → violeta → rosa → naranja), como el logo oficial
    g.font = "900 140px Montserrat, Arial Black, sans-serif";
    g.textAlign = "center";
    g.textBaseline = "middle";
    g.save();
    g.translate(W / 2, H * 0.24);
    g.scale(1, 0.8);
    const ancho = g.measureText("NL").width;
    const grad = g.createLinearGradient(-ancho / 2, 0, ancho / 2, 0);
    grad.addColorStop(0, "#2f7bff");
    grad.addColorStop(0.38, "#8b3dff");
    grad.addColorStop(0.68, "#ff3fa0");
    grad.addColorStop(1, "#ff8a2a");
    g.lineWidth = 16;
    g.strokeStyle = "#24172a";
    g.strokeText("NL", 0, 0);
    g.fillStyle = grad;
    g.fillText("NL", 0, 0);
    g.restore();
    const t = new THREE.CanvasTexture(c);
    t.colorSpace = THREE.SRGBColorSpace;
    t.anisotropy = 4;
    return t;
  }

  gafas() {
    const m = toon(GAFAS);
    [-1, 1].forEach((s) => {
      const aro = new THREE.Mesh(new THREE.TorusGeometry(0.037, 0.0052, 8, 36), m);
      aro.position.set(s * 0.05, 0.142, 0.139);
      aro.rotation.y = s * 0.3;
      aro.scale.set(1.08, 0.92, 1);
      this.cabeza.add(aro);
      const patilla = new THREE.Mesh(new THREE.CylinderGeometry(0.004, 0.004, 0.13, 6), m);
      entre(patilla, v3(s * 0.088, 0.148, 0.122), v3(s * 0.132, 0.14, 0.0));
      this.cabeza.add(patilla);
    });
    const puente = new THREE.Mesh(new THREE.CylinderGeometry(0.0045, 0.0045, 0.03, 6), m);
    puente.rotation.z = Math.PI / 2;
    puente.position.set(0, 0.15, 0.147);
    this.cabeza.add(puente);
  }

  pelo() {
    const m = toon(PELO);
    // casquete: tapa la parte de arriba y de atrás, inclinado hacia atrás para dejar la frente
    const casquete = conTinta(new THREE.SphereGeometry(0.145, 36, 24, 0, Math.PI * 2, 0, Math.PI * 0.6), m, 5);
    casquete.position.set(0, 0.135, -0.004);
    casquete.rotation.x = -0.42;
    casquete.scale.set(1.03, 1.06, 1.02);
    this.cabeza.add(casquete);
    // flequillo barrido hacia un lado
    const fl: [number, number, number, number, number, number][] = [
      // x, y, z, escala x, rot z, rot x
      [-0.062, 0.222, 0.083, 1.35, 0.45, 0.5],
      [0.012, 0.236, 0.092, 1.4, 0.12, 0.45],
      [0.078, 0.214, 0.08, 1.15, -0.55, 0.45],
      [0.11, 0.17, 0.06, 0.8, -1.0, 0.3],
    ];
    fl.forEach(([x, y, z, sx, rz, rx]) => {
      const b = conTinta(new THREE.SphereGeometry(0.052, 18, 12), m, 5);
      b.scale.set(sx, 0.52, 0.62);
      b.position.set(x, y, z);
      b.rotation.set(rx, 0, rz);
      this.cabeza.add(b);
    });
    // mechones a los lados de la cara
    [-1, 1].forEach((s) => {
      const b = conTinta(new THREE.SphereGeometry(0.042, 16, 12), m, 5);
      b.scale.set(0.58, 1.7, 0.78);
      b.position.set(s * 0.127, 0.085, 0.045);
      b.rotation.z = s * 0.12;
      this.cabeza.add(b);
    });
    // moño con goma cian
    const mono = conTinta(new THREE.SphereGeometry(0.062, 20, 14), m, 5);
    mono.position.set(0, 0.292, -0.06);
    mono.scale.set(1, 0.92, 1);
    this.cabeza.add(mono);
    const goma = new THREE.Mesh(new THREE.TorusGeometry(0.036, 0.011, 8, 20), toon(CIAN));
    goma.position.set(0, 0.252, -0.05);
    goma.rotation.x = Math.PI / 2 + 0.35;
    this.cabeza.add(goma);
  }

  actualizar(e: EstadoPresentadora) {
    const k = e.mezcla;
    const cA = poseCuerpo(e.poseA, e.ladoA), cB = poseCuerpo(e.poseB, e.lado);
    const giro = lerp(cA.giro, cB.giro, k);
    const hombros = lerp(cA.hombros, cB.hombros, k);
    const inclina = lerp(cA.inclina, cB.inclina, k);
    const agacha = lerp(cA.agacha, cB.agacha, k);
    const movil = k > 0.5 ? cB.movil : cA.movil;
    // respiración y balanceo (siempre en movimiento: nada de planos congelados)
    const resp = Math.sin(e.tg * 2 * Math.PI / 3.4);
    this.torso.rotation.set(agacha * 2 + e.ritmo * 0.03, giro + 0.03 * Math.sin(e.tg * 0.9), 0.018 * Math.sin(e.tg * 1.3));
    this.torso.scale.set(1, 1 + 0.006 * resp, 1);
    this.brazos.forEach((b) => {
      const lider = b.s === e.lado;
      const liderA = b.s === e.ladoA;
      const pa = poseBrazo(e.poseA, b.s, liderA, e.t + 2);
      const pb = poseBrazo(e.poseB, b.s, lider, e.t);
      const p = mezclaBrazo(pa, pb, k);
      // gesto en las palabras clave: la mano que habla marca el golpe
      if (lider) p.T.y += e.ritmo * 0.035;
      p.T.x += 0.006 * Math.sin(e.tg * 1.7 + b.s);
      p.T.y += 0.006 * Math.sin(e.tg * 2.1 + b.s * 2) + 0.004 * resp;
      b.actualizar(p, hombros + 0.004 * resp, movil && lider);
    });
    // cabeza: cabeceo con la voz, inclinación por pose, mirada
    this.cabeza.rotation.set(
      -0.05 * e.mirar[1] + e.cabeceo * 0.09 + (movil ? 0.28 : 0),
      e.mirar[0] * 0.22 - giro * 0.6,
      inclina + 0.025 * Math.sin(e.tg * 1.1),
    );
    this.cara.actualizar(e);
  }
}
