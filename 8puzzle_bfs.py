from collections import deque

ESTADO_INICIAL = (7, 2, 4,
                  5, 0, 6,
                  8, 3, 1)

ESTADO_OBJETIVO = (0, 1, 2,
                   3, 4, 5,
                   6, 7, 8)


# ─────────────────────────────────────────────
#   FUNCIÓN: Imprimir el tablero
# ─────────────────────────────────────────────
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


# ─────────────────────────────────────────────
#   FUNCIÓN: Obtener movimientos posibles
# ─────────────────────────────────────────────
def obtener_vecinos(estado):
    """
    Dado un estado, devuelve todos los estados
    que se pueden alcanzar en UN solo movimiento.
    
    El espacio vacío (0) puede moverse:
    Arriba, Abajo, Izquierda, Derecha
    """
    vecinos = []
    pos_vacio = estado.index(0)  # Dónde está el espacio vacío?
    fila = pos_vacio // 3        # Fila del espacio (0, 1 o 2)
    col  = pos_vacio % 3         # Columna del espacio (0, 1 o 2)

    movimientos = [
        (-1,  0, "Arriba"),
        ( 1,  0, "Abajo"),
        ( 0, -1, "Izquierda"),
        ( 0,  1, "Derecha"),
    ]

    for df, dc, nombre in movimientos:
        nueva_fila = fila + df
        nueva_col  = col  + dc

        # El movimiento está dentro del tablero 3x3?
        if 0 <= nueva_fila < 3 and 0 <= nueva_col < 3:
            nueva_pos = nueva_fila * 3 + nueva_col

            # Intercambiar el vacío con la ficha adyacente
            lista = list(estado)
            lista[pos_vacio], lista[nueva_pos] = lista[nueva_pos], lista[pos_vacio]

            vecinos.append((tuple(lista), nombre))

    return vecinos


# ─────────────────────────────────────────────
#   FUNCIÓN PRINCIPAL: BFS
# ─────────────────────────────────────────────
def bfs(inicio, objetivo):
    """
    BFS - Búsqueda por Anchura (Breadth-First Search)
    """

    print("AGENTE BFS INICIADO...")
    print(f"   Buscando camino de inicial → objetivo\n")

    cola = deque()
    cola.append((inicio, None))

    origen = {inicio: (None, None)}

    nodos_explorados = 0

    while cola:
        estado_actual, _ = cola.popleft()
        nodos_explorados += 1

        if estado_actual == objetivo:
            print(f"¡SOLUCIÓN ENCONTRADA!")
            print(f"   Nodos explorados: {nodos_explorados}")
            return origen, estado_actual

        for estado_vecino, movimiento in obtener_vecinos(estado_actual):

            if estado_vecino not in origen:
                origen[estado_vecino] = (estado_actual, movimiento)
                cola.append((estado_vecino, movimiento))

    print("No existe solución.")
    return None, None


# ─────────────────────────────────────────────
#   FUNCIÓN: Reconstruir el camino de pasos
# ─────────────────────────────────────────────
def reconstruir_camino(origen, estado_final):
    """
    Desde el estado final, sigue los 'padres'
    hacia atrás hasta llegar al estado inicial.
    """
    camino = []
    estado = estado_final

    while estado is not None:
        padre, movimiento = origen[estado]
        camino.append((estado, movimiento))
        estado = padre

    camino.reverse()  # De inicial → final
    return camino


# ─────────────────────────────────────────────
#   EJECUTAR EL AGENTE
# ─────────────────────────────────────────────
if __name__ == "__main__":

    print("=" * 40)
    print("   JUEGO DE 8 DÍGITOS — AGENTE BFS")
    print("=" * 40)

    imprimir_tablero(ESTADO_INICIAL, "ESTADO INICIAL")
    imprimir_tablero(ESTADO_OBJETIVO, "ESTADO OBJETIVO")

    origen, estado_final = bfs(ESTADO_INICIAL, ESTADO_OBJETIVO)

    if origen is None:
        print("No hay solución posible.")
    else:
        camino = reconstruir_camino(origen, estado_final)

        print(f"SOLUCIÓN EN {len(camino) - 1} MOVIMIENTOS:")
        print("=" * 40)

        for i, (estado, movimiento) in enumerate(camino):
            if i == 0:
                imprimir_tablero(estado, "Paso 0 — Estado Inicial")
            else:
                imprimir_tablero(estado, f"Paso {i} — Mover: {movimiento}")

        print("¡Puzzle resuelto con éxito!")
