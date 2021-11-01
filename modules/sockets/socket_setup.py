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
  new_socket = configure_socket(socket_ip, socket_port)
  #Then run main function   
  mainFunction(new_socket)
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

#Function: Accepting new connections to the sockets (could be combined with select)
#Params:
#   -  agent_socket: the socket object for connections
#Returned: - None
# def accept_new_connections(agent_socket):
  
#   #Get new connection
#   conn, c_addr = agent_socket.accept()
#   print_log_msg("New connection from: " + str(c_addr))
#   return conn,c_addr
 

  #Function: main function
def mainFunction(sock):
  allSocketConnections = [sock]
  allSocketOutputs = []
  allMessageQueues = {}


  while allSocketConnections:
    agent_logger.info("Waiting for next socket event ({})...".format(sock.getsockname()[1]))
    readable, writable, exceptional = select.select(allSocketConnections, allSocketOutputs, allSocketConnections)     #Not working after this.

    for read in readable:
      if read is sock:
        connection, client_address = read.accept()
        agent_logger.info("New connection accepted from: {}.".format(connection.getpeername()))
        connection.setblocking(0)
        allSocketConnections.append(connection)
        allMessageQueues[connection] = queue.Queue()
      else:
        data = receiveSocketData(read)
        if data:
          json_data = json.loads(data)
          #agent_logger.info("Command data receieved {} from ({}).".format(data, read.getpeername()))

          result = jsonProcessor(json_data)
          allMessageQueues[read].put(result)

          """

          if json_data["type"] == "fileupload":
            print("fileupload Received")
            agent_logger.info("Attempting to upload the file: {} at destination: {}.".format(json_data["parameters"]["file"], json_data["parameters"]["destination"]))
            #fileuplaod function
            allMessageQueues[read].put("File Uploaded") #msg back to server
            time.sleep(2)
            agent_logger.info("File: {} uploaded at destination: {}.".format(json_data["parameters"]["file"], json_data["parameters"]["destination"]))
          elif json_data["type"] == "appshutdown":
            print("appshutdown Received")
            agent_logger.info("Attempting to stop application with name: {} and PID: {}.".format(json_data["parameters"]["app_name"], json_data["parameters"]["app_id"]))
            #appshutdown fucntion
            allMessageQueues[read].put("Shutting Down the app")
            time.sleep(2)
            agent_logger.info("Application with details: ({},{}) stopped.".format(json_data["parameters"]["app_name"], json_data["parameters"]["app_id"]))
          elif json_data["type"] == "restartmachine":
            print("restartmachine Received")
            agent_logger.info("Attempting to restart machine {} .".format(json_data["machine_name"]))
            #run the function
            allMessageQueues[read].put("Restarted the machine")
            time.sleep(2)
            agent_logger.info("Restarted machine {} .".format(json_data["machine_name"]))
          elif json_data["type"] == "restartapp":
            print("restartapp Received")
            agent_logger.info("Attempting to restart application with name: {} and PID: {}.".format(json_data["parameters"]["app_name"], json_data["parameters"]["app_id"]))
            #run the function
            allMessageQueues[read].put("Restarting  the app")
            time.sleep(2)
            agent_logger.info("Application with details: ({},{}) restarted.".format(json_data["parameters"]["app_name"], json_data["parameters"]["app_id"]))
          elif json_data["type"] == "custom_command":
            print("custom Received")
            agent_logger.info("Attempting to run the command: {} on machine: {}.".format(json_data["parameters"]["custom_command"], json_data["machine_name"]))
            #run the function
            allMessageQueues[read].put("custom command")
            time.sleep(2)
            agent_logger.info("Command ran sucessfully on machine {}.".format(json_data["machine_name"]))
          elif json_data["type"] == "shutdownmachine":
            print("shutdownmachine Received")
            agent_logger.info("Attempting to shutdown machine {} .".format(json_data["machine_name"]))
            #run the function
            allMessageQueues[read].put("Machine Shutdown")
            time.sleep(2)
            agent_logger.info("Machine Shutdown: {} .".format(json_data["machine_name"]))

        """

          if read not in allSocketOutputs:
            allSocketOutputs.append(read)
        else:
          agent_logger.info("Closing {} after reading no data.".format(read.getpeername()))
          if read in allSocketOutputs:
            allSocketOutputs.remove(read)
          
          read.close()
          del allMessageQueues[read]

    for write in writable:
      try:
        next_msg = allMessageQueues[write].get_nowait()
      except queue.Empty:
        #agent_logger.warning("Output queue for {} is empty.".format(write.getpeername()))
        allSocketOutputs.remove(write)
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