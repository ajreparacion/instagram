# Cola de pedidos a Gemini y Flow

Formato: `AAAA-MM-DD · rol · imagen|vídeo · 9:16|16:9 · descripción · uso` y, al servirlo, `→ HECHO <asset>`.
Se procesa solo cuando el dueño tiene el PC encendido; no esperes por ella (ver DIRECTIVA_VIGENTE «GEMINI Y FLOW · COLA»).

**Orden del dueño, reforzada 21/11/2026:** no sirve de nada generar algo sin objetivo y sin usar. Cada pedido de esta cola debe tener SIEMPRE una pieza concreta de `cola/` esperándolo en el campo «uso» — nunca generar «por si acaso» o para ir llenando la Biblioteca. En cuanto un asset se usa en un render ya publicado, se borra de la Biblioteca en esa misma pasada (no dejarlo para después): lo usado no debe tener que volver a mirarse ni reutilizarse.

## Pendientes
- 2026-11-20 · Claude (orden del dueño, "la intro se puede generar con gemini... se lo puede pedir también a chatgpt") · vídeo · 9:16 · fachada de una casa humilde de barrio español (pared desconchada, ventana con reja, puerta sencilla, tendedero con ropa, antena en el tejado — ver referencia vectorial en `src/studio/characters.js` SETS.casa de Neogest Studio), cámara fija con zoom lento de acercamiento (push-in), luz cálida de atardecer o de noche, sin personas, sin marcas ni matrículas ni número de puerta legible, estilo cabecera de comedia americana (tipo "Cosas de Casa"), 2-3 s, repetible en bucle (primer y último fotograma parecidos) · bucle "Cosas de Casa" de apertura/cierre de El Jambo (`equipo/serie_jambo.md`, `herramientas/estudio/gen_episodios.py`): UNA sola pieza, reutilizada en TODOS los episodios — no hace falta repetir el pedido por episodio. Si Flow/Gemini no lo da bien, el dueño puede pedir lo mismo a ChatGPT (Sora) a mano; cualquiera de los dos sirve, el primero que llegue se usa. Mientras tanto sigue el set vectorial `casa`, no bloquea nada. → HECHO gemini-22-casa-fachada.mp4 (10 s; recortar 2-3 s para el bucle)
- 2026-11-14 · Coordinación · vídeo · 9:16 · dron sigue un coche blanco por una carretera entre olivares andaluces al atardecer, pueblo blanco al fondo · GPS Andaluz → HECHO flow-13-gps-dron-olivares.mp4 + gemini-img-gps-1.jpg
- 2026-11-14 · Coordinación · vídeo · 9:16 · bar de tapas tranquilo tras el servicio, camarero sonriente recoge la barra · solución bar → HECHO flow-14-bar-camarero-recoge.mp4
- 2026-11-14 · Coordinación · vídeo · 9:16 · pequeño equipo de negocio local brindando con café al cerrar · celebración → HECHO flow-15-celebracion-cafe.mp4
- 2026-11-14 · Coordinación · imagen · 9:16 · descargar las 5 imágenes ya generadas en https://gemini.google.com/app/72d865b5fef0e073 (gps-2, bar-1, bar-2, celebracion-1, celebracion-2); la descarga falló · Biblioteca → HECHO gemini-img-gps-2.jpg, gemini-img-bar-1.jpg, gemini-img-bar-2.jpg, gemini-img-celebracion-1.jpg, gemini-img-celebracion-2.jpg

Nota 14/11: créditos de Flow casi agotados (≈6 puntos) hasta el reinicio del 11/12; priorizar Gemini.
