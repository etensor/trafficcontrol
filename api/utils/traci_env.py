import asyncio
import sys
import os
import subprocess
import json
from typing import Dict, List
import traci

from pathlib import Path

# Get the directory of this file
current_dir = Path(__file__).parent.parent

# Load config relative to this file's location
sumo_cfg_path = current_dir / "sumo_config.json"
sumo_cfg = json.loads(sumo_cfg_path.read_text())


from services.sensors_service import subscribe_e1_sensors, subscribe_e2_sensors
from services.traffic_light_service import subscribe_traffic_lights

from .traci_subscriptions import subscription_manager

#sumo_cfg = json.load(open('./sumo_config.json'))

# SUMO_HOME must exist as env var  # this refers to the sumo project repo(?)
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



async def initialize_traci(
    use_gui: bool = False,
    step_length: float = 1.0,
    autostart: bool = True,
    gui_delay: int = 20,
    num_steps: int = 0
) -> asyncio.subprocess.Process:
# -> subprocess.Popen:
    """Initialize SUMO simulation with TraCI connection
    
    Args:
        use_gui: Launch SUMO with graphical interface
        step_length: Simulation time step in seconds
        autostart: Auto-begin simulation (GUI only)
        gui_delay: Visualization delay per step in ms
        num_steps: Immediate steps to execute (headless only)
    """

    if traci.isLoaded():
        print("SUMO is already running")
        return

    # Base command
    sumo_bin = 'sumo-gui' if use_gui else 'sumo'
    cmd = [
        sumo_bin,
        '-c', sumo_cfg['cfg_file'],
        '--remote-port', str(sumo_cfg['port']),
        '--step-length', str(step_length)
    ]

    # GUI-specific parameters
    if use_gui:
        if autostart:
            cmd.append('--start')
        cmd.extend(['--delay', str(gui_delay)])
    
    # Start process
    #process = subprocess.Popen(cmd)
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    #traci.init(sumo_cfg['port'])
    for _ in range(3):
        try:
            traci.init(sumo_cfg['port'])
            # Init subscriptions (traci)
            subscription_manager.subscribe_all()
            return proc
        except traci.FatalTraCIError:
            await asyncio.sleep(0.5)

    # sensor_map = {
    #     'e1': _map_sensors(traci.inductionloop.getIDList(), 'E1'),
    #     'e2': _map_sensors(traci.lanearea.getIDList(), 'E2')
    # }
    
    # # Subscribe to data streams
    # subscribe_e1_sensors(sensor_map['e1'])
    # subscribe_e2_sensors(sensor_map['e2'])
    # subscribe_traffic_lights()

    raise ConnectionError("Failed to connect to SUMO")



def _map_sensors(sensor_ids: List[str], sensor_type: str) -> Dict[str, dict]:
    """Create human-readable sensor mapping"""
    mapping = {}
    for sid in sensor_ids:
        parts = sid.split('_')
        if len(parts) >= 3:
            # Assumes format: E2_E0, E2_N1, etc.
            direction = parts[1][0]  # E, W, N, S
            lane_number = parts[1][1:] or parts[-1]
            readable_name = f"{direction}-{lane_number}"
        else:
            readable_name = sid
            
        mapping[sid] = {
            'id': sid,
            'type': sensor_type,
            'direction': direction if len(parts) >=3 else 'unknown',
            'lane': lane_number if len(parts) >=3 else 'unknown',
            'readable_name': readable_name
        }
    return mapping



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



