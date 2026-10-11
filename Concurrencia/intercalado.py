import threading

from carrera import Cuenta, verificar


def forzar(protegida, espera=0.05):
    barrera = threading.Barrier(2)

    def pausa():
        try:
            barrera.wait(timeout=espera)
        except threading.BrokenBarrierError:
            barrera.reset()

    traza = []
    c = Cuenta(protegida=protegida, pausa=pausa, traza=traza)
    ts = [threading.Thread(target=c.paso, args=("a", "b", 60), name=f"T{i}") for i in (1, 2)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    return c, traza


def mostrar(protegida):
    c, traza = forzar(protegida)
    print(f"protegida={protegida} contador={c.contador} a={c.a} b={c.b} fallos={verificar(c, 2)}")
    t0 = traza[0][0]
    for t, hilo, ev, dato in traza:
        print(f"  {(t - t0) * 1e3:8.3f} ms {hilo} {ev} {dato}")


if __name__ == "__main__":
    mostrar(False)
    mostrar(True)
