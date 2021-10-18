#Import third party libraries
import socket, time, select, queue

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
  while True:
    print_log_msg("Doing stuff on socket (" + str(socket_port) + ")")
    time.sleep(30)

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
def accept_new_connections(agent_socket):
  #Get new connection
  conn, c_addr = agent_socket.accept()
  print_log_msg("New connection from: " + str(c_addr))
  conn.setblocking(0) # or 1

  #Save connection details
  all_socket_connections.append(conn)
  all_message_queues[conn] = queue.Queue()
  
#This will be the main function for handling requests
def agent_request_handling(agent_socket):
  all_socket_connections = [agent_socket]
  all_socket_outputs = []
  all_message_queues = {}

  print_log_msg("Evaluating socket traffic (" + str(agent_socket.getsockname()[1]) + ")...")
  recv, send, exce = select.select(all_socket_connections, all_socket_outputs, all_socket_connections)
  
  print_log_msg("Doing functional stuff")
