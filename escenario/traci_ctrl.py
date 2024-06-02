import traci
import os
import sys

os.environ['SUMO_HOME'] = '/usr/share/sumo'
os.environ['LIBSUMO_AS_TRACI'] = '1'

sumocfg = {
    "use_gui" : True,
    "cfg" : "./osm2.sumocfg"
}

def close_traci():
    if traci.isLoaded():        
        traci.close()

if "SUDO_HOME" in os.environ:
    sys.path.append(os.path.join(os.environ["SUDO_HOME"], 'tools'))

sumo_cmd = 'sumo-gui' if sumocfg["use_gui"] else 'sumo'
sumo_cmd = [sumo_cmd, '-c', sumocfg["cfg"]]
traci.start(sumo_cmd)


