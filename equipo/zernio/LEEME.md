# Zernio — tercera vía de TikTok (21/11/2026)

El dueño conectó la cuenta de TikTok (@neogest.lab) y la de Instagram (@neogestlab) en Zernio
mediante el MCP de Zernio dentro de una sesión de Claude ("mcp zernio", orden del dueño). Ese
mismo día: cuenta de TikTok creada y conectada a Buffer, pero Buffer estaba caído por su propia
incidencia. Zernio queda como tercera vía (además de Buffer y Metricool) y, a diferencia de
Metricool, publica/programa de verdad desde el primer día — no solo borrador — porque su API
tiene documentación pública confirmada (`docs_search` del propio MCP) y el post de prueba pasó
`validate_post` sin avisos con el vídeo del Jambo ya subido a Base44.

## Lo único que falta — 1 paso del dueño

1. Entrar en https://zernio.com/dashboard/api-keys (con la misma cuenta que conectó TikTok/IG).
2. "Create API key" → copiarla (empieza por `sk_`, no se vuelve a mostrar).
3. Pegarla como secreto del repo `ajreparacion/instagram`: Settings → Secrets and variables →
   Actions → New repository secret → nombre `ZERNIO_API_KEY`, valor la clave copiada.

Sin ese secreto el workflow `redes_zernio.yml` se queda en espera sin hacer nada (no falla).

## Cómo funciona

- Workflow `.github/workflows/redes_zernio.yml`, dos pasadas al día (12:45 y 19:45, hora de Madrid).
- Reutiliza la misma selección de piezas y el mismo texto por canal que Buffer/Metricool
  (`herramientas/redes_buffer.py`), para que las 3 vías no publiquen nunca el mismo vídeo dos veces.
- Publica con `POST /v1/posts` (contenido + `scheduledFor` + `platforms: [{platform: tiktok,
  accountId}]`), sin forzar `tiktokSettings` — si Zernio algún día exige privacidad/consentimiento
  explícitos, el error de la API lo dirá con el campo exacto y se añade entonces.
- Cuenta ya fijada en `config.json` (`account_id`): `6b00b30e062d3d918320d801`.

## Si algo falla

`equipo/zernio/estado.json` → `ultimo_error` tiene el mensaje exacto de la última llamada a la
API de Zernio. El Supervisor lo revisa en cada pasada.
