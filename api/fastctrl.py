import traci
import traci.constants as tc
from sumo_rl.environment.traffic_signal import TrafficSignal

def initialize_sumo(cfg_file, use_gui=False):
    sumo_bin = 'sumo-gui' if use_gui else 'sumo'
    sumo_cmd = [sumo_bin, '-c', cfg_file]
    traci.start(sumo_cmd)

def subscribe_e1_e2_sensors():
    # Subscribe to E1 sensors
    for loop_id in traci.inductionloop.getIDList():
        traci.inductionloop.subscribe(loop_id, [tc.LAST_STEP_VEHICLE_NUMBER, tc.LAST_STEP_OCCUPANCY, tc.LAST_STEP_MEAN_SPEED])

    # Subscribe to E2 sensors
    for e2_id in traci.lanearea.getIDList():
        traci.lanearea.subscribe(e2_id, [tc.LAST_STEP_VEHICLE_NUMBER, tc.LAST_STEP_OCCUPANCY, tc.LAST_STEP_MEAN_SPEED])

def subscribe_traffic_lights():
    # Subscribe to traffic light phase and timing
    for tls_id in traci.trafficlight.getIDList():
        traci.trafficlight.subscribe(tls_id, [tc.TL_RED_YELLOW_GREEN_STATE, tc.TL_PHASE_DURATION, 
                                              tc.TL_CURRENT_PHASE, tc.TL_SPENT_DURATION, 
                                              tc.TL_NEXT_SWITCH, tc.TL_CURRENT_PROGRAM, 
                                              tc.TL_CONTROLLED_LANES])

def step_simulation():
    # Step forward in simulation
    traci.simulationStep()

def get_subscription_results():
    # Collect subscription results
    e1_data = {loop_id: traci.inductionloop.getSubscriptionResults(loop_id) for loop_id in traci.inductionloop.getIDList()}
    e2_data = {e2_id: traci.lanearea.getSubscriptionResults(e2_id) for e2_id in traci.lanearea.getIDList()}
    traffic_light_data = {tls_id: traci.trafficlight.getSubscriptionResults(tls_id) for tls_id in traci.trafficlight.getIDList()}

    return e1_data, e2_data, traffic_light_data

# Initialize SUMO
initialize_sumo("../escenario/osm2.sumocfg", use_gui=True)
subscribe_e1_e2_sensors()
subscribe_traffic_lights()

# Step through simulation and collect data
for _ in range(100):
    step_simulation()
    e1_data, e2_data, traffic_light_data = get_subscription_results()

    # Print the raw data structures for inspection
    print("E1 Data:", e1_data)
    print("E2 Data:", e2_data)
    print("Traffic Light Data:", traffic_light_data)

# Don't forget to close the TraCI connection when done
traci.close()
