import paho.mqtt.publish as publish

# Configuración del broker y del topic
broker = "simba.fdi.ucm.es"
topic = "clients/test"

# Mensaje a publicar
mensaje = "Hola desde otro script!"

# Publicar el mensaje en el topic
if __name__ == "__main__":
    print("Escribe mensaje para cortar el envio de mensaje escribe 'N' ")
    mensaje = ""
    while mensaje!='N':
        mensaje = input()
        publish.single(topic, mensaje, hostname=broker)