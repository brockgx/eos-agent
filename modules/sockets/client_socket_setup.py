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
  #Loop to look for data
  while True:
    data = receiveSocketData(s)

    print(data)
    
    if data == 'dataone':
      string1 = "Hello this is string one"
      sendSocketData(s, string1)
    if data == 'datatwo':
      string2 = "Hello this is string two"
      sendSocketData(s, string2)
    if data == 'PINGING':
      sendSocketData(s, " ")