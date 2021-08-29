#Import of any third party libraries
import socket
import os
import time

#Import of any in house modules
#from modules.sockets.socket_data_transfer import sendSocketData, receiveSocketData
from ..sockets.socket_data_transfer import sendSocketData, receiveSocketData

#Constants
HOST = "127.0.0.1"
PORT = 1337

#Function: instantiate socket and connect
def connect_to_server(host, port):
  #Validate port and host
  portmanual = input("Input port #> ")

  #Connect to socket
  sock = socket.socket()
  sock.connect((host,int(portmanual)))

  return sock

#Receive/Send Data
def data_transfer():
  s = connect_to_server(HOST, PORT)
  selection_data = ["Message 1", "Message 2", "Message 3"]
  number = 3
  #Loop to look for data

  print("You connected to the socket")
  while True:
    cmd = input("> ")

    if cmd == "getdata" or cmd == "getmessage":
      sendSocketData(s, cmd)
      time.sleep(2)
      print("Sent data")
      client_response = receiveSocketData(s)
      print(client_response)
      print("Got data")
      break
    if cmd == "ping":
      sendSocketData(s, "PINGING")
      time.sleep(2)
      client_response = receiveSocketData(s)
      print(client_response)
      break

      

data_transfer()