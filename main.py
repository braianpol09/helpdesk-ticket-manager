"""Help Desk Ticket Manager - interfaz de consola.

Uso:
    python main.py          # usa/crea helpdesk.db
    python main.py --demo   # carga datos de ejemplo si la base está vacía
"""
import sys

import database as db
from demo import cargar_demo

ANCHO = 84


# ---------- Utilidades de entrada ----------
def pedir_texto(mensaje, obligatorio=True):
    while True:
        valor = input(mensaje).strip()
        if valor or not obligatorio:
            return valor
        print("  Este campo es obligatorio.")


def pedir_entero(mensaje):
    while True:
        try:
            return int(input(mensaje).strip())
        except ValueError:
            print("  Ingresá un número válido.")


def elegir(mensaje, opciones):
    print(mensaje)
    for i, opcion in enumerate(opciones, 1):
        print(f"  {i}. {opcion}")
    while True:
        n = pedir_entero("  Opción: ")
        if 1 <= n <= len(opciones):
            return opciones[n - 1]
        print("  Opción fuera de rango.")


# ---------- Presentación ----------
def mostrar_tabla(filas):
    if not filas:
        print("\n  (sin resultados)")
        return
    print(f"\n{'ID':<4} {'Cliente':<16} {'Equipo':<17} {'Prior.':<8} {'Estado':<11} Problema")
    print("-" * ANCHO)
    for f in filas:
        problema = f["problema"]
        if len(problema) > 26:
            problema = problema[:23] + "..."
        print(
            f"{f['id']:<4} {f['cliente'][:15]:<16} {f['equipo'][:16]:<17} "
            f"{f['prioridad']:<8} {f['estado']:<11} {problema}"
        )


def mostrar_detalle(conn, ticket_id):
    t = db.obtener_ticket(conn, ticket_id)
    if t is None:
        print("  No existe un ticket con ese ID.")
        return
    print("\n" + "=" * ANCHO)
    print(f"Ticket #{t['id']}  |  {t['estado'].upper()}  |  prioridad {t['prioridad']}")
    print("=" * ANCHO)
    print(f"Cliente : {t['cliente']}  (tel: {t['telefono'] or '-'}, mail: {t['email'] or '-'})")
    print(f"Equipo  : {t['equipo']}")
    print(f"Problema: {t['problema']}")
    print(f"Creado  : {t['creado_en']}   Actualizado: {t['actualizado_en']}")
    if t["resuelto_en"]:
        print(f"Resuelto: {t['resuelto_en']}")
    notas = db.listar_notas(conn, ticket_id)
    print("\nNotas:")
    if not notas:
        print("  (sin notas)")
    for n in notas:
        print(f"  [{n['creado_en']}] {n['texto']}")


# ---------- Acciones del menú ----------
def nuevo_ticket(conn):
    print("\n--- Nuevo ticket ---")
    nombre = pedir_texto("Nombre del cliente: ")
    telefono = pedir_texto("Teléfono (opcional): ", obligatorio=False)
    email = pedir_texto("Email (opcional): ", obligatorio=False)
    equipo = pedir_texto("Equipo (ej: Notebook Lenovo): ")
    problema = pedir_texto("Descripción del problema: ")
    prioridad = elegir("Prioridad:", db.PRIORIDADES)
    cliente_id = db.obtener_o_crear_cliente(conn, nombre, telefono, email)
    ticket_id = db.crear_ticket(conn, cliente_id, equipo, problema, prioridad)
    print(f"\n  Ticket #{ticket_id} creado correctamente.")


def listar(conn):
    filtro = elegir("Filtrar por:", ["Todos", "Estado", "Prioridad"])
    estado = prioridad = None
    if filtro == "Estado":
        estado = elegir("Estado:", db.ESTADOS)
    elif filtro == "Prioridad":
        prioridad = elegir("Prioridad:", db.PRIORIDADES)
    mostrar_tabla(db.listar_tickets(conn, estado, prioridad))


def ver_detalle(conn):
    mostrar_detalle(conn, pedir_entero("ID del ticket: "))


def actualizar_estado(conn):
    ticket_id = pedir_entero("ID del ticket: ")
    if db.obtener_ticket(conn, ticket_id) is None:
        print("  No existe un ticket con ese ID.")
        return
    estado = elegir("Nuevo estado:", db.ESTADOS)
    db.cambiar_estado(conn, ticket_id, estado)
    print(f"  Ticket #{ticket_id} ahora está '{estado}'.")


def agregar_nota(conn):
    ticket_id = pedir_entero("ID del ticket: ")
    if db.obtener_ticket(conn, ticket_id) is None:
        print("  No existe un ticket con ese ID.")
        return
    db.agregar_nota(conn, ticket_id, pedir_texto("Nota: "))
    print("  Nota agregada.")


def buscar(conn):
    texto = pedir_texto("Buscar (problema, equipo o cliente): ")
    mostrar_tabla(db.buscar_tickets(conn, texto))


def ver_estadisticas(conn):
    est = db.estadisticas(conn)
    print("\n--- Estadísticas ---")
    print("Tickets por estado:")
    for f in est["por_estado"]:
        print(f"  {f['estado']:<11} {f['cantidad']}")
    print("Tickets por prioridad:")
    for f in est["por_prioridad"]:
        print(f"  {f['prioridad']:<11} {f['cantidad']}")
    horas = est["horas_promedio_resolucion"]
    if horas is None:
        print("Tiempo promedio de resolución: todavía no hay tickets resueltos")
    else:
        print(f"Tiempo promedio de resolución: {horas:.1f} horas")
    print("Clientes con más tickets:")
    for f in est["top_clientes"]:
        print(f"  {f['nombre']:<20} {f['tickets']}")


def exportar(conn):
    ruta = pedir_texto("Nombre del archivo (Enter = tickets.csv): ", obligatorio=False)
    ruta = ruta or "tickets.csv"
    cantidad = db.exportar_csv(conn, ruta)
    print(f"  {cantidad} tickets exportados a {ruta}")


MENU = [
    ("Nuevo ticket", nuevo_ticket),
    ("Listar tickets", listar),
    ("Ver detalle de un ticket", ver_detalle),
    ("Cambiar estado", actualizar_estado),
    ("Agregar nota", agregar_nota),
    ("Buscar", buscar),
    ("Estadísticas", ver_estadisticas),
    ("Exportar a CSV", exportar),
]


def main():
    conn = db.conectar()
    if "--demo" in sys.argv:
        hay_datos = conn.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
        if hay_datos == 0:
            cargar_demo(conn)
            print("Datos de ejemplo cargados.")
    try:
        while True:
            print("\n=== HELP DESK TICKET MANAGER ===")
            for i, (nombre, _) in enumerate(MENU, 1):
                print(f"  {i}. {nombre}")
            print("  0. Salir")
            opcion = pedir_entero("Opción: ")
            if opcion == 0:
                break
            if 1 <= opcion <= len(MENU):
                MENU[opcion - 1][1](conn)
            else:
                print("  Opción inválida.")
    except (KeyboardInterrupt, EOFError):
        print()
    finally:
        conn.close()
        print("Hasta luego.")


if __name__ == "__main__":
    main()
