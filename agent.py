import os, platform, time, json
from datetime import datetime
from modules.utilities.agent_core import get_agent_details, send_agent_details, data_collection
from modules.utilities.config_setup import retreive_config_details
from modules.sockets.socket_setup import create_socket
from modules.metrics.client_metrics import start_agent as enable_data_collection
from modules.metrics.client_metrics import get_json


#Define any constant expressions
DELAY_TIME = 20
BASEDIR = os.path.abspath(os.path.dirname(__file__))
if platform.system() == "Windows":
  CONFIG_PATH = BASEDIR + "\\agent-config.cfg"
else:
  CONFIG_PATH = BASEDIR + "/agent-config.cfg"

#Import the config
agent_config_details = retreive_config_details(CONFIG_PATH)

#Server API address
api_endpoint = "http://"
if agent_config_details["server_https_enabled"] == "true":
  api_endpoint = "https://"
api_endpoint += "bd80-122-104-255-94.ngrok.io"#+= str(agent_config_details["server_ip"])+":"+str(agent_config_details["server_port"])

#Start up agent, with data collection, socket listeners and loop
#Sending machine details untill successful
while True:
  result = send_agent_details(api_endpoint+"/dash/clientmachines", get_agent_details(agent_config_details))
  if result:
    break
  time.sleep(DELAY_TIME)

#Start the data collection unit
#combine metric collector with metric sender
#possibly collating info and sending every 5 mins
enable_data_collection()
time.sleep(10)
data_collection(api_endpoint+"/metrics/commitmetrics", 10, 180)

#Setup socket listeners (start listening loops)
#Socket on main port for handling commands (thread 2)
create_socket(agent_config_details["server_ip"], agent_config_details["socket_mport"])
#Socket on secondary port for handling data (may not be needed) (thread 3)
create_socket(agent_config_details["server_ip"], agent_config_details["socket_sport"])

#Thread 4, a thread checker? Plus all Keegans threads

# while True:
#   pass
#  time.sleep(DELAY_TIME/2)
#  metrics = json.loads(get_json())
#  print(str(metrics["collection_time"]) + " - " + str(metrics["machine_name"]) + " - " + str(metrics["system_metrics"][0]["cpu"]))
