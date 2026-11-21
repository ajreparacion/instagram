#!/usr/bin/env python3
"""Pruebas SIN RED del control de audio (comparación guion <-> transcripción de Whisper). 15/11/2026 (Mejora).
Uso: python3 herramientas/pruebas/test_control_audio.py   (sale != 0 si algún caso no sale como debe)
Casos reales: pares guion/transcripción sacados de cola/*/control_audio.json y registro.log del 15/11 (Whisper small).
Cada transcripción se trocea en palabras como lo hace faster-whisper («70» y «%» por separado, «9» y «,90») y se pega con texto_de()."""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import control_audio as ca


def comparar(guion, transcripcion):
    pal = [(w, 0.0, 0.0) for w in transcripcion.split()]
    return ca.verificar(guion, ca.texto_de(pal))


# (nombre, guion, lo que escribió Whisper) -> deben PASAR (falsos rechazos del control)
BUENOS = [
    ("320 cifra 2028 (dígitos)", "Dos mil veintiocho. Fecha de la reunión.", "2028. Fecha de la reunión."),
    ("321 27C y ticket", "Asiento veintisiete C, tique veintisiete D.", "Asiento 27C, ticket 27D."),
    ("322 cuarenta", "Han venido cuarenta.", "Han venido 40."),
    ("325 hora 11:47", "A las once cuarenta y siete.", "A las 11:47."),
    ("324/329 doce", "Somos doce y la mitad tiene alergias.", "Somos 12 y la mitad tiene alergias."),
    ("327 70 % (Whisper parte «70» y «%»)", "¡Setenta por ciento en todo! Precios recalculados en tres segundos.",
     "70 % en todo. Precios recalculados en 3 segundos."),
    ("333 10 % y 20 % pegados", "Diez por ciento menos. ¡Veinte por ciento! Tengo doce seguidores.", "10 % menos. 20 % Tengo 12 seguidores."),
    ("326 trescientos/doce/ocho/cuarenta", "Trescientos socios. Vienen doce. Audios de ocho minutos. Han vuelto cuarenta.",
     "300 socios, vienen 12. Audios de 8 minutos, han vuelto 40."),
    ("326 «no gain» -> «no gan»", "¡No pain, no gain! ¡Que se oiga!", "No pain, no gan, que se oiga."),
    ("334 noventa partido en «no venta»", "Ahora noventa. Eso no es trabajo.", "Ahora no venta. Eso no es trabajo."),
    ("334 léelos partido en «lee los»", "Léelos antes de contestar.", "Lee los antes de contestar."),
    ("334 «sin leer» -> «y leer»", "¿Cuántos correos tienes sin leer ahora mismo?", "¿Cuántos correos tienes y leer ahora mismo?"),
    ("334/332 Bola -> Vola (b/v)", "Bola, escribe la oferta de empleo.", "¡Vola! Escribe la oferta de empleo."),
    ("332 Bola -> Bolla (alias)", "Bola, motívame.", "Bolla, motívame."),
    ("318 Jupillo -> Cupillo", "Jupillo, doscientas páginas para mañana.", "¡Cupillo, doscientas páginas para mañana!"),
    ("318 Hechas -> Echas, Hecho -> Echo (h muda)", "Hechas. Son las once. Hecho.", "Echas, son las once. Echo."),
    ("333 Pelota -> «te lota» + haz/hace", "Somos amigos. Pelota, haz el presupuesto con cariño.", "Somos amigos. ¿Te lota? Hace el presupuesto con cariño."),
    ("329 team building mal oído", "¡Team building en la montaña, con nieve!", "Te han wielding en la montaña con nieve."),
    ("328 tour virtual pegado", "Hicimos un tour virtual del piso.", "Hicimos un turvirtual del piso."),
    ("336 pruébala partido en «prueba la»", "Pruébala gratis, sin tarjeta.", "Prueba la gratis sin tarjeta."),
    ("336 Gestoría7D", "Con Gestoría siete de, tus ingresos y gastos van a tus libros.", "Con gestoría 7 de tus ingresos y gastos van a tus libros."),
    ("337 APPCC Fácil -> «app fácil»", "Con APPCC Fácil apuntas cámaras.", "Con app fácil apuntas cámaras."),
    ("337 precio 9,90", "Desde nueve con noventa al mes en pago anual.", "Desde 9,90 al mes en pago anual."),
    ("precio 9,90 € (símbolo)", "Cuesta nueve euros con noventa al mes.", "Cuesta 9,90 € al mes."),
    ("IA como «i a» / I.A.", "Las IA de la oficina.", "Las I.A. de la oficina."),
    ("IA como «ía»", "La IA trabaja.", "La ía trabaja."),
    ("miles con punto", "Dos mil veintiocho euros.", "2.028 euros."),
    ("hora 9:40", "La de las nueve llega a las nueve cuarenta.", "La de las 9 llega a las 9:40."),
    ("ordinal 3.º", "Vive en el tercero.", "Vive en el 3.º."),
    ("grados", "Hace veintisiete grados.", "Hace 27 °C."),
    ("un/uno/una", "Un momentito. Veintiún días.", "Uno momentito. 21 días."),
    ("405/407/409 «tarjeta, sin» -> «tarjetas sin» (s ante s)", "Pide tu prueba gratuita: sin tarjeta, sin datos bancarios y sin compromiso.",
     "Pide tu prueba gratuita, sin tarjetas, sin datos bancarios y sin compromiso."),
    ("404 «apruebas sin» -> «aprueba sin» (s ante s)", "¡Con mentalidad de campeón, tú apruebas sin estudiar!", "Con mentalidad de campeón, tu aprueba sin estudiar."),
]

