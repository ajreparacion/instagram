import json
import os
import tempfile
import unittest

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


if __name__ == "__main__":
    unittest.main()
