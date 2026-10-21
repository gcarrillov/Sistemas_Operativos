<div align="center">
<table>
    <thead>
        <tr>
            <td style="width:25%; text-align:center;"><img src="img/epis.png" alt="EPIS" style="width:80%; height:auto"/></td>
            <td style="text-align:center;">
                <span><b>UNIVERSIDAD NACIONAL DE SAN AGUSTIN</b></span><br />
                <span><b>FACULTAD DE INGENIERÍA DE PRODUCCIÓN Y SERVICIOS</b></span><br />
                <span><b>DEPARTAMENTO ACADÉMICO DE INGENIERÍA DE SISTEMAS E INFORMÁTICA</b></span><br />
                <span><b>ESCUELA PROFESIONAL DE INGENIERÍA DE SISTEMAS</b></span>
            </td>
            <td style="width:25%; text-align:center;"><img src="img/abet.png" alt="ABET" style="width:80%; height:auto"/></td>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td colspan="3"><span><b>Curso</b></span>: Sistemas Operativos</td>
        </tr>
        <tr>
            <td colspan="3"><span><b>Semestre:</b></span>: 2026 - B</td>
        </tr>
    </tbody>
</table>
</div>
<div align="center" style="margin-top: 10px;">
    <img src="img/unsa.png" alt="UNSA" width="450px" height="150px">
    <h1 style="font-weight:bold; font-size: 2em;">Curso completo de Sistemas Operativos</h1>
</div>


## Informes y entregables del curso

Este curso no cuenta con una carpeta de drive. Las tareas, prácticas y entregables se irán insertando en carpetas enlazadas dentro de este repositorio, y cada una se podrá consultar mediante el enlace indicado en el índice.

