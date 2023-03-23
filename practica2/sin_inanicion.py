"""OPCION SIN INANICIÓN"""

import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

SOUTH = 1
NORTH = 0

NCARS = 30
NPED = 6
TIME_CARS_NORTH = 0.5  # a new car enters each 0.5s
TIME_CARS_SOUTH = 0.5  # a new car enters each 0.5s
TIME_PED = 5 # a new pedestrian enters each 5s
TIME_IN_BRIDGE_CARS = (1, 0.5) # normal 1s, 0.5s
TIME_IN_BRIDGE_PEDESTRIAN = (30, 10) # normal 1s, 0.5s

#Creamos dos wait, porque habría que estudiar la frecuencia que entran los coches de un sitio y de otro
WAIT_LIMIT_NCARS_S=2
WAIT_LIMIT_NCARS_N=2  
WAIT_LIMIT_NPED=0 

#En cuanto se llenan estos límites hay que dejar pasar a los otros componentes, pero no siempre tengo que liberar a los peatones o a los coches del sur o el norte
#En el momento que hay un peatón sucedería como con un semáforo, le das al botón y ya pasarías, en el peor caso, el peatón esperaría a que salgan los coches que hay en ese momento

class Monitor():
    def __init__(self):
        self.mutex = Lock() # Inicializa un candado (Lock) para proteger el acceso a las variables compartidas
        self.patata = Value('i', 0) # Variable compartida sin uso específico en este código

        # Número de coches y peatones
        self.ncars_N = Value('i', 0) # Número de coches en dirección Norte
        self.ncars_S = Value('i', 0) # Número de coches en dirección Sur
        self.nped   = Value('i', 0) # Número de peatones

        # Condiciones
        self.can_cars_N=Condition(self.mutex) # Condición para controlar el paso de coches en dirección Norte
        self.can_cars_S=Condition(self.mutex) # Condición para controlar el paso de coches en dirección Sur
        self.can_ped  =Condition(self.mutex) # Condición para controlar el paso de peatones

        
        #Condiciones extras para evitar inanición
        # Inicializar el número de coches esperando en dirección Norte con un valor de 0
        self.n_cars_N_waiting = Value('i', 0)
        # Inicializar el número de coches esperando en dirección Sur con un valor de 0
        self.n_cars_S_waiting = Value('i', 0)
        # Inicializar el número de peatones esperando con un valor de 0
        self.n_ped_waiting = Value('i', 0)

        # Inicializar la condición de espera para coches en dirección Norte asociada al mutex
        self.wait_cars_N = Condition(self.mutex)
        # Inicializar la condición de espera para coches en dirección Sur asociada al mutex
        self.wait_cars_S = Condition(self.mutex)
        # Inicializar la condición de espera para peatones asociada al mutex
        self.wait_ped = Condition(self.mutex)


    # Método para manejar el ingreso de un coche en una dirección específica
    def wants_enter_car(self, direction: int) -> None:
        self.mutex.acquire()  # Adquiere el mutex para proteger el acceso a las variables compartidas

        self.patata.value += 1  # Incrementar el valor de "patata"

        if direction == NORTH:
            # Incrementar el número de coches esperando en dirección Norte
            self.n_cars_N_waiting.value += 1
            self.wait_cars_N.wait_for(self.waiting_cars_N)  # Esperar si se cumplen las condiciones para coches en dirección Norte

            self.can_cars_N.wait_for(self.can_pass_cars_N)  # Esperar si los coches en dirección Norte pueden pasar
            self.ncars_N.value += 1  # Incrementar el número de coches en dirección Norte
            self.n_cars_N_waiting.value -= 1  # Disminuir el número de coches esperando en dirección Norte

            # Notificar a los coches en dirección Sur y a los peatones si se cumplen las condiciones
            if self.n_cars_N_waiting.value <= WAIT_LIMIT_NCARS_N:
                self.can_cars_S.notify_all()
                self.can_ped.notify_all()

        else:
            # Incrementar el número de coches esperando en dirección Sur
            self.n_cars_S_waiting.value += 1
            self.wait_cars_S.wait_for(self.waiting_cars_S)  # Esperar si se cumplen las condiciones para coches en dirección Sur

            self.can_cars_S.wait_for(self.can_pass_cars_S)  # Esperar si los coches en dirección Sur pueden pasar
            self.ncars_S.value += 1  # Incrementar el número de coches en dirección Sur
            self.n_cars_S_waiting.value -= 1  # Disminuir el número de coches esperando en dirección Sur

            # Notificar a los peatones y a los coches en dirección Norte si se cumplen las condiciones
            if self.n_cars_S_waiting.value <= WAIT_LIMIT_NCARS_S:
                self.can_ped.notify_all()
                self.can_cars_N.notify_all()

        self.mutex.release()  # Liberar el mutex

    # Método para manejar la salida de un coche en una dirección específica
    def leaves_car(self, direction: int) -> None:
        self.mutex.acquire()  # Adquirir el mutex
        self.patata.value += 1  # Incrementar el valor de "patata"

        if direction == NORTH:
            self.ncars_N.value -= 1  # Disminuir el número de coches en dirección Norte

            # Si no hay coches en dirección Norte, notificar a los coches en dirección Sur y a los peatones
            if self.ncars_N.value == 0:
                self.can_cars_S.notify_all()
                self.can_ped.notify_all()
        else:
            self.ncars_S.value -= 1  # Disminuir el número de coches en dirección Sur

            # Si no hay coches en dirección Sur, notificar a los coches en dirección Norte y a los peatones
            if self.ncars_S.value == 0:
                self.can_cars_N.notify_all()
                self.can_ped.notify_all()
        self.mutex.release()  # Liberar el mutex


    # Método para manejar el ingreso de un peatón
    def wants_enter_pedestrian(self) -> None:
        self.mutex.acquire()  # Adquirir el mutex
        self.patata.value += 1  # Incrementar el valor de "patata"
        
        self.n_ped_waiting.value += 1  # Incrementar el número de peatones esperando
        self.wait_ped.wait_for(self.waiting_ped)  # Esperar si los peatones están dentro del límite permitido

        # Esperar hasta que los peatones puedan pasar
        self.can_ped.wait_for(self.can_pass_ped)
        self.nped.value += 1  # Incrementar el número de peatones en el puente
        self.n_ped_waiting.value -= 1  # Disminuir el número de peatones esperando

        # Notificar a los coches en ambas direcciones si el número de peatones esperando está dentro del límite permitido
        if self.n_ped_waiting.value <= WAIT_LIMIT_NPED:
            self.wait_cars_N.notify_all()
            self.wait_cars_S.notify_all()
        self.mutex.release()  # Liberar el mutex

    # Método para manejar la salida de un peatón
    def leaves_pedestrian(self) -> None:
        self.mutex.acquire()  # Adquirir el mutex
        self.patata.value += 1  # Incrementar el valor de "patata"
        self.nped.value -= 1  # Disminuir el número de peatones en el puente

        # Si no hay peatones en el puente, notificar a los coches en ambas direcciones
        if self.nped.value == 0:
            self.can_cars_N.notify_all()
            self.can_cars_S.notify_all()
        self.mutex.release()  # Liberar el mutex
        
    # Verifica si los coches en dirección Sur pueden pasar (no hay coches en dirección Norte ni peatones)
    def can_pass_cars_S(self) -> bool:
        return self.ncars_N.value == 0 and self.nped.value == 0

    # Verifica si los coches en dirección Norte pueden pasar (no hay coches en dirección Sur ni peatones)
    def can_pass_cars_N(self) -> bool:
        return self.ncars_S.value == 0 and self.nped.value == 0

    # Verifica si los peatones pueden pasar (no hay coches en ninguna dirección)
    def can_pass_ped(self) -> bool:
        return self.ncars_N.value == 0 and self.ncars_S.value == 0

    # Verifica si los coches en dirección Norte están esperando dentro de los límites permitidos
    def waiting_cars_N(self) -> bool:
        return self.n_cars_S_waiting.value <= WAIT_LIMIT_NCARS_S and self.n_ped_waiting.value <= WAIT_LIMIT_NPED

    # Verifica si los coches en dirección Sur están esperando dentro de los límites permitidos
    def waiting_cars_S(self) -> bool:
        return self.n_cars_N_waiting.value <= WAIT_LIMIT_NCARS_N and self.n_ped_waiting.value <= WAIT_LIMIT_NPED

    # Verifica si los peatones están esperando dentro de los límites permitidos
    def waiting_ped(self) -> bool:
        return self.n_cars_N_waiting.value <= WAIT_LIMIT_NCARS_N and self.n_cars_S_waiting.value <= WAIT_LIMIT_NCARS_S
    
    def __repr__(self) -> str:
        # Retorna una cadena con el valor de la variable patata
        return f'Monitor: {self.patata.value}'



