#import third party libraries
import pickle
import time
import base64

#import personal libraries
# from ..security.AESEncryption import do_encrypt, do_decrypt

#Constants
HEADERSIZE = 10
RECVSIZE = 16

#Global variables

#Function: send data
def sendSocketData(socketConn, message):
  #The full message to send with the buffer
  #full_msg = bytes(f'{len(str(serialized_msg)):<{HEADERSIZE}}' + str(serialized_msg)[2:][:-1], "utf-8")
  #encrypted_test = serialize(message)
  #print(encrypted_test)
  fullMsg = bytes(f'{len(message):<{HEADERSIZE}}' + message, "utf-8")
  #length = bytes(f'{len(str(encrypted_test)):<{HEADERSIZE}}')
  #full_msg = length + encrypted_test
  #print(full_msg)
  

  #Send the message if available
  try:
    socketConn.sendall(fullMsg)
  except:
    print("Failure message")

#Function: receive data
def receiveSocketData(socketConn):
  #function variables
  #receieved_msg = "EMPTY"
  receiveMsg = True
  newMsg = True
  lengthMsg = True
  completeMsg = b''
  compdecr = b''

  while receiveMsg:
    try:
      msg = socketConn.recv(RECVSIZE)
    except:
      receiveMsg = False

    if msg != b'':
      if newMsg:
        lengthMsg = int(msg[:HEADERSIZE])
        newMsg = False
      
      fin = msg[HEADERSIZE:]
      completeMsg += msg
      #compdecr +=decr
      
      if len(completeMsg)-HEADERSIZE == lengthMsg:
        #Do something with the data - print example
        receievedMsg = completeMsg[HEADERSIZE:].decode("utf-8")
        #print(base64.b64decode(completeMsg[HEADERSIZE:]))
        #yolo = base64.b64decode(completeMsg[HEADERSIZE:])
        #decrypt = do_decrypt(yolo)
        #receievedMsg = decrypt.decode("utf-8")
        #receievedMsg = decrypt
        #print("Full message received")
        #Decrypt here
        #my_msg = receieved_msg[2:][:-1]
        #print(my_msg)
        #byte_msg = my_msg.encode()
        #print(byte_msg)
        #deserialized = pickle.loads(byte_msg)


        newMsg = True
        completeMsg = ''
        receiveMsg = False
        
  return receievedMsg