#Import of any third party libraries
import socket
import os
import psutil
import json

#Import of any in house modules
from modules.sockets.socket_data_transfer import sendSocketData, receiveSocketData

#Constants
HOST = "6.tcp.ngrok.io"
PORT = 19134

list_current_processes = []
list_current_processes_sorted = []
system_metrics = None

class application:
    def __init__(self, name, cpu, ram):
        self.name = name
        self.cpu = cpu
        self.ram = ram
    def to_dict(self):
      return {"name": self.name, "cpu": self.cpu, "ram": self.ram}

class system:
    def __init__(self, cpu, ram):
        self.cpu = cpu
        self.ram = ram

def get_list_of_processes(list_processes):
    process_iter = psutil.process_iter()
    cpu_count = psutil.cpu_count()
    for proc in process_iter:
        try:
            exe_path = proc.exe()
            process_name = proc.name()
            if ".exe" in process_name:
                list_processes.append(application(process_name, round(proc.cpu_percent()/cpu_count,2), round(proc.memory_percent(),2)))

            
        #print(process_name , ' ::: ', processID)
        except psutil.Error:
            pass
          
import threading
import time


def thread_application_metrics():
    global list_current_processes
    global list_current_processes_sorted
    while(True):
        list_current_processes.clear()
        get_list_of_processes(list_current_processes)
        list_current_processes.sort(key=lambda x: x.cpu, reverse=True)
        list_current_processes_sorted.clear()
        list_current_processes_sorted = list_current_processes.copy()
        time.sleep(5)

def thread_system_metrics():
    global system_metrics
    while(True):
        system_metrics = system(psutil.cpu_percent(), psutil.virtual_memory().percent)
        time.sleep(5)


from datetime import datetime

def get_json():
    now = datetime.now()
    app_metrics = []
    for i in range(5):
        app_metrics.append(list_current_processes_sorted[i].to_dict())
    x = {
        "machine_name": socket.gethostname(),
        "collection_time": now.strftime("%m/%d/%Y, %H:%M:%S"),
        "app_metrics": app_metrics,
        "system_metrics": [{"cpu":system_metrics.cpu}, {"ram":system_metrics.ram}]
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
  
  application_thread = threading.Thread(target = thread_application_metrics)
  if not application_thread.is_alive():
    application_thread.start()
  system_thread = threading.Thread(target = thread_system_metrics)
  if not system_thread.is_alive():
    system_thread.start()
  
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