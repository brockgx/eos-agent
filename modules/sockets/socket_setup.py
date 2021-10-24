#Import third party libraries
import socket, time, select, queue, json

#Import application specific modules
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
  print_log_msg("Doing stuff on socket (" + str(socket_port) + ")")

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

    print_log_msg("Binding socket to port: " + str(socket_port))
    agent_socket.bind((socket_ip, socket_port))
    agent_socket.listen(5)

    return agent_socket
  except Exception as err_msg:
    print_log_msg("[Error] Socket creation failed.")
    print_log_msg("[Error Msg]: " + str(err_msg))
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
    print("\nWaiting for next event (" + str(sock.getsockname()[1]) + ")...")
    readable, writable, exceptional = select.select(allSocketConnections, allSocketOutputs, allSocketConnections)     #Not working after this.

    for read in readable:
      if read is sock:
        print("Accepting connnections")
        connection, client_address = read.accept()
        connection.setblocking(0)
        allSocketConnections.append(connection)
        allMessageQueues[connection] = queue.Queue()
      else:
        data = receiveSocketData(read)
        if data:
          #json_data = json.loads(data)
          print("Receieved: " + str(data) + " from (" + str(read.getpeername()) + ").")
          if data == "fileupload":
            print("fileupload")

          elif data == "precommand":
            print("precommand")
            #run command function here
            sendSocketData(read, data)
          elif data == "command":
            print("precommand")
          if read not in allSocketOutputs:
            allSocketOutputs.append(read)
        else:
          print("Closing " + str(read.getsockname()) + " after reading no data")
          if read in allSocketOutputs:
            allSocketOutputs.remove(read)
          
          read.close()
          del allMessageQueues[read]

    for write in writable:
      try:
        next_msg = allMessageQueues[write].get_nowait()
      except queue.Empty:
        print("Output queue for " + str(write.getpeername()) + " is empty")
        allSocketOutputs.remove(write)
      else:
        if data == "precommand":
          reply = "precommand received"
          noreply = "didnt receive"
          print("Sending " + str(reply) + " to " + str(write.getpeername()))
          sendSocketData(write, reply)
          allSocketConnections.remove(write) #removing the connection from list after sending
        else:
          print("Sending " + str(noreply) + " to " + str(write.getpeername()))
          sendSocketData(write, noreply)
          allSocketConnections.remove(write) #removing the connection from list after sending


    for exc in exceptional:
      print("Handling exceptional condition for " + str(exc.getpeername()))
      allSocketConnections.remove(exc)
      if exc in allSocketOutputs:
        allSocketOutputs.remove(exc)
      exc.close()
      del allMessageQueues[exc]

