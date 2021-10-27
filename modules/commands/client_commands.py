import os
import json
import base64
import subprocess
import time
from ..utilities.logging_setup import agent_logger

def jsonProcessor(json):
    type = json["type"]
    params = json["parameters"]
    if json["type"] == "fileupload":
        print("fileupload Received")
        agent_logger.info("Attempting to upload the file at destination: {}.".format(params["destination"]))
        return fileProcessor(params)
    elif json["type"] == "appshutdown":
        print("appshutdown Received")
        agent_logger.info("Attempting to stop application with name: {} and PID: {}.".format(params["app_name"], params["app_id"]))
        return "appshutdown"
       #agent_logger.info("Application with details: ({},{}) stopped.".format(params["app_name"], params["app_id"]))     
    elif json["type"] == "restartapp":
        print("appshutdown Received")
        agent_logger.info("Attempting to restart application with name: {} and PID: {}.".format(params["app_name"], params["app_id"]))
        return "restartapp"
       #agent_logger.info("Application with details: ({},{}) restarted.".format(params["app_name"], params["app_id"]))    
    elif json["type"] == "shutdownmachine":
        print("shutdownmachine Received")
        agent_logger.info("Attempting to shutdown machine {} .".format(json["machine_name"]))
        return shutdown(json)
    elif json["type"] == "restartmachine":
        print("restartmachine Received")
        agent_logger.info("Attempting to restart machine {} .".format(json["machine_name"]))
        return restart_command(json)
    elif json["type"] == "custom_command":
        print("custom Received")
        agent_logger.info("Attempting to run the command: {} on machine: {}.".format(params["custom_command"], params["machine_name"]))
        return shellProcessor(params)
          
def shutdown(json):
    os.system("shutdown /s /t 0")
    agent_logger.info("Machine Shutdown: {} .".format(json["machine_name"]))
    return "Shutdown Initiated."

def restart_command(json):
    print("JSON Command Processor")
    agent_logger.info("Restarted machine {} .".format(json["machine_name"]))
    return "Reset Initiated."
    
def fileProcessor(params):
    print("File Processor")
    #print(commandJson)
    #file = params['file']
    b64file = params['b64file']
    destination = params['destination']
    print("File Received")
    #print(b64file)
    # file = base64.b64decode(b64file)
    # outFileHandle = open(destination, "wb")
    # outFileHandle.write(file)
    result = "File Written to " + destination
    print(result)
    agent_logger.info("File: uploaded at destination: {}.".format(destination))
    return result

def shellProcessor(json):
  print("Custom command")
  params = json["parameters"]
  command = params['command']
  if type == "shell":
    print("Shell Command Received")
    print(command)
    left = ""
    right = ""
    if ' ' in command:
      pos = command.find(' ')+1
      left, right = command[:pos], command[pos:]
    else:
      left = command
    result = subprocess.run([left, right], capture_output=True).stdout.decode('utf-8')
    print(result)
    agent_logger.info("Custom Command ran sucessfully on machine {}.".format(json["machine_name"]))
    return result