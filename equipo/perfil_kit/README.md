# Kit visual del perfil @nosabesloquehasvisto (Expedientes · Misterios Reales)

Diseño propio, sin marcas ni logos de terceros, sin texto en las imágenes. Colores: azul noche `#0B1220` (fondo) y ámbar `#F5B82E` (cristal de la lupa, igual que el sello de veredicto de los reels y el hub). Mismo sistema que el hub de enlaces (`equipo/hub_enlaces.md`).

## Archivos

| Archivo | Tamaño | Para qué |
|---|---|---|
| `foto_perfil_1080.png` | 1080x1080 (192 KB) | Foto de perfil: carpeta de expediente blanca con pestaña y lupa de cristal ámbar con interrogación. Comprobada a 110 px en círculo: una sola forma reconocible. |
| `destacado_01_EMPIEZA_1080x1920.png` | 1080x1920 | Portada del destacado **EMPIEZA** (icono: play). |
| `destacado_02_TOP_CASOS_1080x1920.png` | 1080x1920 | Portada de **TOP CASOS** (icono: estrella). |
| `destacado_03_REAL_1080x1920.png` | 1080x1920 | Portada de **¿REAL?** (icono: interrogación). |
| `destacado_04_FUENTES_1080x1920.png` | 1080x1920 | Portada de **FUENTES** (icono: libro abierto). |
| `destacado_05_PARTE_2_1080x1920.png` | 1080x1920 | Portada de **PARTE 2** (icono: carpeta con doble flecha). |
| `captura_hub_390x844.png` | captura | Captura del hub de enlaces a 390x844 (ver `hub_enlaces.md`). |
| `filosofia_visual.md` | texto | Filosofía de diseño del kit (por si hay que crear más piezas iguales). |

Todos los PNG pesan menos de 1 MB. Los iconos de las portadas están centrados en el círculo que Instagram recorta (centro 1080x1080 de la imagen), así que se ven enteros en la burbuja del destacado.

## Cómo subirlos desde la app de Instagram (móvil)

Antes: pasar los 6 PNG al móvil (Google Drive, Telegram «Mensajes guardados», AirDrop o cable) y guardarlos en la galería.

### Foto de perfil
1. Abre tu perfil → **Editar perfil** → toca la foto → **Nueva foto de perfil** (o «Cambiar foto de perfil»).
2. Elige `foto_perfil_1080.png` de la galería. No hagas zoom: ya viene centrada para el recorte circular.
3. **Listo**. Comprueba que a tamaño pequeño (en comentarios o en la lista de historias) se reconoce la carpeta con la lupa ámbar.

### Portadas de destacados
Instagram solo deja poner de portada una imagen de la galería al crear o editar un destacado, y la imagen NO necesita publicarse como story (opción «Editar portada → galería»).

Para cada destacado, en este orden de izquierda a derecha (EMPIEZA, TOP CASOS, ¿REAL?, FUENTES, PARTE 2):
1. Si el destacado ya existe: mantén pulsado su círculo en el perfil → **Editar destacado** → **Editar portada** → icono de galería (abajo a la izquierda) → elige el PNG correspondiente → ajusta sin zoom (el icono ya está centrado) → **Listo** → **Listo**.
2. Si no existe: publica primero la story que irá dentro (el equipo redacta las stories; ver `perfil_propuesto.md` §5) → ábrela → **Destacar** → **Nuevo** → nombre (máx. 10 caracteres: `EMPIEZA`, `TOP CASOS`, `¿REAL?`, `FUENTES`, `PARTE 2`) → **Añadir**. Después, edita la portada como en el paso 1.
3. El orden en el perfil es el de la última story añadida: para fijarlo, añade stories empezando por PARTE 2 y acabando por EMPIEZA (el más reciente queda a la izquierda). Si solo caben 4 en pantalla, FUENTES debe quedar en 2.º lugar.

### Comprobación final
- Foto y 5 burbujas con el mismo azul noche; iconos blancos nítidos; sin texto dentro de las burbujas (el nombre va debajo, lo pone Instagram).
- Enlace de la bio: `https://expedientes-imposibles-bdf431bd.base44.app` con título «Fuentes y libros».

## Regenerar o añadir portadas
Script de origen: HTML/SVG renderizado con Playwright (Chromium) y optimizado con Pillow; no usa fuentes externas (nada de texto). Para una portada nueva basta un icono SVG en trazo blanco de 30 px centrado en (0,0) dentro de un radio de ~220 px, sobre el fondo `#0B1220` de 1080x1920. Mantener: sin texto, sin marcas ajenas, un solo icono, menos de 1 MB.
