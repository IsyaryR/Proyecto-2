import math
import os
import random
import shutil
import subprocess

from GrafoLib_DFS_BFS import (grafoMalla, grafoErdosRenyi, grafoGilbert,
                              grafoGeografico, grafoBarabasiAlbert,
                              grafoDorogovtsevMendes)

SEMILLA = 777
TAMANOS = [30, 100, 500]
MALLAS = {30: (5, 6), 100: (10, 10), 500: (20, 25)}   # filas x columnas = N
CARPETA_GEN = "grafos_generados"
CARPETA_CAL = "grafos_calculados"
IMAGENES = shutil.which("dot") is not None

os.makedirs(CARPETA_GEN, exist_ok=True)
os.makedirs(CARPETA_CAL, exist_ok=True)

#Generadores con parametros escalados con N (grado promedio ~8).
def generadores(N):
    filas, cols = MALLAS[N]
    return {
        "malla":       lambda: grafoMalla(filas, cols),
        "erdos":       lambda: grafoErdosRenyi(N, 4 * N),
        "gilbert":     lambda: grafoGilbert(N, min(0.3, 8 / N)),
        "geografico":  lambda: grafoGeografico(N, math.sqrt(10 / (math.pi * N))),
        "barabasi":    lambda: grafoBarabasiAlbert(N, 3),
        "dorogovtsev": lambda: grafoDorogovtsevMendes(N),
    }


def guardar(grafo, carpeta, nombre, N, motor):
    """Guarda el .dot y, si se puede, la imagen .png."""
    ruta_dot = os.path.join(carpeta, nombre + ".dot")
    grafo.guardarGraphViz(ruta_dot, nombre)
    if IMAGENES:
        estilo = ["-Nshape=circle", "-Nfixedsize=true", "-Nstyle=filled",
                  "-Nfillcolor=lightblue", "-Ecolor=gray45", "-Goverlap=false"]
        estilo += (["-Nlabel=", "-Nwidth=0.12", "-Nheight=0.12"] if N >= 500
                   else ["-Nwidth=0.3", "-Nheight=0.3", "-Nfontsize=9"])
        subprocess.run([motor, "-Tpng", "-Gdpi=100", *estilo, ruta_dot,
                        "-o", os.path.join(carpeta, nombre + ".png")],
                       check=True, stderr=subprocess.DEVNULL)


random.seed(SEMILLA)
print(f"{'grafo':<18}{'nodos':>6}{'aristas':>9}   arbol BFS / DFS_R / DFS_I (aristas)")
for N in TAMANOS:
    for modelo, fabrica in generadores(N).items():
        nombre = f"{modelo}_{N}"
        g = fabrica()
        guardar(g, CARPETA_GEN, nombre, N, "neato" if N <= 100 else "sfdp")

        s = g.obtenerNodo(0)                       # nodo fuente
        arboles = {"BFS": g.BFS(s), "DFS_R": g.DFS_R(s), "DFS_I": g.DFS_I(s)}
        for alg, arbol in arboles.items():
            guardar(arbol, CARPETA_CAL, f"{nombre}_{alg}", N, "dot")

        # DFS recursivo e iterativo deben dar el mismo arbol
        assert arboles["DFS_R"].aristas == arboles["DFS_I"].aristas
        a = [arboles[k].numeroAristas() for k in ("BFS", "DFS_R", "DFS_I")]
        print(f"{nombre:<18}{g.numeroNodos():>6}{g.numeroAristas():>9}   "
              f"{a[0]:>5} / {a[1]:>5} / {a[2]:>5}")

print(f"\nGrafos generados : {len(os.listdir(CARPETA_GEN))} archivos en {CARPETA_GEN}/")
print(f"Grafos calculados: {len(os.listdir(CARPETA_CAL))} archivos en {CARPETA_CAL}/")