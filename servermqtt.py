import paho.mqtt.client as mqtt
import subprocess
import multiprocessing
import time

def run(): 
    while True: 
        s = str(subprocess.check_output("xset -q",shell=True))
        if "Monitor is On" in s:
            subprocess.call("xset -display :0.0 dpms force off", shell=True)
        print("Thread running")
        time.sleep(2)

def on_connect(client, userdata, flags, rc):
       print("Connected with result code "+str(rc))
    client.subscribe(channel)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global flag
    global t1
    message =  str(msg.payload)
    print(message)
    print(msg.topic+" "+str(msg.payload))
    if "OFF" in message:
        flag = False
        t1 = multiprocessing.Process(target=run,) 
        t1.start() 
                
    if "ON" in message:
        subprocess.call(["xset","-display",":0","dpms","force","on"])
        print(type(t1))
        
        t1.terminate()
        print('TERMINATED:', t1, t1.is_alive())

        t1.join()
        print('JOINED:', t1, t1.is_alive())

channel = str(input())
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
 
client.connect("broker.hivemq.com", 1883, 60)
print(on_message)
client.loop_forever()
