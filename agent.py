import os, platform, time
from modules.sockets.agent_core_setup import retreive_config_details, send_agent_details, get_agent_details
from modules.metrics.client_metrics import start_agent as enable_data_collection
from modules.metrics.client_metrics import get_json

#Define any constant expressions
BASEDIR = os.path.abspath(os.path.dirname(__file__))
if platform.system() == "Windows":
  CONFIG_PATH = BASEDIR + "\\agent-config.cfg"
else:
  CONFIG_PATH = BASEDIR + "/agent-config.cfg"

#Import the config
agent_config_details = retreive_config_details(CONFIG_PATH)

#Server API address
api_endpoint = "http://"+str(agent_config_details["server_ip"])+":"+str(agent_config_details["server_port"])

#Start up agent, with data collection, socket listeners and loop
#Sending machine details untill successful
while True:
  result = send_agent_details(api_endpoint, "/test/senddetails", get_agent_details())
  if result:
    break
  time.sleep(60)

#Start the data collection unit
#combine metric collector with metric sender
#possibly collating info and sending every 5 mins
enable_data_collection()

#Setup socket listeners (start listening loops)
import json #temp

while True:
 time.sleep(60)
 metrics = json.loads(get_json())
 print(str(metrics["collection_time"]) + " - " + str(metrics["machine_name"]) + " - " + str(metrics["system_metrics"][0]["cpu"]))
  