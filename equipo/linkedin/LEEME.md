# LinkedIn · página de empresa Neogest Lab

Creado el 16/11/2026 por Coordinación (orden del dueño). Manda `equipo/DIRECTIVA_VIGENTE.md`.

- Qué sale: los mismos reels aprobados (render desde el 14/11), 1 al día de lunes a viernes a las 08:45, alternando 1 promo de app y 1 episodio de El Jambo (el humor de oficina es contenido nativo de LinkedIn). Lo programa `herramientas/redes_buffer.py linkedin` (workflow `redes_buffer.yml`) con Buffer gratis.
- Texto: el del post de Instagram ya verificado, sin sus etiquetas, con 3 etiquetas y el cierre único con el enlace pulsable `/solicitar?app=<slug>&src=linkedin` (en LinkedIn los enlaces del texto sí se pueden pulsar).
- Fuera: carruseles, historias, piezas anteriores al 14/11 y «Parte 2». Configuración en `equipo/linkedin/config.json`; lo enviado y `ultimo_error` en `estado.json`.
- En espera hasta que el dueño cree la página y la conecte en Buffer (pasos en `equipo/pendiente_usuario.md`). Mientras, el workflow termina sin hacer nada.
- Métrica: solicitudes con origen `linkedin` en /panel/solicitudes del Centro.
- Probar sin enviar: `python3 herramientas/redes_buffer.py linkedin --simular`.
