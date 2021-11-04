import os
import json
import base64
import subprocess
from sys import platform
from ..utilities.logging_setup import agent_logger

from enum import Enum
import threading
import time
import psutil

class OS_TYPE(Enum): #Enum to determine the OS
    WINDOWS = 1
    LINUX = 2
    MAC = 3

os_type = OS_TYPE.WINDOWS

def jsonProcessor(json):
    global os_type #Function to identity the platform of the agent
    if platform == "linux" or platform == "linux2":
        print("linux")
        os_type = OS_TYPE.LINUX
    elif platform == "darwin":
        print("mac")
        os_type = OS_TYPE.MAC
    elif platform == "win32":
        print("windows")
        os_type = OS_TYPE.WINDOWS


    #Runs Specific functions based on the type information received from server and  returns the output of the function.   
    json_type = json["type"]
    params = json["parameters"]
    if json["type"] == "fileupload":
        print("fileupload Received")
        agent_logger.info("Attempting to upload the file at destination: {}.".format(params["destination"]))
        return fileProcessor(params)
    elif json["type"] == "appshutdown":
        print("appshutdown Received")
        agent_logger.info("Attempting to stop application with name: {} and PID: {}.".format(params["app_name"], params["app_id"]))
        return appshutdown(params)
    elif json["type"] == "restartapp":
        print("appshutdown Received")
        agent_logger.info("Attempting to restart application with name: {} and PID: {}.".format(params["app_name"], params["app_id"]))
        return apprestart(params)
    elif json["type"] == "shutdownmachine":
        print("shutdownmachine Received")
        agent_logger.info("Attempting to shutdown machine {} .".format(json["machine_name"]))
        #return "Shutting Down Machine"
        return shutdown(json)
    elif json["type"] == "restartmachine":
        print("restartmachine Received")
        agent_logger.info("Attempting to restart machine {} .".format(json["machine_name"]))
        #return "Restarted Machine"
        return restart(json)
    elif json["type"] == "custom_command":
        print("custom Received")
        agent_logger.info("Attempting to run the command: {} on machine: {}.".format(params["custom_command"], json["machine_name"]))
        return shellProcessor(params)
    elif json["type"] == "ping":
        agent_logger.info("Pinging on machine: {}.".format(json["machine_name"]))
        return "PING"
          

#Shutdown App Function
def appshutdown(params):
    pid = params['app_id']
    name = params['app_name']
    try:
        process = psutil.Process(pid)
    except:
        return f"ID:{pid} not found"
    result = killpid(name, pid, process)
    agent_logger.info("Application with details: ({},{}) stopped.".format(pid, name)) 
    return result

#Restart App Function
def apprestart(params):
    pid = params['app_id']
    name = params['app_name']
    try:
        process = psutil.Process(pid)
    except:
        return f"ID:{pid} not found"
    exe_path = process.exe()
    result = killpid(name, pid, process)
    thread = (threading.Thread(target = thread_run_process, args=[exe_path, ""], daemon=True))
    thread.start()
    agent_logger.info("Application with details: ({},{}) restarted.".format(pid, name)) 
    return result

#Killing a Process function
def killpid(name, pid, process):
    result = ""
    if process != None:
        process.kill()
        result = f"Process {name} with ID:{pid} terminated successfully."
    else:
        result = f"No process with ID:{pid} found."
    return result

#Shutting down a machine function
def shutdown(json):
    time.sleep(5)
    global os_type
    if os_type == OS_TYPE.WINDOWS:
        os.system("shutdown /s /t 0")
    else: #Linux and Mac
        os.system("shutdown -h now")
    agent_logger.info("Machine Shutdown: {} .".format(json["machine_name"]))
    return "Shutdown Initiated."

#Restarting a machine function
def restart(json):
    time.sleep(5)
    global os_type
    if os_type == OS_TYPE.WINDOWS:
        os.system("shutdown /r /t 0")
    else: #Linux and Mac
        os.system("shutdown -r now")
    agent_logger.info("Machine Restarted: {} .".format(json["machine_name"]))
    return "Restart Initiated."

#File Upload function
def fileProcessor(params):
    print("File Processor")
    #print(commandJson)
    #file = params['file']
    b64file = params['b64file']
    destination = params['destination']
    print("File Received")
    #print(b64file)
    file = base64.b64decode(b64file)
    outFileHandle = open(destination, "wb")
    outFileHandle.write(file)
    result = "File Written to " + destination
    print(result)
    agent_logger.info("File: uploaded at destination: {}.".format(destination))
    return result


#Thread function to manage shell commands
thread = None
threadOutput = ""
def thread_run_process(command, shell):
    print("Shell Type:")
    print(shell)
    ps_command = command
    global os_type
    if os_type == OS_TYPE.WINDOWS:
        if shell == "powershell":
            ps_command = ["powershell","-Command"]
            ps_command.append(command)
        if shell == "wsl":
            ps_command = "wsl " + command
    else: #Linux and Mac
        print("Linux")
    
    print(ps_command)
    #result = subprocess.run(command, stdout=subprocess.PIPE, shell=True)
    result = subprocess.run(ps_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    print(result.stdout.decode('ascii'))
    print(result.stderr.decode('ascii'))
    global threadOutput
    threadOutput = "stdout:\n" + result.stdout.decode('ascii') + "\nstderr:\n" + result.stderr.decode('ascii')

# The custom command processer
def shellProcessor(params):
    shell = "cmd"
    if "shell" in params:
        shell = params['shell']
    command = params['custom_command']
    print("Shell Command Received")
    print(command)
    thread = (threading.Thread(target = thread_run_process, args=[command, shell], daemon=True))
    thread.start()
    time.sleep(5)
    global threadOutput
    returnResult = threadOutput
    threadOutput = ""
    return returnResult
