"""Versión web del Help Desk Ticket Manager (Flask).

Reutiliza database.py: solo cambia la interfaz.
Uso:  python app.py          (o: python app.py --demo)
Luego abrí http://127.0.0.1:5000 en el navegador.
"""
import sys

from flask import Flask, abort, flash, g, redirect, render_template, request, url_for

import database as db
from demo import cargar_demo

app = Flask(__name__)
app.secret_key = "cambiar-esto-si-lo-publicas"  # necesaria para flash()
app.config["DB_PATH"] = db.DB_PATH


def get_db():
    """Una conexión por petición, guardada en g."""
    if "db" not in g:
        g.db = db.conectar(app.config["DB_PATH"])
    return g.db


@app.teardown_appcontext
def cerrar_db(_error):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


@app.route("/")
def index():
    estado = request.args.get("estado", "")
    prioridad = request.args.get("prioridad", "")
    q = request.args.get("q", "").strip()
    conn = get_db()
    if q:
        tickets = db.buscar_tickets(conn, q)
        tickets = [t for t in tickets
                   if (not estado or t["estado"] == estado)
                   and (not prioridad or t["prioridad"] == prioridad)]
    else:
        tickets = db.listar_tickets(conn, estado or None, prioridad or None)
    conteo = {f["estado"]: f["cantidad"] for f in db.estadisticas(conn)["por_estado"]}
    return render_template("tickets.html", tickets=tickets, conteo=conteo, q=q,
                           estado=estado, prioridad=prioridad,
                           estados=db.ESTADOS, prioridades=db.PRIORIDADES)


@app.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    if request.method == "POST":
        f = {k: request.form.get(k, "").strip() for k in
             ("cliente", "telefono", "email", "equipo", "problema", "prioridad")}
        if not (f["cliente"] and f["equipo"] and f["problema"]):
            flash("Cliente, equipo y problema son obligatorios.", "error")
        elif f["prioridad"] not in db.PRIORIDADES:
            flash("Elegí una prioridad válida.", "error")
        else:
            conn = get_db()
            cid = db.obtener_o_crear_cliente(conn, f["cliente"], f["telefono"], f["email"])
            tid = db.crear_ticket(conn, cid, f["equipo"], f["problema"], f["prioridad"])
            flash(f"Ticket #{tid} creado.", "ok")
            return redirect(url_for("detalle", ticket_id=tid))
        return render_template("nuevo.html", prioridades=db.PRIORIDADES, f=f)
    return render_template("nuevo.html", prioridades=db.PRIORIDADES, f={})


@app.route("/ticket/<int:ticket_id>")
def detalle(ticket_id):
    conn = get_db()
    ticket = db.obtener_ticket(conn, ticket_id)
    if ticket is None:
        abort(404)
    return render_template("detalle.html", t=ticket, estados=db.ESTADOS,
                           notas=db.listar_notas(conn, ticket_id))


@app.route("/ticket/<int:ticket_id>/estado", methods=["POST"])
def cambiar_estado(ticket_id):
    estado = request.form.get("estado", "")
    if estado in db.ESTADOS and db.cambiar_estado(get_db(), ticket_id, estado):
        flash(f"Estado actualizado a '{estado}'.", "ok")
    else:
        flash("No se pudo cambiar el estado.", "error")
    return redirect(url_for("detalle", ticket_id=ticket_id))


@app.route("/ticket/<int:ticket_id>/nota", methods=["POST"])
def nueva_nota(ticket_id):
    texto = request.form.get("texto", "").strip()
    conn = get_db()
    if db.obtener_ticket(conn, ticket_id) is None:
        abort(404)
    if texto:
        db.agregar_nota(conn, ticket_id, texto)
        flash("Nota agregada.", "ok")
    else:
        flash("La nota no puede estar vacía.", "error")
    return redirect(url_for("detalle", ticket_id=ticket_id))


@app.route("/estadisticas")
def estadisticas():
    est = db.estadisticas(get_db())
    total = sum(f["cantidad"] for f in est["por_estado"]) or 1
    return render_template("estadisticas.html", est=est, total=total)


if __name__ == "__main__":
    if "--demo" in sys.argv:
        with app.app_context():
            conn = get_db()
            if conn.execute("SELECT COUNT(*) FROM tickets").fetchone()[0] == 0:
                cargar_demo(conn)
    app.run(debug=True)  # debug=True solo para desarrollo local
