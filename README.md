# Help Desk Ticket Manager

Sistema de gestión de tickets de soporte técnico para consola, hecho con **Python** y **SQLite**.
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

Solo requiere **Python 3.9 o superior**. No usa librerías externas.

```bash
git clone https://github.com/braianpol09/helpdesk-ticket-manager.git
cd helpdesk-ticket-manager
python main.py --demo   # la primera vez, con datos de ejemplo
python main.py          # uso normal
```

## Tests

```bash
python -m unittest -v
```

## Estructura del proyecto

```
main.py            Interfaz de consola (menú y entrada de datos)
database.py        Acceso a datos: tablas, consultas y reportes en SQLite
demo.py            Datos de ejemplo para probar el programa
test_database.py   Tests automáticos de la capa de datos
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

## Ideas para mejorar

- Interfaz web o de escritorio.
- Asignar tickets a distintos técnicos.
- Gráficos de estadísticas.

## Autor

Brian Polanco — [LinkedIn](https://linkedin.com/in/brian-polanco)
