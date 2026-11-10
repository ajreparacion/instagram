# Serie «Matías y las IAs» (biblia v1, 10/11/2026, orden del dueño; la redacta Calidad con el dueño)
Sustituye a la propuesta «Paco y la IA» y al tema del taller (el dueño: «olvidaos del tema taller»). Sin apps de Neogest Lab al principio. Prueba de un mes en @neogestlab, 3 episodios por semana. Se mide con las metas v8 (abandono < 40 %, compartidos/me gusta ≥ 8 %, visualización media ≥ 15 s). Si a los 12 episodios no mejora, se cambia la columna, no el decorado.

## Matías
- Joven vago e ingenioso (24-27 años). Quiere que la IA le haga la vida entera (el trabajo, los deberes, ligar, la excusa para el jefe, la declaración) y casi siempre le sale al revés. Pícaro, simpático, irónico, nunca cruel. Su sarcasmo va contra la situación y contra sí mismo, nunca contra personas reales.
- Frase fija: «Es que yo lo he delegado.» Contador en pantalla en cada episodio: «Cosas que he delegado hoy: N» (sube de episodio en episodio, es el gag que enganchan los seguidores).
- Aspecto (para Mejora): dibujo doodle propio, trazo negro grueso como el resto de la cuenta, un solo acento de color, sudadera con capucha, ojos medio cerrados, un mechón; sofá o escritorio como decorado fijo. Nada de rasgos de personajes ajenos.

## El elenco de IAs (inventadas, sin logos ni nombres de marcas; nombres provisionales)
1. **Bolo** (pelota naranja): lo sabe todo y lo suelta con seguridad total. Se equivoca con una confianza absoluta. Chiste: la autoridad sin razón.
2. **Clara** (círculo con carita sonriente): pasivo-agresiva. Contesta siempre «¡Claro que sí!» y hace otra cosa, o lo hace con un reproche educado. Chiste: el «sí» que significa «no».
3. **Doña Trámite** (cuadrado gris con ventanilla): burócrata. Todo es posible… tras rellenar el impreso 27-B. Chiste: la solución perfecta e inútil.
Cada IA, un color/forma distinta y su nombre en texto cuando habla; en cada episodio sale una o dos, no las tres a la vez salvo capítulo especial.

## Reglas de guion (columnas de equipo/tecnicas_virales.md §3: es humor con personaje)
- 15-20 s, un chiste y un giro. Gancho de ≤ 8 palabras en pantalla desde el primer fotograma, formato «POV: …» o pregunta absurda; primer corte antes de 3 s; cambio visual cada 2,5-3 s.
- Estructura: (1) gancho con el problema cotidiano; (2) Matías delega a una IA; (3) la IA se pasa de lista/falla/hace otra cosa; (4) remate seco de Matías (la ironía); (5) fotograma final guardable: el contador «Cosas que he delegado hoy: N» + frase para enviar.
- Crítica social ligera: reuniones, trabajo, deberes, ligar, burocracia, la suegra, el móvil. Cero política, cero medicina/salud, cero dinero ajeno ni marcas reales, nada de ridiculizar a personas ni colectivos.
- Voz: voz genérica de España (Kokoro em_alex) para Matías; las IAs, en la misma voz con tono/efecto distinto y su globo de texto. Subtítulos grandes palabra a palabra. Música de la biblioteca de Instagram, que se oiga entre frases.
- Pie del post (5 líneas): línea 1 = el gancho con cifra o POV; 2-4 = una frase de contexto o chiste extra; línea 5 = un solo pedido: «Mándaselo al que también delega» (o «Guárdalo para tu próxima reunión»); 1-5 hashtags (#humor #ia #humorespañol #matiasylasias). Sin enlace ni «prueba gratuita» mientras dure la fase sin apps (decisión del dueño 10/11).
- Todo lo que dice cada IA es ficción de un personaje; no se atribuyen afirmaciones sobre productos o empresas reales.

## Primeros 6 episodios (listos para guion.json cuando Mejora tenga el personaje)
1. «POV: le pides a la IA una excusa para tu jefe.» Bolo escribe una excusa tan elaborada que Matías se la cree. Remate: «Ahora no sé si estoy enfermo.» Contador 1.
2. «La reunión que era un correo.» Clara resume la reunión que Bolo ha transcrito. Matías: «O sea, que hoy no ha trabajado nadie.» Contador 2.
3. «Delegué los deberes de mi sobrino.» Doña Trámite pide el impreso 27-B para el trabajo de Lengua. Matías, resignado: «Prefiero hacerlos yo.» Contador 3 (y se arrepiente).
4. «Le pedí a la IA un mensaje para ligar.» Clara escribe «Hola» tres veces con reproches educados. Matías: «Es que yo lo he delegado.» Contador 4.
5. «POV: la IA me hace la declaración.» Doña Trámite responde que está todo correcto, pendiente de una cita previa que no existe. Contador 5.
6. «Mi IA me llama «campeón» cuando falla.» Bolo suelta una respuesta equivocada con total seguridad; Matías la repite en una discusión y pierde. Contador 6 y gag de continuidad.
Los episodios 7-12 se escriben cuando haya datos de los 6 primeros (el contador es el hilo).

## Producción (peticiones a Mejora y Creador)
- Mejora: dibujar a Matías (voz que mueve la boca, acciones: delega, se desespera, remata) y a Bolo, Clara y Doña Trámite (personajes simples: forma + ojos + boca), plantilla «sketch» en hacer_reel.py (gancho POV desde el fotograma 0, globos de diálogo con la IA que habla, contador «delegado» que sube, fotograma final guardable, efectos de sonido al giro).
- Creador: guion.json de los episodios 1-3 para 12/11-14/11 y de los 4-6 para la semana siguiente; 3 a la semana.
- Calidad: revisa con la v8; el humor se evalúa con B1 (gancho), B2 (espina: humor/personaje), B3 (frase para enviar) y B5 (ritmo). Se vigilan las 48 h de cada episodio con ig_post_stats.
