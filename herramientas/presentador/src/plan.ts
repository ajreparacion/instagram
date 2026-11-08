// Contrato con preparar.py: todos los tiempos van en FOTOGRAMAS absolutos (30 fps). preparar.py es la única fuente
// de verdad de los tiempos (así la imagen y los efectos de sonido caen en el mismo fotograma).
export type Palabra = { t: string; a: number; b: number; clave: boolean };
export type Mensaje = { de: "yo" | "otro" | "app"; texto: string; f: number };
export type Elemento = {
  tipo: "captura" | "movil" | "terminal" | "tarjeta" | "broll" | "cierre";
  f: number; // fotograma de entrada
  src?: string; // imagen en public/ (capturas/...)
  zoom?: [number, number, number]; // centro x, y (0-1) y escala final del zoom sobre la captura
  lineas?: string[]; // terminal
  tipeo?: [number, number]; // fotogramas de inicio y fin del tecleo
  titulo?: string; // tarjeta / cierre / barra del móvil
  items?: string[]; // tarjeta
  checks?: number[]; // fotograma de cada check
  pegatina?: string; // «guárdalo»
  pegatina_f?: number;
  chip?: string; // pastilla amarilla bajo la tarjeta / cierre
  mensajes?: Mensaje[]; // móvil con chat
  etiqueta?: string; // rótulo pequeño sobre la captura («Demo con datos de ejemplo»)
};
export type Escena = {
  a: number;
  b: number;
  fondo: string;
  titular?: string;
  titular_estilo?: "amarillo" | "blanco" | "sello" | "cian" | "rosa";
  titular_f?: number;
  presentador: string; // pose
  expresion: string;
  lado: number; // 1 = mano/elemento a la derecha de la pantalla, -1 = izquierda
  bit: string;
  bit_cara?: string;
  plano: string; // medio | primer | abajo | lejos
  giro: number; // ángulo de cámara (rad) para que cada corte parezca otra cámara
  elemento?: Elemento;
  palabras: Palabra[];
  flash?: number; // fotograma del destello blanco
  golpes?: number[]; // fotogramas de sacudida (sello, impacto)
  oculto?: boolean; // presentadora fuera de plano (b-roll a pantalla completa)
  sub?: number; // subcorte a mitad de una escena larga (otra cámara y otro fondo, misma frase)
  fondo2?: string;
};
export type Plan = {
  frames: number;
  fps: number;
  escenas: Escena[];
  boca: number[]; // apertura de boca por fotograma (0-1), de la envolvente real de la voz
  acento: string;
  app: string;
  marca: { logo: string; firma: string };
};

export const PLAN_VACIO: Plan = {
  frames: 90,
  fps: 30,
  acento: "#1f5bff",
  app: "Neogest Lab",
  marca: { logo: "marca/logo.png", firma: "By Neogest Lab" },
  boca: [],
  escenas: [
    {
      a: 0, b: 90, fondo: "morado", titular: "MODO PRESENTADOR", titular_estilo: "amarillo", titular_f: 4,
      presentador: "saluda", expresion: "feliz", lado: 1, bit: "entra", plano: "medio", giro: 0,
      palabras: [{ t: "Hola,", a: 4, b: 20, clave: false }, { t: "soy", a: 20, b: 30, clave: false }, { t: "Nea", a: 30, b: 50, clave: true }],
    },
  ],
};

export const escenaEn = (plan: Plan, f: number) => {
  const e = plan.escenas;
  for (let i = e.length - 1; i >= 0; i--) if (f >= e[i].a) return i;
  return 0;
};

export const clamp = (x: number, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const suave = (x: number) => { const t = clamp(x); return t * t * (3 - 2 * t); };
export const muySuave = (x: number) => { const t = clamp(x); return t * t * t * (t * (t * 6 - 15) + 10); };
export const salidaAtras = (x: number, k = 1.70158) => { const t = clamp(x) - 1; return 1 + (k + 1) * t * t * t + k * t * t; };
export const elastico = (x: number) => { const t = clamp(x); return t === 0 || t === 1 ? t : Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * ((2 * Math.PI) / 3)) + 1; };
// pseudoaleatorio determinista (cada fotograma se puede renderizar en cualquier orden y en cualquier pestaña)
export const azar = (n: number) => { const x = Math.sin(n * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
// pulso 0→1→0 que empieza en el fotograma f0 y dura d fotogramas
export const pulso = (f: number, f0: number, d: number) => { const t = (f - f0) / d; return t < 0 || t > 1 ? 0 : Math.sin(Math.PI * t) * (1 - t * 0.3); };

export const FONDOS: Record<string, string> = {
  verde: "#18c45a", magenta: "#ec1c8c", morado: "#7b2ff0", cian: "#0fb4ea", rojo: "#e6262e", negro: "#141118",
  azul: "#2a5cff", amarillo: "#ffd21a", naranja: "#ff7a1a", turquesa: "#10c4b0", rosa: "#ff5fa8",
};
export const colorFondo = (n: string) => FONDOS[n] || (n && n.startsWith("#") ? n : FONDOS.morado);
