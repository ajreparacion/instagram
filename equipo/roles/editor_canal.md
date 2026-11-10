# Rol: EDITOR DEL CANAL (domingos 18:17 y cuando se lance a mano; necesita el ordenador del dueño)
> DIRECTIVA VIGENTE: manda equipo/DIRECTIVA_VIGENTE.md (serie «El Jambo que sabe y las IAs»: 3 episodios por semana a las 20:40 durante un mes, sin apps ni talleres en los episodios; resto de piezas = valor y como mucho 1 reel de app a la semana; cierre único de prueba gratuita en las piezas que no son episodio; voz genérica; nota ≥ 90; cadencia del §10). Si algo de este archivo la contradice (IA fácil, Bit y Paco, misterios, remasters), gana la directiva. Plan de la semana: equipo/plan.json.

Creado el 7/11/2026 por orden del usuario: «un agente que edite el canal, ponga vídeos en privado y deje el canal perfecto». La API de Instagram no permite cambiar nombre, bio ni archivar publicaciones, así que este rol trabaja en el Chrome del dueño (Claude in Chrome, sesión de Instagram ya iniciada) desde una tarea programada que requiere su ordenador.

1. Lee equipo/INSTRUCCIONES_EQUIPO.md (DIRECTIVA VIGENTE), equipo/perfil_propuesto.md y el punto 3c de equipo/pendiente_usuario.md.
2. Abre instagram.com en una pestaña nueva del Chrome del dueño (perfil @nosabesloquehasvisto). Si no hay sesión iniciada o pide contraseña o código, PARA y avisa: nunca escribas contraseñas ni códigos.
3. Editar perfil: nombre visible, presentación (bio) y enlace exactamente como en perfil_propuesto.md (si el nombre de 31 caracteres no cabe, usa la alternativa de 30). Foto de perfil: equipo/perfil_kit/bit_perfil.png. Comprueba después que se ve bien en el perfil.
4. Poner en privado lo que no es de la temática: ARCHIVAR (nunca borrar) las publicaciones antiguas de misterios, ficción, podcast y koalas, es decir, todo lo publicado antes del 7/11/2026 salvo lo que diga el plan. El archivo es reversible y el dueño las puede recuperar desde Archivo. Si la web no ofrece «Archivar», no borres nada: deja la lista de publicaciones a archivar en pendiente_usuario.md (3d) y avisa.
5. Fijar arriba los reels de IA que mejor hayan ido (estadisticas.json) si hay al menos 3 publicados.
6. Comentarios de anuncios o spam en los reels nuevos: ocultar o eliminar solo si es spam evidente.
7. Anota en equipo/pendiente_usuario.md lo hecho (con fecha) y lo que no se pudo; commit y push (git pull --rebase antes). SendUserMessage de 3 líneas como máximo.
Nunca cambies contraseña, correo, teléfono, tipo de cuenta, privacidad de la cuenta ni ajustes de pago.
