# Créditos del modo presentador

La técnica de este modo (personajes de dibujo animado en un mundo 3D con three.js dentro de Remotion, contorno de
tinta de grosor constante, sombreado por bandas, todo calculado a partir del número de fotograma, fotogramas sueltos
para revisar el look, y sonido sintetizado por código con tabla de eventos, música agachada bajo la voz y máster por
sonoridad) viene de la skill de código abierto **«claude-animated-shorts»**, de **Mr omi**
(github.com/mromidev/claude-animated-shorts), publicada con licencia **MIT**. Su licencia completa está en
`LICENSE.claude-animated-shorts`.

Autorizado por el dueño de Neogest Lab el 8/11/2026 («Usar esa herramienta MIT»).

Qué se ha reutilizado y qué es propio:
- Reutilizado (adaptado): la idea del contorno por casco invertido con grosor en píxeles a 1080x1920 y el color de
  tinta ciruela (`src/personajes/toon.ts`), el patrón de actualizar el mundo three.js dentro del render de React a
  partir del fotograma (`src/Escena3D.tsx`), el script de fotogramas sueltos (`fotogramas.mjs`, basado en
  `scripts/bridge-stills.mjs`) y la estructura del sonido (`audio.py`, basada en `templates/audio`).
- Propio de Neogest Lab: la presentadora «Nea» (personaje original, no es ninguna persona real), el robot «Bit»
  (mascota de Neogest Lab), las maquetas, los guiones, la música y todo el código de `preparar.py`.
- No se ha copiado nada de los personajes, historias ni plano alguno de los vídeos de referencia de la skill, y sus
  fotogramas de referencia (`references/frames`, `references/sheets`) no están en este repositorio.

Tipografías: Montserrat (SIL OFL, `herramientas/fonts/`) y Anton (SIL OFL, se descarga de google/fonts al renderizar).
Remotion se usa con su licencia gratuita para particulares y empresas de hasta 3 personas (remotion.dev/license).
