# Biblioteca de música sin derechos

Deja aquí los mp3/wav/ogg/m4a que quieras usar como música base de los reels y las historias, y apúntalos en `pistas.json`
(sin ficha, la pista NO se usa):

```json
[
  {"archivo": "mi_pista.mp3", "titulo": "Nombre", "autor": "Artista", "licencia": "Pixabay Content License",
   "url": "https://pixabay.com/music/...", "atribucion": ""}
]
```

- `atribucion`: solo si la licencia la exige (CC-BY…); se añade sola al final del texto del post.
- `bpm` y `salto_s` (segundo del primer golpe) son opcionales: si faltan, se detectan solos.
- Sirven pistas de 1 a 4 minutos, rítmicas (house, hip hop, funk, pop…). La pista arranca en un golpe y se corta con fundido.
- Mientras la carpeta no tenga pistas con ficha, los reels usan la canción de la biblioteca de Instagram (`equipo/musica_instagram.json`).
- Con pistas aquí, la música va DENTRO del vídeo (máster a -14 LUFS en los reels de demo; voz con ducking en los reels con voz) y no se usa la de Instagram.
