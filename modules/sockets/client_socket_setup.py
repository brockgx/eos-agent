#Import of any third party libraries
import socket
import os

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
    s.send(bytes(" ","utf-8")) #Empty string to establish target
    data = s.recv(20480)

    print(data.decode())
    
    if data.decode() == 'dataone':
      string1 = ("Hello this is string one")
      s.send(str.encode(string1))
    if data.decode() == 'datatwo':
      string2 = ("Hello this is string two")
      s.send(str.encode(string2))
