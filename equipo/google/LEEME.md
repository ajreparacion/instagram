# Google Business Profile · ficha de Neogest Lab

Creado el 16/11/2026 por Coordinación (orden del dueño). Manda `equipo/DIRECTIVA_VIGENTE.md`.

- Google no admite vídeo por API: se publica una «Novedad» con una imagen (primer fotograma del reel, 1080x1080 sobre fondo #071226), el texto y el botón «Registrarse» que lleva a `/solicitar?app=<slug>&src=google`.
- Qué sale: solo promos de apps de negocio y de uso general (nada de El Jambo ni de GPS Andaluz), lunes, miércoles y viernes a las 10:15. Lo programa `herramientas/redes_buffer.py google` (workflow `redes_buffer.yml`) con Buffer gratis.
- Texto: el del post de Instagram ya verificado, sin etiquetas, sin llamadas a comentar o reenviar, máximo 1.450 caracteres, sin teléfonos (Google los rechaza).
- Requisito: la ficha tiene que estar VERIFICADA por Google; sin verificar, Buffer no la conecta. Pasos del dueño en `equipo/pendiente_usuario.md`.
- Configuración en `equipo/google/config.json`; lo enviado y `ultimo_error` en `estado.json`. Métrica: solicitudes con origen `google`.
- Probar sin enviar: `python3 herramientas/redes_buffer.py google --simular`.
