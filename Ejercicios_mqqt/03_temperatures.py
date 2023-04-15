# -*- coding: utf-8 -*-
#python t2.py simba.fdi.ucm.es temperatures
""" toma un diccionario de temperaturas para cada sensor y calcula la temperatura máxima, mínima y media para cada sensor y de todos los sensores. Luego, dentro del bucle principal, llamamos a esta función y mostramos las estadísticas calculadas por consola. Además, hemos modificado la lógica para procesar los datos recibidos del servidor MQTT para que los valores de temperatura se conviertan a float antes de ser agregados al diccionario de datos."""
from paho.mqtt.client import Client
from time import sleep

def on_message(mqttc, data, msg):
    print('on_message', msg.topic, msg.payload)
    n = len('temperature/')
    key = msg.topic[n:]
    if key in data:
        data['temp'][key].append(float(msg.payload))
    else:
        data['temp'][key] = [float(msg.payload)]
    print('on_message', data)

def calculate_statistics(data):
    statistics = {'max': {}, 'min': {}, 'mean': {}}
    for key, temp in data.items():
        statistics['max'][key] = max(temp)
        statistics['min'][key] = min(temp)
        statistics['mean'][key] = sum(temp) / len(temp)
    statistics['max_all'] = max(max_temp for max_temp in statistics['max'].values())
    statistics['min_all'] = min(min_temp for min_temp in statistics['min'].values())
    statistics['mean_all'] = sum(statistics['mean'].values()) / len(statistics['mean'])
    return statistics

def main(broker):
    data = {'temp': {}}
    mqttc = Client(userdata=data)
    mqttc.on_message = on_message
    mqttc.connect(broker)
    mqttc.subscribe('temperature/#')
    mqttc.loop_start()
    while True:
        sleep(5)
        statistics = calculate_statistics(data['temp'])
        print('Max temperature:', statistics['max_all'])
        print('Min temperature:', statistics['min_all'])
        print('Mean temperature:', statistics['mean_all'])
        print('Per-sensor statistics:')
        for key in sorted(data['temp'].keys()):
            print(f'{key}: Max {statistics["max"][key]}, Min {statistics["min"][key]}, Mean {statistics["mean"][key]}')
        data['temp'] = {}

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} broker")
        sys.exit(1)
    broker = sys.argv[1]
    main(broker)
