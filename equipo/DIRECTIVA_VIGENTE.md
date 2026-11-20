# DIRECTIVA VIGENTE · equipo de redes de Neogest Lab
Versión limpia del 15/11/2026 (orden del dueño). Sustituye a todo lo anterior; la versión apilada está íntegra en `equipo/archivo/DIRECTIVA_hasta_2026-11-15.md` (solo consulta, no manda).

## 1. Cómo se usa y cómo se cambia
- Cada pasada lee esta directiva y su archivo de rol (`equipo/roles/<rol>.md`). Si algo de otro archivo del repo la contradice, manda esta directiva; si dos textos chocan y aquí no se resuelve, manda la orden más reciente del dueño.
- Solo el Estratega (o Coordinación por orden del dueño) edita este archivo. Una orden nueva SUSTITUYE la línea antigua en su sección y se anota en una línea en «Registro de cambios»; nunca se apila encima ni se añaden cabeceras «ignora lo de abajo».
- Los archivos de rol no repiten la directiva: solo misión, horario, pasos y límites propios. Lo técnico de formatos de render antiguos (modos app, presentador, plantilla, datos) está en `equipo/archivo/INSTRUCCIONES_EQUIPO_hasta_2026-11-15.md` y en `equipo/FORMATO_DATOS.md`.
- El prompt de tu tarea programada puede traer capas antiguas (DIRECTIVA DE VÍDEO del 14/11, pasos de add_repo o clonado, @iafacil.trucos, fire_trigger, «reserva anulada», tope de 30 s para todo…). Están derogadas: solo valen esta directiva y tu archivo de rol.
- Español de España en todo. No se le pregunta al dueño: se decide, se deja constancia y se le entregan informes.

## 2. Mapa del equipo y horarios (hora de Madrid)
| Rol | Cuándo | Modelo | Archivo |
|---|---|---|---|
| Creador | 09:51 y 15:51 a diario | Sonnet | roles/creador.md |
| Calidad | 11:41 y 17:41 (tarea única «Calidad»; después de cada pasada del Creador) | Sonnet, **API directa con tool use (piloto, no Claude Code)** | roles/calidad.md + `herramientas/calidad_api.py` |
| Supervisor | 12:27 y 18:27 a diario | Haiku, **API directa (no Claude Code)** | roles/supervisor.md + `herramientas/supervisor_api.py` |
| Cazador de virales | lunes 08:23 | Sonnet | roles/cazador.md |
| Remasterizador | lunes, miércoles y viernes 09:00 | Sonnet | roles/remasterizador.md |
| Analista (+ monetización los domingos) | martes, jueves y domingo 23:23 | Haiku | roles/analista.md |
| Estratega | lunes 10:13 | Sonnet | roles/estratega.md |
| Mejora de producción | miércoles 11:13 | Sonnet | roles/mejora.md |
| Comunidad | 19:37 a diario | Haiku | roles/comunidad.md |
| Centro (vídeos y demos del Centro) | lunes y jueves 11:17 | Sonnet | roles/centro.md |
| Repescador (vía API, no Claude Code) | cada 2 h, 08:33-20:33 | determinista (sin modelo salvo varios casos) | roles/repescador.md + `herramientas/repescador_api.py` |
| Ventas · prospección | L-V 09:43, EN PAUSA (ver su rol) | Sonnet | roles/ventas.md |
Aviso (16/11, comprobado por Coordinación): la tarea programada llamada «IG nube · Supervisor (repo)» (13:27 a diario) NO ejecuta el checklist de `roles/supervisor.md` — su prompt real es «cerrar la cola de Gemini» (marcar `equipo/cola_gemini.md` con los assets ya subidos a Base44), tarea distinta y necesaria porque la tarea de Gemini no puede hacer push. El checklist real del Supervisor no tenía ninguna tarea programada propia desde el 15/11 (solo una prueba manual); desde el 16/11 corre por `.github/workflows/supervisor_api.yml` (ver fila de arriba). No tocar ni renombrar esa tarea de Claude Code sin avisar: sigue cerrando la cola de Gemini.
Tareas en pausa desde el 15/11 (si alguna se dispara, NO trabaja: termina en una línea, sin tablón ni commit):
- «IG nube · Calidad (repo)» de las 12:51 y «IG nube · Calidad (noche) (repo)» de las 19:31: fusionadas en la Calidad de cada 2 h.
- «IG nube · Analista de monetización (repo)» (domingos 18:17): fusionada en el Analista.
- «Ventas · Prospección (repo)»: en pausa.
Fuera del repo (no leen este archivo, se citan para el mapa):
- «Lote diario de comentarios» (08:21): prepara comentarios para que el dueño los publique a mano; doc del proyecto `claude/redes/comentarios_diarios.md`.
- «Laboratorio de ideas» (sábados): propuestas de apps nuevas en el doc del proyecto `claude/ideas/propuestas-apps.md`.
- «Gemini: procesar cola» (15:48, solo con el PC del dueño encendido): sirve `equipo/cola_gemini.md` y sube el resultado a la Biblioteca de Neogest Studio.
- «Guionista Gemini (API)» (09:15 y 15:15, 36 min antes de cada Creador; orden del dueño 17/11): pide guiones de El Jambo a Gemini (API directa, gratis) con la biblia, los motivos de rechazo de Calidad y los patrones virales; deja borradores en `equipo/guiones_gemini/pendientes/` que el Creador usa, ajusta o descarta — nunca bloquea su pasada. `.github/workflows/guionista_gemini.yml` + `herramientas/guionista_gemini.py`.
Aviso (18/11, orden del dueño, PR pendiente de revisión): Calidad pasa entera a API directa con tool use (`.github/workflows/calidad_api.yml` + `herramientas/calidad_api.py`, Sonnet, mismo horario y criterio que `roles/calidad.md`); no lee hechos_verificados/prohibido_afirmar de Base44 (ese MCP no existe fuera de Claude Code). Creador: SOLO la parte mecánica (texto/metadata de post.json de piezas rechazadas, sin tocar vídeo) pasa a API directa (`.github/workflows/creador_api.yml`, solo `workflow_dispatch` hasta validarlo); el resto del rol (guiones, render real en Neogest Studio) sigue en Claude Code porque necesita el MCP de Base44. Detalle y motivos en `equipo/tablon.md` (18/11/2026).

