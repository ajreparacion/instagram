# Hub de enlaces «Expedientes Imposibles» (enlace de la bio)

- URL pública: https://expedientes-imposibles-bdf431bd.base44.app
- App Base44: «Expedientes Imposibles», id `6aecf6db89aecc23bdf431bd` (TanStack Start, React, JS).
- Regla fija: se edita SOLO con las herramientas de código del MCP de Base44 (`read_file`, `edit_file`, `write_file`, `run_command`, `create_checkpoint`). Nunca `edit_base44_app` ni `create_base44_app` con prompt (gastan créditos del builder).
- Texto del botón de enlace en Instagram (campo «Título»): «Fuentes y libros».

## Estado (6/11/2026, agente Hub)

- Rediseño hecho y guardado en el sandbox de Base44: checkpoint **`hub-movil-fuentes-apps-ref-ig`** (id `6aee18e83b6d5df298984d29`, commit `65240d7`). Punto de vuelta atrás: checkpoint `antes-hub-movil-fuentes-apps` (id `6aee1629f2b284dbb046e944`).
- **PENDIENTE DEL USUARIO: publicar.** El despliegue a producción (`POST /api/apps/{id}/deploy`) lo bloquea el sistema de permisos de la sesión del agente, así que la URL pública sigue sirviendo la versión anterior (comprobado 6/11 18:05: aún muestra «PARA SEGUIR INVESTIGANDO» y el botón de TikTok). Para publicarla: abrir la app en Base44 → botón «Publish» (o que una sesión con permiso ejecute `POST /api/apps/6aecf6db89aecc23bdf431bd/deploy` con `{"checkpoint_id": "6aee18e83b6d5df298984d29"}`). Publicar no gasta créditos del builder.
- Verificación hecha: `npm run build` sin errores en el sandbox; HTML renderizado en servidor (`http://localhost:5173` del sandbox) comprobado: las 4 secciones, 7 enlaces externos con `?ref=ig`, sin TikTok, sin frase de afiliado (correcto: ningún libro tiene `afiliado: true`), firma «By Neogest Lab» y logo `/marca-neogest/neogest-lab.webp` presentes.
- Captura: `equipo/perfil_kit/captura_hub_390x844.png` (Playwright, 390x844 a 2x, página completa). Es el HTML renderizado por el sandbox, abierto en local: el proxy de la sesión del agente bloquea `*.base44.app`, por eso el logo Neogest sale como hueco gris y la fuente es la del sistema en vez de Montserrat. En la app real se ven el logo y Montserrat.

## Estructura de la página (`src/routes/index.jsx`)

1. Cabecera: marca propia (carpeta + lupa ámbar, SVG en línea), sello «EXPEDIENTE ABIERTO», nombre, promesa, horario y botón «Seguir en Instagram».
2. «FUENTES Y LIBROS DE ESTA SEMANA»: una ficha por entrada de `src/datos/libros.json`. Debajo, la frase legal de Afiliados de Amazon **solo si alguna entrada tiene `afiliado: true`** (la misma condición activa la frase en /aviso-legal, vía `src/lib/rgpd/config.js`).
3. «APPS GRATUITAS DE NEOGEST LAB» + «Son nuestras…»: fichas de `hub.json → apps` con `visible: true` (orden: Insultator, GPS Andaluz).
4. «ÚLTIMO EXPEDIENTE»: `hub.json → ultimo_expediente` (número, fecha, resumen y botón «Ver el reel»).
5. «COLABORACIONES» (texto fijo) y pie: logo + «By Neogest Lab» + enlaces legales.

Todos los enlaces externos llevan `?ref=ig` (función `conRef` en `index.jsx`). Colores: azul noche `#0B1220`, ámbar `#F5B82E` (los mismos que la foto de perfil y las portadas de destacados).

## Cómo actualizar los libros y fuentes (cada semana, rol Mejora/Hub)

Archivo: **`src/datos/libros.json`** (array). Campos de cada entrada:

| Campo | Qué poner |
|---|---|
| `titulo` | Título exacto del libro, artículo o documental tal como aparece tras «Fuentes:» en el post.json publicado. Para un expediente sin libro, el texto de la línea de fuentes. |
| `autor` | Autor (y medio, p. ej. «John Waller · The Lancet»). Vacío si no procede. |
| `anio` | Año como texto («2008»). Vacío si no procede. |
| `expediente` | Número del expediente («001»). |
| `tema` | Título corto del caso (se muestra en gris). |
| `tipo` | `libro`, `articulo`, `documental` o `fuente` (cambia la etiqueta y el texto del botón). |
| `url` | Enlace. Vacío = se muestra sin botón. Con afiliado: la URL de Amazon.es CON la etiqueta. |
| `afiliado` | `true` solo si la `url` lleva etiqueta de afiliado de Amazon. Activa la frase legal y `rel="sponsored"`. |

Pasos:
1. Leer la línea «Fuentes:» de `publicados/NNN_*/post.json`. Solo libros, artículos o documentales REALES citados ahí; nunca inventar títulos ni URLs. Si una URL no se puede comprobar, dejar `url` vacía.
2. `read_file` de `src/datos/libros.json`; añadir las entradas nuevas arriba (lo más reciente primero) y quitar las de hace más de 2-3 semanas; `write_file` con `overwrite: true`.
3. Actualizar en `src/datos/hub.json` el bloque `ultimo_expediente` con el permalink del último reel (`publicados/NNN_*/resultado.json → enlace` o `estadisticas.json → posts[0].permalink`).
4. `run_command`: `node -e "JSON.parse(require('fs').readFileSync('src/datos/libros.json'))"` y `npm run build` (debe acabar sin error).
5. `create_checkpoint` con nombre descriptivo y publicar (botón «Publish» en Base44 o `POST /api/apps/{id}/deploy`).
6. Comprobar la URL pública (WebFetch funciona aunque curl esté bloqueado) y anotar la fecha aquí.

Cuando el usuario tenga el ID de Afiliados de Amazon.es: poner la URL con etiqueta en `url`, `afiliado: true`, y comprobar que la frase «En calidad de Afiliado de Amazon…» aparece en la página y en /aviso-legal.

## Apps (hub.json → apps)

URLs confirmadas el 6/11 con `GET /api/apps/platform/{id}/published-url`: Insultator `https://insultator-1259793a.base44.app`, GPS Andaluz `https://ruta-mia-alma.base44.app`. Las demás están con `visible: false` (no encajan con el canal; MEDICATOR no se promociona nunca).
