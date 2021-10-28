import os
import json
import base64
import subprocess
from sys import platform

from enum import Enum
import threading
import time
import psutil
class OS_TYPE(Enum):
    WINDOWS = 1
    LINUX = 2
    MAC = 3

os_type = OS_TYPE.WINDOWS

def jsonProcessor(json):
    global os_type
    if platform == "linux" or platform == "linux2":
        print("linux")
        os_type = OS_TYPE.LINUX
    elif platform == "darwin":
        print("mac")
        os_type = OS_TYPE.MAC
    elif platform == "win32":
        print("windows")
        os_type = OS_TYPE.WINDOWS
        
    json_type = json["type"]
    params = json["parameters"]
    if json_type == "fileupload":
        return fileProcessor(params)
    elif json_type == "appshutdown":
        return appshutdown(params)
    elif json_type == "apprestart":
        return apprestart(params)
    elif json_type == "command":
        return commandProcessor(params)
    elif json_type == "shell":
        return shellProcessor(params)
    
def appshutdown(params):
    pid = params['pid']
    name = params['name']
    try:
        process = psutil.Process(pid)
    except:
        return f"ID:{pid} not found"
    result = killpid(name, pid, process)
    return result

def apprestart(params):
    pid = params['pid']
    name = params['name']
    try:
        process = psutil.Process(pid)
    except:
        return f"ID:{pid} not found"
    exe_path = process.exe()
    result = killpid(name, pid, process)
    thread = (threading.Thread(target = thread_run_process, args=[exe_path, ""], daemon=True))
    thread.start()
    return result

def killpid(name, pid, process):
    result = ""
    if process != None:
        process.kill()
        result = f"Process {name} with ID:{pid} terminated successfully."
    else:
        result = f"No process with ID:{pid} found."
    return result

def shutdown():
    time.sleep(5)
    global os_type
    if os_type == OS_TYPE.WINDOWS:
        os.system("shutdown /s /t 0")
    else: #Linux and Mac
        os.system("sudo shutdown -h now")
        
def restart():
    time.sleep(5)
    global os_type
    if os_type == OS_TYPE.WINDOWS:
        os.system("shutdown /r /t 0")
    else: #Linux and Mac
        os.system("sudo shutdown -r now")

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
    return result

def commandProcessor(params, os_type):
    print("JSON Command Processor")
    command = params['command']
    if command == "shutdown":
        print("Shutdown Initiated")
        shutdown()
        return "Shutdown Initiated."
    elif command == "reset" or command == "restart":
        print("Reset Initiated")
        restart()
        return "Reset Initiated."


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
    print("Thread End")



def shellProcessor(params):
    print("Shell command")
    #print(commandJson)
    shell = "cmd"
    if "shell" in params:
        shell = params['shell']
    command = params['command']
    print("Shell Command Received")
    print(command)
    thread = (threading.Thread(target = thread_run_process, args=[command, shell], daemon=True))
    thread.start()
    time.sleep(5)
    print("Main End")
    global threadOutput
    returnResult = threadOutput
    threadOutput = ""
    return returnResult