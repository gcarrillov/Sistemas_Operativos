import os
import unittest

from carrera import Cuenta, ejecutar, verificar
from intercalado import forzar


PROTEGIDA = os.environ.get("PROTEGIDA", "1") == "1"


class PruebasInvariantes(unittest.TestCase):
    def test_version_protegida_conserva_invariantes(self):
        for hilos in (2, 4):
            for r in range(30):
                c, fallos, _ = ejecutar(hilos, 30, PROTEGIDA, 0.0005, r)
                self.assertEqual(fallos, [], f"hilos={hilos} rep={r} estado={c.contador},{c.a},{c.b}")

    def test_intercalado_forzado_con_proteccion(self):
        c, _ = forzar(True)
        self.assertEqual(verificar(c, 2), [])

    def test_verificador_detecta_estado_corrupto(self):
        c = Cuenta()
        c.contador, c.a, c.b, c.limite_roto = 1, -20, 230, True
        self.assertEqual(sorted(verificar(c, 2)), ["contador", "limite", "suma"])

    def test_intercalado_forzado_sin_proteccion_rompe_invariantes(self):
        c, _ = forzar(False)
        self.assertEqual(sorted(verificar(c, 2)), ["contador", "limite", "suma"])


if __name__ == "__main__":
    unittest.main()
