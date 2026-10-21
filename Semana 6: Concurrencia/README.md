# Semana 6: condicion de carrera y reparacion controlada

Sistemas Operativos - UNSA - 2026-B

Varios threads actualizan un contador y transfieren unidades entre dos saldos compartidos. La version sin proteccion rompe los invariantes; la version con `threading.Lock` los conserva.

## Contenido

| archivo | funcion |
| :--- | :--- |
| `carrera.py` | modelo de la cuenta, operaciones, verificador de invariantes y ejecucion con N threads |
| `experimento.py` | campana de 100 repeticiones por escenario y medicion de costo con y sin pausas |
| `intercalado.py` | fuerza un intercalado defectuoso y muestra la traza (quien, que, cuando, dato) |
| `test_invariantes.py` | pruebas automatizadas que fallan si un invariante se rompe |
| `resultados/` | `corridas.csv`, `resumen.txt` y trazas generadas |
| `informe.tex` | informe para compilar en Overleaf |

## Como funciona

- Estado compartido: `contador`, `a` y `b` (saldos iniciales 100 y 100).
- Cada paso incrementa el contador y transfiere entre 1 y 60 unidades en direccion aleatoria, con pausas aleatorias de hasta 1 ms entre lectura y escritura.
- Invariantes: el contador es igual al numero de pasos, `a + b` es constante (200) y ningun saldo es negativo.
- `Cuenta(protegida=False)` ejecuta los pasos sin sincronizacion; `Cuenta(protegida=True)` envuelve el paso completo en un `Lock`.

## Uso

Requiere Python 3.8 o superior, sin dependencias externas.

```bash
python3 intercalado.py        # traza del intercalado defectuoso y del corregido
python3 experimento.py        # 100 repeticiones x {2, 4} threads x {sin, con lock}
python3 -m unittest -v        # pruebas automatizadas
PROTEGIDA=0 python3 -m unittest test_invariantes.PruebasInvariantes.test_version_protegida_conserva_invariantes   # debe fallar
```

`experimento.py` tarda cerca de un minuto y reescribe los archivos de `resultados/`.
