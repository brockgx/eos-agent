#Import of any third party libraries
import socket
import os
import psutil
import json

#Import of any in house modules
from modules.sockets.socket_data_transfer import sendSocketData, receiveSocketData

#Constants
HOST = "0.tcp.ngrok.io"
PORT = 12463

from datetime import datetime

def get_json():
    now = datetime.now()
    x = {
        "machine_name": socket.gethostname(),
        "collection_time": now.strftime("%m/%d/%Y, %H:%M:%S"),
        "app_metrics": [{"name":"python.exe", "cpu_usage": 20.3, "ram_usage": 10.1}, {"name":"discord.exe", "cpu_usage": 5.76, "ram_usage": 23.6}],
        "system_metrics": [{"cpu":psutil.cpu_percent()}, {"ram":psutil.virtual_memory().percent}]
    }
    return json.dumps(x)



#Function: instantiate socket and connect
def connect_to_server(host, port):
  #Validate port and host

  #Connect to socket
  sock = socket.socket()
  sock.connect((host,port))

  return sock

#Receive/Send Data
def data_transfer():
  s = connect_to_server(HOST, PORT)
  selection_data = ["Message 1", "Message 2", "Message 3"]
  number = 3
  #Loop to look for data
  while True:
    data = receiveSocketData(s)

    print(data)
    
    if data == 'dataone':
      string1 = "Hello this is string one"
      sendSocketData(s, string1)
    if data == 'datatwo':
      json_output = get_json()
      sendSocketData(s, json_output)
      selection_data.pop(0)
      number = number + 1
      selection_data.append("Message " + str(number))
    if data == 'PINGING':
      sendSocketData(s, " ")