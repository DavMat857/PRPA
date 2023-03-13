from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Lock, Semaphore
from multiprocessing import current_process
from multiprocessing import Value, Array

from time import sleep
import random   

N = 3 # Cantidad de números que queremos que genere cada proceso
NPROD = 4 # Cantidad de procesos

def delay(factor = 3): #Introduce un factor de retraso aleatorio
    sleep(random.random()/factor)

# Devuelve el mínimo de los productores teniendo en cuenta que -1 es vacío
def min_list(lista): 
    return min([x for x in lista if x > 0])


def producir(valor, almacen_personal, empty, non_empty):
   
 # Introducimos un valor del proceso_j en su almacen_personal_j
    for i in range(N):
        empty.acquire()

        print(f"Producer {current_process().name} produciendo", flush=True)
        
        # Aumentamos el valor de la variable compartida asociada a un proceso
        valor.value += random.randint(3, 10)
        delay()
        
        almacen_personal[i] = valor.value
        print(f"Producer {current_process().name} almacenado {valor.value}")

        non_empty.release()
        delay()
        
    
    
    print(f"Producer {current_process().name} finalizado")

        
def consumir(almacen_final, almacenes_productores, semaforos_empty, semaforos_non_empty, posiciones):
    # Inicializamos el índice del almacén 
    almacen_index = 0
    
    finalizado = BoundedSemaphore(NPROD)
    
    for i in range(NPROD):
        semaforos_non_empty[i].acquire()
        semaforos_non_empty[i].release() 

    while True:

        if finalizado.get_value() == 0:
            break 

        # Esperar a que todos los productores hayan producido al menos un valor

        # Extraer elementos de los almacenes de los productores
        comparacion = [alm[i] if i < len(alm) else -1 for alm, i in zip(almacenes_productores, posiciones)]
        
        # Escoger el mínimo de los valores producidos por los productores
        print("Comparación actual:", comparacion[:])
        minimo = min_list(comparacion)
        delay()
        print("El mínimo de la lista comparacion es:" , minimo)

        # Obtener el índice del mínimo
        index_minimo = comparacion.index(minimo)

        semaforos_empty[index_minimo].release()  
        
        # Insertar el mínimo en el array final
        almacen_final[almacen_index] = minimo

        # Actualizar el índice del array final
        almacen_index += 1
        
        # Actualizar el índice del almacen del productor correspondiente
        posiciones[index_minimo] += 1

        if posiciones[index_minimo] == N:
            finalizado.acquire()

        semaforos_non_empty[index_minimo].acquire()  
        
        print("Almacen por el momento", almacen_final[:])
        delay()
        
def main():
    
    almacen_final = Array('i', N * NPROD) # Almacenamiento de todos los valores
    posiciones = Array('i', NPROD) # Array que nos sirve para realizar comparaciones intermedias y tomar los valores
    

    
    for i in range(NPROD):
        posiciones[i] = 0
        
    for i in range(N * NPROD):
        almacen_final[i] = -2

    semaforos_empty = [Lock() for _ in range(NPROD)]
    semaforos_non_empty = [Semaphore(0) for _ in range(NPROD)]
        
    valores_iniciales = [Value('i', -2) for _ in range(NPROD)]
    almacenes_productores = [Array('i', N) for _ in range(NPROD)]

    for b in almacenes_productores:
        for i in range(N):
            b[i] = -2
    
    productores = [Process(target=producir,
                              name=f'p_{i}',
                              args=(valores_iniciales[i],
                                    almacenes_productores[i],
                                    semaforos_empty[i],
                                    semaforos_non_empty[i]))
                     for i in range(NPROD)]
    
    consumidor = Process(target=consumir, name="c", args=(almacen_final,
                                                          almacenes_productores,
                                                          semaforos_empty,
                                                          semaforos_non_empty,
                                                          posiciones))
    
    for p in productores + [consumidor]:
        p.start()
    
    
    for p in productores + [consumidor]:
        p.join()
    
    
    print("Almacén final", almacen_final[:])
    
if __name__ == "__main__":
    main()
