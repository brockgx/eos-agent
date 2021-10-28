import subprocess
from sys import stdout
import sys
import threading
import time

def thread_run_process(string):
    #command = ["powershell"].append(string.split())
    #result = subprocess.run(command, stdout=subprocess.PIPE, shell=True)
    result = subprocess.run("notepad", stdout=subprocess.PIPE, shell=True)
    print(result.stdout.decode('ascii'))
    print("Thread End")


threads = []
def main():
    threads.append(threading.Thread(target = thread_run_process, args=["hello"]))
    threads.append(threading.Thread(target = thread_run_process, args=["hello"]))
    threads.append(threading.Thread(target = thread_run_process, args=["hello"]))
    threads.append(threading.Thread(target = thread_run_process, args=["hello"]))
    threads.append(threading.Thread(target = thread_run_process, args=["hello"]))
    for i in range(len(threads)):
        threads[i].daemon = True
        threads[i].start()
    time.sleep(2)
    print("Main End")
    #result = subprocess.run("notepad", capture_output=True, shell=True).stdout.decode('utf-8')

    #result = subprocess.run(["powershell","dir",""], stdout=subprocess.PIPE, shell=True)
    
    #print(result.stdout.decode('ascii'))
    #print(result.stdout)
    #print(result)

main()