# -*- coding: utf-8 -*-

from paho.mqtt.client import Client

def on_message(mqttc, data, msg):
    print ('on_message', msg.topic, msg.payload)
    n = len('temperature/')
    key = msg.topic[n:]
    if key in data:
        data[key].append(msg.payload)
    else:
        data[key]=[msg.payload]
    print ('on_message', data)

def main():
    mqttc = Client(userdata={})
    mqttc.on_message = on_message
    mqttc.connect("wild.mat.ucm.es")
    mqttc.subscribe('temperature/#')
    mqttc.loop_forever()

if __name__ == "__main__":
    main()