# deben FALLAR (errores reales de voz: palabra distinta, cortada, inventada u omitida)
MALOS = [
    ("palabra cortada", "Y la de las diez ya está en la puerta.", "Y la de las diez ya está en puerta.", ["la"]),
    ("palabra inventada", "Precios recalculados en tres segundos.", "Precios recalculados muy rápido en 3 segundos.", None),
    ("cifra distinta (cuarenta frente a 14)", "Han vuelto cuarenta.", "Han vuelto 14.", ["cuarenta"]),
    ("porcentaje distinto (diez frente a 20 %)", "Diez por ciento menos.", "20 % menos.", None),
    ("personaje omitido (sin «te lota» ni parecido)", "Somos amigos. Pelota, presupuesto con cariño.", "Somos amigos. Presupuesto con cariño.", ["pelota"]),
    ("328 curiosos -> furiosos (palabra distinta)", "Curiosos filtrados. Solo vienen los que van en serio.", "Furiosos filtrados. Sólo vienen los que van en serio.", ["curiosos"]),
    ("336 calcula -> calcule (otra forma verbal)", "Calcula y prepara: tú presentas.", "Calcule y prepara, tú presentas.", ["calcula"]),
    ("la frase final falta entera", "Que lo haga la Jupillo. ¿Cuánto esperas tú?", "Que lo haga la Jupillo.", None),
    ("«sin» omitido sin ser «y leer»", "Tienes sin leer cuarenta correos.", "Tienes leer cuarenta correos.", ["sin"]),
    ("plural distinto sin «s» detrás (tarjeta -> tarjetas de)", "Sin tarjeta de crédito.", "Sin tarjetas de crédito.", ["tarjeta"]),
    ("verbo distinto sin «s» detrás (apruebas -> aprueba el)", "Tú apruebas el examen.", "Tú aprueba el examen.", ["apruebas"]),
]


def main():
    fallos = 0
    print("== Deben PASAR (%d) ==" % len(BUENOS))
    for nombre, g, t in BUENOS:
        faltan, sobran = comparar(g, t)
        ok = not faltan and not sobran
        fallos += not ok
        print(("  OK    " if ok else "  MAL   ") + nombre + ("" if ok else "  faltan=%s sobran=%s" % (faltan, sobran)))
    print("== Deben FALLAR (%d) ==" % len(MALOS))
    for nombre, g, t, debe_faltar in MALOS:
        faltan, sobran = comparar(g, t)
        ok = bool(faltan or sobran) and (debe_faltar is None or all(w in faltan for w in debe_faltar))
        fallos += not ok
        print(("  OK    " if ok else "  MAL   ") + nombre + "  -> faltan=%s sobran=%s" % (faltan, sobran))
    # normalización directa
    print("== Normalización ==")
    for a, b in [("9:40", "nueve cuarenta"), ("70%", "setenta por ciento"), ("2.028", "dos mil veintiocho"), ("1.º", "primero"), ("9,90 €", "nueve con noventa")]:
        ok = ca.norm(a) == ca.norm(b)
        fallos += not ok
        print(("  OK    " if ok else "  MAL   ") + "%r == %r  (%s | %s)" % (a, b, ca.norm(a), ca.norm(b)))
    print("RESULTADO: %s (%d casos)" % ("TODO COMO DEBE" if not fallos else "%d FALLOS" % fallos, len(BUENOS) + len(MALOS) + 5))
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