## 3. Protocolo de cada pasada
0. Mira el mapa (§2): si tu tarea está fusionada, en pausa o se ha disparado fuera del día u hora de tu rol, termina en una línea sin hacer nada.
1. Repo: las tareas son de tipo Claude Code con `ajreparacion/instagram` conectado. Nada de add_repo ni clonar de nuevo: `git checkout main && git pull --rebase origin main`.
2. Lee esta directiva, tu rol y las últimas 40 líneas de `equipo/tablon.md`; atiende o responde lo que otro rol te pida allí.
3. Trabaja. Lee solo lo que vayas a usar. Toca solo tus archivos: otros roles escriben a la vez en main.
4. Al terminar, UNA línea al final de `equipo/tablon.md`: «AAAA-MM-DD HH:MM UTC · <rol> · qué hiciste · qué necesitas y de qué rol (o "nada")», dentro de tu commit.
5. Commit en main («<rol>: <qué>») y `git push origin main`. Si lo rechaza por cambios remotos: `git pull --rebase` y repite (máx. 3). Conflicto en tablón o pendiente_usuario: quédate con la versión remota y vuelve a añadir tus líneas. Si da 403: anótalo en `equipo/pendiente_usuario.md` («Acceso al repo», con el nombre de la tarea) y no reintentes.
6. Las tareas no se lanzan unas a otras (list_triggers/fire_trigger no sirven): la coordinación pasa por el tablón.
7. Mensaje al dueño solo si tu rol lo prevé o algo bloquea; si no había nada que hacer, termina en una línea.

## 4. Marca y cuentas
- Cuentas: Instagram @neogestlab · YouTube NeogestLab (@neogestlab, ID UCEDMuvCre43IhS0sR6aNEew) · página de Facebook Neogestlab (ID 1437632859434095) · TikTok @neogestlab (cuenta de empresa, alta el 16/11/2026; pendiente de que el dueño la cree y conecte Buffer) · página de LinkedIn y ficha de Google Business Profile de Neogest Lab (pendientes de que el dueño las cree y conecte en Buffer). @iafacil.trucos y @nosabesloquehasvisto son nombres antiguos de la misma cuenta.
- Logo 2026: isotipo «N» de circuitos + «NEOGEST LAB». Kit oficial (solo estos archivos, nunca redibujar): https://flashy-seven-flow-pro.base44.app/marca-2026/ (negativo para fondo oscuro, color para fondo claro, transparente, isotipos, iconos, intro v3). URL permanente: https://media.base44.com/images/public/6ae5244d4e2b32702f0a3cd6/711454aae_neogestlab-logo-2026.webp
- PROHIBIDO el logo «NL» neón (c25965060_neogest-lab-logo.webp) y su paleta azul/magenta/coral: donde aparezca, se sustituye.
- Paleta 2026: #13305A, #12B8C8, #8DC63F, #404040, fondo negativo #071226. Tipografía Montserrat. Firma exacta «By Neogest Lab». Cada app conserva su nombre; la empresa es siempre Neogest Lab.
- Repo PÚBLICO (Instagram descarga por jsDelivr y la release): nunca claves, tokens, contraseñas, cookies ni datos personales en archivos, commits o registros. Secretos solo en GitHub Actions (nombres: YOUTUBE_API_KEY, YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN, FACEBOOK_PAGE_TOKEN, PAGE_TOKEN, PUENTE_TOKEN, BUFFER_API_KEY, GEMINI_API_KEY).

