from multiprocessing import Process
from multiprocessing import BoundedSemaphore
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

    return min([x for x in lista if x >= 0])


def producir(valor, almacen_personal, generado):
   # Introducimos un valor del proceso_j en su almacen_personal_j
   
    for i in range(N):
       
        print(f"Producer {current_process().name} produciendo", flush=True)
        
        # Aumentamos el valor de la variable compartida asociada a un proceso
        valor.value += random.randint(3, 10)
        delay(2)
        almacen_personal[i] = valor.value
        
        print(f"Producer {current_process().name} almacenado {valor.value}", flush=True)

       # Me indica cuántos valores han sido generados por el proceso
        generado.value = i
    
    
    print(f"Producer {current_process().name} finalizado", flush=True)
    generado.value = N + 1
    
        
def consumir(almacen_final, index, almacenes_productores, posiciones, generados):
    
    almacen_index = 0
    finalizado = BoundedSemaphore(NPROD) # para tener en cuenta el número de procesos finalizados
    while True:
        
        condicion_seguir = all(pos <= n.value for pos, n in zip(posiciones, generados))
        
       
        if condicion_seguir:    # Esta condicional sirve para comprobar si cumplimos las condiciones para tomar el mínimo
            comparacion = [alm[i] if i<len(alm) else -1 for alm, i in zip(almacenes_productores, posiciones)]
            
            
            #Esta condición indica si ya se ha llenado el almacén, y por tanto hemos acabado
            if  finalizado.get_value() == 0:
                break
            
            
            minimo = min_list(comparacion) #Tomamos el mínimo dentro de la lista comparación
            delay()
            print("El mínimo de la lista comparacion es:" , minimo)

            # Obtener el índice del mínimo
            index.value = comparacion.index(minimo)
            
            # Insertar el mínimo en el array final
            almacen_final[almacen_index] = minimo

            # Actualizar el índice del array final
            almacen_index += 1
            
            
            posiciones[index.value] += 1
            if posiciones[index.value] == N:
                finalizado.acquire()
            
            print("Comparación actual:", comparacion[:])
            print("Almacen por el momento", almacen_final[:])
            
        else: #Esperamos a que se genere un valor por cada proceso que podamos tomar
            delay()
        
def main():
    
    almacen_final = Array('i', N * NPROD) # Almacenamiento de todos los valores
    comparacion = Array('i', NPROD)    # Array que nos sirve para realizar comparaciones intermedias y tomar los valores
    index = Value('i', 0)

    almacenes_productores = [Array('i', N) for _ in range(NPROD)]
    posiciones = Array('i', NPROD) # Es un array que contiene la última posición del almacen_productores introducido
    
    for i in range(NPROD):
        comparacion[i] = -2
    
    for i in range(NPROD):
        posiciones[i] = 0
        
    for i in range(N * NPROD):
        almacen_final[i] = -2
        
    valores_iniciales = [Value('i', -2) for _ in range(NPROD)]
    generados = [Value('i', -1) for _ in range(NPROD)] # Es un array que contiene cuanto elementos ha generado un productor
    
    
    productores = [Process(target=producir,
                              name=f'p_{i}',
                              args=(valores_iniciales[i],            
                                    almacenes_productores[i],
                                    generados[i]))
                     for i in range(NPROD)]
    
    consumidor = Process(target=consumir, args=(almacen_final,
                                                index,
                                                almacenes_productores,
                                                posiciones,
                                                generados))
    
    for p in productores + [consumidor]:
        p.start()
    
    
    for p in productores + [consumidor]:
        p.join()
    
    
    print("Almacén final", almacen_final[:])
    
if __name__ == "__main__":
    main()