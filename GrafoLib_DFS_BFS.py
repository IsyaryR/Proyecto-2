import random
import math
import sys


class Nodo:
    def __init__(self, id):
        self.id = id #identificador unico 

    def __repr__(self): #Para imprimir en consola
        return f"Nodo(id={self.id})" #Nodo(id=1)

    def __eq__(self, other): #definicion de nodos iguales si son la misma id
        return isinstance(other, Nodo) and self.id == other.id

    def __hash__(self): #Para ser hashable en diccionario
        return hash(self.id)


class Arista:
    def __init__(self, u, v):
        self.u = u  # Nodo origen
        self.v = v  # Nodo destino

    def __repr__(self):
        return f"Arista({self.u.id} -> {self.v.id})" #Arista(0 -> 1)

    def __eq__(self, other): #definicion de arista igual, si tiene el mismo nodo origen y destino
        if not isinstance(other, Arista):
            return False
        return self.u == other.u and self.v == other.v

    def __hash__(self):
        return hash((self.u, self.v))


class Grafo:
    def __init__(self, dirigido=False):
        self.dirigido = dirigido # si es false A -- B; si es true A -> B no implica B -> A
        self.nodos = {} #diccionario de nodos registrados
        self.aristas = [] #lista con todas las aristas
        self.adyacencia = {}  # Diccionario para guardar vecinos de cada nodo id -> set(id_vecino)

    def agregarNodo(self, nodo): #Funcion para agregar nodo 
        if nodo.id not in self.nodos:
            self.nodos[nodo.id] = nodo
            self.adyacencia[nodo.id] = set()
        return self.nodos[nodo.id]

    def obtenerNodo(self, id):
        return self.nodos[id]  #Regresa el nodo con el id dado.

    def agregarArista(self, u, v): #Conecta dos nodos
        if u.id not in self.nodos:
            self.agregarNodo(u)
        if v.id not in self.nodos:
            self.agregarNodo(v)

        # Evitar aristas duplicadas
        if v.id in self.adyacencia[u.id]:
            return None

        arista = Arista(u, v)
        self.aristas.append(arista)
        self.adyacencia[u.id].add(v.id)
        if not self.dirigido:
            self.adyacencia[v.id].add(u.id)
        return arista

    def vecinos(self, nodo):#Devuelve la lista de nodos que estan conectados directamente al nodo
        return [self.nodos[i] for i in self.adyacencia[nodo.id]]

    def grado(self, nodo):
        return len(self.adyacencia[nodo.id])

    def numeroNodos(self):
        return len(self.nodos)

    def numeroAristas(self):
        return len(self.aristas)

    def _paresPosibles(self): #Devuelve todos los pares (i, j) con i < j sobre los ids actuales.
        ids = list(self.nodos.keys()) #diccionario donde las claves son los nodos [0,1,2,3]
        pares = [] #lista vacia para guardar cada pareja en forma de tupla
        for i in range(len(ids)):
            for j in range(i+1, len(ids)):
                pares.append((ids[i], ids[j]))
        return pares #[(0,1),(0,2),(1,2),...]

    def guardarGraphViz(self, ruta, nombre="Grafo"): #Guarda el grafo en formato DOT (GraphViz simple).
        tipo = "digraph" if self.dirigido else "graph"
        conector = "->" if self.dirigido else "--"

        lineas = [f'{tipo} {nombre} {{']
        for nodo in self.nodos.values():
            lineas.append(f'    {nodo.id};')
        for a in self.aristas:
            lineas.append(f'    {a.u.id} {conector} {a.v.id};')
        lineas.append("}")

        with open(ruta, "w", encoding="utf-8") as f:
            f.write("\n".join(lineas))
    # =========================================================
    #  BFS y DFS (recursivo e iterativo)
    #  Cada uno devuelve el arbol inducido por el recorrido
    #  desde el nodo fuente s, como un Grafo(dirigido=True).
    # =========================================================

    def _validarFuente(self, s): #Verifica que s sea un Nodo registrado en el grafo.
        if not isinstance(s, Nodo):
            raise TypeError("s debe ser una instancia de Nodo")
        if s.id not in self.nodos:
            raise ValueError(f"El nodo fuente {s.id} no existe en el grafo")

    def _nuevoArbol(self, s):#Crea el grafo (dirigido) que representara el arbol inducido.
        arbol = Grafo(dirigido=True)
        arbol.agregarNodo(Nodo(s.id))
        return arbol