## 5. Formatos
Las cifras de 20, 22 o 35 s de textos antiguos quedan derogadas.

**El Jambo que sabe (serie de humor; personajes desde el 16/11: Rosa Melano —jefa tirana—, Felipe Lotas y Sindy Entes —empleados que lo sufren—, Neo —la IA que resuelve—; biblia v3 en `equipo/serie_jambo.md`)**
| Campo | Regla |
|---|---|
| Duración | 15-25 s, nunca más de 30 |
| Estructura | 0-0,5 s la IMAGEN sola ya cuenta la situación reconocible, sin necesitar leer ni oír nada · 0-2 s texto + 1.ª frase confirmándola («Cuando…», «POV:» o pregunta) · 2-6 s planteamiento que deja una pregunta abierta en la cabeza del espectador (qué va a pasar, no solo qué pasa) · 6-16 s escalada en 3 golpes, cada uno peor · 16-21 s giro que resuelve el conflicto rompiendo lo que el espectador esperaba · 21-24 s cierre, que vuelve al mismo plano/pose/elemento del gancho (bucle visual sin costura) y abre el siguiente bucle (parte 2 o pregunta) antes de que el anterior se sienta del todo cerrado. Un conflicto por episodio. «Que lo haga la Jupillo» solo si es el remate. Bucle de retención (orden del dueño 20/11, inspirado en el bucle de dopamina de casino): apuestas (algo que Felipe o Sindy pueden perder de verdad) → pregunta (curiosidad explícita, no solo planteamiento) → giro (sorpresa real, no previsible) → reenganche (el cierre ya abre el siguiente bucle, nunca deja la tensión en reposo) |
| Imagen | Dibujos de calidad de Neogest Studio (ver §6); subtítulos palabra a palabra; cambio de plano cada 1,5-2 s |
| Silencios máx. | 0,6 s |
| Volumen | −14 LUFS, pico real −1 dB |
| Voz | edge-tts por personaje (§6) |
| Música | en primer plano (§6), con atribución si es MacLeod |
| Cierre en vídeo | giro de Neo + moraleja en una línea (siempre, orden del dueño 16/11) + seguir para la parte 2 o pregunta |
| Cierre en el post | dato con fuente · «Pide tu prueba gratuita: sin tarjeta, sin datos bancarios y sin compromiso» con el enlace /solicitar · «Mándaselo a…» · atribución musical · una pregunta concreta (una palabra o un número) · «Voz y personajes generados por IA» |

**Promo de app**
| Campo | Regla |
|---|---|
| Duración | 25-45 s |
| Estructura | ANTES/DESPUÉS con bucle de retención: apuestas (problema real que duele, 2 s) → pregunta (qué pasa si la app lo resuelve, antes de enseñarlo) → giro (la app lo resuelve en pantalla con datos ficticios, de forma más rápida o distinta de lo esperado) → resultado. Abre con lo que no hacen las demás (IA, cámara, lectura de documentos…; brief del proyecto `claude/redes/promos_diferenciales_2026-11-15.md`); «la única» solo con prueba de competencia anotada. Nada de escaparate de funciones básicas ni cifras intermedias sin explicar; calculadoras congeladas hasta rehacerlas así |
| Silencios máx. | 1,5 s |
| Volumen | −14 LUFS |
| Voz | ElevenLabs Johnny en la versión final (se produce en el estudio de vídeo del Centro, como los cortos 7xx); ensayos y respaldo con edge-tts (es-ES-ElviraNeural) si el presupuesto del mes está agotado |
| Música | en primer plano (§6) |
| Cierre en vídeo | estático ≤ 3 s con el logo 2026 y «By Neogest Lab»; «Enlace en el perfil», nunca la URL base44 en pantalla |
| Cierre en el post | cierre único de prueba gratuita con el enlace /solicitar?app=<slug>&src=<canal>; excepción documentada: Factura7D «Pruébala gratis: 2 facturas al mes, sin permanencia» |

