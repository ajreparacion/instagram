// «Bit», la mascota de Neogest Lab en 3D: robotito redondo blanco con pantalla-cara cian, antena con bola cian,
// manos y pies de bola que flotan. La cara se dibuja en un canvas en cada fotograma (expresiones y parpadeo).
import * as THREE from "three";
import { conTinta, plano, toon } from "./toon";

export type EstadoBit = {
  visible: boolean;
  pos: THREE.Vector3;
  escala: number;
  giroY: number;
  giroZ: number;
  giroX: number;
  aplasta: number; // >0 estira en vertical, <0 aplasta
  cara: string; // feliz | normal | sorpresa | corazon | guino | estrella | piensa | habla | triste
  parpadeo: number;
  habla: number;
  manos: [number, number]; // altura extra de cada mano (saludar, señalar)
  t: number;
};

export class Bit {
  raiz = new THREE.Group();
  cuerpo = new THREE.Group();
  manos: THREE.Mesh[] = [];
  pies: THREE.Mesh[] = [];
  lienzo: HTMLCanvasElement;
  textura: THREE.CanvasTexture;
  ultimaCara = "";
  constructor() {
    this.raiz.add(this.cuerpo);
    const blanco = toon("#f6f8fb");
    const cuerpo = conTinta(new THREE.SphereGeometry(1, 36, 28), blanco, 5);
    this.cuerpo.add(cuerpo);
    // pantalla-cara: visera curva (trozo de cilindro) con la cara dibujada en un canvas con esquinas redondeadas
    this.lienzo = document.createElement("canvas");
    this.lienzo.width = 420;
    this.lienzo.height = 230;
    this.textura = new THREE.CanvasTexture(this.lienzo);
    this.textura.colorSpace = THREE.SRGBColorSpace;
    this.textura.anisotropy = 4;
    const visera = new THREE.Mesh(
      new THREE.CylinderGeometry(1.03, 1.03, 0.84, 40, 1, true, -0.8, 1.6),
      new THREE.MeshBasicMaterial({ map: this.textura, transparent: true, toneMapped: false, side: THREE.FrontSide }),
    );
    visera.position.set(0, 0.05, 0);
    this.cuerpo.add(visera);
    // orejas laterales
    [-1, 1].forEach((s) => {
      const o = conTinta(new THREE.CylinderGeometry(0.24, 0.24, 0.16, 20), toon("#cfd8e3"), 4);
      o.rotation.z = Math.PI / 2;
      o.position.set(s * 0.98, 0.05, 0);
      this.cuerpo.add(o);
    });
    // antena
    const palo = conTinta(new THREE.CylinderGeometry(0.045, 0.045, 0.42, 8), toon("#9aa8b8"), 3);
    palo.position.set(0, 1.17, 0);
    this.cuerpo.add(palo);
    const bola = conTinta(new THREE.SphereGeometry(0.15, 16, 12), plano("#3be3ff"), 4);
    bola.position.set(0, 1.44, 0);
    this.cuerpo.add(bola);
    // manos y pies flotantes
    [-1, 1].forEach((s) => {
      const m = conTinta(new THREE.SphereGeometry(0.25, 18, 12), blanco, 4);
      this.raiz.add(m);
      this.manos.push(m);
      const p = conTinta(new THREE.SphereGeometry(0.24, 18, 12), blanco, 4);
      this.raiz.add(p);
      this.pies.push(p);
    });
  }