#--------------------------------------------------------------------------------------
#   Busqueda a lo ancho (Breadth-First Search) desde s.
#   Devuelve el arbol inducido (Grafo dirigido) con aristas padre -> hijo.
#--------------------------------------------------------------------------------------
    def BFS(self, s):
        self._validarFuente(s)

        arbol = self._nuevoArbol(s)
        visitados = {s.id}
        cola = [s]                       # lista como cola FIFO
        cabeza = 0                       # indice del frente para evitar pop(0)

        while cabeza < len(cola):
            u = cola[cabeza]
            cabeza += 1
            # Recorrido de vecinos en orden (sorted para reproducibilidad)
            for v_id in sorted(self.adyacencia[u.id]):
                if v_id not in visitados:
                    visitados.add(v_id)
                    # Arista del arbol: u -> v (v descubierto desde u)
                    arbol.agregarArista(Nodo(u.id), Nodo(v_id))
                    cola.append(self.nodos[v_id])

        return arbol
#-----------------------------------------------------------------------------
#   Recorrido en profundidad (DFS) recursivo desde s.
#   Devuelve el arbol inducido (Grafo dirigido) con aristas padre -> hijo.
#-----------------------------------------------------------------------------
    def DFS_R(self, s):
        self._validarFuente(s)

        # la profundidad de recursion puede llegar a |V|
        sys.setrecursionlimit(max(sys.getrecursionlimit(), len(self.nodos) + 100))

        arbol = self._nuevoArbol(s)
        visitados = {s.id}
        self._DFS_R_visita(s, visitados, arbol)
        return arbol

    def _DFS_R_visita(self, u, visitados, arbol): #Auxiliar recursivo de DFS_R.
        for v_id in sorted(self.adyacencia[u.id]):
            if v_id not in visitados:
                visitados.add(v_id)
                # Arista del arbol: u -> v (v descubierto desde u)
                arbol.agregarArista(Nodo(u.id), Nodo(v_id))
                self._DFS_R_visita(self.nodos[v_id], visitados, arbol)
# -----------------------------------------------------------------------------
#   Busqueda en profundidad (DFS) iterativo desde s, con pila explicita.
#   El nodo se marca como visitado al SACARLO de la pila (no al meterlo),
#   y cada elemento de la pila guarda quien lo descubrio: (padre, nodo).
#   Los vecinos se apilan en orden inverso, asi el resultado coincide
#   con DFS_R. Devuelve el arbol inducido (Grafo dirigido) padre -> hijo.
#------------------------------------------------------------------------------
    def DFS_I(self, s):
        self._validarFuente(s)

        arbol = self._nuevoArbol(s)
        visitados = set()
        pila = [(None, s.id)]            # pares (padre, nodo)

        while pila:
            padre, u = pila.pop()
            if u in visitados:
                continue
            visitados.add(u)             # se marca al sacar, no al meter
            if padre is not None:
                arbol.agregarArista(Nodo(padre), Nodo(u))
            for v_id in sorted(self.adyacencia[u], reverse=True):
                if v_id not in visitados:
                    pila.append((u, v_id))

        return arbol

