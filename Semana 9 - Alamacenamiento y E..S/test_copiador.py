import errno
import hashlib
import os
import tempfile
import threading
import unittest
from unittest import mock

import copiador


def sha(ruta):
    with open(ruta, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


class pruebas_copiador(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.d = self._dir.name
        self.origen = os.path.join(self.d, "origen.bin")
        self.destino = os.path.join(self.d, "destino.bin")

    def tearDown(self):
        self._dir.cleanup()

    def crear(self, n):
        with open(self.origen, "wb") as f:
            f.write(os.urandom(n))

    def crear_destino_previo(self):
        with open(self.destino, "wb") as f:
            f.write(b"contenido previo valido")

    def sin_temporales(self):
        return [x for x in os.listdir(self.d) if x.endswith(".tmp")] == []

    def previo_intacto(self):
        with open(self.destino, "rb") as f:
            return f.read() == b"contenido previo valido"

    def test_archivo_vacio(self):
        self.crear(0)
        r = copiador.copiar(self.origen, self.destino, 4096)
        self.assertEqual(os.path.getsize(self.destino), 0)
        self.assertEqual(r.bytes_copiados, 0)
        self.assertTrue(self.sin_temporales())

    def test_archivo_pequeno(self):
        self.crear(100)
        copiador.copiar(self.origen, self.destino, 4096)
        self.assertEqual(sha(self.origen), sha(self.destino))

    def test_archivo_mayor_al_buffer(self):
        self.crear(1000003)
        r = copiador.copiar(self.origen, self.destino, 4096)
        self.assertEqual(sha(self.origen), sha(self.destino))
        self.assertEqual(r.lecturas, 245)

    def test_escrituras_parciales_se_completan(self):
        self.crear(5000)
        corta = lambda fd, datos: os.write(fd, datos[:7])
        r = copiador.copiar(self.origen, self.destino, 1024, escribir=corta)
        self.assertEqual(sha(self.origen), sha(self.destino))
        self.assertGreater(r.escrituras_parciales, 0)

    def test_lecturas_parciales_se_completan(self):
        self.crear(5000)
        corta = lambda fd, n: os.read(fd, min(n, 5))
        r = copiador.copiar(self.origen, self.destino, 1024, leer=corta)
        self.assertEqual(sha(self.origen), sha(self.destino))
        self.assertGreater(r.lecturas_cortas, 0)

    def test_escritura_que_devuelve_cero_falla_y_limpia(self):
        self.crear(5000)
        self.crear_destino_previo()
        with self.assertRaises(OSError):
            copiador.copiar(self.origen, self.destino, 1024, escribir=lambda fd, datos: 0)
        self.assertTrue(self.previo_intacto())
        self.assertTrue(self.sin_temporales())

    def test_error_durante_escritura_preserva_destino(self):
        self.crear(10000)
        self.crear_destino_previo()
        cuenta = {"n": 0}

        def falla(fd, datos):
            cuenta["n"] += 1
            if cuenta["n"] == 3:
                raise OSError(errno.EIO, "error simulado")
            return os.write(fd, datos)

        with self.assertRaises(OSError):
            copiador.copiar(self.origen, self.destino, 1024, escribir=falla)
        self.assertTrue(self.previo_intacto())
        self.assertTrue(self.sin_temporales())

    def test_falta_de_espacio_en_escritura(self):
        self.crear(10000)
        self.crear_destino_previo()

        def lleno(fd, datos):
            raise OSError(errno.ENOSPC, "disco lleno")

        with self.assertRaises(OSError) as cm:
            copiador.copiar(self.origen, self.destino, 1024, escribir=lleno)
        self.assertEqual(cm.exception.errno, errno.ENOSPC)
        self.assertTrue(self.previo_intacto())
        self.assertTrue(self.sin_temporales())

    def test_falta_de_espacio_detectada_antes_de_copiar(self):
        self.crear(10000)
        with mock.patch("copiador.shutil.disk_usage") as du:
            du.return_value = mock.Mock(free=10)
            with self.assertRaises(OSError) as cm:
                copiador.copiar(self.origen, self.destino, 1024)
        self.assertEqual(cm.exception.errno, errno.ENOSPC)
        self.assertFalse(os.path.exists(self.destino))
        self.assertTrue(self.sin_temporales())

    def test_cancelacion_cooperativa(self):
        self.crear(100000)
        self.crear_destino_previo()
        evento = threading.Event()

        def avisar(hecho, total):
            if hecho >= 4096:
                evento.set()

        with self.assertRaises(copiador.cancelado):
            copiador.copiar(self.origen, self.destino, 1024, progreso=avisar, intervalo=0, cancelar=evento)
        self.assertTrue(self.previo_intacto())
        self.assertTrue(self.sin_temporales())

    def test_corrupcion_detectada_por_hash(self):
        self.crear(5000)
        self.crear_destino_previo()

        def corrompe(fd, datos):
            return os.write(fd, bytes([datos[0] ^ 1]) + bytes(datos[1:]))

        with self.assertRaises(copiador.error_verificacion):
            copiador.copiar(self.origen, self.destino, 1024, escribir=corrompe)
        self.assertTrue(self.previo_intacto())
        self.assertTrue(self.sin_temporales())

    def test_destino_se_reemplaza_solo_al_completar(self):
        self.crear(10000)
        self.crear_destino_previo()
        vistos = []

        def espia(fd, datos):
            vistos.append(self.previo_intacto())
            return os.write(fd, datos)

        copiador.copiar(self.origen, self.destino, 1024, escribir=espia)
        self.assertTrue(all(vistos))
        self.assertEqual(sha(self.origen), sha(self.destino))

    def test_progreso_no_satura_la_salida(self):
        self.crear(200000)
        llamadas = []
        copiador.copiar(self.origen, self.destino, 512, progreso=lambda a, b: llamadas.append(a), intervalo=60)
        self.assertLessEqual(len(llamadas), 2)
        self.assertEqual(llamadas[-1], 200000)

    def test_origen_inexistente_no_toca_destino(self):
        self.crear_destino_previo()
        with self.assertRaises(FileNotFoundError):
            copiador.copiar(os.path.join(self.d, "no_existe"), self.destino, 1024)
        self.assertTrue(self.previo_intacto())
        self.assertTrue(self.sin_temporales())

    def test_bloque_invalido(self):
        self.crear(10)
        with self.assertRaises(ValueError):
            copiador.copiar(self.origen, self.destino, 0)


if __name__ == "__main__":
    unittest.main()
