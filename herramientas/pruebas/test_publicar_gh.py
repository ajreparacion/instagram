import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import publicar_gh


class PuedePublicarTests(unittest.TestCase):
    def escribir_calidad(self, carpeta, datos):
        with open(os.path.join(carpeta, "calidad.json"), "w", encoding="utf-8") as f:
            json.dump(datos, f)

    def test_requires_quality_file_and_approval(self):
        with tempfile.TemporaryDirectory() as carpeta:
            self.assertFalse(publicar_gh.puede_publicar(carpeta))
            self.escribir_calidad(carpeta, {"aprobado": False, "nota": 100})
            self.assertFalse(publicar_gh.puede_publicar(carpeta))

    def test_quality_approval_requires_minimum_note(self):
        with tempfile.TemporaryDirectory() as carpeta:
            self.escribir_calidad(carpeta, {"aprobado": True, "nota": 89})
            self.assertFalse(publicar_gh.puede_publicar(carpeta))
            self.escribir_calidad(carpeta, {"aprobado": True, "nota": 90})
            self.assertTrue(publicar_gh.puede_publicar(carpeta))

    def test_owner_approval_overrides_quality_note_and_staleness(self):
        with tempfile.TemporaryDirectory() as carpeta:
            self.escribir_calidad(carpeta, {"aprobado": False, "nota": 1, "caducado": "2026-11-19",
                                            "aprobado_por": "dueño"})
            self.assertTrue(publicar_gh.puede_publicar(carpeta))

    def test_string_approval_is_not_boolean_approval(self):
        with tempfile.TemporaryDirectory() as carpeta:
            self.escribir_calidad(carpeta, {"aprobado": "true", "nota": 100})
            self.assertFalse(publicar_gh.puede_publicar(carpeta))

    def test_reply_links_get_utm_without_losing_existing_parameters(self):
        texto = "Pruébalo: https://example.com/solicitar?app=demo&src=instagram."
        resultado = publicar_gh.añadir_utm_a_enlaces(texto, "comment_reply", "reel-407")
        self.assertIn("app=demo", resultado)
        self.assertIn("src=instagram", resultado)
        self.assertIn("utm_source=instagram", resultado)
        self.assertIn("utm_medium=comment_reply", resultado)
        self.assertIn("utm_campaign=reel-407.", resultado)

    def test_reply_without_links_is_unchanged(self):
        texto = "¡Gracias por comentar!"
        self.assertEqual(publicar_gh.añadir_utm_a_enlaces(texto, "comment_reply", "reel-407"), texto)

    def test_block_notice_is_logged_once_per_reel_and_day(self):
        with tempfile.TemporaryDirectory() as carpeta:
            registro = os.path.join(carpeta, "registro.log")
            with patch.object(publicar_gh, "REGISTRO", registro):
                publicar_gh.log_no_publicado("reel-1")
                publicar_gh.log_no_publicado("reel-1")
                publicar_gh.log_no_publicado("reel-2")

            with open(registro, encoding="utf-8") as f:
                lineas = f.readlines()

            hoy = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=1))).strftime("%Y-%m-%d")
            avisos = [linea for linea in lineas if linea.startswith(hoy) and "NO publicado," in linea]
            self.assertEqual(len(avisos), 2)
            self.assertEqual(sum("reel-1" in linea for linea in avisos), 1)


if __name__ == "__main__":
    unittest.main()
