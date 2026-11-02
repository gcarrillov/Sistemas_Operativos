import argparse
import errno
import hashlib
import os
import shutil
import signal
import stat
import sys
import tempfile
import threading
import time
from dataclasses import dataclass


class cancelado(Exception):
    pass


class error_verificacion(Exception):
    pass


@dataclass
class resultado:
    bytes_copiados: int = 0
    sha256: str = ""
    lecturas: int = 0
    lecturas_cortas: int = 0
    escrituras: int = 0
    escrituras_parciales: int = 0
    t_copia: float = 0.0
    t_fsync: float = 0.0
    t_verificacion: float = 0.0

    @property
    def t_total(self):
        return self.t_copia + self.t_fsync + self.t_verificacion


def escribir_todo(fd, datos, escribir, res):
    vista = memoryview(datos)
    while vista:
        n = escribir(fd, vista)
        res.escrituras += 1
        if n is None or n <= 0:
            raise OSError(errno.EIO, "escritura incompleta")
        if n < len(vista):
            res.escrituras_parciales += 1
        vista = vista[n:]


def hash_fd(fd, bloque):
    h = hashlib.sha256()
    os.lseek(fd, 0, os.SEEK_SET)
    while True:
        datos = os.read(fd, bloque)
        if not datos:
            return h.hexdigest()
        h.update(datos)


def soltar_cache(fd):
    if hasattr(os, "posix_fadvise"):
        os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_DONTNEED)


def verificar_espacio(carpeta, necesario):
    if shutil.disk_usage(carpeta).free < necesario:
        raise OSError(errno.ENOSPC, "espacio insuficiente en " + carpeta)


def copiar(origen, destino, bloque=65536, progreso=None, intervalo=0.5, cancelar=None,
           leer=os.read, escribir=os.write, usar_fsync=True, releer_disco=True):
    if bloque <= 0:
        raise ValueError("el bloque debe ser positivo")
    carpeta = os.path.dirname(os.path.abspath(destino))
    res = resultado()
    h = hashlib.sha256()
    fd_origen = os.open(origen, os.O_RDONLY)
    try:
        info = os.fstat(fd_origen)
        total = info.st_size
        verificar_espacio(carpeta, total)
        fd_tmp, ruta_tmp = tempfile.mkstemp(dir=carpeta, prefix="." + os.path.basename(destino) + ".", suffix=".tmp")
        try:
            os.fchmod(fd_tmp, stat.S_IMODE(info.st_mode))
            ultimo = 0.0

            def avisar(forzar=False):
                nonlocal ultimo
                if progreso is None:
                    return
                ahora = time.monotonic()
                if forzar or ahora - ultimo >= intervalo:
                    ultimo = ahora
                    progreso(res.bytes_copiados, total)

            ini = time.perf_counter()
            while True:
                if cancelar is not None and cancelar.is_set():
                    raise cancelado()
                datos = leer(fd_origen, bloque)
                if not datos:
                    break
                res.lecturas += 1
                if len(datos) < bloque and res.bytes_copiados + len(datos) < total:
                    res.lecturas_cortas += 1
                h.update(datos)
                escribir_todo(fd_tmp, datos, escribir, res)
                res.bytes_copiados += len(datos)
                avisar()
            res.t_copia = time.perf_counter() - ini
            avisar(True)

            ini = time.perf_counter()
            if usar_fsync:
                os.fsync(fd_tmp)
            res.t_fsync = time.perf_counter() - ini

            ini = time.perf_counter()
            if usar_fsync and releer_disco:
                soltar_cache(fd_tmp)
            res.sha256 = h.hexdigest()
            if os.fstat(fd_tmp).st_size != res.bytes_copiados or res.bytes_copiados != total:
                raise error_verificacion("tamano distinto: origen=%d copiado=%d temporal=%d"
                                         % (total, res.bytes_copiados, os.fstat(fd_tmp).st_size))
            if hash_fd(fd_tmp, bloque) != res.sha256:
                raise error_verificacion("hash distinto entre origen y temporal")
            res.t_verificacion = time.perf_counter() - ini

            os.close(fd_tmp)
            fd_tmp = None
            os.replace(ruta_tmp, destino)
            ruta_tmp = None
            if usar_fsync:
                fd_dir = os.open(carpeta, os.O_RDONLY)
                try:
                    os.fsync(fd_dir)
                finally:
                    os.close(fd_dir)
            return res
        except BaseException:
            if fd_tmp is not None:
                os.close(fd_tmp)
            if ruta_tmp is not None and os.path.exists(ruta_tmp):
                os.unlink(ruta_tmp)
            raise
    finally:
        os.close(fd_origen)


def parsear_bloque(texto):
    texto = texto.strip().lower()
    mult = {"k": 1024, "m": 1024 * 1024}
    if texto[-1] in mult:
        return int(texto[:-1]) * mult[texto[-1]]
    return int(texto)


def main(argv=None):
    ap = argparse.ArgumentParser(description="copia de archivos con verificacion y reemplazo atomico")
    ap.add_argument("origen")
    ap.add_argument("destino")
    ap.add_argument("--bloque", default="64k", help="tamano de bloque, ej: 4k, 64k, 1m")
    ap.add_argument("--intervalo", type=float, default=0.5, help="segundos entre reportes de progreso")
    ap.add_argument("--sin-progreso", action="store_true")
    ap.add_argument("--sin-fsync", action="store_true")
    a = ap.parse_args(argv)

    evento = threading.Event()
    signal.signal(signal.SIGINT, lambda *_: evento.set())
    signal.signal(signal.SIGTERM, lambda *_: evento.set())

    def mostrar(hecho, total):
        pct = 100.0 if total == 0 else 100.0 * hecho / total
        sys.stderr.write("\r%d/%d bytes (%.1f%%)" % (hecho, total, pct))
        sys.stderr.flush()

    try:
        r = copiar(a.origen, a.destino, parsear_bloque(a.bloque),
                   None if a.sin_progreso else mostrar, a.intervalo, evento, usar_fsync=not a.sin_fsync)
    except cancelado:
        sys.stderr.write("\ncancelado: destino intacto y temporal eliminado\n")
        return 130
    except (OSError, error_verificacion) as e:
        sys.stderr.write("\nerror: %s (destino intacto y temporal eliminado)\n" % e)
        return 1
    sys.stderr.write("\n")
    print("bytes=%d sha256=%s" % (r.bytes_copiados, r.sha256))
    print("lecturas=%d (cortas=%d) escrituras=%d (parciales=%d)"
          % (r.lecturas, r.lecturas_cortas, r.escrituras, r.escrituras_parciales))
    print("t_copia=%.4f t_fsync=%.4f t_verificacion=%.4f" % (r.t_copia, r.t_fsync, r.t_verificacion))
    return 0


if __name__ == "__main__":
    sys.exit(main())
