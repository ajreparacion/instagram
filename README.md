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
| `herramientas/datos.py`, `control_datos.py` | Modo `datos`: reels explicativos con datos verificados y gráficos animados (contadores, barras, líneas, comparativas, anillos, rankings); ficha de datos obligatoria y control de calidad automático. Manual: `equipo/FORMATO_DATOS.md` |

## Secreto necesario
`PAGE_TOKEN` en *Settings → Secrets and variables → Actions*: token de página de Facebook vinculado a la cuenta (no caduca salvo cambio de contraseña).

Para lanzar un ciclo a mano: pestaña *Actions → Ciclo Instagram → Run workflow*.

## Voz
- Motor de voz en `equipo/voz.json` (`"motor"`) y cadena de respaldo (`"respaldo"`, Piper siempre al final; toda la locución sale del mismo motor):
  - `chatterbox`: Chatterbox de Resemble AI (código y pesos MIT, uso comercial libre; github.com/resemble-ai/chatterbox). Afinado para español de España `ResembleAI/Chatterbox-Multilingual-es-es` (MIT) sobre el multilingüe; CPU, en su propio venv (`herramientas/voz_chatterbox.py`). Expresividad: `exageracion` y `cfg`. Referencia de voz: solo `voces/referencia_usuario.wav` (la del propio usuario, si la deja en el repo) o una sintética con licencia libre generada con Kokoro (`referencia_kokoro`); nunca la de otra persona real.
  - `kokoro`: Kokoro-82M (Apache 2.0; hexgrad/Kokoro-82M), voces españolas `em_alex`, `ef_dora`, `em_santa`; muy rápido en CPU (`herramientas/voz_kokoro.py`).
  - `pocket`: Kyutai Pocket TTS (código MIT, pesos CC BY 4.0), voz «lola». Atribución obligatoria **Voz: Kyutai Pocket TTS (CC BY 4.0)**: se añade sola al final del texto de cada post que lleva esta voz. La voz «lola» procede de un clip de Mozilla Common Voice (CC0).
  - `piper`: Piper (MIT), voz `es_ES-davefx-medium`.
- Flujo «voz primero» (reels nuevos con guion.json): se genera la voz antes del render, cada escena se alarga a la duración real de su frase (la voz no se acelera) y los subtítulos palabra a palabra siguen el ritmo real de cada frase.
- Prueba comparativa a mano: *Actions → Prueba de voz → Run workflow* (resultado en `equipo/pruebas/prueba_voz.json`, vídeos y mp3 de voz sola en la release `pruebas`).