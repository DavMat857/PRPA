import random
from paho.mqtt.client import Client

def on_message(mqttc, userdata, msg):
    print("MESSAGE:", userdata, msg.topic, msg.qos, msg.payload, msg.retain)
    num = float(msg.payload)
    if num.is_integer() and is_prime(int(num)):
        print(f"{num} is prime")
    else:
        print(f"{num} is not prime")


def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**(1/2))+1):
        if n % i == 0:
            return False
    return True

def main(broker, topic):
    mqttc = Client()

    mqttc.on_message = on_message
    mqttc.connect(broker)

    mqttc.subscribe(topic)
    mqttc.loop_forever()

if __name__ == "__main__":
    import sys
    if len(sys.argv)<3:
        print(f"Usage: {sys.argv[0]} broker topic")
        sys.exit(1)
    broker = sys.argv[1]
    topic = sys.argv[2]
    main(broker, topic)
