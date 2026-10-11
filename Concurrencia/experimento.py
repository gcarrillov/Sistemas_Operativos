import csv
import statistics

from carrera import ejecutar

REPETICIONES = 100
OPERACIONES = 50
HILOS = (2, 4)


def campana():
    filas = []
    for protegida in (False, True):
        for hilos in HILOS:
            for r in range(REPETICIONES):
                c, fallos, dur = ejecutar(hilos, OPERACIONES, protegida, 0.001, r)
                filas.append({
                    "protegida": int(protegida), "hilos": hilos, "rep": r + 1,
                    "contador": c.contador, "esperado": hilos * OPERACIONES,
                    "a": c.a, "b": c.b, "suma": c.a + c.b,
                    "f_contador": int("contador" in fallos),
                    "f_suma": int("suma" in fallos),
                    "f_limite": int("limite" in fallos),
                    "duracion": round(dur, 6),
                })
    return filas


def costo_sin_pausa(operaciones=20000, reps=10):
    res = []
    for protegida in (False, True):
        for hilos in HILOS:
            tiempos, malas = [], 0
            for r in range(reps):
                _, fallos, dur = ejecutar(hilos, operaciones, protegida, 0, r)
                tiempos.append(dur)
                malas += bool(fallos)
            res.append((protegida, hilos, statistics.median(tiempos), malas))
    return res


def resumen(filas):
    lineas = []
    for protegida in (0, 1):
        for hilos in HILOS:
            g = [f for f in filas if f["protegida"] == protegida and f["hilos"] == hilos]
            n = len(g)
            con_fallo = sum(1 for f in g if f["f_contador"] or f["f_suma"] or f["f_limite"])
            lineas.append(
                f"protegida={protegida} hilos={hilos} corridas={n} "
                f"fallo_contador={sum(f['f_contador'] for f in g)} "
                f"fallo_suma={sum(f['f_suma'] for f in g)} "
                f"fallo_limite={sum(f['f_limite'] for f in g)} "
                f"con_algun_fallo={con_fallo} "
                f"mediana_s={statistics.median(f['duracion'] for f in g):.4f}"
            )
            perdidas = [f["esperado"] - f["contador"] for f in g]
            desv = [abs(f["suma"] - 200) for f in g]
            lineas.append(
                f"   contador perdido: media={statistics.mean(perdidas):.1f} max={max(perdidas)} | "
                f"desvio suma: media={statistics.mean(desv):.1f} max={max(desv)}"
            )
    return lineas


if __name__ == "__main__":
    filas = campana()
    with open("resultados/corridas.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=filas[0].keys())
        w.writeheader()
        w.writerows(filas)
    out = resumen(filas)
    out.append("")
    out.append("costo sin pausas (20000 ops por hilo, mediana de 10)")
    for protegida, hilos, med, malas in costo_sin_pausa():
        out.append(f"protegida={int(protegida)} hilos={hilos} mediana_s={med:.4f} corridas_con_fallo={malas}")
    texto = "\n".join(out)
    with open("resultados/resumen.txt", "w") as f:
        f.write(texto + "\n")
    print(texto)
