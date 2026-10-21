# Semana 8: bloqueos mutuos y algoritmo del banquero

Sistemas Operativos - UNSA - 2026-B

Simulación y prevención de bloqueos mutuos (*deadlocks*) mediante la implementación del Algoritmo del Banquero. El sistema gestiona la asignación de múltiples tipos de recursos compartidos entre varios procesos y evalúa preventivamente si una concesión conduce a un estado seguro antes de otorgar recursos.

## Contenido

| archivo | función |
| :--- | :--- |
| `banquero.py` | representación del estado del sistema (`Allocation`, `Max`, `Need`, `Available`) y algoritmo de verificación de seguridad |
| `experimento.py` | simulación de solicitudes dinámicas de recursos y análisis de estados seguros e inseguros |
| `test_banquero.py` | pruebas unitarias automatizadas para validar la detección de secuencias de seguridad |
| `resultados/` | trazas de asignación, secuencias calculadas y reportes de ejecución |
| `main.tex` | informe académico para compilar en Overleaf |

## Cómo funciona

- **Estado del sistema:** Se gestionan vectores de recursos disponibles ($Available$) y matrices de recursos asignados ($Allocation$), recursos máximos requeridos ($Max$) y necesidades restantes ($Need = Max - Allocation$).
- **Algoritmo de seguridad:** Para evaluar o conceder una solicitud, el sistema simula la asignación hipotética y busca la existencia de al menos una secuencia segura $\langle P_0, P_1, \dots, P_{n-1} \rangle$ que garantice la finalización de todos los procesos sin caer en interbloqueo.
- **Prevención de deadlock:** Si el estado resultante es seguro, la solicitud es aprobada; de lo contrario, el proceso solicitante entra en espera y el sistema conserva su estado anterior.

## Uso

Requiere Python 3.10 o superior, sin dependencias externas.

```bash
python3 -c 'from banquero import ejemplo_clasico; print(ejemplo_clasico().seguridad())'   # demostración del algoritmo de seguridad
python3 -m unittest -v                                                                    # pruebas automatizadas del sistema
```