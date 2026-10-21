import random
import threading
import time
from contextlib import nullcontext

SALDO_INICIAL = 100
UNIDAD_MAX = 60


class Cuenta:
    def __init__(self, protegida=False, pausa_max=0.001, pausa=None, traza=None):
        self.contador = 0
        self.a = SALDO_INICIAL
        self.b = SALDO_INICIAL
        self.total = 2 * SALDO_INICIAL
        self.limite_roto = False
        self.protegida = protegida
        self.lock = threading.Lock() if protegida else nullcontext()
        self.pausa = pausa or (lambda: self._pausa_aleatoria(pausa_max))
        self.traza = traza

    @staticmethod
    def _pausa_aleatoria(maximo):
        if maximo > 0:
            time.sleep(random.uniform(0, maximo))

    def _log(self, evento, dato):
        if self.traza is not None:
            self.traza.append((time.perf_counter(), threading.current_thread().name, evento, dato))

    def incrementar(self):
        v = self.contador
        self._log("lee contador", v)
        self.pausa()
        self.contador = v + 1
        self._log("escribe contador", v + 1)

    def transferir(self, origen, destino, unidades):
        saldo_origen = getattr(self, origen)
        self._log("lee " + origen, saldo_origen)
        if saldo_origen < unidades:
            return False
        self.pausa()
        nuevo = getattr(self, origen) - unidades
        setattr(self, origen, nuevo)
        self._log("escribe " + origen, nuevo)
        if nuevo < 0:
            self.limite_roto = True
        saldo_destino = getattr(self, destino)
        self._log("lee " + destino, saldo_destino)
        self.pausa()
        setattr(self, destino, saldo_destino + unidades)
        self._log("escribe " + destino, saldo_destino + unidades)
        return True

    def paso(self, origen, destino, unidades):
        with self.lock:
            self.incrementar()
            self.transferir(origen, destino, unidades)


def trabajador(cuenta, operaciones, semilla):
    rng = random.Random(semilla)
    for _ in range(operaciones):
        origen, destino = ("a", "b") if rng.random() < 0.5 else ("b", "a")
        cuenta.paso(origen, destino, rng.randint(1, UNIDAD_MAX))


def verificar(cuenta, operaciones_totales):
    fallos = []
    if cuenta.contador != operaciones_totales:
        fallos.append("contador")
    if cuenta.a + cuenta.b != cuenta.total:
        fallos.append("suma")
    if cuenta.limite_roto or cuenta.a < 0 or cuenta.b < 0:
        fallos.append("limite")
    return fallos


def ejecutar(hilos, operaciones, protegida, pausa_max=0.001, semilla=0):
    cuenta = Cuenta(protegida=protegida, pausa_max=pausa_max)
    ts = [threading.Thread(target=trabajador, args=(cuenta, operaciones, semilla * 100 + i), name=f"T{i + 1}")
          for i in range(hilos)]
    ini = time.perf_counter()
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    duracion = time.perf_counter() - ini
    return cuenta, verificar(cuenta, hilos * operaciones), duracion
