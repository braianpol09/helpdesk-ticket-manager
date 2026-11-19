"""Tests de la capa de datos. Ejecutar con: python -m unittest -v"""
import unittest

import database as db


class TestTickets(unittest.TestCase):
    def setUp(self):
        # Base en memoria: cada test arranca limpio y no toca helpdesk.db
        self.conn = db.conectar(":memory:")
        self.cliente = db.obtener_o_crear_cliente(self.conn, "Ana Test")

    def tearDown(self):
        self.conn.close()

    def test_crear_y_obtener_ticket(self):
        tid = db.crear_ticket(self.conn, self.cliente, "PC", "No enciende", "alta")
        ticket = db.obtener_ticket(self.conn, tid)
        self.assertEqual(ticket["estado"], "abierto")
        self.assertEqual(ticket["cliente"], "Ana Test")

    def test_prioridad_invalida(self):
        with self.assertRaises(ValueError):
            db.crear_ticket(self.conn, self.cliente, "PC", "x", "urgentisima")

    def test_cliente_no_se_duplica(self):
        otra_vez = db.obtener_o_crear_cliente(self.conn, "ana test")
        self.assertEqual(otra_vez, self.cliente)

    def test_resolver_guarda_fecha_y_reabrir_la_borra(self):
        tid = db.crear_ticket(self.conn, self.cliente, "PC", "Lenta", "media")
        db.cambiar_estado(self.conn, tid, "resuelto")
        self.assertIsNotNone(db.obtener_ticket(self.conn, tid)["resuelto_en"])
        db.cambiar_estado(self.conn, tid, "abierto")
        self.assertIsNone(db.obtener_ticket(self.conn, tid)["resuelto_en"])

    def test_estado_inexistente(self):
        self.assertFalse(db.cambiar_estado(self.conn, 999, "resuelto"))

    def test_orden_por_prioridad(self):
        db.crear_ticket(self.conn, self.cliente, "A", "baja", "baja")
        db.crear_ticket(self.conn, self.cliente, "B", "critica", "critica")
        tickets = db.listar_tickets(self.conn)
        self.assertEqual(tickets[0]["prioridad"], "critica")

    def test_buscar_y_notas(self):
        tid = db.crear_ticket(self.conn, self.cliente, "Router", "Sin internet", "alta")
        db.agregar_nota(self.conn, tid, "Se reinició el equipo")
        self.assertEqual(len(db.buscar_tickets(self.conn, "internet")), 1)
        self.assertEqual(len(db.listar_notas(self.conn, tid)), 1)


if __name__ == "__main__":
    unittest.main()