# =========================================================
#  Funciones de generacion de grafos
# =========================================================
#---------------------------------------
#         Grafo de malla m x n.
#  Conecta cada nodo con su vecino de 
#  la derecha y su vecino de abajo
#---------------------------------------
def grafoMalla(m, n, dirigido=False):
    if m<1 or n<1:#Validacion de la malla minimo 1 fila y minimo 1 columna
        raise ValueError("m y n deben ser >= 1")
    g=Grafo(dirigido=dirigido)#instancia vacia 

    for i in range(m): #recorre las filas de 0 a m-1
        for j in range(n):#recorre las columnas de 0 a n-1
            g.agregarNodo(Nodo(i*n+j))

    for i in range(m):
        for j in range(n):
            actual=g.obtenerNodo(i*n+j)
            if i+1 < m: #conexion vertical con el nodo de abajo
                g.agregarArista(actual, g.obtenerNodo((i +1)*n+j))
            if j+1 < n: #conexion horizontal con el nodo de la derecha
                g.agregarArista(actual, g.obtenerNodo(i*n + (j+1)))
    return g
#---------------------------------------------------------
#  Grafo aleatorio Erdos-Renyi con n nodos y m aristas.
# Obtiene las posibles parejas de nodos posibles para conectarse
#---------------------------------------------------------
def grafoErdosRenyi(n, m, dirigido=False):
    if n <= 0: #verifica que numero de nodos n sea mayor a 0
        raise ValueError("n debe ser > 0")
    g = Grafo(dirigido=dirigido)#grafo vacio
    for i in range(n): #crea n nodos ennumerados de 0 a n-1 
        g.agregarNodo(Nodo(i))

    max_aristas = n*(n-1) if dirigido else n*(n-1) // 2 #calculo de aristas unicas maximas en el grafo
    if m > max_aristas:
        raise ValueError(f"m={m} excede el máximo posible de aristas ({max_aristas})")

    pares = g._paresPosibles()#regresa lista con todos los pares (u,v)  u<v
    if dirigido: #si es dirigido, duplica pares por el sentido inverso de cada combinacion
        pares_dir = []
        for (u, v) in pares:
            pares_dir.append((u, v))
            pares_dir.append((v, u))
        pares = pares_dir

    for (u_id, v_id) in random.sample(pares, m):#Elige m elementos de la lista pares sin repeticion y uniforme
        g.agregarArista(g.obtenerNodo(u_id), g.obtenerNodo(v_id))
    return g
#-----------------------------------------------------------
#  Grafo aleatorio Gilbert con cada arista con probabilidad p.
#  Grafo aleatorio basado en probabilidad
#-----------------------------------------------------------
def grafoGilbert(n, p, dirigido=False):
    if n <= 0: #validacion de numeros positivos
        raise ValueError("n debe ser > 0")
    if not (0.0 <= p <= 1.0):#probabilidad entre 0 a 100%
        raise ValueError("p debe estar en [0, 1]")
    g = Grafo(dirigido=dirigido)
    for i in range(n): #crea n nodos iniciales del 0 al n-1
        g.agregarNodo(Nodo(i))

    for (u_id, v_id) in g._paresPosibles():#recorre todas las combinaciones posibles de pares de nodos
        if random.random() < p: #compara el numero decimal general aleatorio con la probabilidad de p
            g.agregarArista(g.obtenerNodo(u_id), g.obtenerNodo(v_id))
        if dirigido and random.random() < p: #segundo lanzamiento para ver si existe arista en sentido contrario
            g.agregarArista(g.obtenerNodo(v_id), g.obtenerNodo(u_id))
    return g
#--------------------------------------------------------------------
#   Grafo geografico: nodos en [0,1]^2, arista si distancia <= r.
# Simula nodos ubicados en un cuadrado de 1 x 1 (Plano 2D)
#--------------------------------------------------------------------
def grafoGeografico(n, r, dirigido=False):
    if n <= 0: #validacion de nodos mayor a 0
        raise ValueError("n debe ser > 0")
    if not (0.0 < r < 1.0):#radio de cobertura dentro de 0 a 1
        raise ValueError("r debe estar en (0, 1)")
    g = Grafo(dirigido=dirigido)
    coords = [] #lista de coordenadas para guardar la posicion de cada nodo
    for i in range(n): #posicionamiento de nodos
        coords.append((random.random(), random.random()))#para cada nodo asigna una coordenada aleatoria
        g.agregarNodo(Nodo(i)) #añade tupla a lista de coords y registra nodo(i) en grafo

    for i in range(n):
        for j in range(i+1, n):
            xi, yi = coords[i] #extrae coordenadas de nodo i
            xj, yj = coords[j] #extrae coordenadas de nodo j
            if math.hypot(xi-xj, yi-yj) <= r: #teorema de pitagoras para distancia euclidiana, si  la distancia es >= r crea la arista
                g.agregarArista(g.obtenerNodo(i), g.obtenerNodo(j))
                if dirigido:# si es dirigido añade la arista en sentido inverso
                    g.agregarArista(g.obtenerNodo(j), g.obtenerNodo(i))
    return g
