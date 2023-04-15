import sys
from paho.mqtt.client import Client
from multiprocessing import Manager
import statistics as st
import time
import math

COTA_VALORES_LEIDOS = 1000


def calcula_media(lst):
    return st.mean(lst)

def es_primo(n):
    if n <= 1:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def on_message_humidity(mqttc, userdata, msg):
    print("MESSAGE:", userdata, msg.topic, msg.qos, msg.payload)
    hum = float(msg.payload)
    print("Valor de humedad leído: " + str(hum))
    if len(userdata['shared_lst']) <= COTA_VALORES_LEIDOS:
        userdata['shared_lst'].append(hum)
        print("valor almacenado correctamente")
    else:
        print("El valor leido no se ha podido almacenar porque la lista ha llegado a su capacidad maxima de " + str(COTA_VALORES_LEIDOS) + " elementos.")

def on_message_numbers(mqttc, userdata, msg):
    print("MESSAGE:", userdata, msg.topic, msg.qos, msg.payload)
    num = int(msg.payload)
    if es_primo(num):
        #si el numero es primo, leemos datos de la ruta '/humidity' y la almacenamos en la lista durante el numero primo de segundos.
        #despues, calculamos la media de los valores obtenidos y nos desconectamos de '/humidity' y volvemos a leer en '/numbers'
        mqttc.unsubscribe("/numbers")
        mqttc.subscribe ("/humidity")
        
        mqttc.message_callback_add("/humidity", on_message_humidity) #cada vez que leamos de la ruta '/humidity', se va a ejecutar la funcion 'on_message_humidity' automaticamente
        time.sleep(num) #esperamos 'num' segundos
        
        med = calcula_media(userdata['shared_lst'])
        print ("La media de los valores de humedad leídos es: " + str(med))
        #reseteamos la lista para que no siga acumulando valores
        userdata['shared_lst'] = Manager().list()
        
        mqttc.message_callback_remove("/humidity", on_message_humidity) #se deja de ejecutar automaticamente cuando leamos un dato de "/humidity"
        mqttc.subscribe("/numbers") #nos volvemos a conectar a la ruta de numeros
    else:
        print ("El numero " + str(num) + " ha sido leído y no es primo")

def main(broker, ruta):
    userdata = {
        'broker': broker,
        'shared_lst': Manager().list()
    }
    mqttc = Client(userdata = userdata)
    mqttc.connect(broker)
    mqttc.on_message = on_message_numbers
    mqttc.message_callback_add("/numbers", on_message_numbers)
    mqttc.subscribe("/numbers")
    mqttc.loop_forever() #escuchamos indefinidamente hasta que paremos manualmente

if __name__ == "__main__":
    if len(sys.argv) < 3:
        #sys.argv es una lista. Cuando en la terminal se introduce 'Python3 nombre1.py nombre2 .....'
        #usando sys.argv podemos acceder a cada una de esas componentes (es la lista de lo que introducimos, separadas justo donde está el espacio)
        #así, para poder recuperar 'nombre2', por ejemplo, basta con poner sys.argv[1]
        #por defecto, sys.argv[0] es el nombre del script de Python (nombre.py)
        print ("Faltan argumentos por introducir. Hazlo de la siguiente manera:")
        print ("Python3 " + sys.argv[0] + " broker ruta")
        print ("Donde broker es algo del tipo: 'simba.fdi.ucm.es'")
        print ("Y ruta hay que poner '/numbers'.")
        sys.exit(1) #salimos del programa indicando que ha habido un fallo. Por eso el 1.
    else:
        broker = sys.argv[1]
        ruta = sys.argv[2]
        main(broker)
