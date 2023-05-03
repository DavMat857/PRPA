Tenemos 3 archivos de extensión .py y luego archivos de texto que forman parte del contenido de clase y ej1g1.txt es el propuesto como ejemplo.

Comencemos con la explicación de cada programa:

# 3-ciclos1.py: realiza el cálculo de los 3-ciclos de un grafo definido como listas de aristas.

Se ejecuta de la siguiente forma: python3 3-ciclos1.py "grafo.txt". Siendo este útilmo un grafo definido como listas de aristas

Además de lo pedido en el ejercicio, se complementa una imagen del grafo, usando "import networkx as nx" y
"from networkx.drawing.nx_pylab import draw"


# 3-ciclos2.py: calcula los 3-ciclos de un grafo que se encuentra definido en múltiples ficheros de entrada.

Se ejecuta de la siguiente forma: python3 3-ciclos1.py "grafo1.txt" "grafo2.txt" ... "grafon.txt". 

Además de lo pedido en el ejercicio, se complementa una imagen del grafo resultante de la superposición de cada grafo

# 3-cilos3.py: calcula independientemente los 3-ciclos de cada uno de los ficheros de entrada

Se ejecuta de la misma manera que `3-ciclos2.py`. Además se muestra una figura con todos los grafos graficados.

## Observación:
Uso `plt.pause(4)` y `plt.show(block=False)`, para que se cierre la gráfica, sin embargo si la queremos mantener cambiamos esas dos líneas por `plt.show()`