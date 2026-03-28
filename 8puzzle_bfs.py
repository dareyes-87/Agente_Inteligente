from collections import deque
import heapq
import time

# ─────────────────────────────────────────────
#   ESTADOS DEL PUZZLE
# ─────────────────────────────────────────────
ESTADO_INICIAL = (7, 2, 4,
                  5, 0, 6,
                  8, 3, 1)

ESTADO_OBJETIVO = (0, 1, 2,
                   3, 4, 5,
                   6, 7, 8)

# Posiciones objetivo de cada ficha (para cálculo rápido)
POS_OBJETIVO = {}
for i, val in enumerate(ESTADO_OBJETIVO):
    POS_OBJETIVO[val] = (i // 3, i % 3)


# ═══════════════════════════════════════════════
#   FUNCIONES AUXILIARES
# ═══════════════════════════════════════════════

def imprimir_tablero(estado, titulo=""):
    if titulo:
        print(f"\n{'─'*17}")
        print(f"  {titulo}")
    print(f"{'─'*17}")
    for fila in range(3):
        fila_nums = []
        for col in range(3):
            val = estado[fila * 3 + col]
            fila_nums.append("_" if val == 0 else str(val))
        print(f"  {fila_nums[0]} | {fila_nums[1]} | {fila_nums[2]}")
    print(f"{'─'*17}")


def obtener_vecinos(estado):
    """
    Devuelve todos los estados alcanzables en UN movimiento.
    El espacio vacío (0) se intercambia con una ficha adyacente.
    """
    vecinos = []
    pos_vacio = estado.index(0)
    fila = pos_vacio // 3
    col  = pos_vacio % 3

    movimientos = [
        (-1,  0, "Arriba"),
        ( 1,  0, "Abajo"),
        ( 0, -1, "Izquierda"),
        ( 0,  1, "Derecha"),
    ]

    for df, dc, nombre in movimientos:
        nf, nc = fila + df, col + dc
        if 0 <= nf < 3 and 0 <= nc < 3:
            nueva_pos = nf * 3 + nc
            lista = list(estado)
            lista[pos_vacio], lista[nueva_pos] = lista[nueva_pos], lista[pos_vacio]
            vecinos.append((tuple(lista), nombre))

    return vecinos


def reconstruir_camino(origen, estado_final):
    """Reconstruye la secuencia de pasos desde el inicio hasta el final."""
    camino = []
    estado = estado_final
    while estado is not None:
        padre, movimiento = origen[estado]
        camino.append((estado, movimiento))
        estado = padre
    camino.reverse()
    return camino


def mostrar_solucion(nombre_algoritmo, origen, estado_final, nodos_explorados, tiempo):
    """Muestra la solución de forma uniforme para cualquier algoritmo."""
    if origen is None:
        print(f"\n[{nombre_algoritmo}] No hay solución posible.")
        return

    camino = reconstruir_camino(origen, estado_final)
    n_pasos = len(camino) - 1

    print(f"\n{'='*50}")
    print(f"  {nombre_algoritmo}")
    print(f"{'='*50}")
    print(f"  ✔ Solución encontrada en {n_pasos} movimientos")
    print(f"  ✔ Nodos explorados: {nodos_explorados}")
    print(f"  ✔ Tiempo: {tiempo:.4f} segundos")
    print(f"{'='*50}")

    for i, (estado, movimiento) in enumerate(camino):
        if i == 0:
            imprimir_tablero(estado, "Paso 0 — Estado Inicial")
        else:
            imprimir_tablero(estado, f"Paso {i} — Mover: {movimiento}")

    print("¡Puzzle resuelto con éxito!\n")
    return n_pasos


# ═══════════════════════════════════════════════
#   FUNCIONES HEURÍSTICAS
# ═══════════════════════════════════════════════

def h_manhattan(estado):
    """
    HEURÍSTICA: Distancia Manhattan
    ────────────────────────────────
    Para cada ficha, calcula cuántas casillas
    (horizontal + vertical) la separan de su
    posición objetivo.

    Suma total = estimación del costo mínimo.

    Ejemplo: Si la ficha 7 está en (0,0) pero
    debería estar en (2,1), su distancia es
    |0-2| + |0-1| = 3.

    Es ADMISIBLE: nunca sobreestima el costo real.
    Es CONSISTENTE: satisface la desigualdad triangular.
    """
    distancia = 0
    for i, val in enumerate(estado):
        if val != 0:  # No contamos el espacio vacío
            fila_actual = i // 3
            col_actual  = i % 3
            fila_obj, col_obj = POS_OBJETIVO[val]
            distancia += abs(fila_actual - fila_obj) + abs(col_actual - col_obj)
    return distancia


def h_fichas_mal_colocadas(estado):
    """
    HEURÍSTICA: Fichas Mal Colocadas (Hamming)
    ───────────────────────────────────────────
    Cuenta cuántas fichas NO están en su
    posición objetivo.

    Ejemplo: Si solo las fichas 2, 5 y 8 están
    en su lugar correcto, h = 8 - 3 = 5
    (sin contar el espacio vacío).

    Es ADMISIBLE: cada ficha mal colocada necesita
    al menos 1 movimiento → nunca sobreestima.
    Pero es MENOS INFORMADA que Manhattan.
    """
    mal_colocadas = 0
    for i, val in enumerate(estado):
        if val != 0 and val != ESTADO_OBJETIVO[i]:
            mal_colocadas += 1
    return mal_colocadas


def h_manhattan_lineal_conflicto(estado):
    """
    HEURÍSTICA: Manhattan + Conflicto Lineal
    ─────────────────────────────────────────
    Mejora sobre Manhattan pura.

    Un "conflicto lineal" ocurre cuando dos fichas
    están en su fila/columna objetivo pero en orden
    invertido. Cada conflicto requiere al menos 2
    movimientos adicionales sobre Manhattan.

    Es ADMISIBLE y CONSISTENTE.
    Es la heurística más informada de las tres.
    """
    distancia = h_manhattan(estado)
    conflictos = 0

    # Conflictos en filas
    for fila in range(3):
        fichas_en_fila = []
        for col in range(3):
            val = estado[fila * 3 + col]
            if val != 0:
                fila_obj, _ = POS_OBJETIVO[val]
                if fila_obj == fila:  # La ficha pertenece a esta fila
                    fichas_en_fila.append((col, val))

        # Buscar pares en conflicto
        for i in range(len(fichas_en_fila)):
            for j in range(i + 1, len(fichas_en_fila)):
                col_i, val_i = fichas_en_fila[i]
                col_j, val_j = fichas_en_fila[j]
                _, col_obj_i = POS_OBJETIVO[val_i]
                _, col_obj_j = POS_OBJETIVO[val_j]
                # Si están invertidas respecto a sus posiciones objetivo
                if col_i < col_j and col_obj_i > col_obj_j:
                    conflictos += 1

    # Conflictos en columnas
    for col in range(3):
        fichas_en_col = []
        for fila in range(3):
            val = estado[fila * 3 + col]
            if val != 0:
                _, col_obj = POS_OBJETIVO[val]
                if col_obj == col:  # La ficha pertenece a esta columna
                    fichas_en_col.append((fila, val))

        for i in range(len(fichas_en_col)):
            for j in range(i + 1, len(fichas_en_col)):
                fila_i, val_i = fichas_en_col[i]
                fila_j, val_j = fichas_en_col[j]
                fila_obj_i, _ = POS_OBJETIVO[val_i]
                fila_obj_j, _ = POS_OBJETIVO[val_j]
                if fila_i < fila_j and fila_obj_i > fila_obj_j:
                    conflictos += 1

    return distancia + 2 * conflictos


# ═══════════════════════════════════════════════
#   ALGORITMO 1: BFS (tu versión original)
# ═══════════════════════════════════════════════

def bfs(inicio, objetivo):
    """
    BFS — Búsqueda por Anchura (Breadth-First Search)
    ──────────────────────────────────────────────────
    SIN heurística. Explora TODOS los nodos nivel
    por nivel. Garantiza solución óptima en número
    de pasos, pero explora muchísimos nodos.

    Complejidad: O(b^d) donde b=ramificación, d=profundidad
    """
    cola = deque()
    cola.append((inicio, None))
    origen = {inicio: (None, None)}
    nodos_explorados = 0

    while cola:
        estado_actual, _ = cola.popleft()
        nodos_explorados += 1

        if estado_actual == objetivo:
            return origen, estado_actual, nodos_explorados

        for estado_vecino, movimiento in obtener_vecinos(estado_actual):
            if estado_vecino not in origen:
                origen[estado_vecino] = (estado_actual, movimiento)
                cola.append((estado_vecino, movimiento))

    return None, None, nodos_explorados


# ═══════════════════════════════════════════════
#   ALGORITMO 2: A* (A-Estrella)
# ═══════════════════════════════════════════════

def a_estrella(inicio, objetivo, heuristica, nombre_h=""):
    """
    A* — Búsqueda A-Estrella
    ─────────────────────────
    Usa: f(n) = g(n) + h(n)

      g(n) = costo real desde el inicio hasta n
      h(n) = estimación heurística de n al objetivo
      f(n) = costo total estimado

    La cola de prioridad siempre expande el nodo
    con MENOR f(n). Si h es admisible, A* encuentra
    la solución ÓPTIMA explorando muchos menos nodos
    que BFS.

    Se usa heapq (min-heap) como cola de prioridad.
    El desempate se hace con un contador para evitar
    comparar tuplas directamente.
    """
    contador = 0  # Desempate para el heap
    h_inicio = heuristica(inicio)

    # Heap: (f, contador, estado, g)
    heap = [(h_inicio, contador, inicio, 0)]
    origen = {inicio: (None, None)}
    costo = {inicio: 0}  # g(n) para cada estado visitado
    nodos_explorados = 0

    while heap:
        f_actual, _, estado_actual, g_actual = heapq.heappop(heap)

        # Si ya encontramos un camino más corto, saltamos
        if g_actual > costo.get(estado_actual, float('inf')):
            continue

        nodos_explorados += 1

        if estado_actual == objetivo:
            return origen, estado_actual, nodos_explorados

        for estado_vecino, movimiento in obtener_vecinos(estado_actual):
            nuevo_g = g_actual + 1  # Cada movimiento cuesta 1

            # Solo expandir si encontramos un camino mejor
            if nuevo_g < costo.get(estado_vecino, float('inf')):
                costo[estado_vecino] = nuevo_g
                h_vecino = heuristica(estado_vecino)
                f_vecino = nuevo_g + h_vecino  # f = g + h
                contador += 1
                heapq.heappush(heap, (f_vecino, contador, estado_vecino, nuevo_g))
                origen[estado_vecino] = (estado_actual, movimiento)

    return None, None, nodos_explorados


# ═══════════════════════════════════════════════
#   ALGORITMO 3: Greedy Best-First Search
# ═══════════════════════════════════════════════

def greedy_best_first(inicio, objetivo, heuristica):
    """
    Greedy Best-First Search
    ────────────────────────
    Usa: f(n) = h(n)   (SOLO heurística, ignora g)

    Siempre expande el nodo que PARECE más cercano
    al objetivo. Es más rápido que A* pero NO
    garantiza la solución óptima.

    Puede encontrar soluciones más largas que A*,
    pero explora menos nodos en muchos casos.
    """
    contador = 0
    h_inicio = heuristica(inicio)

    heap = [(h_inicio, contador, inicio)]
    origen = {inicio: (None, None)}
    nodos_explorados = 0

    while heap:
        _, _, estado_actual = heapq.heappop(heap)
        nodos_explorados += 1

        if estado_actual == objetivo:
            return origen, estado_actual, nodos_explorados

        for estado_vecino, movimiento in obtener_vecinos(estado_actual):
            if estado_vecino not in origen:
                origen[estado_vecino] = (estado_actual, movimiento)
                h_vecino = heuristica(estado_vecino)
                contador += 1
                heapq.heappush(heap, (h_vecino, contador, estado_vecino))

    return None, None, nodos_explorados


# ═══════════════════════════════════════════════
#   EJECUTAR TODOS LOS AGENTES Y COMPARAR
# ═══════════════════════════════════════════════

if __name__ == "__main__":

    print("╔" + "═"*54 + "╗")
    print("║   JUEGO DE 8 DÍGITOS — AGENTES CON HEURÍSTICAS     ║")
    print("╚" + "═"*54 + "╝")

    imprimir_tablero(ESTADO_INICIAL, "ESTADO INICIAL")
    imprimir_tablero(ESTADO_OBJETIVO, "ESTADO OBJETIVO")

    # ── Tabla comparativa ──
    resultados = []

    # 1) BFS (sin heurística — referencia)
    print("\n▶ Ejecutando BFS (sin heurística)...")
    t0 = time.time()
    orig, final, nodos = bfs(ESTADO_INICIAL, ESTADO_OBJETIVO)
    t1 = time.time()
    pasos = mostrar_solucion("BFS (Sin Heurística)", orig, final, nodos, t1-t0)
    resultados.append(("BFS (Sin Heurística)", "Ninguna", nodos, pasos, t1-t0))

    # 2) A* con Fichas Mal Colocadas (Hamming)
    print("\n▶ Ejecutando A* con Fichas Mal Colocadas...")
    t0 = time.time()
    orig, final, nodos = a_estrella(ESTADO_INICIAL, ESTADO_OBJETIVO, h_fichas_mal_colocadas)
    t1 = time.time()
    pasos = mostrar_solucion("A* + Fichas Mal Colocadas (Hamming)", orig, final, nodos, t1-t0)
    resultados.append(("A* + Hamming", "Fichas mal colocadas", nodos, pasos, t1-t0))

    # 3) A* con Distancia Manhattan
    print("\n▶ Ejecutando A* con Distancia Manhattan...")
    t0 = time.time()
    orig, final, nodos = a_estrella(ESTADO_INICIAL, ESTADO_OBJETIVO, h_manhattan)
    t1 = time.time()
    pasos = mostrar_solucion("A* + Distancia Manhattan", orig, final, nodos, t1-t0)
    resultados.append(("A* + Manhattan", "Distancia Manhattan", nodos, pasos, t1-t0))

    # 4) A* con Manhattan + Conflicto Lineal
    print("\n▶ Ejecutando A* con Manhattan + Conflicto Lineal...")
    t0 = time.time()
    orig, final, nodos = a_estrella(ESTADO_INICIAL, ESTADO_OBJETIVO, h_manhattan_lineal_conflicto)
    t1 = time.time()
    pasos = mostrar_solucion("A* + Manhattan + Conflicto Lineal", orig, final, nodos, t1-t0)
    resultados.append(("A* + Conflicto Lineal", "Manhattan + Confl. Lineal", nodos, pasos, t1-t0))

    # 5) Greedy Best-First con Manhattan
    print("\n▶ Ejecutando Greedy Best-First con Manhattan...")
    t0 = time.time()
    orig, final, nodos = greedy_best_first(ESTADO_INICIAL, ESTADO_OBJETIVO, h_manhattan)
    t1 = time.time()
    pasos = mostrar_solucion("Greedy Best-First + Manhattan", orig, final, nodos, t1-t0)
    resultados.append(("Greedy + Manhattan", "Distancia Manhattan", nodos, pasos, t1-t0))

    # ── TABLA COMPARATIVA FINAL ──
    print("\n")
    print("╔" + "═"*74 + "╗")
    print("║" + "  TABLA COMPARATIVA DE ALGORITMOS".center(74) + "║")
    print("╠" + "═"*74 + "╣")
    print("║  {:.<28s} {:.<18s} {:>8s}  {:>6s}  {:>8s} ║".format(
        "Algoritmo", "Heurística", "Nodos", "Pasos", "Tiempo"))
    print("╠" + "─"*74 + "╣")
    for nombre, heur, nodos, pasos, tiempo in resultados:
        print("║  {:.<28s} {:.<18s} {:>8,d}  {:>6d}  {:>7.4f}s ║".format(
            nombre, heur, nodos, pasos, tiempo))
    print("╚" + "═"*74 + "╝")
