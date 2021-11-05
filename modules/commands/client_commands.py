#Import third party libraries
import os, json, base64, subprocess
import threading, time, psutil
from sys import platform
from enum import Enum

#Import any custom made modules
from ..utilities.logging_setup import agent_logger

class OS_TYPE(Enum): #Enum to determine the OS
    WINDOWS = 1
    LINUX = 2
    MAC = 3

# Set os_type to windows by default.
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


    #Runs Specific functions based on the type information received from server and
    # returns the output of the function.   
    json_type = json["type"]
    params = json["parameters"]
    # File receiving.
    if json_type == "fileupload":
        print("fileupload Received")
        agent_logger.info("Attempting to upload the file at destination: {}.".format(params["destination"]))
        return fileProcessor(params)
    # Kill an app
    elif json_type == "appshutdown":
        print("appshutdown Received")
        agent_logger.info("Attempting to stop application with name: {} and PID: {}.".format(params["app_name"], params["app_id"]))
        return appshutdown(params)
    # Restart an app
    elif json_type == "restartapp":
        print("appshutdown Received")
        agent_logger.info("Attempting to restart application with name: {} and PID: {}.".format(params["app_name"], params["app_id"]))
        return apprestart(params)
    # Shutdown the machine
    elif json_type == "shutdownmachine":
        print("shutdownmachine Received")
        agent_logger.info("Attempting to shutdown machine {} .".format(json["machine_name"]))
        return shutdown(json)
    # Restart the machine
    elif json_type == "restartmachine":
        print("restartmachine Received")
        agent_logger.info("Attempting to restart machine {} .".format(json["machine_name"]))
        return restart(json)
    # Run commands on cmd/powershell/bash/wsl
    elif json_type == "custom_command":
        print("custom Received")
        agent_logger.info("Attempting to run the command: {} on machine: {}.".format(params["custom_command"], json["machine_name"]))
        return shellProcessor(params)
    # Ping
    elif json_type == "ping":
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
    b64file = params['b64file']
    destination = params['destination']
    file = base64.b64decode(b64file)
    outFileHandle = open(destination, "wb")
    outFileHandle.write(file)
    result = "File Written to " + destination
    agent_logger.info("File: uploaded at destination: {}.".format(destination))
    return result


#Thread function to manage shell commands
thread = None
threadOutput = ""
def thread_run_process(command, shell):
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
    thread = (threading.Thread(target = thread_run_process, args=[command, shell], daemon=True))
    thread.start()
    time.sleep(5)
    global threadOutput
    returnResult = threadOutput
    threadOutput = ""
    return returnResult