Repositorio principal: [Sistemas_Operativos](https://github.com/gcarrillov/Sistemas_Operativos)

## Índice

| Semana | Práctica / Tarea | Tema | Presentado en |
| :--- | :--- | :--- | :--- |
| Semana 6 | [descripcion concurrencia](#concurrencia) | Concurrencia y Threads | [Concurrencia](https://github.com/gcarrillov/Sistemas_Operativos/tree/7ddaef59b1b8a0acbc2bf45541262280760ab61e/Concurrencia) |
| Semana 7 | [descripcion sincronizacion](#sincronización-de-procesos) | Sincronización de Procesos | [Sincronización de Procesos](https://github.com/gcarrillov/Sistemas_Operativos/tree/14172c37b9ef96bff8d49bce56625acd261949f1/Semana%207%3A%20Sincronizaci%C3%B3n%20de%20Procesos) |
| Semana 8 | [descripcion bloqueos mutuos](#bloqueos-mutuos) | Bloqueos Mutuos | [Bloqueos Mutuos](https://github.com/gcarrillov/Sistemas_Operativos/tree/14172c37b9ef96bff8d49bce56625acd261949f1/Semana%208%3A%20Bloqueos%20Mutuos) |

1. [Equipo y Recursos Varios](#equipo-y-recursos-varios)


# Prácticas y Tareas

### Concurrencia
Semana 6 · Unidad II · Capítulo III

Esta práctica estudia cómo varias ejecuciones comparten tiempo, memoria y recursos. Se provoca una condición de carrera con varios threads que actualizan un contador y transfieren unidades entre dos saldos compartidos, y luego se corrige y se mide. Entre los puntos principales se trabajó en:

- Provocar el fallo: dos y cuatro threads con pausas aleatorias entre lectura y escritura, repitiendo 100 veces y registrando las corridas que violan la suma total o los límites.

- Definir invariantes: contador igual al número de pasos, suma de saldos constante y saldos no negativos.

- Corrección: protección de la transición completa con un `Lock`, repitiendo las mismas pruebas.

- Medición: costo de la protección con y sin pausas.

- Atomicidad y visibilidad: explicación de lo obtenido con la exclusión mutua y la relación happens-before.

- Prueba automatizada: pruebas con `unittest` que fallan si algún invariante se rompe.

La carpeta incluye el código fuente, los resultados de las corridas, el informe en LaTeX y un README propio que explica cómo ejecutarlo.

**Para detallar en el desarrollo ingresar a [Concurrencia](https://github.com/gcarrillov/Sistemas_Operativos/tree/7ddaef59b1b8a0acbc2bf45541262280760ab61e/Concurrencia)**

### Sincronización de Procesos
Semana 7 · Unidad II · Capítulo IV

Esta práctica explora los mecanismos de sincronización de procesos y el control de acceso a la sección crítica mediante la implementación de un sistema de reservas concurrentes. Se evalúa la protección de recursos compartidos para evitar condiciones de carrera, inconsistencias de estado y sobre-reservas (*overbooking*). Entre los puntos principales se trabajó en:

- Exclusión mutua en la sección crítica: uso de primitivas de sincronización (`Lock`, `Semaphore` y `Condition`) para garantizar el acceso seguro a la consulta y actualización de disponibilidad.

- Sincronización condicional: gestión de procesos en espera activa o suspendida cuando se agotan los cupos, notificando adecuadamente tras la liberación de recursos.

- Verificación de invariantes: preservación de los límites del sistema garantizando que el número de reservas $R$ y la capacidad máxima $C$ cumplan en todo momento $0 \le R \le C$.

- Pruebas automatizadas: ejecución de casos de prueba con `unittest` para verificar que la consistencia del sistema se mantiene intacta bajo alta concurrencia.

La carpeta incluye el código ejecutable (`reservas.py`), pruebas unitarias (`test_reservas.py`), registros en `resultados/`, el informe en LaTeX (`main.tex`) y su README con instrucciones.

**Para detallar en el desarrollo ingresar a [Sincronización de Procesos](https://github.com/gcarrillov/Sistemas_Operativos/tree/14172c37b9ef96bff8d49bce56625acd261949f1/Semana%207%3A%20Sincronizaci%C3%B3n%20de%20Procesos)**

### Bloqueos Mutuos
Semana 8 · Unidad II · Capítulo V

Esta práctica aborda el problema de los bloqueos mutuos (*deadlocks*) en entornos multiproceso y la prevención de estados inseguros mediante el Algoritmo del Banquero de Dijkstra. Se modela la asignación y liberación de recursos de manera segura. Entre los puntos principales se trabajó en:

- Modelado matricial de recursos: representación formal del estado del sistema mediante vectores y matrices de Disponibles ($A$), Máximos ($M$), Asignados ($C$) y Necesidad ($N$).

- Algoritmo de seguridad: determinación de secuencias seguras de ejecución que garantizan que todos los procesos puedan finalizar sin caer en interbloqueo.

- Simulación y prevención: validación previa a la asignación de peticiones para evitar la transición a estados inseguros.

- Verificación automatizada: suite de pruebas unitarias con `unittest` para comprobar la detección de *deadlocks* y el funcionamiento correcto del simulador.

La carpeta incluye la implementación principal (`banquero.py`), pruebas automatizadas (`test_banquero.py`), trazas de ejecución, el informe en LaTeX (`main.tex`) listo para Overleaf y un README explicativo.

**Para detallar en el desarrollo ingresar a [Bloqueos Mutuos](https://github.com/gcarrillov/Sistemas_Operativos/tree/14172c37b9ef96bff8d49bce56625acd261949f1/Semana%208%3A%20Bloqueos%20Mutuos)**

### Próximas prácticas
Las siguientes tareas se agregarán como nuevas carpetas enlazadas en este mismo repositorio y se actualizará el índice.


# Equipo y Recursos Varios

En esta sección se presenta al integrante del curso junto con el enlace a su repositorio. Además, se incluyen recursos adicionales que complementan el trabajo realizado.

## Autor

- **Gustavo Alonso Carrillo Villalta** → [Este Repositorio](https://github.com/gcarrillov/Sistemas_Operativos.git)
```text
https://github.com/gcarrillov/Sistemas_Operativos.git
```

## Docente

- **MSc. Norman Patrick Harvey Arce**

## Recursos Complementarios

- Informes de cada práctica en LaTeX dentro de su carpeta
- Código fuente y resultados reproducibles de cada tarea