Agente Inteligente — Solucionador del 8-Puzzle

Este proyecto implementa un agente inteligente capaz de resolver el clásico problema del 8-puzzle utilizando diversas estrategias de búsqueda en Inteligencia Artificial. Permite comparar el rendimiento de algoritmos de búsqueda no informada frente a búsqueda informada con funciones heurísticas avanzadas.


**Estado Inicial**   **Estado Objetivo**
```text
┌───┬───┬───┐          ┌───┬───┬───┐
│ 7 │ 2 │ 4 │          │   │ 1 │ 2 │
├───┼───┼───┤          ├───┼───┼───┤
│ 5 │   │ 6 │    →     │ 3 │ 4 │ 5 │
├───┼───┼───┤          ├───┼───┼───┤
│ 8 │ 3 │ 1 │          │ 6 │ 7 │ 8 │
└───┴───┴───┘          └───┴───┴───┘
```

---

Algoritmos Implementados

* **BFS (Búsqueda por Anchura):** Explora todos los estados nivel por nivel. Garantiza encontrar la solución con el menor número de pasos, pero es muy costoso en memoria y tiempo al no tener información que guíe la búsqueda.
* **A\* (A-Estrella):** Algoritmo central del proyecto. Es una búsqueda informada que decide qué estado explorar usando la fórmula $f(n) = g(n) + h(n)$ (costo acumulado + estimación heurística). Garantiza la solución óptima si la heurística es admisible.
* **Greedy Best-First (Búsqueda Voraz):** Utiliza solamente la heurística ($f(n) = h(n)$). Es extremadamente rápido porque siempre elige el camino que "parece" más directo, pero sacrifica la optimalidad y puede generar soluciones más largas.

---

Funciones Heurísticas

El rendimiento de **A\*** depende directamente de la heurística utilizada para estimar la cercanía a la solución:

1.  **Hamming (Fichas mal colocadas):** Cuenta cuántas fichas no están en su posición objetivo. Es admisible, pero poco informada.
2.  **Distancia Manhattan:** Suma la distancia horizontal y vertical de cada ficha hasta su posición final. Al indicar "qué tan lejos" está cada pieza, es mucho más eficiente que Hamming.
3.  **Manhattan + Conflicto Lineal:** La heurística más avanzada del proyecto. Suma la distancia Manhattan más una penalización por conflictos lineales (dos fichas en la fila/columna correcta pero en orden invertido, lo que requiere movimientos extra para resolverse).
