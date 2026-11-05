# Expedientes Imposibles · @nosabesloquehasvisto

Sistema automático de la cuenta de Instagram. Funciona sin ningún dispositivo encendido.

## Cómo funciona
- **Agentes de Claude** (tareas programadas en la nube): investigan, escriben el guion (`cola/<NNN_tema>/guion.json` o `remaster.json`) y el texto (`post.json`), revisan la calidad (`calidad.json`), analizan y planifican (`equipo/`).
- **GitHub Actions** (`.github/workflows/ciclo.yml`, cada 30 min por la tarde-noche): `publicar_gh.py` renderiza el vídeo, le pone la voz, lo guarda en la release `cola`, lo publica a su hora si Calidad lo aprobó, responde comentarios con la palabra clave y actualiza `estadisticas.json`.

## Carpetas
| Carpeta | Qué hay |
|---|---|
| `cola/` | Reels pendientes (solo JSON; el vídeo está en la release `cola`) |
| `publicados/` | Reels ya publicados con su `resultado.json` (enlace e id) |
| `revision/` | Reels que Calidad no aprobó |
| `errores/` | Reels que fallaron 3 veces |
| `originales/` | Datos de los reels antiguos de la cuenta (para remasterizar) |
| `equipo/` | Plan semanal, aprendizajes, estándar de calidad, ajustes de voz, mejoras |
| `herramientas/` | Generadores de vídeo (`hacer_reel.py`, `remaster.py`) |

## Secreto necesario
`PAGE_TOKEN` en *Settings → Secrets and variables → Actions*: token de página de Facebook vinculado a la cuenta (no caduca salvo cambio de contraseña).

Para lanzar un ciclo a mano: pestaña *Actions → Ciclo Instagram → Run workflow*.