#RETRASOS
# Función de retraso para coches en dirección Norte
def delay_car_north(factor = 3) -> None:
    time.sleep(random.random()/factor) # Espera un tiempo aleatorio dividido por el factor

# Función de retraso para coches en dirección Sur
def delay_car_south(factor = 3) -> None:
    time.sleep(random.random()/factor) # Espera un tiempo aleatorio dividido por el factor

# Función de retraso para peatones
def delay_pedestrian(factor = 3) -> None:
    time.sleep(random.random()/factor) # Espera un tiempo aleatorio dividido por el factor

# Función para simular el paso de un coche por el puente
def car(cid: int, direction: int, monitor: Monitor)  -> None:
    # Muestra que el coche quiere entrar al puente
    print(f"car {cid} heading {direction} wants to enter. {monitor}",flush=True)
    monitor.wants_enter_car(direction) # Solicita entrada al puente
    # Muestra que el coche entra al puente
    print(f"car {cid} heading {direction} enters the bridge. {monitor}",flush=True)
    
    # Aplica un retraso según la dirección del coche
    if direction==NORTH :
        delay_car_north()
    else:
        delay_car_south()
    
    # Muestra que el coche está dejando el puente
    print(f"car {cid} heading {direction} leaving the bridge. {monitor}",flush=True)
    monitor.leaves_car(direction) # Indica que el coche sale del puente
    # Muestra que el coche ha salido del puente
    print(f"car {cid} heading {direction} out of the bridge. {monitor}",flush=True)

