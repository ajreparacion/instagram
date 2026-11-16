# TikTok @neogestlab · cómo funciona

Creado el 16/11/2026 por Coordinación (orden del dueño). Manda `equipo/DIRECTIVA_VIGENTE.md`; esto es el manual operativo.

## Qué hace
`herramientas/redes_buffer.py tiktok` (workflow `redes_buffer.yml`, 07:23 y 16:23 hora de Madrid) coge los reels de `publicados/` con calidad aprobada y render desde el 14/11/2026, descarga el vídeo de Instagram, lo deja en la release pública «redes» y lo programa en Buffer (plan gratis) para TikTok. No hay producción aparte: TikTok vive de lo que Calidad ya aprobó.

- Huecos: 13:30 y 20:30 (Madrid), 2 piezas al día. Se cambian en `equipo/tiktok/config.json` (`huecos`).
- Mezcla: 2 de El Jambo por 1 de app. Orden de arranque en `orden_inicial`; después, por número de pieza.
- Como mucho 8 posts programados a la vez (Buffer gratis admite 10 por canal).
- Texto: el mismo del post de Instagram ya verificado, sin sus etiquetas, con el cierre único y etiquetas de TikTok. Factura7D lleva su cierre propio.
- Quedan fuera: carruseles e historias, piezas anteriores al 14/11 (logo antiguo sin comprobar), las «Parte 2» (en TikTok no está su parte 1) y cualquier texto con cierres prohibidos. Calidad puede rescatar una pieza antigua añadiéndola a `incluir_antiguos` si lleva el logo 2026.
- Lo enviado queda en `equipo/tiktok/estado.json`; `ultimo_error` no vacío = algo falló (lo mira el Supervisor).

## Qué necesita (una sola vez, lo hace el dueño)
Cuenta de TikTok de empresa, cuenta gratis de Buffer con ese TikTok conectado y el secreto `BUFFER_API_KEY` en GitHub. Pasos en `equipo/pendiente_usuario.md`. Sin el secreto el workflow termina sin hacer nada.

## Límites conocidos
- Etiqueta de IA: cada vídeo se envía con `isAiGenerated: true` (la etiqueta oficial «Generado por IA» de TikTok), y el texto lleva además «Voz (y personajes) generados por IA».
- La música va incrustada en el vídeo (MacLeod CC BY 4.0 o Pixabay, con atribución). Si TikTok silencia una pieza por música, se anota y esa pista deja de usarse.
- El enlace de la bio es `/solicitar?src=tiktok`; las altas con origen `tiktok` se ven en /panel/solicitudes del Centro.
- Probar sin enviar nada: `python3 herramientas/redes_buffer.py tiktok --simular`.
