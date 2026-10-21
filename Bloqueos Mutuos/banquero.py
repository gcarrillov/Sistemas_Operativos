from copy import deepcopy

class GestorBanquero:
    def __init__(self, maximo, allocation, total):
        self._validar_matrices(maximo, allocation, total)
        self.maximo = deepcopy(maximo)
        self.allocation = deepcopy(allocation)
        self.total = list(total)
        self.n = len(maximo)
        self.m = len(total)
        self.available = [self.total[j] - sum(self.allocation[i][j] for i in range(self.n))
                          for j in range(self.m)]
        self.need = [[self.maximo[i][j] - self.allocation[i][j] for j in range(self.m)]
                     for i in range(self.n)]

    @staticmethod
    def _validar_matrices(maximo, allocation, total):
        if not isinstance(total, list) or not total or any(type(x) is not int or x < 0 for x in total):
            raise ValueError("total debe ser una lista no vacía de enteros no negativos")
        if not isinstance(maximo, list) or not maximo or not isinstance(allocation, list):
            raise ValueError("matrices no vacías requeridas")
        if len(maximo) != len(allocation):
            raise ValueError("Max y Allocation deben tener igual número de procesos")
        m = len(total)
        for matriz in (maximo, allocation):
            for fila in matriz:
                if not isinstance(fila, list) or len(fila) != m:
                    raise ValueError("dimensiones incompatibles")
                if any(type(x) is not int or x < 0 for x in fila):
                    raise ValueError("las matrices requieren enteros no negativos")
        for i in range(len(maximo)):
            for j in range(m):
                if allocation[i][j] > maximo[i][j]:
                    raise ValueError("Allocation no puede superar Max")
        for j in range(m):
            if sum(f[j] for f in allocation) > total[j]:
                raise ValueError("Allocation total supera recursos existentes")
            if any(maximo[i][j] > total[j] for i in range(len(maximo))):
                raise ValueError("Max de un proceso supera el total existente")

    def estado(self):
        return {"Total": self.total[:], "Available": self.available[:],
                "Max": deepcopy(self.maximo), "Allocation": deepcopy(self.allocation),
                "Need": deepcopy(self.need)}

    @staticmethod
    def _menor_igual(a, b):
        return all(x <= y for x, y in zip(a, b))

    def seguridad(self, available=None, allocation=None, need=None):
        work = list(self.available if available is None else available)
        alloc = self.allocation if allocation is None else allocation
        needs = self.need if need is None else need
        finish = [False] * self.n
        pasos = []
        secuencia = []
        while True:
            elegido = None
            for i in range(self.n):
                if not finish[i] and self._menor_igual(needs[i], work):
                    elegido = i
                    break
            if elegido is None:
                break
            antes = work[:]
            work = [work[j] + alloc[elegido][j] for j in range(self.m)]
            finish[elegido] = True
            secuencia.append(elegido)
            pasos.append({"proceso": elegido, "Work_antes": antes,
                          "Allocation_liberada": alloc[elegido][:],
                          "Work_despues": work[:], "Finish": finish[:]})
        return {"seguro": all(finish), "secuencia": secuencia,
                "Work_final": work, "Finish_final": finish, "pasos": pasos}

    def solicitar(self, proceso, request):
        # Todas las validaciones ocurren antes de mutar; las simulaciones usan copias.
        if type(proceso) is not int or not 0 <= proceso < self.n:
            return {"decision": "rechazada", "motivo": "proceso inválido"}
        if not isinstance(request, list) or len(request) != self.m or any(type(x) is not int or x < 0 for x in request):
            return {"decision": "rechazada", "motivo": "vector Request inválido"}
        if not self._menor_igual(request, self.need[proceso]):
            return {"decision": "rechazada", "motivo": "Request supera Need"}
        if not self._menor_igual(request, self.available):
            return {"decision": "postergada", "motivo": "recursos no disponibles"}
        av = [self.available[j] - request[j] for j in range(self.m)]
        al = deepcopy(self.allocation)
        ne = deepcopy(self.need)
        al[proceso] = [al[proceso][j] + request[j] for j in range(self.m)]
        ne[proceso] = [ne[proceso][j] - request[j] for j in range(self.m)]
        prueba = self.seguridad(av, al, ne)
        if not prueba["seguro"]:
            return {"decision": "rechazada", "motivo": "la asignación produciría estado inseguro",
                    "prueba": prueba}
        self.available = av
        self.allocation = al
        self.need = ne
        return {"decision": "concedida", "motivo": "el estado resultante es seguro",
                "secuencia": prueba["secuencia"], "prueba": prueba}

    def liberar(self, proceso, unidades):
        if type(proceso) is not int or not 0 <= proceso < self.n:
            raise ValueError("proceso inválido")
        if not isinstance(unidades, list) or len(unidades) != self.m or any(type(x) is not int or x < 0 for x in unidades):
            raise ValueError("vector de liberación inválido")
        if any(unidades[j] > self.allocation[proceso][j] for j in range(self.m)):
            raise ValueError("no se puede liberar más de lo asignado")
        for j in range(self.m):
            self.allocation[proceso][j] -= unidades[j]
            self.available[j] += unidades[j]
            self.need[proceso][j] += unidades[j]

def ejemplo_clasico():
    maximo = [[7,5,3],[3,2,2],[9,0,2],[2,2,2],[4,3,3]]
    allocation = [[0,1,0],[2,0,0],[3,0,2],[2,1,1],[0,0,2]]
    return GestorBanquero(maximo, allocation, [10,5,7])

def ejemplo_solicitud_insegura():
    # Caso clásico: P1 solicita [3,3,0]; solicitud <= Need y <= Available,
    # pero la simulación no conserva una secuencia segura.
    g = GestorBanquero(
        [[3,2],[1,2],[3,3]],
        [[1,0],[0,1],[1,1]],
        [3,3])
    return g
