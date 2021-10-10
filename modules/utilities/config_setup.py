#Import third party libraries
from configparser import ConfigParser

## Functions ##
#Function: Read and save the details from the config file
#Params:
#   - file_path: the location of the config file
#Returned:
#   - Dict object of the config details
def retreive_config_details(file_path):
  config = ConfigParser()
  config.read(file_path)

  required_properties = ["SERVER_ADDRESS", "SERVER_PORT", "HTTPS_ENABLED", "MAIN_PORT", "SECONDARY_PORT"]
  details = {**config['server-details'], **config['socket-details']}
  try:
    for key in details:
      if key.upper() not in required_properties:
        raise ValueError("Invalid property " + key.upper() + " in config file (" + str(file_path) + ")", ",".join(required_properties))
  except ValueError as err:
    print_log_msg(str(err.args[0]))
    print_log_msg("Looking for properties: " + str(err.args[1:]))
    sys.exit(1)
  return {
      "server_ip": details["server_address"],
      "server_port": int(details["server_port"]),
      "server_https_enabled": details["https_enabled"],
      "socket_mport": int(details["main_port"]),
      "socket_sport": int(details["secondary_port"]),
    }