from modules.sockets.client_socket_setup import createSockets as newCreateSockets
from modules.test.new_agent_socket_setup import createSockets, create_jobs

cmd = input("Select a module [0 or 1] > ")

if cmd == "0":
    createSockets()
    create_jobs()
elif cmd == "1":
    newCreateSockets()
    while True:
        pass
else:
    print("No command")