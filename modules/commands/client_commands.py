import os
import json
import base64
import subprocess
from sys import platform

from enum import Enum
import threading
import time
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
        
    type = json["type"]
    params = json["parameters"]
    if json["type"] == "fileupload":
        return fileProcessor(params)
    elif json["type"] == "appshutdown":
        return "killapp"
    elif json["type"] == "command":
        return commandProcessor(params)
    elif json["type"] == "shell":
        return shellProcessor(params)

def shutdown():
    global os_type
    if os_type == OS_TYPE.WINDOWS:
        os.system("shutdown /s /t 0")
    else: #Linux and Mac
        os.system("shutdown now -h")
    
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
    #print(commandJson)
    command = params['command']
    # App kill
    # App shutdown
    if command == "shutdown":
        print("Shutdown Initiated")
        shutdown()
        return "Shutdown Initiated."
    elif command == "reset":
        print("Reset Initiated")
        return "Reset Initiated."


thread = None
threadOutput = ""
def thread_run_process(command, shell):
    print("Shell Type:")
    print(shell)
    ps_command = command
    global os_type
    if os_type == OS_TYPE.WINDOWS:
        #if shell == "cmd":
            #ps_command = ["powershell","-Command"]
            #ps_command.extend(command.split())
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
    #left = ""
    #right = ""
    #if ' ' in command:
    #    pos = command.find(' ')+1
    #    left, right = command[:pos-1], command[pos:]
    #else:
    #    left = command
    #print("left")
    #print(left)
    #print("right")
    #print(right)
    #print("[left, right]")
    #print([left, right])
    #result = subprocess.run(["powershell", left, right], stdout=subprocess.PIPE, shell=True).stdout.decode('utf-8')

    thread = (threading.Thread(target = thread_run_process, args=[command, shell], daemon=True))
    thread.start()
    #for i in range(len(threads)):
        #threads[i].daemon = True
        #threads[i].start()
    time.sleep(5)
    #threads.remove(0)
    print("Main End")
    global threadOutput
    returnResult = threadOutput
    threadOutput = ""
    return returnResult
    #print(result)
    #return result