# El Jambo en Neogest Studio (formato de dibujos de calidad) · 15/11/2026

Orden del dueño (15/11): «El Jambo continúa con el nuevo formato de dibujos de calidad»; «los guiones tienen que tener más sentido, efectos de retención y que se entienda el mensaje».
El motor «sketch» de este repo queda SUSTITUIDO para la serie. Cada episodio se renderiza en Neogest Studio (Base44 6af862101565c330cf06389f, `node scripts/render.mjs spec.json salida.mp4 --hoja`) y se pone en `post.json` como `"video_externo": "<url pública mp4>"` con `"renderizado": false`; el ciclo lo descarga y lo sube a la release (su calidad.json caduca y Calidad lo evalúa).

## Cómo se monta un episodio (ver la receta en gen_episodios.py)
- Apertura de 1,3 s con un clip real de la Biblioteca (MediaAsset tags flow/gemini) y el gancho en texto con «whoosh».
- Personajes del estudio (jambo, jupillo, pelota, bola, tramites, cliente) sobre decorado (oficina, despacho, bar, calle, reunion), boca sincronizada; plano distinto en cada frase; primer plano + destello + sello con «impacto» en el remate.
- Voz edge-tts por personaje con marcas de palabra (subtítulos exactos): Jambo AlvaroNeural +6 %/−3 Hz, Jupillo XimenaNeural, Pelota ElviraNeural +8 Hz, Bola ElviraNeural −10 Hz, Trámites ElviraNeural −4 Hz, cliente AlvaroNeural −10 Hz.
- Emoji en cada golpe de la escalada, barra de progreso, música Pixabay «comedia» de la biblioteca del estudio con ducking.
- Cierre: MORALEJA en una línea (el mensaje que tiene que quedar) + pregunta para comentar + cierre de marca. Duración ≤ 30 s (escenas con "duration" 0,4 para que mande la voz).

## Reglas de guion (para que se entienda)
1. Planteamiento claro en la primera frase: quién quiere qué y por qué es absurdo.
2. Cada golpe de la escalada sigue la lógica del anterior y es peor; nada de frases sueltas.
3. El giro resuelve el conflicto planteado (no otro) y se entiende sin contexto.
4. Moraleja explícita en el cierre, en 6-9 palabras («Tu trabajo vale lo mismo para todos»).
5. Cifras en letra y cero palabras en inglés en la voz.

## Pasos en una sesión en la nube (todo por el MCP de Base44, app 6af862101565c330cf06389f)
1. Escribe en el sandbox de la app (`write_file`) este `gen_episodios.py` y un `eps.json` con los episodios. Cada episodio: `slug` (empieza por el número de la pieza), `set` (oficina, despacho, bar, calle o reunion), `hora` (0-23), `flow` (URL de un clip de la Biblioteca: entidad MediaAsset, tags flow/gemini), `moraleja` (6-9 palabras) y `escenas`.
2. Un guion del motor antiguo (`guion.json` con `escenas[].estilo/hablante/voz/texto/dibujo`) se pasa así a cada escena del estudio: `e` = estilo (gancho, gag, remate; la última escena va como `cierre`), `h` = hablante, `v` = voz, `t` = texto, `p` = dibujo.personajes, `a` = dibujo.acciones, `sello` (opcional, texto corto del remate).
3. En el sandbox (`run_command`): `pip install edge-tts`, `python3 gen_episodios.py eps.json /tmp/jb` y, por episodio, `node scripts/render.mjs /tmp/jb/<n>.json /tmp/jb/<n>.mp4 --hoja`. Mira la hoja `.jpg` y el `.qc.json` antes de dar el vídeo por bueno (≤ 30 s).
4. El render deja una copia publicable en `public/_render/`. Súbela con `upload_app_asset` usando `fileUrl = https://<preview_url>/_render/<archivo>?preview_token=<token>` (el token sale de `GET /api/apps/{app_id}/sandbox/preview-url`). La URL resultante (`https://media.base44.com/videos/public/6af862101565c330cf06389f/…mp4`) es el `video_externo`.
5. En `cola/NNN_…/post.json`: `"video_externo": "<esa URL>"`, `"renderizado": false` y `"motor": "neogest-studio"`. El ciclo de GitHub descarga el vídeo, pasa el control de audio y lo sube a la release; después lo evalúa Calidad.
6. Si /tmp del sandbox se ha borrado, repite el paso 1; si Base44 responde «busy» o 503, espera y reintenta.
