import os
import json
import base64
import subprocess

def jsonProcessor(json):
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
    os.system("shutdown /s /t 0")
    
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

def commandProcessor(params):
    print("JSON Command Processor")
    #print(commandJson)
    command = params['command']
    if command == "shutdown":
        print("Shutdown Initiated")
        return "Shutdown Initiated."
        #shutdown()
    elif command == "reset":
        print("Reset Initiated")
        return "Reset Initiated."

def shellProcessor(params):
  print("Shell command")
  #print(commandJson)
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
    return result