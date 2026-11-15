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
