// Materiales de dibujo animado: sombreado por bandas (MeshToonMaterial) y contorno de tinta por «casco invertido».
// Idea tomada de claude-animated-shorts (Mr omi, MIT): tinta casi negra color ciruela, grosor constante en píxeles
// (se especifica a 1080x1920 y no cambia con el zoom de la cámara).
import * as THREE from "three";

export const TINTA = "#24172a";
// focal en píxeles con fov 30° a 1920 px de alto: (1920/2)/tan(15°) ≈ 3583
const FOCAL_PX = 3583;

let rampa: THREE.DataTexture | null = null;
export const gradiente = () => {
  if (!rampa) {
    // tres bandas: sombra, medio tono, luz (valores multiplicadores lineales)
    const v = [72, 72, 72, 150, 226, 255];
    const d = new Uint8Array(v.flatMap((x) => [x, x, x, 255]));
    rampa = new THREE.DataTexture(d, v.length, 1, THREE.RGBAFormat);
    rampa.minFilter = THREE.NearestFilter;
    rampa.magFilter = THREE.NearestFilter;
    rampa.generateMipmaps = false;
    rampa.needsUpdate = true;
  }
  return rampa;
};

const cacheToon = new Map<string, THREE.MeshToonMaterial>();
export const toon = (color: string, extra: Partial<THREE.MeshToonMaterialParameters> = {}, clave?: string) => {
  const k = clave ?? (Object.keys(extra).length ? "" : color);
  if (k && cacheToon.has(k)) return cacheToon.get(k)!;
  const m = new THREE.MeshToonMaterial({ color, gradientMap: gradiente(), ...extra });
  if (k) cacheToon.set(k, m);
  return m;
};

export const plano = (color: string, extra: Partial<THREE.MeshBasicMaterialParameters> = {}) =>
  new THREE.MeshBasicMaterial({ color, toneMapped: false, ...extra });

const cacheTinta = new Map<number, THREE.ShaderMaterial>();
/** material del contorno: grosor `px` píxeles a 1080x1920 */
export const tinta = (px = 5) => {
  if (cacheTinta.has(px)) return cacheTinta.get(px)!;
  const m = new THREE.ShaderMaterial({
    uniforms: { w: { value: px / FOCAL_PX }, c: { value: new THREE.Color(TINTA) } },
    vertexShader: `
      uniform float w;
      void main() {
        vec4 mv = modelViewMatrix * vec4(position, 1.0);
        vec3 n = normalize(normalMatrix * normal);
        mv.xyz += n * w * max(0.3, -mv.z);
        gl_Position = projectionMatrix * mv;
      }`,
    fragmentShader: `
      uniform vec3 c;
      void main() {
        gl_FragColor = vec4(c, 1.0);
        #include <colorspace_fragment>
      }`,
    side: THREE.BackSide,
  });
  cacheTinta.set(px, m);
  return m;
};

/** malla con su contorno (hijo que comparte la geometría) */
export const conTinta = (geo: THREE.BufferGeometry, mat: THREE.Material, px = 5) => {
  const m = new THREE.Mesh(geo, mat);
  if (px > 0) {
    const t = new THREE.Mesh(geo, tinta(px));
    t.name = "tinta";
    m.add(t);
  }
  return m;
};

export const malla = (geo: THREE.BufferGeometry, color: string, px = 5, extra: Partial<THREE.MeshToonMaterialParameters> = {}) =>
  conTinta(geo, toon(color, extra), px);

/** coloca una malla (cilindro/cápsula orientada en Y) entre dos puntos */
const Y = new THREE.Vector3(0, 1, 0);
const tmp = new THREE.Vector3();
export const entre = (obj: THREE.Object3D, a: THREE.Vector3, b: THREE.Vector3) => {
  obj.position.copy(a).add(b).multiplyScalar(0.5);
  tmp.copy(b).sub(a);
  const l = tmp.length();
  if (l > 1e-6) obj.quaternion.setFromUnitVectors(Y, tmp.multiplyScalar(1 / l));
  return l;
};

export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
export const v3 = (x = 0, y = 0, z = 0) => new THREE.Vector3(x, y, z);
