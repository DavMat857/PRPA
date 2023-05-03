import sys
from pyspark import SparkContext
import networkx as nx
from networkx.drawing.nx_pylab import draw
import matplotlib.pyplot as plt

#Vamos a calcular los 3-ciclos de un grafo definido como listas de aristas

def valor_a_lista (tupla): 
    return tupla[0], list(tupla[1])

def ordenar_values(tupla): 
    return tupla[0], sorted(tupla[1])

def read_graph(filename):
    graph = nx.Graph()
    with open(filename) as f:
        for line in f :
            graph.add_edge(*line.strip().split(','))

    return graph

def get_edges(line): 
    edge = line.strip().split(',')
    n1 = edge[0]
    n2 = edge[1]
    if n1 < n2:
         return (n1,n2)
    elif n1 > n2:
         return (n2,n1)
    else:
        pass #n1 == n2

def get_rdd_distict_edges(sc, filename):
    return sc.textFile(filename).\
        map(get_edges).\
        filter(lambda x: x is not None).\
        distinct()



from itertools import combinations

def lista_asociada(tupla):
    nodo_actual, lista_nodos = tupla
    combinaciones = list(combinations(lista_nodos, 2))
    return [((nodo_actual, nodo), 'exists') for nodo in lista_nodos] + [((nodo1, nodo2), ('pending', nodo_actual)) for nodo1, nodo2 in combinaciones]

def condicion_filter(tupla): 
    return (len(tupla[1])>= 2 and 'exists' in tupla[1])

def genera_ternas(tupla):
    return [(tupla[0][0], tupla[0][1], elem[1]) for elem in tupla[1] if elem != 'exists']

def main(sc, filename):
    
    
    g = read_graph(filename)
    draw(g, with_labels = True)
    
    plt.pause(4)
    plt.show(block=False)

    aristas_grafo_rdd = get_rdd_distict_edges(sc,filename) 
    
    
    lista_adyacentes = aristas_grafo_rdd.groupByKey().\
        map(valor_a_lista).\
        sortByKey().\
        map(ordenar_values) 
    
    lista = lista_adyacentes.flatMap(lista_asociada).\
        groupByKey() 
    
    lista_triciclos = lista.map(valor_a_lista).\
        filter(condicion_filter).\
        flatMap(genera_ternas)
    
    print()
    print("-------------------- RESULTADOS --------------------")
    print("Cantidad de triciclos encontrados en el grafo: ", lista_triciclos.count())
    print(lista_triciclos.collect())
    
    return lista_triciclos.collect()
    
    
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 {0} <file>".format(sys.argv[0]))
    else:
        with SparkContext() as sc:
            sc.setLogLevel("ERROR")
            main(sc, sys.argv[1])
