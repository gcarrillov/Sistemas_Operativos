# Semana 7: sincronización de procesos y sección crítica

Sistemas Operativos - UNSA - 2026-B

Implementación de mecanismos de sincronización de procesos y control de acceso a la sección crítica mediante un sistema de reservas concurrentes. El proyecto evalúa el uso de primitivas de sincronización para evitar condiciones de carrera, inconsistencias en el estado compartido y sobre-reservas (*overbooking*).

## Contenido

| archivo | función |
| :--- | :--- |
| `reservas.py` | simulación del sistema de reservas concurrentes con primitivas de exclusión mutua |
| `test_reservas.py` | pruebas unitarias automatizadas para verificar la consistencia del estado y la exclusión mutua |
| `resultados/` | trazas de ejecución, logs de asignación de asientos y reportes de concurrencia |
| `main.tex` | informe académico para compilar en Overleaf |

## Cómo funciona

- **Exclusión mutua en la sección crítica:** Se protegen las operaciones de consulta y modificación de cupos mediante primitivas de sincronización (`Lock`, `Semaphore` o `Condition`), evitando que múltiples solicitudes interfieran entre sí.
- **Sincronización condicional:** Manejo de hilos en espera cuando la capacidad se agota, notificando oportunamente a los procesos suspendidos en cuanto se libera una reserva.
- **Invariante del sistema:** Si $C$ representa la capacidad máxima y $R$ el número total de reservas confirmadas, el sistema garantiza en todo momento que $0 \le R \le C$, impidiendo estados inconsistentes bajo alta concurrencia.

## Uso

Requiere Python 3.10 o superior, sin dependencias externas.

```bash
python3 reservas.py          # demostración del sistema de reservas sincronizado
python3 -m unittest -v       # pruebas automatizadas del sistema
```