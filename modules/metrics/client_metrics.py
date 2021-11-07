#Import third party modules
import threading, time, json, psutil
from getmac import get_mac_address

list_current_processes = []
list_current_processes_sorted = []
system_metrics = None
network_percent = 0.0
network_string = ""
disk_bytes_write = 0.0
disk_write_string = ""
disk_bytes_read = 0.0
disk_read_string = ""
disk_metrics_list = []


# Application class
# This handles the data for individual applications
# Pid, Name, CPU, RAM
class application:
    def __init__(self, pid, name, cpu, ram):
        self.pid = pid
        self.name = name
        self.cpu = cpu
        self.ram = ram
    def to_dict(self):
        return {"pid": self.pid, "name": self.name, "cpu": self.cpu, "ram": self.ram}

# System class
# This handles the data for the system
# CPU, RAM
class system:
    def __init__(self, cpu, ram):
        self.cpu = cpu
        self.ram = ram
        

# Disk class
# This handles the data for the disks
# Device, Mountpoint, Percent
class disk:
    def __init__(self, device, mountpoint, percent):
        self.device = device
        self.mountpoint = mountpoint
        self.percent = percent
    def to_dict(self):
        return {"device": self.device, "mountpoint": self.mountpoint, "percent": self.percent}


# Function to check for all processes and return in a python list
def get_list_of_processes(list_processes):
    process_iter = psutil.process_iter()
    cpu_count = psutil.cpu_count()
    for proc in process_iter:
        try:
            exe_path = proc.exe()
            process_name = proc.name()
            process_pid = proc.pid
            if process_name != "":
                list_processes.append(application(process_pid, process_name, round(proc.cpu_percent()/cpu_count,2), round(proc.memory_percent(),2)))

            
        except psutil.Error:
            pass

# Thread to handle gathering of application metrics
def thread_application_metrics():
    global list_current_processes
    global list_current_processes_sorted
    while(True):
        # Clear the list
        list_current_processes.clear()
        # Get list of processes
        get_list_of_processes(list_current_processes)
        # Sort list by cpu
        list_current_processes.sort(key=lambda x: x.cpu, reverse=True)
        # Clear global sorted list
        list_current_processes_sorted.clear()
        # return sorted list
        list_current_processes_sorted = list_current_processes.copy()
        time.sleep(5)

# Thread to handle system/disk metrics
def thread_system_metrics():
    global system_metrics
    global disk_metrics_list
    while(True):
        disk_metrics_list.clear()
        # Get partitions
        partitions = psutil.disk_partitions()
        # For each parition
        for partition in partitions:
            try:
                # If not cd rom
                if partition.opts != "cdrom":
                    # add disk to list
                    disk_metrics_list.append(disk(partition.device, partition.mountpoint, psutil.disk_usage(partition.mountpoint).percent))
            except:
                print("Error with disk ", end="")
                print(partition.mountpoint)
        # get system metrics and place in object
        system_metrics = system(psutil.cpu_percent(), psutil.virtual_memory().percent)
        time.sleep(5)

# Thread for gathering network metrics
def thread_network_metrics():
    global network_percent
    global network_string
    while True:
        # Get current network usage
        new_value = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv

        # dont return until new value gathered
        if network_percent:
            # get network string
            network_string = ("%0.2f" % convert_to_gbit(new_value - network_percent))

        # set percent to old value
        network_percent = new_value

        time.sleep(1)

# Thread for disk metrics
def thread_disk_metrics():
    global disk_bytes_write
    global disk_write_string
    global disk_bytes_read
    global disk_read_string
    while True:
        # Get disk write/read byte count
        write_bytes = psutil.disk_io_counters().write_bytes
        read_bytes = psutil.disk_io_counters().read_bytes

        # if bytes written
        if disk_bytes_write:
            # return disk write
            disk_write_string = ("%d" % (write_bytes - disk_bytes_write))
        
        if disk_bytes_read:
            # return disk read
            disk_read_string = ("%d" % (read_bytes - disk_bytes_read))

        # save value for next read
        disk_bytes_write = write_bytes
        disk_bytes_read = read_bytes

        time.sleep(5)

# Convert bits to gigabits
def convert_to_gbit(value):
    return value/1024./1024./1024.*8

# Test function for json output
#def thread_json():
#    time.sleep(5)
#    while(True):
#        print(get_json())
#        time.sleep(5)


from datetime import datetime

# Gets the data and saves into a json format to return to the server
def get_json():
    now = datetime.timestamp(datetime.now())
    app_metrics = []
    disk_metrics = []
    rangeCount = len(list_current_processes_sorted)
    #Used to limit the applicatin entries returned
    #max = 10
    #if rangeCount > max:
    #    rangeCount = 10
    for i in range(rangeCount):
        app_metrics.append(list_current_processes_sorted[i].to_dict())
    for i in range(len(disk_metrics_list)):
        disk_metrics.append(disk_metrics_list[i].to_dict())
    x = {
        "machine": get_mac_address(),
        "timestamp": now,
        "app_metrics": app_metrics,
        "system_metrics": {
            "cpu":system_metrics.cpu,
            "ram":system_metrics.ram,
            "disk_metrics": disk_metrics,
            "disk_bytes_written": disk_write_string,
            "disk_bytes_read": disk_read_string,
            "network_percent": network_string
        }
    }
    return json.dumps(x)

# Start agent
def start_agent():
    # Start application metrics thread
    application_thread = threading.Thread(target = thread_application_metrics)
    if not application_thread.is_alive():
        application_thread.start()
    # Start system metrics thread
    system_thread = threading.Thread(target = thread_system_metrics)
    if not system_thread.is_alive():
        system_thread.start()
    # Start network metrics thread
    network_thread = threading.Thread(target = thread_network_metrics)
    if not network_thread.is_alive():
        network_thread.start()
    # Start disk metrics thread
    disk_thread = threading.Thread(target = thread_disk_metrics)
    if not disk_thread.is_alive():
        disk_thread.start()


def main():
    # Start agent
    start_agent()
    # Create thread for 
    #json_thread = threading.Thread(target = thread_json)
    #if not json_thread.is_alive():
    #    json_thread.start()

if __name__ == "__main__":
    main()