#Import third party libraries
import socket, threading, time, sys, platform, requests, ipaddress
import ifcfg #needs pip install
from datetime import datetime
from configparser import ConfigParser

#Import application specific modules
from .data_transfer import sendSocketData, receiveSocketData

## Functions ##
#Custom logging print message
def print_log_msg(msg):
  print("["+str(datetime.now())+"] "+ str(msg))

#Get config file details
def retreive_config_details(file_path):
  config = ConfigParser()
  config.read(file_path)

  required_properties = ["SERVER_ADDRESS", "SERVER_PORT", "MAIN_PORT", "SECONDARY_PORT"]
  details = {**config['server-details'], **config['socket-details']}
  try:
    for key in details:
      if key.upper() not in required_properties:
        raise ValueError("Invalid property " + key.upper() + " in config file (" + str(file_path) + ")", ",".join(required_properties))
  except ValueError as err:
    print_log_msg(str(err.args[0]))
    print_log_msg("Looking for properties: " + str(err.args[1:]))
    sys.exit(1)
  
  return {
      "server_ip": details["server_address"],
      "server_port": details["server_port"],
      "socket_mport": details["main_port"],
      "socket_sport": details["secondary_port"]
    }

#Create, configure and run a thread
def create_new_thread(targetFunction, targetArgs = ()):
  t = threading.Thread(target=targetFunction, args=targetArgs)
  t.daemon = True
  t.start()

#Get agent machine details
def get_agent_details():
  return {
    "os_type": platform.system(),
    "os_details": platform.platform(),
    "os_release": platform.release(),
    "os_version": platform.version(),
    "processor_type": platform.processor(),
    "host_name": socket.gethostname(),
    "ip_addr_v4": socket.gethostbyname(socket.gethostname())
  }

#Send agent details to the API for storage
def send_agent_details(server_address, post_route, agent_details):
  print_log_msg("Sending the agent details to " + server_address + post_route)
  try:
    api_result = requests.post(server_address + post_route, json=agent_details)
    if api_result.status_code == 200 and api_result.text == "Success":
      print_log_msg("Sent the agent details successfully")
      return True
    elif api_result.status_code == 200:
      print_log_msg("Connect to the endpoint was good; however, an error occurred.")
      print_log_msg(str(api_result.text))
      return False
    else:
      print_log_msg("Failure occurred: (" + str(api_result.status_code) + ") " + str(api_result.reason))
      return False
  except Exception as err:
    print_log_msg("Failed to connect to: " + server_address + post_route)
    return False


