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

  return (sock,portmanual)

#Receive/Send Data
def data_transfer():


  print("You connected to the socket")
  while True:
    s = connect_to_server(HOST, PORT)
    print(f"You connected to the socket on port: {s[1]}")

    while True:
      cmd = input(f"[{HOST} : {s[1]}]> ")

      if cmd == "getdata" or cmd == "getmessage":
        sendSocketData(s[0], cmd)
        time.sleep(2)
        client_response = receiveSocketData(s[0])
        print(client_response)
      if cmd == "ping":
        sendSocketData(s[0], "PINGING")
        time.sleep(2)
        client_response = receiveSocketData(s[0])
        print(client_response)
      if cmd == 'exit':
        print
        break

      

data_transfer()