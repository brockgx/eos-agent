#Import of any third party libraries
import socket
import os

#Import of any in house modules
from modules.sockets.socket_data_transfer import sendSocketData, receiveSocketData

#Constants
HOST = "127.0.0.1"
PORT = 1337

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
      sendSocketData(s, selection_data[0])
      selection_data.pop(0)
      number = number + 1
      selection_data.append("Message " + str(number))
    if data == 'PINGING':
      sendSocketData(s, " ")