  dibujarCara(cara: string, parpadeo: number, habla: number) {
    const clave = `${cara}|${parpadeo.toFixed(2)}|${habla.toFixed(2)}`;
    if (clave === this.ultimaCara) return;
    this.ultimaCara = clave;
    const g = this.lienzo.getContext("2d", { willReadFrequently: true })!;
    const W = this.lienzo.width, H = this.lienzo.height;
    g.shadowBlur = 0;
    g.shadowColor = "transparent";
    g.clearRect(0, 0, W, H);
    const rr = (x: number, y: number, w: number, h: number, r: number) => {
      g.beginPath();
      g.moveTo(x + r, y);
      g.arcTo(x + w, y, x + w, y + h, r);
      g.arcTo(x + w, y + h, x, y + h, r);
      g.arcTo(x, y + h, x, y, r);
      g.arcTo(x, y, x + w, y, r);
      g.closePath();
    };
    rr(6, 6, W - 12, H - 12, 56);
    g.fillStyle = "#24172a";
    g.fill();
    rr(16, 16, W - 32, H - 32, 46);
    const fondo = g.createLinearGradient(0, 0, 0, H);
    fondo.addColorStop(0, "#3fe4ff");
    fondo.addColorStop(1, "#0aa6cc");
    g.fillStyle = fondo;
    g.fill();
    g.save();
    g.clip();
    g.fillStyle = "rgba(255,255,255,0.18)";
    g.beginPath();
    g.ellipse(W * 0.3, H * 0.2, W * 0.32, H * 0.12, -0.15, 0, Math.PI * 2);
    g.fill();
    g.restore();
    g.strokeStyle = "#ffffff";
    g.fillStyle = "#ffffff";
    g.lineCap = "round";
    g.lineJoin = "round";
    g.lineWidth = 18;
    const ex = [W * 0.33, W * 0.67], ey = H * 0.43;
    const arco = (x: number, arriba: boolean) => { g.beginPath(); g.arc(x, ey + (arriba ? 16 : -10), 32, arriba ? Math.PI * 1.12 : Math.PI * 0.12, arriba ? Math.PI * 1.88 : Math.PI * 0.88); g.stroke(); };
    const ojo = (x: number) => {
      const h = Math.max(6, 64 * (1 - parpadeo));
      g.beginPath();
      g.ellipse(x, ey, 22, h / 2, 0, 0, Math.PI * 2);
      g.fill();
    };
    const corazon = (x: number) => {
      g.beginPath();
      const y = ey - 6, s = 1.15;
      g.moveTo(x, y + 26 * s);
      g.bezierCurveTo(x - 40 * s, y - 2 * s, x - 18 * s, y - 30 * s, x, y - 10 * s);
      g.bezierCurveTo(x + 18 * s, y - 30 * s, x + 40 * s, y - 2 * s, x, y + 26 * s);
      g.fillStyle = "#ff4fa3";
      g.fill();
      g.fillStyle = "#ffffff";
    };
    const estrella = (x: number) => {
      g.beginPath();
      for (let i = 0; i < 10; i++) {
        const r = i % 2 ? 12 : 30, a = -Math.PI / 2 + (i * Math.PI) / 5;
        g.lineTo(x + r * Math.cos(a), ey + r * Math.sin(a));
      }
      g.closePath();
      g.fillStyle = "#ffe14a";
      g.fill();
      g.fillStyle = "#ffffff";
    };
    const boca = (tipo: string) => {
      g.beginPath();
      if (tipo === "sonrisa") g.arc(W * 0.5, H * 0.56, 40, Math.PI * 0.18, Math.PI * 0.82);
      else if (tipo === "grande") { g.arc(W * 0.5, H * 0.62, 40, 0, Math.PI); g.closePath(); g.fill(); return; }
      else if (tipo === "o") { g.ellipse(W * 0.5, H * 0.76, 18, 22, 0, 0, Math.PI * 2); g.stroke(); return; }
      else if (tipo === "triste") g.arc(W * 0.5, H * 0.9, 34, Math.PI * 1.22, Math.PI * 1.78);
      else if (tipo === "habla") { g.ellipse(W * 0.5, H * 0.76, 28, 5 + 20 * habla, 0, 0, Math.PI * 2); g.fill(); return; }
      else if (tipo === "linea") { g.moveTo(W * 0.42, H * 0.76); g.lineTo(W * 0.58, H * 0.76); }
      g.stroke();
    };
    switch (cara) {
      case "feliz": arco(ex[0], true); arco(ex[1], true); boca("sonrisa"); break;
      case "risa": arco(ex[0], true); arco(ex[1], true); boca("grande"); break;
      case "sorpresa": g.lineWidth = 12; g.beginPath(); g.arc(ex[0], ey, 22, 0, Math.PI * 2); g.stroke(); g.beginPath(); g.arc(ex[1], ey, 22, 0, Math.PI * 2); g.stroke(); boca("o"); break;
      case "corazon": corazon(ex[0]); corazon(ex[1]); boca("sonrisa"); break;
      case "estrella": estrella(ex[0]); estrella(ex[1]); boca("grande"); break;
      case "guino": ojo(ex[0]); arco(ex[1], true); boca("sonrisa"); break;
      case "piensa": g.beginPath(); g.ellipse(ex[0] + 8, ey - 10, 15, 20, 0, 0, Math.PI * 2); g.ellipse(ex[1] + 8, ey - 10, 15, 20, 0, 0, Math.PI * 2); g.fill(); boca("linea"); break;
      case "triste": ojo(ex[0]); ojo(ex[1]); boca("triste"); break;
      case "habla": ojo(ex[0]); ojo(ex[1]); boca("habla"); break;
      default: ojo(ex[0]); ojo(ex[1]); boca("sonrisa");
    }
    this.textura.needsUpdate = true;
  }

  actualizar(e: EstadoBit) {
    this.raiz.visible = e.visible && e.escala > 0.001;
    if (!this.raiz.visible) return;
    this.raiz.position.copy(e.pos);
    const s = e.escala;
    const st = 1 + e.aplasta;
    this.raiz.scale.set(s / Math.sqrt(st), s * st, s / Math.sqrt(st));
    this.raiz.rotation.set(e.giroX, e.giroY, e.giroZ);
    const t = e.t;
    this.manos.forEach((m, i) => {
      const sx = i === 0 ? -1 : 1;
      m.position.set(sx * 1.32, -0.15 + 0.08 * Math.sin(t * 5 + i * 1.7) + e.manos[i], 0.15);
    });
    this.pies.forEach((p, i) => {
      const sx = i === 0 ? -1 : 1;
      p.position.set(sx * 0.42, -1.32 + 0.05 * Math.sin(t * 4 + i * 2.1), 0.05);
    });
    this.dibujarCara(e.cara, e.parpadeo, e.habla);
  }
}
