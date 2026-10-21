import unittest
from banquero import GestorBanquero, ejemplo_clasico, ejemplo_solicitud_insegura

class TestBanquero(unittest.TestCase):
    def test_estado_inicial_tiene_secuencia_segura(self):
        g = ejemplo_clasico()
        r = g.seguridad()
        self.assertTrue(r["seguro"])
        self.assertEqual(r["secuencia"], [1, 3, 0, 2, 4])

    def test_request_superior_a_need_rechazada_sin_mutacion(self):
        g = ejemplo_clasico()
        antes = g.estado()
        r = g.solicitar(1, [2, 0, 0])  # Need de P1 = [1,2,2]
        self.assertEqual(r["decision"], "rechazada")
        self.assertEqual(r["motivo"], "Request supera Need")
        self.assertEqual(g.estado(), antes)

    def test_request_superior_a_available_se_posterga(self):
        g = ejemplo_clasico()
        antes = g.estado()
        r = g.solicitar(0, [4, 0, 0])
        self.assertEqual(r["decision"], "postergada")
        self.assertEqual(g.estado(), antes)

    def test_solicitud_valida_pero_insegura(self):
        g = ejemplo_clasico()
        antes = g.estado()
        # P4: Request [3,3,0] <= Need [4,3,1] y <= Available [3,3,2],
        # pero el estado resultante no conserva una secuencia segura.
        r = g.solicitar(4, [3, 3, 0])
        self.assertEqual(r["decision"], "rechazada")
        self.assertEqual(r["motivo"], "la asignación produciría estado inseguro")
        self.assertEqual(g.estado(), antes)

    def test_datos_invalidos_no_alteran_estado(self):
        g = ejemplo_clasico()
        antes = g.estado()
        r = g.solicitar(99, [1, 0, 0])
        self.assertEqual(r["decision"], "rechazada")
        self.assertEqual(g.estado(), antes)

    def test_matrices_invalidas(self):
        with self.assertRaises(ValueError):
            GestorBanquero([[2, 1]], [[3, 0]], [3, 2])

    def test_liberacion_actualiza_need_y_available(self):
        g = ejemplo_clasico()
        g.liberar(0, [0, 1, 0])
        self.assertEqual(g.available, [3, 4, 2])
        self.assertEqual(g.need[0], [7, 5, 3])

if __name__ == "__main__":
    unittest.main(verbosity=2)
