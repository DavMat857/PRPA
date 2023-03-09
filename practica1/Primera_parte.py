from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array

from time import sleep
import random

N = 3 # Cantidad de números que quiero que genere cada proceso
NPROD = 5

def delay(factor = 3): #Introduce un factor de retraso aleatorio
    sleep(random.random()/factor)


def min_list(lista): #Devuelve el mínimo de la lista sin tener en cuenta el valor -1 

    lista_filtrada = [x for x in lista if x != -1] #Elimino los valores -1  
    if lista_filtrada: # Si no es vacía entra
        return min(lista_filtrada)
    
    return None


def producir(value, semaforo_general, semaphore, index, comparacion, terminate):

    # Produce un valor y lo almacena en un valor compartido: valores_inciales[i] para el proceso i
    for _ in range(N):
        
        semaphore.acquire()
        print(f"Producer {current_process().name} produciendo...")

        # Aumentamos el valor de la variable compartida asociada a un proceso
        value.value += random.randint(2, 7)
        delay()

        # Introducimos el elemento en la posición correspondiente del almacen comparación
        comparacion[index.value] = value.value
        index.value += 1
        semaforo_general.acquire()
        
        print(f"Producer {current_process().name} almacenado {value.value}")
    
    # Después de N veces ejecutado un proceso i se introduce un -1 para mostrar que ese hueco del almacén está vacío
    print(f"Producer {current_process().name} ha finalizado")
    semaphore.acquire()
    terminate.acquire()
    value.value = -1
    comparacion[index.value] = -1
    semaforo_general.acquire()

        
def consumir(almacen_final, semaforo_general, semaphores, comparacion, index, terminate):
    
    almacen_index = 0
    while True:
        # Esperar a que algún productor haya generado un número en caso contrario esperar
        if semaforo_general.get_value() == 0:
            
            # Cuando cada proceso tenga un número
            if terminate.get_value() == 0:
                break
            
            # Escoger el mínimo de los valores producidos por los productores
            minimo = min_list(comparacion[:])
            delay()
            print("El mínimo de la lista comparacion es:" , minimo)

            # Hayamos el índice del proceso que ha generado el mínimo
            index.value = comparacion[:].index(minimo)

            # Insertar en la posición correspondiente del almacen, posteriomente actualizarlo sumando 1
            almacen_final[almacen_index] = minimo
            almacen_index += 1
            
            # Liberar el semáforo correspondiente al productor del mínimo
            
            semaphores[index.value].release()
            print("Comparación actual:", comparacion[:])
            print("Almacen por el momento", almacen_final[:])
            
            semaforo_general.release()
            
        else:
            delay()
        
def main():
    
    almacen_final = Array('i', N * NPROD) #Guardo toda la información de forma ordenada
    semaforo_general = BoundedSemaphore(NPROD) #Me sirve para saber cuantos procesos puedo ejecutar
    comparacion = Array('i', NPROD) #Almacén auxiliar que toma el mínimo de cada proceso
    index = Value('i', 0) #Valor compartido que me sirve para conocer en que posición añadir un elemento al almacen_final 
    
    #Inicializo todo en -2 que significa que es vacío
    for i in range(NPROD): 
        comparacion[i] = -2
        
    for i in range(N * NPROD):
        almacen_final[i] = -2
        
    valores_iniciales = [Value('i', -2) for _ in range(NPROD)] #Genero el valor compartido de cada proceso
    semaforos = [Lock() for _ in range(NPROD)] #Semáforo asociado a cada proceso
    terminate = BoundedSemaphore(NPROD) #Semáforo para seleccionar número cuando se hayan generado todos los procesos
    
    productores = [Process(target=producir,
                              name=f'productor_{i}',
                              args=(valores_iniciales[i],
                                  semaforo_general,
                                  semaforos[i],
                                  index,
                                  comparacion,
                                  terminate))
                     for i in range(NPROD)]
    
    consumidor = Process(target=consumir, args=(almacen_final,
                                                semaforo_general,
                                                semaforos,
                                                comparacion,
                                                index,
                                                terminate))
    
    for p in productores:
        p.start()
    consumidor.start()
    
    for p in productores:
        p.join()
    consumidor.join()
    
    print("Almacén final", almacen_final[:])
    
if __name__ == "__main__":
    main()