#---------------------------------------------------------
#           Grafo aleatorio Barabasi-Albert.
#---------------------------------------------------------
def grafoBarabasiAlbert(n, d, dirigido=False):
    if n <= 0:#Validacion
        raise ValueError("n debe ser > 0")
    if d < 1:
        raise ValueError("d debe ser >= 1")
    if d >= n:# inicializacion
        d = n - 1

    g = Grafo(dirigido=dirigido)
    for i in range(n):
        g.agregarNodo(Nodo(i))

    iniciales = min(d+1, n)# crea iniciales con d+1
    for i in range(iniciales):
        for j in range(i+1, iniciales):
            g.agregarArista(g.obtenerNodo(i), g.obtenerNodo(j))

    for nuevo in range(iniciales, n):#para cada nodo que ingresa 
        existentes = list(range(nuevo))#lista de id de nodos que forman parte dle grafo
        grados = [max(g.grado(g.obtenerNodo(k)), 1) for k in existentes]#cuantas conexiones tiene cada nodo

        seleccionados = set() #se usa set() y while para garantizar que el nuevo nodo eliga d vecinos diferentes sin duplicar conexiones
        while len(seleccionados) < d and len(seleccionados) < len(existentes):
            elegido = random.choices(existentes, weights=grados, k=1)[0]
            seleccionados.add(elegido)

        for objetivo in seleccionados:#crea d aristas entre el nodo nuevo y cada nodo objetivo elegido
            g.agregarArista(g.obtenerNodo(nuevo), g.obtenerNodo(objetivo))
            if dirigido:
                g.agregarArista(g.obtenerNodo(objetivo), g.obtenerNodo(nuevo))
    return g
#---------------------------------------------------------
#        Grafo aleatorio Dorogovtsev-Mendes.
#---------------------------------------------------------
def grafoDorogovtsevMendes(n, dirigido=False):
    if n<3:# requiere 3 nodos minimo para el triangulo
        raise ValueError("n debe ser >= 3")
    g = Grafo(dirigido=dirigido)
    for i in range(3): #crea la estructura del grafo con 3 nodos(0,1,2)
        g.agregarNodo(Nodo(i))
    #conecta los nodos 0,1 y 2 para formar triangulo
    g.agregarArista(g.obtenerNodo(0), g.obtenerNodo(1))
    g.agregarArista(g.obtenerNodo(1), g.obtenerNodo(2))
    g.agregarArista(g.obtenerNodo(2), g.obtenerNodo(0))
    #Para cada nuevo nodo desde 3 a n-1
    for nuevo in range(3, n):
        g.agregarNodo(Nodo(nuevo))#registra nodo nuevo
        arista = random.choice(g.aristas)#elige una arista al azar 
        u, v = arista.u, arista.v #extrae extremos de u y v
        #conecta nodo nuevo con u y v para formar nuevo triangulo
        g.agregarArista(g.obtenerNodo(nuevo), g.obtenerNodo(u.id))
        g.agregarArista(g.obtenerNodo(nuevo), g.obtenerNodo(v.id))
        if dirigido:
            g.agregarArista(g.obtenerNodo(u.id), g.obtenerNodo(nuevo))
            g.agregarArista(g.obtenerNodo(v.id), g.obtenerNodo(nuevo))
    return g