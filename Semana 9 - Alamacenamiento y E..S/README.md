# Semana 9: copiador verificable y observable

Sistemas Operativos - UNSA - 2026-B

Implementación de una utilidad de copia de archivos con tamaño de bloque configurable, capaz de gestionar lecturas y escrituras parciales, falta de espacio y cancelaciones. El sistema garantiza la integridad de los datos mediante la verificación del tamaño y del hash SHA-256, utilizando un archivo temporal y un reemplazo atómico para evitar que el destino quede en un estado inválido ante cualquier error.

## Contenido

| archivo | función |
| :--- | :--- |
| `copiador.py` | utilidad de copia de archivos (función `copiar()` y línea de comandos) |
| `test_copiador.py` | 15 pruebas automatizadas con `unittest` |
| `medir.py` | medición con tres tamaños de bloque, efecto de `fsync` y de la caché |
| `resultados/` | `medicion.csv`, `resumen.txt` y `demo_cli.txt` |
| `informe.tex` | informe académico para compilar en Overleaf |

## Cómo funciona

- **Verificación inicial:** Se abre el archivo de origen, se obtiene su tamaño y se comprueba que exista espacio disponible en el sistema de archivos del destino.
- **Copia segura:** Se crea un archivo temporal en la misma carpeta del destino para evitar modificar el archivo original durante la operación.
- **Transferencia de datos:** Se procesan bloques de tamaño configurable, gestionando las lecturas y escrituras parciales. Durante la copia se calcula el hash SHA-256 y se informa del progreso según el intervalo establecido.
- **Sincronización y validación:** Se ejecuta `fsync` sobre el archivo temporal, se libera su caché cuando corresponde y se vuelve a leer para verificar que el tamaño y el hash SHA-256 coincidan con los datos originales.
- **Reemplazo atómico:** Si la verificación finaliza correctamente, se utiliza `os.replace` para sustituir el destino y se sincroniza el directorio.
- **Gestión de errores:** Ante un error o una cancelación, se elimina el archivo temporal y se conserva intacto el destino anterior.

## Uso

Requiere Python 3.8 o superior en Linux, sin dependencias externas.

```bash
python3 copiador.py origen.bin destino.bin --bloque 64k
python3 copiador.py origen.bin destino.bin --bloque 4k --intervalo 0.2
python3 copiador.py origen.bin destino.bin --sin-progreso --sin-fsync
python3 -m unittest -v
python3 medir.py /ruta/con/espacio
```

## Opciones principales:

- **bloque:** establece el tamaño del bloque en bytes o mediante los sufijos k y m.

- **intervalo:** define el intervalo en segundos entre los reportes de progreso.

- **sin-progreso:** desactiva los mensajes de progreso.

- **sin-fsync:** omite las operaciones de sincronización explícita.

## Códigos de salida: 0 indica éxito, 1 indica un error y 130 indica una cancelación mediante Ctrl+C o SIGTERM.

### Nota: El script medir.py genera un archivo de 128 MiB, puede tardar aproximadamente un minuto y sobrescribe los archivos de resultados almacenados en resultados/.