# Función para simular el paso de un peatón por el puente
def pedestrian(pid: int, monitor: Monitor) -> None:
    # Muestra que el peatón quiere entrar al puente
    print(f"pedestrian {pid} wants to enter. {monitor}",flush=True)
    monitor.wants_enter_pedestrian() # Solicita entrada al puente
    # Muestra que el peatón entra al puente
    print(f"pedestrian {pid} enters the bridge. {monitor}",flush=True)
    delay_pedestrian() # Aplica un retraso al peatón
    # Muestra que el peatón está dejando el puente
    print(f"pedestrian {pid} leaving the bridge. {monitor}",flush=True)
    monitor.leaves_pedestrian() # Indica que el peatón sale del puente
    # Muestra que el peatón ha salido del puente
    print(f"pedestrian {pid} out of the bridge. {monitor}",flush=True)



#Funciones de generación de peatones y coches

# Función para generar peatones y simular su paso por el puente
def gen_pedestrian(monitor: Monitor) -> None:
    pid = 0 # Inicializa el identificador del peatón
    plst = [] # Lista para almacenar los procesos de peatones
    for _ in range(NPED): # Repite NPED veces
        pid += 1 # Incrementa el identificador del peatón
        # Crea un nuevo proceso para el peatón y lo inicia
        p = Process(target=pedestrian, args=(pid, monitor))
        p.start()
        plst.append(p) # Añade el proceso a la lista
        # Espera un tiempo aleatorio basado en una distribución exponencial
        time.sleep(random.expovariate(1/TIME_PED))

    for p in plst: # Espera a que todos los peatones terminen
        p.join()

# Función para generar coches en una dirección y simular su paso por el puente
def gen_cars(direction: int, time_cars, monitor: Monitor) -> Monitor:
    cid = 0 # Inicializa el identificador del coche
    plst = [] # Lista para almacenar los procesos de coches
    for _ in range(NCARS): # Repite NCARS veces
        cid += 1 # Incrementa el identificador del coche
        # Crea un nuevo proceso para el coche y lo inicia
        p = Process(target=car, args=(cid, direction, monitor))
        p.start()
        plst.append(p) # Añade el proceso a la lista
        # Espera un tiempo aleatorio basado en una distribución exponencial
        time.sleep(random.expovariate(1/time_cars))

    for p in plst: # Espera a que todos los coches terminen
        p.join()

# Función principal del programa
def main():
    monitor = Monitor() # Crea una instancia del monitor
    # Crea procesos para generar coches en dirección norte y sur, y peatones
    gcars_north = Process(target=gen_cars, args=(NORTH, TIME_CARS_NORTH, monitor))
    gcars_south = Process(target=gen_cars, args=(SOUTH, TIME_CARS_SOUTH, monitor))
    gped = Process(target=gen_pedestrian, args=(monitor,))
    # Inicia los procesos
    gcars_north.start()
    gcars_south.start()
    gped.start()
    # Espera a que los procesos terminen
    gcars_north.join()
    gcars_south.join()
    gped.join()
    print("Se acabo el programa") # Imprime un mensaje cuando termina el programa

if __name__ == '__main__':
    main() # Llama a la función principal
