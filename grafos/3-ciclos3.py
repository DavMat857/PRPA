
import sys
from pyspark import SparkContext
import networkx as nx
from networkx.drawing.nx_pylab import draw
import matplotlib.pyplot as plt

def get_edges_plus(line,filename):
    edge = line.strip().split(',')
    n1 = edge[0]
    n2 = edge[1]
    if n1 < n2:
         return ((n1,filename),(n2,filename))
    elif n1 > n2:
         return ((n2,filename),(n1,filename))
     
def read_graph(filename):
    graph = nx.Graph()
    with open(filename) as f:
        for line in f :
            graph.add_edge(*line.strip().split(','))

    return graph

def valor_a_lista (tupla): 
    return tupla[0], list(tupla[1])

def ordenar_values(tupla): 
    return tupla[0], sorted(tupla[1])

from itertools import combinations

def lista_asociada(tupla):
    nodo_actual, lista_nodos = tupla
    combinaciones = list(combinations(lista_nodos, 2))
    return [((nodo_actual, nodo), 'exists') for nodo in lista_nodos] + [((nodo1, nodo2), ('pending', nodo_actual)) for nodo1, nodo2 in combinaciones]

    
def condicion_filter(tupla):
    return (len(tupla[1])>= 2 and 'exists' in tupla[1])

def genera_ternas(tupla):
    return [(tupla[0][0], tupla[0][1], elem[1]) for elem in tupla[1] if elem != 'exists']


def write_useful(tupla):
    return [(tupla[0][0], tupla[1][0], tupla[2][0])]


def main(sc, files):
    rdd_contenido = sc.emptyRDD()
    

    # Crear una figura con subplots
    fig, axs = plt.subplots(1, len(files), figsize=(len(files)*5, 5))

    # Iterar sobre los archivos y dibujar cada grafo en un subplot
    for i, file in enumerate(files):
        g = read_graph(file)
        draw(g, with_labels=True, ax=axs[i])
        axs[i].set_title(file)

        file_rdd = sc.textFile(file).map(lambda a : get_edges_plus(a,file)).\
            filter(lambda x: x is not None).distinct()
        

        rdd_contenido = rdd_contenido.union(file_rdd).distinct()

    # Mostrar la figura con todas las subfiguras

    lista_adyacentes = rdd_contenido.groupByKey().\
        map(valor_a_lista).\
        sortByKey().\
        map(ordenar_values)
    
    lista = lista_adyacentes.flatMap(lista_asociada).\
        groupByKey()
    
    lista_triciclos = lista.map(valor_a_lista).\
        filter(condicion_filter).\
        flatMap(genera_ternas)
    
    plt.pause(4)
    plt.show(block=False)
    print("-------------------- RESULTADOS --------------------")
    for file in files:
        rdd_filtrado = lista_triciclos.filter(lambda tupla: tupla[0][1] == file).\
            flatMap(write_useful)
        print("Cantidad de triciclos encontrados en el grafo ", file, ": ", rdd_filtrado.count())
        print("lista de triciclos encontrados: ", rdd_filtrado.collect())
        print()

    

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Uso: python3 {0} <filename 1> <filename 2> <filename 3> ··· <filename n>".format(sys.argv[0]))
    else:
        lst = [sys.argv[i] for i in range(1,(len(sys.argv)))] #lista con los nombres de archivos
        with SparkContext() as sc:
            sc.setLogLevel("ERROR")
            main(sc, lst)