"""Carga datos de ejemplo para probar el programa (python main.py --demo)."""
import database as db

TICKETS = [
    # cliente, equipo, problema, prioridad, estado, creado, resuelto
    ("Laura Gómez", "Notebook Lenovo", "No enciende, la batería no carga", "alta",
     "resuelto", "2026-11-02 10:00:00", "2026-11-02 15:30:00"),
    ("Laura Gómez", "Impresora HP", "No imprime por WiFi", "media",
     "cerrado", "2026-11-05 09:15:00", "2026-11-05 11:00:00"),
    ("Carlos Pérez", "PC de escritorio", "Pantalla azul al iniciar Windows", "critica",
     "en_proceso", "2026-11-17 08:30:00", None),
    ("Carlos Pérez", "PC de escritorio", "Instalar Office y antivirus", "baja",
     "abierto", "2026-11-18 16:00:00", None),
    ("Marta Ruiz", "Router TP-Link", "Se cae internet cada pocas horas", "alta",
     "resuelto", "2026-11-10 18:00:00", "2026-11-11 10:00:00"),
    ("Marta Ruiz", "Notebook Dell", "Muy lenta, tarda 10 minutos en iniciar", "media",
     "abierto", "2026-11-18 11:20:00", None),
    ("Diego Silva", "PC gamer", "Se reinicia sola en juegos (posible temperatura)", "alta",
     "en_proceso", "2026-11-16 20:00:00", None),
]


def cargar_demo(conn):
    for cliente, equipo, problema, prio, estado, creado, resuelto in TICKETS:
        cid = db.obtener_o_crear_cliente(conn, cliente)
        conn.execute(
            """INSERT INTO tickets (cliente_id, equipo, problema, prioridad,
               estado, creado_en, actualizado_en, resuelto_en)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (cid, equipo, problema, prio, estado, creado, resuelto or creado, resuelto),
        )
    conn.commit()
