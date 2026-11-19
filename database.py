"""Capa de acceso a datos del sistema de tickets (SQLite).

Todas las consultas usan parámetros (?) para evitar inyección SQL.
"""
import csv
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "helpdesk.db"
PRIORIDADES = ("baja", "media", "alta", "critica")
ESTADOS = ("abierto", "en_proceso", "resuelto", "cerrado")

# Las más urgentes primero al listar
ORDEN_PRIORIDAD = """CASE t.prioridad
    WHEN 'critica' THEN 1 WHEN 'alta' THEN 2 WHEN 'media' THEN 3 ELSE 4 END"""


def ahora():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def conectar(ruta=DB_PATH):
    """Abre la base (o la crea) y deja las tablas listas."""
    conn = sqlite3.connect(ruta)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    crear_tablas(conn)
    return conn


def crear_tablas(conn):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS clientes (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre   TEXT NOT NULL UNIQUE,
            telefono TEXT,
            email    TEXT
        );
        CREATE TABLE IF NOT EXISTS tickets (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id     INTEGER NOT NULL REFERENCES clientes(id),
            equipo         TEXT NOT NULL,
            problema       TEXT NOT NULL,
            prioridad      TEXT NOT NULL
                CHECK (prioridad IN ('baja','media','alta','critica')),
            estado         TEXT NOT NULL DEFAULT 'abierto'
                CHECK (estado IN ('abierto','en_proceso','resuelto','cerrado')),
            creado_en      TEXT NOT NULL,
            actualizado_en TEXT NOT NULL,
            resuelto_en    TEXT
        );
        CREATE TABLE IF NOT EXISTS notas (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
            texto     TEXT NOT NULL,
            creado_en TEXT NOT NULL
        );
        """
    )
    conn.commit()


# ---------- Clientes ----------
def obtener_o_crear_cliente(conn, nombre, telefono="", email=""):
    """Devuelve el id del cliente; si no existe, lo crea."""
    fila = conn.execute(
        "SELECT id FROM clientes WHERE nombre = ? COLLATE NOCASE", (nombre,)
    ).fetchone()
    if fila:
        return fila["id"]
    cur = conn.execute(
        "INSERT INTO clientes (nombre, telefono, email) VALUES (?, ?, ?)",
        (nombre, telefono, email),
    )
    conn.commit()
    return cur.lastrowid


# ---------- Tickets ----------
def crear_ticket(conn, cliente_id, equipo, problema, prioridad):
    if prioridad not in PRIORIDADES:
        raise ValueError(f"Prioridad inválida: {prioridad}")
    ts = ahora()
    cur = conn.execute(
        """INSERT INTO tickets
           (cliente_id, equipo, problema, prioridad, creado_en, actualizado_en)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (cliente_id, equipo, problema, prioridad, ts, ts),
    )
    conn.commit()
    return cur.lastrowid


def listar_tickets(conn, estado=None, prioridad=None):
    consulta = """
        SELECT t.id, c.nombre AS cliente, t.equipo, t.problema,
               t.prioridad, t.estado, t.creado_en
        FROM tickets t
        JOIN clientes c ON c.id = t.cliente_id
        WHERE 1 = 1"""
    params = []
    if estado:
        consulta += " AND t.estado = ?"
        params.append(estado)
    if prioridad:
        consulta += " AND t.prioridad = ?"
        params.append(prioridad)
    consulta += f" ORDER BY {ORDEN_PRIORIDAD}, t.creado_en"
    return conn.execute(consulta, params).fetchall()


def obtener_ticket(conn, ticket_id):
    return conn.execute(
        """SELECT t.*, c.nombre AS cliente, c.telefono, c.email
           FROM tickets t JOIN clientes c ON c.id = t.cliente_id
           WHERE t.id = ?""",
        (ticket_id,),
    ).fetchone()


def cambiar_estado(conn, ticket_id, estado):
    """Cambia el estado. Devuelve True si el ticket existía."""
    if estado not in ESTADOS:
        raise ValueError(f"Estado inválido: {estado}")
    ts = ahora()
    if estado in ("resuelto", "cerrado"):
        cur = conn.execute(
            """UPDATE tickets
               SET estado = ?, actualizado_en = ?,
                   resuelto_en = COALESCE(resuelto_en, ?)
               WHERE id = ?""",
            (estado, ts, ts, ticket_id),
        )
    else:  # si se reabre, ya no está resuelto
        cur = conn.execute(
            """UPDATE tickets
               SET estado = ?, actualizado_en = ?, resuelto_en = NULL
               WHERE id = ?""",
            (estado, ts, ticket_id),
        )
    conn.commit()
    return cur.rowcount > 0


def buscar_tickets(conn, texto):
    """Busca por problema, equipo o nombre del cliente."""
    patron = f"%{texto}%"
    return conn.execute(
        f"""SELECT t.id, c.nombre AS cliente, t.equipo, t.problema,
                   t.prioridad, t.estado, t.creado_en
            FROM tickets t JOIN clientes c ON c.id = t.cliente_id
            WHERE t.problema LIKE ? OR t.equipo LIKE ? OR c.nombre LIKE ?
            ORDER BY {ORDEN_PRIORIDAD}, t.creado_en""",
        (patron, patron, patron),
    ).fetchall()


# ---------- Notas ----------
def agregar_nota(conn, ticket_id, texto):
    ts = ahora()
    conn.execute(
        "INSERT INTO notas (ticket_id, texto, creado_en) VALUES (?, ?, ?)",
        (ticket_id, texto, ts),
    )
    conn.execute(
        "UPDATE tickets SET actualizado_en = ? WHERE id = ?", (ts, ticket_id)
    )
    conn.commit()


def listar_notas(conn, ticket_id):
    return conn.execute(
        "SELECT texto, creado_en FROM notas WHERE ticket_id = ? ORDER BY id",
        (ticket_id,),
    ).fetchall()


# ---------- Reportes ----------
def estadisticas(conn):
    por_estado = conn.execute(
        "SELECT estado, COUNT(*) AS cantidad FROM tickets GROUP BY estado"
    ).fetchall()
    por_prioridad = conn.execute(
        "SELECT prioridad, COUNT(*) AS cantidad FROM tickets GROUP BY prioridad"
    ).fetchall()
    horas = conn.execute(
        """SELECT AVG((julianday(resuelto_en) - julianday(creado_en)) * 24) AS horas
           FROM tickets WHERE resuelto_en IS NOT NULL"""
    ).fetchone()["horas"]
    top_clientes = conn.execute(
        """SELECT c.nombre, COUNT(t.id) AS tickets
           FROM clientes c JOIN tickets t ON t.cliente_id = c.id
           GROUP BY c.id ORDER BY tickets DESC, c.nombre LIMIT 5"""
    ).fetchall()
    return {
        "por_estado": por_estado,
        "por_prioridad": por_prioridad,
        "horas_promedio_resolucion": horas,
        "top_clientes": top_clientes,
    }


def exportar_csv(conn, ruta):
    """Exporta todos los tickets a un CSV. Devuelve la cantidad exportada."""
    filas = listar_tickets(conn)
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(
            ["id", "cliente", "equipo", "problema", "prioridad", "estado", "creado_en"]
        )
        for fila in filas:
            escritor.writerow(list(fila))
    return len(filas)
