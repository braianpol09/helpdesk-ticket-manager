"""Tests de la versión web. Ejecutar con: python -m unittest -v"""
import os
import tempfile
import unittest

import database as db
from app import app


class TestWeb(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        app.config["DB_PATH"] = self.tmp.name
        app.config["TESTING"] = True
        self.client = app.test_client()

    def tearDown(self):
        app.config["DB_PATH"] = db.DB_PATH
        os.unlink(self.tmp.name)

    def crear(self, **extra):
        datos = {"cliente": "Ana", "equipo": "PC", "problema": "No enciende", "prioridad": "alta"}
        datos.update(extra)
        return self.client.post("/nuevo", data=datos, follow_redirects=True)

    def test_paginas_principales(self):
        for ruta in ("/", "/nuevo", "/estadisticas"):
            self.assertEqual(self.client.get(ruta).status_code, 200)

    def test_crear_ticket_aparece_en_listado(self):
        self.assertIn(b"Ticket #1 creado", self.crear().data)
        self.assertIn(b"No enciende", self.client.get("/").data)

    def test_validacion_campos_vacios(self):
        self.assertIn(b"son obligatorios", self.crear(problema="").data)

    def test_ticket_inexistente_da_404(self):
        self.assertEqual(self.client.get("/ticket/999").status_code, 404)

    def test_cambiar_estado_y_nota(self):
        self.crear()
        r = self.client.post("/ticket/1/estado", data={"estado": "resuelto"}, follow_redirects=True)
        self.assertIn(b"resuelto", r.data)
        r = self.client.post("/ticket/1/nota", data={"texto": "Cambié la fuente"}, follow_redirects=True)
        self.assertIn("Cambié la fuente".encode(), r.data)

    def test_html_se_escapa(self):
        self.crear(problema="<script>alert(1)</script>")
        self.assertNotIn(b"<script>alert(1)</script>", self.client.get("/ticket/1").data)


if __name__ == "__main__":
    unittest.main()
