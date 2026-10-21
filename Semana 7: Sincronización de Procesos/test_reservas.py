import threading
import unittest
from reservas import ServicioReservas, demo_carrera

class TestReservas(unittest.TestCase):
    def test_no_doble_reserva(self):
        s = ServicioReservas(1)
        barrera = threading.Barrier(8)
        resultados = []
        def w(i):
            barrera.wait()
            resultados.append(s.reservar(0, f"W{i}"))
        ts = [threading.Thread(target=w, args=(i,)) for i in range(8)]
        for t in ts: t.start()
        for t in ts: t.join()
        self.assertEqual(sum(x is not None for x in resultados), 1)
        self.assertEqual(s.estado()["reservados"], 1)

    def test_cancelacion_libera_recurso(self):
        s = ServicioReservas(1)
        rid = s.reservar(0, "A")
        self.assertTrue(s.cancelar(rid))
        self.assertEqual(s.consultar(), [0])

    def test_timeout(self):
        s = ServicioReservas(1)
        s.reservar(0, "A")
        self.assertIsNone(s.esperar_y_reservar(0, "B", 0.02))
        self.assertGreaterEqual(s.metricas()["espera_max_s"], 0.01)

    def test_espera_se_despierta_tras_cancelar(self):
        s = ServicioReservas(1)
        rid = s.reservar(0, "A")
        resultado = []
        t = threading.Thread(target=lambda: resultado.append(s.esperar_y_reservar(0, "B", 1.0)))
        t.start()
        s.cancelar(rid)
        t.join(1.5)
        self.assertFalse(t.is_alive())
        self.assertIsNotNone(resultado[0])

    def test_cierre_despierta_esperadores(self):
        s = ServicioReservas(1)
        s.reservar(0, "A")
        resultado = []
        t = threading.Thread(target=lambda: resultado.append(s.esperar_y_reservar(0, "B", 5))
        )
        t.start()
        s.cerrar()
        t.join(1)
        self.assertFalse(t.is_alive())
        self.assertIsNone(resultado[0])

    def test_datos_invalidos(self):
        s = ServicioReservas(2)
        with self.assertRaises(ValueError): s.reservar(4, "A")
        with self.assertRaises(ValueError): s.esperar_y_reservar(0, "B", -1)
        self.assertEqual(s.estado()["reservados"], 0)

    def test_carrera_defectuosa_reproducible(self):
        reservas, _ = demo_carrera()
        self.assertEqual(reservas, 2)

if __name__ == "__main__":
    unittest.main(verbosity=2)