**Vídeo de presentación del Centro**: manda el doc del proyecto `claude/redes/rehacer_videos_centro_elevenlabs.md`. Resumen de lo que consta en el repo y en la tarea del Centro: vertical, gancho ≤ 8 palabras en el fotograma 0, las 3 funciones más destacables en ANTES/DESPUÉS, cierre ≤ 3 s, subtítulos fuera de la zona que tapa Instagram, plano cada 1,5-2 s, −14 LUFS y pico −1 dB, voz final ElevenLabs Johnny (ensayos con edge-tts). Detalle operativo en roles/centro.md.

**Reels de datos (6xx)**: manual `equipo/FORMATO_DATOS.md`; cada cifra con fuente oficial abierta y `estado: "verificado"`; misma voz, música y volumen que la promo.

## 6. Voz y música
- Redes (El Jambo y reels): edge-tts. Rosa es-ES-ElviraNeural −4 Hz · Felipe es-ES-AlvaroNeural −4 % / −2 Hz · Sindy es-ES-XimenaNeural +8 % / +4 Hz · Neo es-ES-AlvaroNeural (pitch 0); detalle en `equipo/voz.json` y `herramientas/estudio/LEEME.md`.
- Cadena de audio del 14/11: una frase por archivo, silenceremove a −45 dB, aresample 48 kHz, highpass 70 Hz, compresor 2,5:1 a −20 dB (ataque 8 ms, suelta 120 ms), +2 dB en 3,5 kHz, sin reverb ni paso bajo; música 0,6 con ducking 2,5:1; máster −14 LUFS, pico real −1 dB.
- ElevenLabs voz Johnny (única herramienta de pago autorizada; plan Starter, 39.756 caracteres al mes): solo en la versión final de los vídeos de presentación del Centro, las promos de app y los reels de datos. Presupuesto: 30.000 caracteres al mes entre todo (unas 55 piezas de ~500 caracteres); el resto del saldo es reserva y nunca se compra saldo extra. Antes de gastar se suma el registro de `claude/redes/rehacer_videos_centro_elevenlabs.md` y `gasto.log`; agotado el presupuesto, edge-tts. El Jambo sigue con edge-tts para reservar los caracteres del presupuesto compartido a las promos de app y los reels de datos.
- Audios guardados y reutilizados SIEMPRE (orden del dueño 16/11): ningún audio de ElevenLabs se genera dos veces. Cada frase se guarda fuera del sandbox (release «voces» del repo o Biblioteca de Neogest Studio) con nombre `eleven_<voz>_<hash del texto>.mp3` y un índice `equipo/voces_indice.json` (texto, voz, fichero, caracteres, fecha); antes de gastar se busca ahí y solo se genera lo que falte. Las frases fijas (cierre de prueba gratuita, «Enlace en el perfil», nombres de apps) se generan una vez y se reutilizan en todas las piezas. Lo mismo para música, efectos, clips de Flow/Gemini, capturas de demo y renders: se reutiliza lo que ya existe antes de producir nada nuevo. `/tmp` no vale como almacén (se borra al reiniciar el sandbox).
- PROHIBIDA la voz del dueño (voz_dueno/*, referencias, clones). Retirados Chatterbox, MeloTTS, Kokoro y Piper.
- Pronunciación: «AJ» = «Ajota» de corrido; «Excel» = «Éxcel». Cifras en letra, sin palabras en inglés ni «IA» en la voz, y nunca un nombre propio como primera palabra (whisper falla).
- Música en primer plano, que resalte (con voz baja como mucho 6 dB y se oye clara entre frases). Fuentes: Kevin MacLeod (incompetech.com, CC BY 4.0; en el post: «Música: "<título>" de Kevin MacLeod (incompetech.com), licencia CC BY 4.0») o la biblioteca Pixabay de Neogest Studio. Nada con licencia dudosa.
- Recursos que hay que usar de verdad (orden 15/11): Neogest Studio (Base44 6af862101565c330cf06389f: render vertical, personajes con boca sincronizada, decorados, música y SFX, cierre con logo 2026), su Biblioteca de clips Flow/Gemini (entidad MediaAsset, tags flow/gemini + categoría) y la música Pixabay del estudio. Lo que falte se pide en `equipo/cola_gemini.md` (fecha · rol · imagen/vídeo · 9:16/16:9 · descripción · para qué pieza) y no bloquea. Sin caras reconocibles, marcas ni texto en esas imágenes.

## 7. Control de calidad y publicación
- Calidad revisa cada vídeo en cuanto está renderizado (no solo lo que sale pronto), en su pasada siguiente (11:41 o 17:41). Aprobado solo con nota ≥ 90 según `equipo/estandar_calidad.md` (v9: «parece hecho por humanos»; si suena a IA, máximo 89).
- Los reels de redes se publican solo con `calidad.json` aprobado; el ciclo no publica sin él. Una pieza con visto bueno expreso del dueño (`"aprobado_por": "dueño"` en su calidad.json) no se reevalúa, no se rechaza ni se mueve: sale a su hora; Calidad solo añade sus observaciones en `nota_calidad`. Solo los vídeos de presentación del Centro esperan además el aprobado del dueño en el editor del Centro (VideoMezcla).
- Todo lo programado debe salir a su hora: si una pieza no tiene nota ≥ 90 a 60 min de su hora, se mueve al siguiente hueco libre; nunca dos piezas en el mismo hueco ni encima de una aprobada.
- Publicación: GitHub Actions (`ciclo.yml`, relanzado por `reloj.yml` cada 15 min) renderiza, publica en Instagram, Facebook (por ID de página, `/video_reels` para reels) y YouTube (Short con `herramientas/youtube.py`; `"youtube": {"omitir": true}` para no subir uno), y actualiza estadisticas.json y registro.log. Las llamadas a las API de Facebook y YouTube solo funcionan dentro de Actions.
- Un `video_externo` en post.json (vídeo ya terminado, p. ej. de Neogest Studio) lo descarga el ciclo y lo sube a la release; su calidad.json anterior caduca.
- Vídeos y audios nunca en git: van a la release «cola». Descarga: `ID=$(gh api repos/ajreparacion/instagram/releases/tags/cola --jq '.assets[] | select(.name=="NOMBRE.mp4") | .id')` y `gh api -H "Accept: application/octet-stream" repos/ajreparacion/instagram/releases/assets/$ID > NOMBRE.mp4`.
- post.json de un reel lleva siempre: `texto`, `cuando` (AAAA-MM-DDTHH:MM:00+01:00), `prueba_no_seguidores`, `comentario_fijado`, `avance_siguiente`, bloque `monetizacion` {objetivo, oferta, paso_embudo}, bloque `youtube` {titulo ≤ 100 caracteres con #Shorts, descripcion con /solicitar?…&src=youtube y «By Neogest Lab», etiquetas} y, si procede, `facebook`. `python3 herramientas/pre_entrega.py` sin ERRORES antes de entregar.
- Sin textos repetidos. Si Meta rechaza el token (código 190), se anota la hora en pendiente_usuario.md; nadie publica a mano para compensar.

## 8. Cadencia
- Dos reels al día (orden del dueño 19/11/2026): 70 % para autónomos y pymes sobre presupuestos y facturas, y 30 % trucos de IA (reparto semanal aproximado de 10 y 4 en 14 piezas). Se publica solo con aprobación de Calidad ≥ 90 o aprobación expresa del dueño; si falta, el hueco queda libre.
- Máximo 6 publicaciones al día por canal, con al menos 100 min entre piezas del mismo canal, salvo parrilla expresa del dueño (manda la suya ese día).
- Facebook y YouTube publican además todo el material existente aprobado (colas de `atrasos/`, `atrasos/politica.json`), lo mejor primero, dentro de esos límites y de la cuota de YouTube (~6 subidas al día).
- Redes vía Buffer gratis (workflow `redes_buffer.yml`, `herramientas/redes_buffer.py`; solo reels ya aprobados y publicados en Instagram con render desde el 14/11; sin producción propia; cada canal queda en espera hasta que el dueño lo conecte): **TikTok** 2 al día (13:30 y 20:30), 2 de El Jambo por 1 de app · **LinkedIn** (página de empresa) 1 al día de lunes a viernes (08:45), 1 de app por 1 de El Jambo, con el enlace /solicitar en el texto · **Google Business Profile** lunes, miércoles y viernes (10:15), solo promos de apps, como imagen con botón al formulario. Manuales y configuración en `equipo/tiktok/`, `equipo/linkedin/` y `equipo/google/`; el Estratega ajusta huecos y orden en cada `config.json` y el Supervisor vigila `ultimo_error` de cada `estado.json`. TikTok sube a 3 al día cuando el tiempo visto medio pase del 60 % dos semanas seguidas.
- Secuela («Parte 2») de cada reel que supere el objetivo, en 24-48 h. Objetivo a 48 h: salto < 35 % y tiempo visto > 60 % de la duración.

## 9. Apps y promoción
- Solo funciones verificadas: `hechos_verificados` (y nunca `prohibido_afirmar`) de la entidad Producto del Centro de Contenido Apps (Base44 6ae5244d4e2b32702f0a3cd6). Nada de clientes, reseñas, cifras ni precios inventados; no decir «gratis para siempre».
- Ninguna app se presenta para un solo sector. Demos y capturas solo con datos ficticios (entornos de pruebas).
- AjReparacion Gestión original (698ebd645b1870b1a0a9be3b) y la web del taller son intocables; demos en AJ Sistema DEMO (6ae702b32d473b8561ad5afb).
- Gestoría7D SE PROMOCIONA YA (orden del dueño 15/11 19:45).
- Recepcionista 24h (servicio nuevo, orden del dueño 16/11): asistente telefónico con inteligencia artificial que Neogest Lab configura y mantiene; slug `recepcionista-24h`. Se promociona con las reglas de `equipo/encargos/recepcionista_24h.md`: llamadas reales grabadas por el dueño a su propio asistente (rótulo «Llamada real a un asistente en funcionamiento») o, si aún no las hay, recreadas y rotuladas «Recreación», sin nombrar al proveedor, en posts solo «desde 150 € al mes», cierre «Solicita información gratuita».
- Planes gratis vigentes: Factura7D 2 facturas al mes; APPCC Fácil 2 puntos e informe de 1 día.
- MEDICATOR: «consulta la base de datos oficial de la AEMPS» (nunca «avalada»), sin consejos médicos; su lectura de papeles es OCR local + reglas: no decir «IA».
- Métrica que manda: altas en prueba gratuita de Gestión Integral 7D (por encima de seguidores y vistas). Enlace con `src` del canal: https://centro-de-contenido-apps-2f0a3cd6.base44.app/solicitar?app=<slug>&src=instagram|facebook|youtube|tiktok|linkedin|google
- Cierres prohibidos en todo (vídeo, post, DM, automatizaciones): «comenta X y te envío» y «palabra clave → DM».
- Nunca se escribe a negocios ni personas que no lo hayan pedido (LSSI art. 21). Sin publicidad de pago salvo que el dueño lo pida.

## 10. Gasto, modelos y nube
- Reserva del 10 % del límite semanal SIEMPRE vigente (la anulación del 13/11 fue puntual y caducó). Si queda poco, se hace lo imprescindible y se termina.
- Lo mecánico en Haiku; redactar, evaluar y programar en Sonnet; Opus solo si Sonnet no basta; NUNCA Fable. Al delegar con Agent se pasa siempre `model`. Leer solo lo necesario.
- Nube obligatoria: nada depende del ordenador del dueño (ni remote-devices, ni su Chrome, ni tareas que lo requieran). Lo que solo se pueda hacer en su PC se anota en pendiente_usuario.md («Requiere PC») y se sigue. Única excepción: la cola de Gemini/Flow se procesa cuando su PC está encendido.
- Base44: cambios editando código por el MCP, nunca el builder IA; checkpoint, build y publicar (deploy) siempre al terminar cada cambio, sin preguntar.

## 11. Qué se le pide al dueño
- Nada que el equipo pueda hacer. Lo que solo él puede hacer (identidad, móvil, decisiones, claves, acciones manuales) va a `equipo/pendiente_usuario.md`, una línea por cosa, con lo más importante arriba; lo resuelto se marca hecho.
- El Supervisor mantiene ese archivo al día y solo le avisa si algo bloquea.

## 12. Pendiente de decidir
- Precios: la auditoría del Centro (14/11) dice que Gestión Integral 7D tiene plan de 19 €/usuario/mes; la regla antigua prohíbe publicar precios hasta que el dueño los fije. Mientras no decida, no se publican.
- Enlace en el texto de Instagram: la orden de vídeo del 14/11 pone /solicitar en el post y una regla del 13/11 lo quitaba de Instagram. Se aplica el 14/11; `pre_entrega.py` aún avisa de «prueba gratuita» en el texto de los episodios (aviso, no error): Mejora debe alinearlo.
- Duración de los episodios del estudio: la receta de Neogest Studio ha dado 25,8-30 s; el formato pide 15-25 s (máx. 30).
- Medios de pago que se nombran en las piezas de 7D (Stripe/Redsys/Bizum o genérico): va en genérico hasta que el dueño diga.

## 13. Registro de cambios (una línea por cambio)
- 2026-11-20 · Coordinación (orden del dueño, «todo lo que se puede por API, lo hacemos») · Comunidad (Facebook/YouTube) migrada a API directa: `equipo/hechos_verificados.json` (caché por app, mantenido por Mejora y Centro en cada pasada) + `herramientas/comunidad_api.py` (Haiku) dentro de `comunidad.yml`; `roles/comunidad.md` se queda solo con Instagram/leads/invitaciones (necesitan Buzzfy, Claude Code). El Jambo: los 5 episodios en cola/ sin vídeo producido (309,310,311,312,314) descartados por orden del dueño; los que ya tienen vídeo siguen su calendario; sin nuevos episodios de Jambo hasta nueva orden. Pendiente del dueño: especificar el formato visual de los próximos episodios de Neo antes de encargar guiones nuevos.
- 2026-11-20 · Coordinación (orden del dueño) · bucle de retención de 4 pasos (apuestas → pregunta → giro → reenganche, por el bucle de dopamina de casino) aplicado a los formatos de El Jambo y promo de app (§5); biblia (`equipo/serie_jambo.md`) y prompt del Guionista Gemini (`herramientas/guionista_gemini.py`) alineados en el mismo cambio.
- 2026-11-20 · Coordinación (orden del dueño, "cuello de botella cero") · nuevo rol Repescador vía API directa (§2, roles/repescador.md): recoloca en cola/ piezas sin material cuyo render real ya existe en revision/ o errores/; corregidos a mano 107_catalogo_stock y 108_cobrar_facturas (el caso que lo motivó). `creador_api.yml` (piloto texto) pasa de solo workflow_dispatch a cron propio (10:51/16:51) para no depender solo del límite semanal. Pendiente de decisión del dueño: desactivar la tarea de Claude Code "IG nube · Calidad" (duplica `calidad_api.yml` en el mismo horario, 11:41/17:41) — el bloqueo lo tiene el propio dueño porque la herramienta de tareas programadas pide su confirmación para desactivarla.
- 2026-11-15 · Coordinación (orden del dueño) · directiva y roles reescritos en limpio; deroga lo apilado hasta hoy (ver archivo/).
- 2026-11-15 · Coordinación · Calidad pasa a una sola tarea cada 2 h de 08:41 a 22:41; Analista de monetización fusionado en Analista; Ventas en pausa.
- 2026-11-15 · Coordinación · las tareas creadas por el dueño no se pueden editar desde un agente: sus prompts antiguos quedan derogados por §1, las duplicadas se anulan por §2 y el Creador trabaja en una pasada hasta que el dueño amplíe su horario.
- 2026-11-15 · Coordinación · hecho en claude.ai: prompts de las tareas reducidos a «lee la directiva y tu rol»; Creador a 3 pasadas; Cazador lunes, miércoles y viernes; en pausa Calidad 12:51, Calidad noche, Analista de monetización y Ventas.
- 2026-11-15 · Coordinación · el visto bueno del dueño en una pieza manda sobre la nota de Calidad (§7).
- 2026-11-15 · Coordinación · prueba del ciclo hecha (20:37-21:10): Creador, Calidad, Supervisor, Analista, Remasterizador, Mejora y Comunidad completaron su pasada con los prompts nuevos; retirada la excepción temporal de horario.
- 2026-11-16 · Coordinación (orden del dueño) · TikTok @neogestlab entra como cuarto canal: republica lo aprobado vía Buffer gratis (§4, §8, §9; equipo/tiktok/).
- 2026-11-16 · Coordinación (orden del dueño) · LinkedIn y Google Business Profile entran por el mismo flujo de Buffer que TikTok (§4, §8, §9); TikTok se envía con la etiqueta oficial de IA.
- 2026-11-16 · Coordinación (orden del dueño: «si bastan los créditos, sí») · ElevenLabs Johnny pasa a ser la voz final de promos de app y reels de datos, con presupuesto de 30.000 caracteres al mes; El Jambo sigue con edge-tts porque los créditos no alcanzan (§5, §6).
- 2026-11-16 · Coordinación (orden del dueño) · los audios se guardan y se reutilizan siempre; índice en equipo/voces_indice.json (§6).
- 2026-11-16 · Coordinación (orden del dueño) · servicio nuevo Recepcionista 24h en promoción (§9; equipo/encargos/recepcionista_24h.md).
- 2026-11-16 · Coordinación (orden del dueño) · reparto nuevo de El Jambo que sabe: Rosa Melano, Felipe Lotas, Sindy Entes y Neo sustituyen a Jambo, Jupillo, Pelota, Bola y Trámites; moraleja de cierre obligatoria en todo episodio nuevo (§5, §6; equipo/serie_jambo.md biblia v3; voces en equipo/voz.json).
- 2026-11-16 · Coordinación (orden del dueño: bajar pasadas para ahorrar) · Creador 2 al día, Calidad 2, Supervisor 1, Comunidad 1, Remasterizador y Analista 3 por semana, Cazador y Mejora 1 por semana, Gemini 1 al día, Laboratorio de ideas pasa al sábado (el 16/11 la cuenta iba por el 78 % del límite semanal). El 16/11 hubo 4 pasadas de Calidad y 2 de Comunidad sin nada que hacer.
- 2026-11-16 · Coordinación (orden del dueño: «usa los 100 $ de créditos de la API para lo que sea más conveniente» / «todo lo que se pueda usar con la API y no gastar tokens, se hace») · Supervisor sale de Claude Code y pasa a API directa de Anthropic (Haiku) vía GitHub Actions, pagada con esos créditos y no con el límite semanal del plan Max: `.github/workflows/supervisor_api.yml` + `herramientas/supervisor_api.py`, 12:27 y 18:27 Madrid, probado con workflow_dispatch. v1 solo diagnostica en el tablón (no edita pendiente_usuario.md ni lanza ciclo.yml todavía). Comunidad y Analista NO se han podido pasar igual: dependen de los conectores Buzzfy/Base44/Meta-Business, que solo existen dentro de una sesión de Claude Code — moverlos exigiría una integración directa nueva (tokens propios de Instagram/Facebook/Base44) en vez de un cambio simple; queda pendiente de que el dueño decida si se construye.
- 2026-11-17 · Coordinación (orden del dueño, vía claude.ai: «los guiones de los videos no enganchan... pide a Gemini los guiones, automatiza esa tarea») · nuevo paso «Guionista Gemini (API)» 36 min antes de cada pasada del Creador (09:15 y 15:15 Madrid): `.github/workflows/guionista_gemini.yml` + `herramientas/guionista_gemini.py` piden guiones de El Jambo a la API de Gemini (gratis, cuenta darbish) usando la biblia de la serie, los motivos de rechazo repetidos de Calidad y los patrones virales ya estudiados; deja borradores validados en `equipo/guiones_gemini/pendientes/` (§2, §4, roles/creador.md). El Creador sigue siendo quien elige, ajusta y aprueba cada guion para producción; si Gemini falla, el Creador escribe el suyo como antes — el paso no bloquea. Nuevo secreto GEMINI_API_KEY pendiente de que el dueño lo cree (Google AI Studio, cuenta darbish) y lo añada en GitHub → Settings → Secrets.
- 2026-11-18 · Coordinación (orden del dueño: migrar Calidad y Creador a API directa, como Supervisor; PR pendiente de revisión antes de entrar en producción) · Calidad entera pasa a API directa con tool use real (Sonnet): descarga el mp4 (release «cola» o video_externo), ffprobe + silencedetect + LUFS/pico + 3 fotogramas, y el modelo escribe calidad.json con el criterio de `roles/calidad.md` y `estandar_calidad.md` v9 (`.github/workflows/calidad_api.yml` + `herramientas/calidad_api.py`, 11:41/17:41 Madrid). Limitación documentada: no lee hechos_verificados/prohibido_afirmar de Base44 (ese MCP no existe fuera de Claude Code); para apps, solo contrasta con las fuentes que el post.json ya cita. Creador: solo es viable por API la parte mecánica — arreglar texto/metadata de post.json de piezas ya rechazadas, sin tocar vídeo (`.github/workflows/creador_api.yml`, solo `workflow_dispatch`, `herramientas/creador_api.py`); escribir guiones y renderizar en Neogest Studio sigue exigiendo el MCP de Base44, que no existe fuera de Claude Code — pendiente de que el dueño decida si se construye una integración HTTP directa (fase 2). Limpieza de cola/ en la misma pasada: lote 501-515 (motor «sketch» retirado, no recortable) movido a `descartados/`; 336 arreglado en texto (sin precio, con youtube) pero sigue rechazado por el vídeo; 803 sin tocar (necesita música de la biblioteca del estudio en Base44, no la de este repo). Detalle en `equipo/tablon.md`.
- 2026-11-19 · Coordinación (orden del dueño) · cadencia fijada en 2 reels diarios; mezcla semanal 70 % presupuestos y facturas para autónomos y pymes y 30 % trucos de IA (§8, `equipo/plan.json` y roles de Estratega y Supervisor).
