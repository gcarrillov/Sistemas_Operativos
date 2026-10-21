import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

class ServicioReservas:
    """Servicio concurrente: cada recurso admite como máximo una reserva."""
    def __init__(self, cantidad):
        if not isinstance(cantidad, int) or cantidad <= 0:
            raise ValueError("cantidad debe ser un entero positivo")
        self.cantidad = cantidad
        self.reservas = {}                 # recurso -> identificador de reserva
        self._lock = threading.Lock()
        self._cond = threading.Condition(self._lock)
        self._cerrado = False
        self._siguiente_id = 1
        self._esperas = []
        self._operaciones = Counter()

    def _validar_recurso(self, recurso):
        if not isinstance(recurso, int) or not 0 <= recurso < self.cantidad:
            raise ValueError(f"recurso fuera de rango: {recurso}")

    def consultar(self):
        with self._lock:
            self._operaciones["consulta"] += 1
            return [i for i in range(self.cantidad) if i not in self.reservas]

    def reservar(self, recurso, cliente):
        self._validar_recurso(recurso)
        with self._cond:
            if self._cerrado:
                return None
            if recurso in self.reservas:
                self._operaciones["rechazo_ocupado"] += 1
                return None
            reserva_id = self._siguiente_id
            self._siguiente_id += 1
            self.reservas[recurso] = (reserva_id, cliente)
            self._operaciones["reserva"] += 1
            self._comprobar_invariantes()
            return reserva_id

    def esperar_y_reservar(self, recurso, cliente, timeout):
        self._validar_recurso(recurso)
        if timeout is not None and timeout < 0:
            raise ValueError("timeout no puede ser negativo")
        inicio = time.perf_counter()
        limite = None if timeout is None else inicio + timeout
        with self._cond:
            while recurso in self.reservas and not self._cerrado:
                restante = None if limite is None else limite - time.perf_counter()
                if restante is not None and restante <= 0:
                    self._esperas.append(time.perf_counter() - inicio)
                    self._operaciones["timeout"] += 1
                    return None
                self._cond.wait(restante)
            self._esperas.append(time.perf_counter() - inicio)
            if self._cerrado:
                self._operaciones["cancelada_cierre"] += 1
                return None
            reserva_id = self._siguiente_id
            self._siguiente_id += 1
            self.reservas[recurso] = (reserva_id, cliente)
            self._operaciones["reserva_tras_espera"] += 1
            self._comprobar_invariantes()
            return reserva_id

    def cancelar(self, reserva_id):
        with self._cond:
            for recurso, dato in list(self.reservas.items()):
                if dato[0] == reserva_id:
                    del self.reservas[recurso]
                    self._operaciones["cancelacion"] += 1
                    self._comprobar_invariantes()
                    self._cond.notify_all()
                    return True
            self._operaciones["cancelacion_no_encontrada"] += 1
            return False

    def cerrar(self):
        with self._cond:
            self._cerrado = True
            self._cond.notify_all()

    def estado(self):
        with self._lock:
            return {"capacidad": self.cantidad,
                    "reservados": len(self.reservas),
                    "disponibles": self.cantidad - len(self.reservas),
                    "reservas": dict(self.reservas),
                    "cerrado": self._cerrado}

    def metricas(self):
        with self._lock:
            esperas = sorted(self._esperas)
            n = len(esperas)
            return {"operaciones": dict(self._operaciones),
                    "muestras_espera": n,
                    "espera_media_s": sum(esperas)/n if n else 0.0,
                    "espera_max_s": max(esperas) if n else 0.0}

    def _comprobar_invariantes(self):
        assert 0 <= len(self.reservas) <= self.cantidad
        assert len({x[0] for x in self.reservas.values()}) == len(self.reservas)
        assert self.cantidad - len(self.reservas) >= 0


# Demostración defectuosa: lectura y escritura separadas sin exclusión mutua.
class ServicioDefectuoso:
    def __init__(self):
        self.ocupado = False
        self.reservas = 0
    def reservar_con_barrera(self, barrera):
        disponible = not self.ocupado
        barrera.wait(timeout=2)
        if disponible:
            self.ocupado = True
            self.reservas += 1
            return True
        return False

def demo_carrera():
    barrera = threading.Barrier(2)
    servicio = ServicioDefectuoso()
    resultados = []
    def worker():
        resultados.append(servicio.reservar_con_barrera(barrera))
    ts = [threading.Thread(target=worker) for _ in range(2)]
    for t in ts: t.start()
    for t in ts: t.join()
    return servicio.reservas, resultados

def demo_carga(workers=8, operaciones_por_worker=100):
    servicio = ServicioReservas(4)
    inicio = time.perf_counter()
    def worker(w):
        for i in range(operaciones_por_worker):
            recurso = (w + i) % 4
            rid = servicio.reservar(recurso, f"W{w}")
            if rid is not None:
                servicio.cancelar(rid)
            else:
                servicio.consultar()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        list(pool.map(worker, range(workers)))
    duracion = time.perf_counter() - inicio
    return {"workers": workers, "operaciones_intentadas": workers*operaciones_por_worker,
            "duracion_s": duracion,
            "ops_s": workers*operaciones_por_worker/duracion if duracion else 0,
            "estado_final": servicio.estado(), "metricas": servicio.metricas()}

if __name__ == "__main__":
    print("Carrera defectuosa (reservas aceptadas):", demo_carrera()[0])
    print("Carga concurrente:", demo_carga())
