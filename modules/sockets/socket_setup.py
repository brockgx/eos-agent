#Import third party libraries
import socket, time, select, queue, json

from modules.commands.client_commands import jsonProcessor

#Import application specific modules
from ..utilities.logging_setup import agent_logger
from ..utilities.agent_core import print_log_msg, create_new_thread
from .data_transfer import sendSocketData, receiveSocketData

## Functions ##
#Function: To create a new socket via wrapper function
#Params:
#   - socket_ip: the address of the socket
#   - socket_port: the port number to use for the socket
#Returned: - None
def create_socket(socket_ip, socket_port):
  create_new_thread(setup_socket_listener, (socket_ip, socket_port))

#Function: Socket wrapper function to configure new socket and run main function
#Params:
#   - socket_ip: the address of the socket
#   - socket_port: the port number to use for the socket
#Returned: - None
def setup_socket_listener(socket_ip, socket_port):
  new_socket = configure_socket(socket_ip, socket_port) #Creates a new socket
  #Then run main function   
  mainFunction(new_socket) # Main function to handle all incoming connections
  agent_logger.info("Socket is now listening on ({},{}).".format(socket_ip, socket_port))

#Function: Generate the server socket
#Params:
#   - socketIp:    the socket IP
#   - socketPort:  the socket port #
#Returned:
#   - The created socket or False (if error occurs)
def configure_socket(socket_ip, socket_port):
  try:
    agent_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    agent_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    agent_logger.info("Binding socket to port: {}".format(socket_port))
    agent_socket.bind((socket_ip, socket_port))
    agent_socket.listen(5)

    return agent_socket
  except Exception as err_msg:
    agent_logger.critical("Socket creation failed on port: {}".format(socket_port))
    agent_logger.critical(err_msg)
    return False

#Function: To setup command handling and listening functionality
#Params:
#   - sock: the socket of the agent listener
#Returned: - None
def mainFunction(sock):
  allSocketConnections = [sock]
  allSocketOutputs = []
  allMessageQueues = {}

  while allSocketConnections:
    agent_logger.info("Waiting for next socket event ({})...".format(sock.getsockname()[1]))
    readable, writable, exceptional = select.select(allSocketConnections, allSocketOutputs, allSocketConnections)    #Select Setup 

    for read in readable: #Receiving
      if read is sock:
        connection, client_address = read.accept() #Accepts the connection
        agent_logger.info("New connection accepted from: {}.".format(connection.getpeername())) #Logs it into the agent logger file
        connection.setblocking(0) #Connecting Blocking set to 0
        allSocketConnections.append(connection) #Adds socket connection to the list
        allMessageQueues[connection] = queue.Queue() #Connection is now in queue
      else:
        data = receiveSocketData(read) #If connection is established, recevied data
        if data:
          json_data = json.loads(data) #Loads data into the var
          agent_logger.info("Command data receieved {} from ({}).".format(data, read.getpeername())) #Logs it to the agent logger file
          result = jsonProcessor(json_data) #Running the command procressor function
          allMessageQueues[read].put(result) #Adds the output to the messages queue to be displayed

          if read not in allSocketOutputs:
            allSocketOutputs.append(read)
        else:
          agent_logger.info("Closing {} after reading no data.".format(read.getpeername()))
          if read in allSocketOutputs:
            allSocketOutputs.remove(read)
          
          read.close()
          del allMessageQueues[read]

    for write in writable: #Sending
      try:
        next_msg = allMessageQueues[write].get_nowait()
      except queue.Empty:
        allSocketOutputs.remove(write) #if queue is empty removes the connection
      else:
        agent_logger.info("Sending {} to {}.".format(next_msg, write.getpeername()))
        sendSocketData(write, next_msg)
        allSocketConnections.remove(write) #removing the connection from list after sending

    for exc in exceptional:
      agent_logger.info("Handling exceptional condition for {}.".format(exc.getpeername()))
      allSocketConnections.remove(exc)
      if exc in allSocketOutputs:
        allSocketOutputs.remove(exc)
      exc.close()
      del allMessageQueues[exc]