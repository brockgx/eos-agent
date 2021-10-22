#Import third party libraries
import socket, threading, sys, platform, ipaddress, requests, time, json
import ifcfg #needs pip install
from datetime import datetime
from getmac import get_mac_address

from ..metrics.client_metrics import get_json

## Functions ##
#Function: Generate a structured message for printing to the console
#Params:
#   - msg: a string to be displayed
#Returned: - None
def print_log_msg(msg):
  print("["+str(datetime.now())+"] "+ str(msg))

#Function: Generate and start a new thread
#Params:
#   - target_function: the function the thread will run
#   - target_args:     the corresponding function arguments
#Returned:
#   - None (the thread?? or add thread to a list for checking)
def create_new_thread(target_function, target_args = ()):
  t = threading.Thread(target=target_function, args=target_args)
  t.daemon = True
  t.start()

#Function: Get the agents machine details
#Params: - None
#Returned:
#   - Dict/JSON object of the required machine details
def get_agent_details(config_details):
  return {
    "os_type": platform.system(),
    "os_details": platform.platform(),
    "os_release": platform.release(),
    "os_version": platform.version(),
    "processor_type": platform.processor(),
    "host_name": socket.gethostname(),
    "ip_addr_v4": int(ipaddress.IPv4Address(socket.gethostbyname(socket.gethostname()))),
    "port_numbers": [str(config_details["socket_mport"]),str(config_details["socket_sport"])], 
    "mac_addr": get_mac_address()
  }

#Function: Send the collected machine details to the API
#Params:
#   - server_address_route: API route to send the message e.g. http://localhost:5000/senddetails
#   - agent_details: the collected agent details
#Returned:
#   - True (if successful) or False (if unsuccessful)
def send_agent_details(server_address_route, agent_details):
  print_log_msg("Sending the agent details to " + server_address_route)
  try:
    api_result = requests.post(server_address_route, json=agent_details)
    if api_result.status_code == 200 and api_result.text == "Success":
      print_log_msg("Sent the agent details successfully")
      return True
    elif api_result.status_code == 200:
      print_log_msg("Connection to the endpoint was good; however, an error occurred.")
      print_log_msg(str(api_result.text))
      return False
    else:
      print_log_msg("Failure occurred: (" + str(api_result.status_code) + ") " + str(api_result.reason))
      return False
  except Exception as err:
    print_log_msg("Failed to connect to: " + server_address_route)
    return False

#Function: Collect the machine data and send
def data_processing(api_route, collection_interval, post_interval):
  timeout = post_interval
  while True:
    timeout_start = datetime.timestamp(datetime.now())
    metrics = []

    while datetime.timestamp(datetime.now()) < timeout_start + timeout:
      data = json.loads(get_json())
      print(data)
      metrics.append(data)
      time.sleep(collection_interval)
    
    print_log_msg("3 mins reached. Posting metric data")
    requests.post(api_route, json={"content": metrics})

#Function: Commands


#Function: Thread Data collection
def data_collection(api_route, coll_interval, post_interval):
  create_new_thread(data_processing, [api_route, coll_interval, post_interval])
  print_log_msg("Data collection thread started.")