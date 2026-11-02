import csv
import hashlib
import os
import statistics
import sys
import tempfile
import time

import copiador

TAMANO = 128 * 1024 * 1024
BLOQUES = (4096, 65536, 1048576)
REPS = 5


def crear_origen(ruta, tamano):
    with open(ruta, "wb") as f:
        restante = tamano
        while restante:
            n = min(restante, 1024 * 1024)
            f.write(os.urandom(n))
            restante -= n
        f.flush()
        os.fsync(f.fileno())


def enfriar(ruta):
    fd = os.open(ruta, os.O_RDONLY)
    try:
        os.fsync(fd)
        copiador.soltar_cache(fd)
    finally:
        os.close(fd)


def copia_pura(origen, destino, bloque):
    fi = os.open(origen, os.O_RDONLY)
    fo = os.open(destino, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    ini = time.perf_counter()
    while True:
        datos = os.read(fi, bloque)
        if not datos:
            break
        vista = memoryview(datos)
        while vista:
            vista = vista[os.write(fo, vista):]
    t = time.perf_counter() - ini
    os.close(fi)
    os.close(fo)
    return t


def mediana(valores):
    return statistics.median(valores)


def serie(origen, destino, bloque, reps, **kw):
    filas = []
    for _ in range(reps):
        if kw.pop("frio", False):
            enfriar(origen)
        r = copiador.copiar(origen, destino, bloque, **{k: v for k, v in kw.items() if k != "frio"})
        filas.append(r)
    return filas


def main(carpeta):
    origen = os.path.join(carpeta, "origen.bin")
    destino = os.path.join(carpeta, "destino.bin")
    crear_origen(origen, TAMANO)
    mib = TAMANO / 1024 / 1024
    salida = []
    filas_csv = []

    salida.append("a) tres tamanos de bloque (128 MiB, fsync, origen caliente, mediana de %d)" % REPS)
    for b in BLOQUES:
        rs = [copiador.copiar(origen, destino, b) for _ in range(REPS)]
        for i, r in enumerate(rs):
            filas_csv.append(["bloque", b, i + 1, r.lecturas, r.escrituras, r.t_copia, r.t_fsync, r.t_verificacion, r.t_total])
        mc, mf, mv, mt = (mediana([getattr(r, k) for r in rs]) for k in ("t_copia", "t_fsync", "t_verificacion", "t_total"))
        salida.append("bloque=%8d lecturas=%6d escrituras=%6d t_copia=%.4f t_fsync=%.4f t_verif=%.4f t_total=%.4f mib_s_copia=%.0f mib_s_total=%.0f"
                      % (b, rs[0].lecturas, rs[0].escrituras, mc, mf, mv, mt, mib / mc, mib / mt))

    salida.append("")
    salida.append("b) efecto de fsync (bloque 65536, mediana de %d)" % REPS)
    for usar in (False, True):
        rs = [copiador.copiar(origen, destino, 65536, usar_fsync=usar) for _ in range(REPS)]
        for i, r in enumerate(rs):
            filas_csv.append(["fsync_%d" % usar, 65536, i + 1, r.lecturas, r.escrituras, r.t_copia, r.t_fsync, r.t_verificacion, r.t_total])
        salida.append("fsync=%d t_copia=%.4f t_fsync=%.4f t_verif=%.4f t_total=%.4f"
                      % (usar, mediana([r.t_copia for r in rs]), mediana([r.t_fsync for r in rs]),
                         mediana([r.t_verificacion for r in rs]), mediana([r.t_total for r in rs])))

    salida.append("")
    salida.append("c) verificacion con cache caliente y con cache soltada (bloque 65536, mediana de %d)" % REPS)
    for releer in (False, True):
        rs = [copiador.copiar(origen, destino, 65536, releer_disco=releer) for _ in range(REPS)]
        for i, r in enumerate(rs):
            filas_csv.append(["releer_%d" % releer, 65536, i + 1, r.lecturas, r.escrituras, r.t_copia, r.t_fsync, r.t_verificacion, r.t_total])
        salida.append("releer_disco=%d t_verif=%.4f" % (releer, mediana([r.t_verificacion for r in rs])))

    salida.append("")
    salida.append("d) lectura del origen: cache soltada vs caliente (bloque 65536, mediana de %d)" % REPS)
    frios, calientes = [], []
    for _ in range(REPS):
        enfriar(origen)
        frios.append(copiador.copiar(origen, destino, 65536).t_copia)
        calientes.append(copiador.copiar(origen, destino, 65536).t_copia)
    for nombre, v in (("frio", frios), ("caliente", calientes)):
        for i, t in enumerate(v):
            filas_csv.append(["origen_" + nombre, 65536, i + 1, 0, 0, t, 0, 0, t])
    salida.append("origen_frio t_copia=%.4f | origen_caliente t_copia=%.4f" % (mediana(frios), mediana(calientes)))

    salida.append("")
    salida.append("e) bucle de lectura/escritura sin hash ni fsync (mediana de %d)" % REPS)
    for b in BLOQUES:
        ts = [copia_pura(origen, destino, b) for _ in range(REPS)]
        for i, t in enumerate(ts):
            filas_csv.append(["pura", b, i + 1, 0, 0, t, 0, 0, t])
        salida.append("bloque=%8d t_bucle=%.4f mib_s=%.0f" % (b, mediana(ts), mib / mediana(ts)))

    datos = open(origen, "rb").read()
    ts = []
    for _ in range(REPS):
        ini = time.perf_counter()
        hashlib.sha256(datos).hexdigest()
        ts.append(time.perf_counter() - ini)
    salida.append("")
    salida.append("f) sha256 de 128 MiB en memoria: mediana=%.4f mib_s=%.0f" % (mediana(ts), mib / mediana(ts)))

    with open("resultados/medicion.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["escenario", "bloque", "rep", "lecturas", "escrituras", "t_copia", "t_fsync", "t_verificacion", "t_total"])
        w.writerows(filas_csv)
    texto = "\n".join(salida)
    with open("resultados/resumen.txt", "w") as f:
        f.write(texto + "\n")
    print(texto)
    os.unlink(origen)
    os.unlink(destino)


if __name__ == "__main__":
    base = sys.argv[1] if len(sys.argv) > 1 else tempfile.gettempdir()
    with tempfile.TemporaryDirectory(dir=base) as d:
        main(d)
