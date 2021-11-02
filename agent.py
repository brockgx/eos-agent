#
#  Agent main file, this will be the main execution point of the agent.
#  It will handle:
#    - Importing config file details
#    - Sending agent details to server
#    - Starting data collection and sending functionality
#    - Starting command listener threads
#
#    https://github.com/brockgofficial/eos-agent
#


#Import any third party dependencies
import os, platform, time, json
from datetime import datetime

#Import any custom mode modules for the agent
from modules.utilities.logging_setup import agent_logger
from modules.utilities.agent_core import get_agent_details, send_agent_details, data_collection
from modules.utilities.config_setup import get_config_details
from modules.sockets.socket_setup import create_socket
from modules.metrics.client_metrics import start_agent as enable_data_collection
from modules.metrics.client_metrics import get_json

#Import the configuration file details
agent_config_details = get_config_details()

#Verify whether the config details are correct and continue running the agent
if agent_config_details != False:
  agent_logger.debug("=================================================")
  agent_logger.info("Starting the agent on {}.".format(platform.node()))
  agent_logger.info("Agent configuration options: {}".format(agent_config_details))

  #Buld the server API address based on configuration options
  api_endpoint = "http://"
  if agent_config_details["SERVER-DETAILS"]["HTTPS-ENABLED"]:
    api_endpoint = "https://"
  if agent_config_details["SERVER-DETAILS"]["PORT-ENABLED"]:
    api_endpoint += str(agent_config_details["SERVER-DETAILS"]["SERVER-ADDRESS"])+":"+str(agent_config_details["SERVER-DETAILS"]["SERVER-PORT"])
  else:
    api_endpoint += str(agent_config_details["SERVER-DETAILS"]["SERVER-ADDRESS"])

  #Start up agent, with data collection, socket listeners and loop
  #Sending machine details untill successful
  while True:
    result = send_agent_details(api_endpoint+"/dash/clientmachines", get_agent_details(agent_config_details["SOCKET-DETAILS"]["SOCKET-ADDRESS"],agent_config_details["SOCKET-DETAILS"]["MAIN-PORT"],agent_config_details["SOCKET-DETAILS"]["SECONDARY-PORT"]), agent_config_details["GENERAL-DETAILS"]["DELAY-TIME"])
    if result:
      break
    time.sleep(agent_config_details["GENERAL-DETAILS"]["DELAY-TIME"])

  #Start the data collection unit
  #comines data polling collectors with data sender
  #collect per the COLLECTION-INTERVAL and sending per the POST-INTERVAL
  data_collection(api_endpoint+"/metrics/commitmetrics", agent_config_details["GENERAL-DETAILS"]["COLLECTION-INTERVAL"], agent_config_details["GENERAL-DETAILS"]["POST-INTERVAL"])

  #Setup socket listeners (start listening loops)
  #Socket on main port for handling commands
  create_socket(agent_config_details["SOCKET-DETAILS"]["SOCKET-ADDRESS"], agent_config_details["SOCKET-DETAILS"]["MAIN-PORT"])
  #Socket on secondary port for handling data (may not be needed)
  create_socket(agent_config_details["SOCKET-DETAILS"]["SOCKET-ADDRESS"], agent_config_details["SOCKET-DETAILS"]["SECONDARY-PORT"])
else:
  #Log the message and issue with the config file
  agent_logger.critical("Failed to start the Agent, issue with config file.")
