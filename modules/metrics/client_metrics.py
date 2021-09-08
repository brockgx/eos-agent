import threading
import time
import socket
import json
import psutil

list_current_processes = []
list_current_processes_sorted = []
system_metrics = None
disk_metrics_list = []
#disk_metrics = None

class application:
    def __init__(self, name, cpu, ram):
        self.name = name
        self.cpu = cpu
        self.ram = ram
    def to_dict(self):
        return {"name": self.name, "cpu": self.cpu, "ram": self.ram}

class system:
    def __init__(self, cpu, ram):
        self.cpu = cpu
        self.ram = ram
        

class disk:
    def __init__(self, device, mountpoint, percent):
        self.device = device
        self.mountpoint = mountpoint
        self.percent = percent
    def to_dict(self):
        return {"device": self.device, "mountpoint": self.mountpoint, "percent": self.percent}

def get_list_of_processes(list_processes):
    process_iter = psutil.process_iter()
    cpu_count = psutil.cpu_count()
    for proc in process_iter:
        try:
            exe_path = proc.exe()
            process_name = proc.name()
            if process_name != "":
                list_processes.append(application(process_name, round(proc.cpu_percent()/cpu_count,2), round(proc.memory_percent(),2)))

            
        #print(process_name , ' ::: ', processID)
        except psutil.Error:
            pass



def thread_application_metrics():
    global list_current_processes
    global list_current_processes_sorted
    while(True):
        list_current_processes.clear()
        get_list_of_processes(list_current_processes)
        list_current_processes.sort(key=lambda x: x.cpu, reverse=True)
        list_current_processes_sorted.clear()
        list_current_processes_sorted = list_current_processes.copy()
        time.sleep(5)

def thread_system_metrics():
    global system_metrics
    global disk_metrics_list
    while(True):
        disk_metrics_list.clear()
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                #print(partition)
                if partition.opts != "cdrom":
                    disk_metrics_list.append(disk(partition.device, partition.mountpoint, psutil.disk_usage(partition.mountpoint).percent))
            except:
                print("Error with disk ", end="")
                print(partition.mountpoint)
        system_metrics = system(psutil.cpu_percent(), psutil.virtual_memory().percent)
        time.sleep(5)
        
def thread_json():
    time.sleep(5)
    while(True):
        print(get_json())
        time.sleep(5)


from datetime import datetime

def get_json():
    now = datetime.now()
    app_metrics = []
    disk_metrics = []
    rangeCount = len(list_current_processes_sorted)
    max = 10
    if rangeCount > max:
        rangeCount = 10
    for i in range(rangeCount):
        app_metrics.append(list_current_processes_sorted[i].to_dict())
    for i in range(len(disk_metrics_list)):
        disk_metrics.append(disk_metrics_list[i].to_dict())
    x = {
        "machine_name": socket.gethostname(),
        "collection_time": now.strftime("%m/%d/%Y, %H:%M:%S"),
        "app_metrics": app_metrics,
        "system_metrics": [{"cpu":system_metrics.cpu}, {"ram":system_metrics.ram}],
        "disk_metrics": disk_metrics
    }
    return json.dumps(x)

def start_agent():
    application_thread = threading.Thread(target = thread_application_metrics)
    if not application_thread.is_alive():
        application_thread.start()
    system_thread = threading.Thread(target = thread_system_metrics)
    if not system_thread.is_alive():
        system_thread.start()


def main():
    #partitions = psutil.disk_partitions()
    #for partition in partitions:
    #    print(partition)
    #print(partitions)
    start_agent()
    json_thread = threading.Thread(target = thread_json)
    if not json_thread.is_alive():
        json_thread.start()

if __name__ == "__main__":
    main()