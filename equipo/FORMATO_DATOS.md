# Formato «datos» (reels explicativos con datos verificados y gráficos animados)

Manual para Estratega, Investigador/Creador y Calidad. Código: `herramientas/datos.py` (render), `herramientas/control_datos.py` (control), ejemplo: `herramientas/ejemplo_guion_datos.json`.

## Cuándo usarlo
Reels para @neogestlab sobre IA, negocios, digitalización y ahorro de tiempo con apps, en los que **una cifra con fuente** es el gancho. Mismo cierre único de siempre («Pide tu prueba gratuita: sin tarjeta, sin datos bancarios y sin compromiso»; en pantalla «Prueba gratuita · sin tarjeta · sin compromiso») y mismo bloque `monetizacion` en `post.json`. Sin música cocida: la pone Instagram (`audio_ig`); el vídeo lleva voz y efectos sintetizados. Voz genérica de España (flujo voz primero ya existente), nunca la del dueño.

## Las 5 fases
1. **Ficha de datos.** Una entrada por cifra con fuente oficial (INE, Eurostat, Banco de España, ministerios, informes públicos…), `url`, `anio` y `comprobado` (fecha y cómo: «11/11/2026, abierta la tabla X de la web del INE, columna Y»). Solo se pone `"estado": "verificado"` tras **abrir la fuente** y ver la cifra. Si no se puede comprobar, `"pendiente"` y no se publica.
2. **Tres ganchos** (3-8 palabras, con la cifra) y se elige uno con criterio escrito (qué sorprende, qué promete, que se entienda sin sonido). Se anotan los tres y el motivo en el `post.json` (`_ganchos`).
3. **Guion escena a escena**, un gráfico por escena (`grafico`), 12-45 s, escenas de 2,4 s o más.
4. **Voz primero** con el motor vigente (publicar_gh.py ya lo hace: `--solo-locucion`, voz, `--tiempos`). Las cifras en la voz van **con letras** y deben coincidir con la ficha.
5. **Render + control + Calidad.** `control_datos.py` y nota de Calidad ≥ 90.

## Esquema del guion
```json
{
  "titulo": "Datos 001: ...", "semilla": 1, "modo": "datos", "musica": false,
  "portada_texto": "...", "gancho_corto": "Pierdes *14 horas* al mes",
  "datos": [
    {"id": "d1", "valor": 12.5, "unidad": "%", "etiqueta": "de las pymes ...", "fuente": "INE", "url": "https://...",
     "anio": 2025, "estado": "verificado", "comprobado": "11/11/2026: abierta la tabla ... del INE"},
    {"id": "d2", "unidad": "h", "etiqueta": "horas por tarea", "serie": [{"etiqueta": "Facturas", "valor": 6}, {"etiqueta": "Citas", "valor": 4}],
     "fuente": "...", "url": "https://...", "anio": 2025, "estado": "verificado", "comprobado": "..."}
  ],
  "escenas": [
    {"estilo": "gancho", "grafico": "texto", "texto": "Pierdes *14 horas* al mes", "voz": "Pierdes *catorce horas* al mes."},
    {"estilo": "dato", "grafico": "contador", "datos": ["d1"], "texto": "Titular de la escena", "voz": "..."},
    {"estilo": "giro", "grafico": "texto", "texto": "Y se hace *solo*", "voz": "..."},
    {"estilo": "cierre", "grafico": "texto", "texto": "Pide tu *prueba gratuita*", "voz": "Pide tu *prueba gratuita*: sin tarjeta, sin datos bancarios y sin compromiso."}
  ]
}
```
- `grafico`: `contador` (1 dato) · `barras` (2-6 elementos; `"destacar"`: id, posición o etiqueta; por defecto el mayor) · `linea` (2-9 puntos, normalmente una `serie` con los años; `"eje_cero": false` solo si se explica) · `comparar` (2 datos; `"ratio": false` quita el «×N veces») · `porcentaje` (1 dato entre 0 y 100) · `ranking` (2-5 elementos, ordenados de mayor a menor; `"orden": "dado"` respeta el del guion) · `texto` (texto cinético: gancho, giro, cierre).
- Los valores que se pintan salen **solo** de la ficha. Cada escena con gráfico lleva `"datos": ["id", ...]`; cada elemento de barras/ranking/línea es un id o una `serie`.
- Formato: números a la española (1.234,5); `%` con espacio fino; `"escala": "M"` pinta el valor dividido entre un millón con «M»; `"decimales"` fija decimales.
- `*palabra*` marca énfasis (voz y texto); en el gancho la palabra acentuada sale en cian.
- Cada escena con datos muestra el pie «Fuente: <fuente> (<año>)» (año siempre visible).
- **Puerta dura:** si un dato referenciado no tiene fuente, url, anio, comprobado o su estado no es `verificado`, `hacer_reel.py` termina con error. `--ensayo` salta la puerta y pinta «ENSAYO · DATOS FICTICIOS» en todos los fotogramas: **solo para pruebas; publicar_gh.py nunca lo pasa** y `pre_entrega.py` marca error si la ficha no está verificada.

## Reglas
- Nunca cifras sin fuente ni inventadas; ni una sola en la voz que no esté en la ficha.
- Redondeos honestos (el que se pinta es el real redondeado, nunca hacia lo que conviene); no cortar ejes para exagerar; el rótulo «×N veces» sale de los valores de la ficha.
- El año de la cifra siempre visible; si la fuente es de hace más de 3 años, decirlo en la voz.
- Nada de marcas de terceros (ver `marcas_prohibidas.json`).
- Modelos baratos: Haiku para tareas mecánicas (rellenar la ficha, comprobar formatos), Sonnet para guion; nunca Fable.

## Comandos
```
cd herramientas
python3 hacer_reel.py ejemplo_guion_datos.json /tmp/datos_test/prueba.mp4 --ensayo     # prueba con cifras ficticias
python3 hacer_reel.py ../cola/NNN_x/guion.json ../cola/NNN_x/video.mp4                 # real (el ciclo usa publicar_gh.py)
python3 control_datos.py ../cola/NNN_x/guion.json ../cola/NNN_x/video.mp4 --salida ../cola/NNN_x/calidad_datos.json
python3 pre_entrega.py ../cola/NNN_x
```
`control_datos.py` bloquea: ficha incompleta, duración fuera de 12-45 s, escena de menos de 1,2 s, gancho de más de 8 palabras, tramo estático ≥ 1 s, fotogramas negros, pico > -1 dBTP, sin cierre. Avisa de: sonoridad fuera de -14 ± 1,5 LUFS (el vídeo va sin música y la voz se mezcla después), más de 4 palabras/s, cifras de la voz que no salen de la ficha, cierre sin prueba gratuita, falta `monetizacion`. Guarda `control/gancho.jpg`, `medio.jpg` y `cierre.jpg` junto al guion: Calidad los mira (fotograma 0 = el gancho).
