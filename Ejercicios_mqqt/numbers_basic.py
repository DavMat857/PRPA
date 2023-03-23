# -*- coding: utf-8 -*-

from paho.mqtt.client import Client

def on_message(mqttc, userdata, msg):
    d = float(msg.payload)
    n = int(round(d))
    print("Número",msg.payload,'int',n,'float',d, 'entero' if d==n else 'real')

def main():
    mqttc = Client()
    mqttc.on_message = on_message
    mqttc.connect("simba.fdi.ucm.es")
    mqttc.subscribe('numbers')
    mqttc.loop_forever()


if __name__ == '__main__':
    main()
