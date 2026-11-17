# Guiones de El Jambo pedidos a Gemini (17/11/2026, orden del dueño)

El dueño ha visto lo publicado y los guiones no engachan ("no tiene sentido"). Desde el
17/11, antes de cada pasada del Creador (09:51 y 15:51 Madrid) se dispara
`.github/workflows/guionista_gemini.yml`, que llama a `herramientas/guionista_gemini.py`
(Gemini API, cuenta darbish, capa gratis) con la biblia de la serie, los motivos de
rechazo más repetidos de Calidad y los patrones de reels virales ya estudiados, y pide
guiones nuevos de El Jambo con más gancho y lógica.

- `pendientes/` — borradores validados (JSON), uno por episodio, sin usar todavía.
- `usados/` — los que el Creador ya ha convertido en una pieza de `cola/` (se mueven aquí,
  no se borran, para no repetir situación).

El Creador elige uno (o varios) de `pendientes/`, decide el decorado/hora/clip de la
Biblioteca que le faltan, revisa en voz alta que la voz pase el control (cifras en letra,
sin nombres propios al inicio de frase) y lo pasa por `gen_episodios.py` como siempre. Si
no hay nada en `pendientes/` (Gemini falló o no hay clave), el Creador escribe el guion él
mismo como hacía hasta ahora: este paso es una ayuda, nunca un bloqueo.

Si un guion de Gemini no vale, el Creador lo descarta (no lo deja en `pendientes/`) y anota
el motivo en el tablón, igual que con cualquier pieza rechazada — eso retroalimenta el
siguiente prompt a través de `equipo/lecciones_calidad.md`.
