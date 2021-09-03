#Import appropriate libraries
import socket
import threading
import time
from queue import Queue

#Import in house libraries
from ..sockets.socket_data_transfer import sendSocketData, receiveSocketData

#Define any constant expressions
IP_RT = "127.0.0.1"
IP_DC = "127.0.0.1"
PORT_RT = 1337
PORT_DC = 1338
NUMBER_OF_THREADS = 2

#Define any variables
all_connections = []
all_addresses = []
JOB_NUMBER = [1, 2]
queue = Queue()

#Create the server socket and start listening
def start_socket_listener():
  try:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    return server_socket

  except socket.error as err_msg:
    print("Socket creation failed - Error: " + str(err_msg))

##Binding socket to port
def bind_socket(soc, port, ip):
  try:
    print("Binding socket to port: " + str(port))

    soc.bind((ip,port))
    soc.listen(2)
  
  except socket.error as err_msg:
    print("Socket binding failed - Error: " + str(err_msg))

#Accepting connections
def accept_new_connections(soc):
  for c in all_connections:
    c.close()

  del all_connections[:]
  del all_addresses[:]

  try:
    while True:
      clientsocket, address = soc.accept()
      soc.setblocking(1)

      all_connections.append(clientsocket)
      all_addresses.append(address)

      print(f"Connection from {address} has been established!")

      #Start a new thread
      #t = threading.Thread(target=run_agent, args=(clientsocket,))
      #t.daemon = True
      #t.start()
  
  except:
    print("Error accepting new connection")

def run_agent(sock):
  print(f'New thread created for connection {sock}')
  while True:
    data = receiveSocketData(sock)
    #data = sock.recv(2048).decode("utf-8")

    print(data)

    if data == 'getdata':
      string1 = "Welcome to the socket"
      sendSocketData(sock, string1)
    if data == 'getmessage':
      string1 = "Hello this is string one"
      sendSocketData(sock, string1)
    if data == 'PINGING':
      sendSocketData(sock, "I'm Alive")

#Run this for threading
def setup_agent_sockets():
  while True:
    x = queue.get()
    if x == 1:
      socone = start_socket_listener()
      bind_socket(socone, PORT_DC, IP_DC)
      accept_new_connections(socone)
    if x == 2:
      socone = start_socket_listener()
      bind_socket(socone, PORT_RT, IP_RT)
      accept_new_connections(socone)
    if x == 3:
      run_agent()

# Create worker threads
def createSockets():
  for i in range(NUMBER_OF_THREADS):
    t = threading.Thread(target=setup_agent_sockets)
    t.daemon = True
    t.start()

def create_jobs():
  for x in JOB_NUMBER:
    queue.put(x)

  queue.join()

