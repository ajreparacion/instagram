# El Jambo en Neogest Studio (formato de dibujos de calidad) · 16/11/2026

Orden del dueño (15/11): «El Jambo continúa con el nuevo formato de dibujos de calidad»; «los guiones tienen que tener más sentido, efectos de retención y que se entienda el mensaje». Orden del dueño (16/11): reparto nuevo — ver `equipo/serie_jambo.md` (biblia v3) y `claude/redes/jambo_reparto_nuevo_2026-11-16.md`.
El motor «sketch» de este repo queda SUSTITUIDO para la serie. Cada episodio se renderiza en Neogest Studio (Base44 6af862101565c330cf06389f, `node scripts/render.mjs spec.json salida.mp4 --hoja`) y se pone en `post.json` como `"video_externo": "<url pública mp4>"` con `"renderizado": false`; el ciclo lo descarga y lo sube a la release (su calidad.json caduca y Calidad lo evalúa).

## Cómo se monta un episodio (ver la receta en gen_episodios.py)
- Apertura de 1,3 s con un clip real de la Biblioteca (MediaAsset tags flow/gemini) y el gancho en texto con «whoosh».
- Personajes del estudio (rosa, felipe, sindy, neo, cliente) sobre decorado (oficina, despacho, bar, calle, reunion), boca sincronizada; plano distinto en cada frase; primer plano + destello + sello con «impacto» en el remate. **Pendiente de dibujar en `src/studio/characters.js` de Neogest Studio** (hasta entonces usan el aspecto que tuvieran asignado los slugs retirados): Rosa Melano (jefa, traje chaqueta, gesto cortante), Felipe Lotas (empleado, cara de empanado, reacciona siempre tarde), Sindy Entes (empleada, le faltan todos los dientes salvo 3, mucho carácter), Neo (IA que resuelve, diseño sintético/robótico sobrio).
- Voz edge-tts por personaje con marcas de palabra (subtítulos exactos): Rosa ElviraNeural −4 Hz, Felipe AlvaroNeural −4 %/−2 Hz, Sindy XimenaNeural +8 %/+4 Hz, Neo AlvaroNeural (pitch 0, distinto de Felipe por el rate/pitch), cliente AlvaroNeural −10 Hz.
- Emoji en cada golpe de la escalada, barra de progreso, música Pixabay «comedia» de la biblioteca del estudio con ducking.
- Cierre: MORALEJA en una línea (el mensaje que tiene que quedar) + pregunta para comentar + cierre de marca. Duración ≤ 30 s (escenas con "duration" 0,4 para que mande la voz).

## Reglas de guion (para que se entienda)
1. Planteamiento claro en la primera frase: quién quiere qué y por qué es absurdo.
2. Cada golpe de la escalada sigue la lógica del anterior y es peor; nada de frases sueltas.
3. El giro resuelve el conflicto planteado (no otro) y se entiende sin contexto.
4. Moraleja explícita en el cierre, en 6-9 palabras («Quien más controla tu tiempo suele controlar peor el suyo»). La dice Neo o aparece en pantalla, nunca Rosa.
5. Cifras en letra y cero palabras en inglés en la voz.

## Pasos en una sesión en la nube (todo por el MCP de Base44, app 6af862101565c330cf06389f)
1. Escribe en el sandbox de la app (`write_file`) este `gen_episodios.py` (v5.1, 20/11 noche) y un `eps.json` con los episodios. Cada episodio: `slug` (empieza por el número de la pieza), `set` (oficina, despacho, bar, calle o reunion), `hora` (0-23), `moraleja` (6-9 palabras) y `escenas`. Ya NO lleva `flow`: la apertura y el cierre son SIEMPRE la misma tarjeta «Cosas de Casa» (función `bookend()`, idéntica en los dos extremos para que el bucle no se note); en cuanto haya un vídeo real de fachada de barrio se cambia ahí una sola vez, para todos los episodios.
2. Un guion del motor antiguo (`guion.json` con `escenas[].estilo/hablante/voz/texto/dibujo`) se pasa así a cada escena del estudio: `e` = estilo (gancho, gag, remate; la última escena va como `cierre`), `h` = hablante, `v` = voz, `t` = texto, `p` = dibujo.personajes, `a` = dibujo.acciones (incluye `fria` para réplicas de humor negro frío, además de habla/desespera/delega/presume — cada una modula también la voz), `sello` (opcional, texto corto del remate), `risas` (opcional, `true`: añade sfx de risas de sitcom al final de la réplica — úsalo en el golpe más fuerte de cada escalada, no en todas).
3. En el sandbox (`run_command`): `pip install edge-tts`, `python3 gen_episodios.py eps.json /tmp/jb` y, por episodio, `node scripts/render.mjs /tmp/jb/<n>.json /tmp/jb/<n>.mp4 --hoja`. Mira la hoja `.jpg` y el `.qc.json` antes de dar el vídeo por bueno (≤ 30 s).
4. El render (`render.mjs`) aplica solo el MÁSTER (`scripts/masterizar.mjs`: loudnorm −14 LUFS, limitador, pico ≈ −1,3 dBFS, bitrate que deja el mp4 < 19 MB; si el sandbox no trae ffmpeg, instala el binario estático de `imageio-ffmpeg` con pip) y copia el mp4 a `public/entregas/<archivo>.mp4`. Subida (VÍA PROBADA el 16/11 con 308 y 323; el `preview_token` da 401 y `public/_render/` está en .gitignore, no sirven):
   a. `create_checkpoint` y `POST /api/apps/6af862101565c330cf06389f/deploy` (cuerpo `{}`); espera ~20 s hasta que `curl -I https://neogest-studio-cf06389f.base44.app/entregas/<archivo>.mp4` dé 200.
   b. `upload_app_asset` con `fileUrl = https://neogest-studio-cf06389f.base44.app/entregas/<archivo>.mp4` y `fileName`. La URL resultante (`https://media.base44.com/videos/public/6af862101565c330cf06389f/…mp4`) es el `video_externo`.
   c. Limpieza: `rm public/entregas/*.mp4`, `create_checkpoint` y deploy (para no acumular mp4 en el repo del estudio).
   Para re-masterizar un mp4 ya existente: `node scripts/masterizar.mjs entrada.mp4 salida.mp4` (imprime lufs, pico y MB).
5. En `cola/NNN_…/post.json`: `"video_externo": "<esa URL>"`, `"renderizado": false` y `"motor": "neogest-studio"`. El ciclo de GitHub descarga el vídeo, pasa el control de audio y lo sube a la release; después lo evalúa Calidad.
6. Si /tmp del sandbox se ha borrado, repite el paso 1; si Base44 responde «busy» o 503, espera y reintenta.
