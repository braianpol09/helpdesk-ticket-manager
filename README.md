# Help Desk Ticket Manager

Sistema de gestión de tickets de soporte técnico con **Python** y **SQLite**, con dos interfaces: una **web (Flask)** y una de **consola**.
Nació de mi trabajo como técnico independiente: necesitaba llevar el registro de equipos, fallas y
reparaciones de mis clientes en un solo lugar.

## Qué hace

- Registrar tickets con cliente, equipo, descripción del problema y prioridad (baja, media, alta, crítica).
- Listar tickets, ordenados por urgencia, con filtros por estado o prioridad.
- Cambiar el estado de un ticket (abierto → en proceso → resuelto → cerrado) y guardar la fecha de resolución.
- Agregar notas de seguimiento a cada ticket.
- Buscar por problema, equipo o nombre de cliente.
- Ver estadísticas: tickets por estado y prioridad, tiempo promedio de resolución y clientes con más tickets.
- Exportar todos los tickets a CSV.

## Cómo ejecutarlo

Requiere **Python 3.9 o superior**.

```bash
git clone https://github.com/braianpol09/helpdesk-ticket-manager.git
cd helpdesk-ticket-manager
```

**Versión web** (usa Flask):

```bash
pip install -r requirements.txt
python app.py --demo    # la primera vez, con datos de ejemplo
python app.py           # uso normal
```

Después abrí http://127.0.0.1:5000 en el navegador.

**Versión de consola** (no necesita librerías externas):

```bash
python main.py --demo
```

## Tests

```bash
python -m unittest -v
```

## Estructura del proyecto

```
app.py             Interfaz web (rutas de Flask)
templates/         Páginas HTML (Jinja2)
static/style.css   Estilos (con modo claro y oscuro)
main.py            Interfaz de consola (menú y entrada de datos)
database.py        Acceso a datos: tablas, consultas y reportes en SQLite
demo.py            Datos de ejemplo para probar el programa
test_database.py   Tests de la capa de datos
test_app.py        Tests de la versión web
```

## Modelo de datos

```
clientes (id, nombre, telefono, email)
    1 ──< tickets (id, cliente_id, equipo, problema, prioridad, estado,
                   creado_en, actualizado_en, resuelto_en)
              1 ──< notas (id, ticket_id, texto, creado_en)
```

Los reportes usan `JOIN`, `GROUP BY` y funciones de fecha de SQLite.
Todas las consultas están parametrizadas.

## Qué aprendí

- Diseñar una base relacional con claves foráneas y restricciones (`CHECK`).
- Separar la lógica de datos de la interfaz.
- Escribir tests con `unittest` usando una base en memoria.
- Armar una app web con Flask reutilizando la misma capa de datos (rutas, formularios, plantillas Jinja2).
- Validar los datos del formulario del lado del servidor y evitar XSS (las plantillas escapan el HTML).

## Ideas para mejorar

- Asignar tickets a distintos técnicos y agregar inicio de sesión.
- Gráficos de estadísticas.

## Autor

Brian Polanco — [LinkedIn](https://linkedin.com/in/brian-polanco)
