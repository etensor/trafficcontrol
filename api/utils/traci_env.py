import sys
import os
import subprocess
import json
import traci

from services.sensors_service import subscribe_e1_sensors, subscribe_e2_sensors
from services.traffic_light_service import subscribe_traffic_lights


sumo_cfg = json.load(open('./api/sumo_config.json'))

# SUMO_HOME must exist as env var 
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("Declare env variable SUDO_HOME in .env or system variable")


def is_traci_loaded():
    return traci.isLoaded()

def simulationStep():
    traci.simulationStep()

def set_simulation_time_step(step_length: float = 16.6): # en ms
    traci.simulation.setDeltaT(step_length)


def initialize_traci(
        cfg_file : str = sumo_cfg['cfg_file'],
        #net_file : str = sumo_cfg['net_file'],
        #route_file : str = sumo_cfg['route_file'],  
        #add_file : None | str = sumo_cfg['add_file'],
        use_gui : bool = sumo_cfg['use_gui'],
        port : int = sumo_cfg['port'],
        step_length : float = None): # seconds
    
    sumo_bin = 'sumo-gui' if use_gui else 'sumo'

    #sumo_cmd = [sumo_bin, '-c', cfg_file, '-n', net_file, '-r', route_file]
    #if add_file:
    #    sumo_cmd.extend(['-a', add_file])
    sumo_cmd = [sumo_bin, '-c', cfg_file, '--remote-port', str(port)]
    if step_length > 0 and step_length <= 1:
        sumo_cmd.extend(['--step-length', str(step_length)])

    process = subprocess.Popen(sumo_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #traci.start(sumo_cmd)
    
    # init traci conn
    traci.init(port=port)


    # Subscribe to sumo tcp streams
    subscribe_e1_sensors()
    subscribe_e2_sensors()
    subscribe_traffic_lights()

    return process # -> pid -> app.state.sumo_pid



def try_reconnect_sumo():
    if not traci.isLoaded():
        # Attempt to reconnect to SUMO on the default port or another port used in your setup
        try:
            traci.init(port=8813)  # Example port, adjust if necessary
            print("Reconnected to SUMO instance.")
        except Exception as e:
            print(f"Failed to reconnect to SUMO: {e}")
            return False
    return True



def close_traci():
    if traci.isLoaded():
    #.getConnection("default")
        traci.close()



