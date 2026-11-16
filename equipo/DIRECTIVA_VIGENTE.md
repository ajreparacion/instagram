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
| Calidad | 11:41 y 17:41 (tarea única «Calidad»; después de cada pasada del Creador) | Sonnet | roles/calidad.md |
| Supervisor | 13:27 a diario | Haiku | roles/supervisor.md |
| Cazador de virales | lunes 08:23 | Sonnet | roles/cazador.md |
| Remasterizador | lunes, miércoles y viernes 09:00 | Sonnet | roles/remasterizador.md |
| Analista (+ monetización los domingos) | martes, jueves y domingo 23:23 | Haiku | roles/analista.md |
| Estratega | lunes 10:13 | Sonnet | roles/estratega.md |
| Mejora de producción | miércoles 11:13 | Sonnet | roles/mejora.md |
| Comunidad | 19:37 a diario | Haiku | roles/comunidad.md |
| Centro (vídeos y demos del Centro) | lunes y jueves 11:17 | Sonnet | roles/centro.md |
| Ventas · prospección | L-V 09:43, EN PAUSA (ver su rol) | Sonnet | roles/ventas.md |
Tareas en pausa desde el 15/11 (si alguna se dispara, NO trabaja: termina en una línea, sin tablón ni commit):
- «IG nube · Calidad (repo)» de las 12:51 y «IG nube · Calidad (noche) (repo)» de las 19:31: fusionadas en la Calidad de cada 2 h.
- «IG nube · Analista de monetización (repo)» (domingos 18:17): fusionada en el Analista.
- «Ventas · Prospección (repo)»: en pausa.
Fuera del repo (no leen este archivo, se citan para el mapa):
- «Lote diario de comentarios» (08:21): prepara comentarios para que el dueño los publique a mano; doc del proyecto `claude/redes/comentarios_diarios.md`.
- «Laboratorio de ideas» (sábados): propuestas de apps nuevas en el doc del proyecto `claude/ideas/propuestas-apps.md`.
- «Gemini: procesar cola» (15:48, solo con el PC del dueño encendido): sirve `equipo/cola_gemini.md` y sube el resultado a la Biblioteca de Neogest Studio.

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
- Repo PÚBLICO (Instagram descarga por jsDelivr y la release): nunca claves, tokens, contraseñas, cookies ni datos personales en archivos, commits o registros. Secretos solo en GitHub Actions (nombres: YOUTUBE_API_KEY, YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN, FACEBOOK_PAGE_TOKEN, PAGE_TOKEN, PUENTE_TOKEN, BUFFER_API_KEY).

## 5. Formatos
Las cifras de 20, 22 o 35 s de textos antiguos quedan derogadas.

**El Jambo que sabe (serie de humor; personajes desde el 16/11: Rosa Melano —jefa tirana—, Felipe Lotas y Sindy Entes —empleados que lo sufren—, Neo —la IA que resuelve—; biblia v3 en `equipo/serie_jambo.md`)**
| Campo | Regla |
|---|---|
| Duración | 15-25 s, nunca más de 30 |
| Estructura | 0-2 s situación reconocible (texto + 1.ª frase: «Cuando…», «POV:» o pregunta) · 2-6 s planteamiento en una frase · 6-16 s escalada en 3 golpes, cada uno peor · 16-21 s giro que resuelve el conflicto · 21-24 s cierre. Un conflicto por episodio. «Que lo haga la Jupillo» solo si es el remate |
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
| Estructura | ANTES/DESPUÉS: problema real en 2 s → la app lo resuelve en pantalla con datos ficticios → resultado. Abre con lo que no hacen las demás (IA, cámara, lectura de documentos…; brief del proyecto `claude/redes/promos_diferenciales_2026-11-15.md`); «la única» solo con prueba de competencia anotada. Nada de escaparate de funciones básicas ni cifras intermedias sin explicar; calculadoras congeladas hasta rehacerlas así |
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
- ElevenLabs voz Johnny (única herramienta de pago autorizada; plan Starter, 39.756 caracteres al mes): solo en la versión final de los vídeos de presentación del Centro, las promos de app y los reels de datos. Presupuesto: 30.000 caracteres al mes entre todo (unas 55 piezas de ~500 caracteres); el resto del saldo es reserva y nunca se compra saldo extra. Antes de gastar se suma el registro de `claude/redes/rehacer_videos_centro_elevenlabs.md` y `gasto.log`; agotado el presupuesto, edge-tts. El Jambo NO usa ElevenLabs: a 3 episodios al día gastaría unos 43.000 caracteres al mes, más que el plan entero.
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
- Mínimo 3 episodios NUEVOS de El Jambo al día (orden 15/11), con colchón en cola.
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
