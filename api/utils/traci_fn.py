import traci
from sumo_rl.environment.traffic_signal import TrafficSignal
from .traci_env import initialize_traci, close_traci, sumo_cfg



# reset environment
# def custom_reset(env):
#     env.sumo = traci.start(env.sumo_cmd, label=env.label)
#     env.sumo_conn = traci.getConnection(env.label)
#     for ts in env.ts_ids:
#         env.ts[ts].reset()
#     return env._compute_observations()
def custom_reset(self):
    try:
        obs = self._compute_observations()
        if obs is None or any(x is None for x in obs):
            raise ValueError("Observation computed is None")
        return obs[self.ts_ids[0]], self._compute_info()
    except Exception as e:
        print(f"Error during reset: {e}")
        raise



# lanes
def get_len_lanes():
    return len(traci.lane.getIDList())

#cuantos detectors hay en el escenario
def get_len_detectors():
    try:
        # if not traci.isLoaded():
        #     initialize_traci(sumo_cfg['cfg_file'], sumo_cfg['net_file'], sumo_cfg['route_file'], sumo_cfg['add_file'])
        detectors = traci.inductionloop.getIDList()
        return len(detectors)
    except Exception as e:
        return str(e)
    finally:
        close_traci()


def get_detectors_by_street():
    try:
        if not traci.isLoaded():
            initialize_traci(sumo_cfg['cfg_file'], sumo_cfg['net_file'], sumo_cfg['route_file'], sumo_cfg['add_file'])
        detectors = traci.inductionloop.getIDList()
        detectors_by_street = {}
        for detector in detectors:
            street = traci.inductionloop.getLaneID(detector)
            if street not in detectors_by_street:
                detectors_by_street[street] = []
            detectors_by_street[street].append(detector)
        return detectors_by_street
    finally:
        close_traci()



def get_vehicle_count():
    return traci.vehicle.getIDCount()

def get_average_speed():
    vehicle_ids = traci.vehicle.getIDList()
    speeds = [traci.vehicle.getSpeed(veh_id) for veh_id in vehicle_ids]
    if len(speeds) > 0:
        return sum(speeds) / len(speeds)
    return 0

def get_waiting_time():
    vehicle_ids = traci.vehicle.getIDList()
    waiting_times = [traci.vehicle.getWaitingTime(veh_id) for veh_id in vehicle_ids]
    return sum(waiting_times)

def get_queue_length():
    vehicle_ids = traci.vehicle.getIDList()
    return len(vehicle_ids)


def get_lanes_by_street():
    lanes_by_street = []
    lanes = traci.lane.getIDList()
    for lane in lanes:
        street = lane.split('_')[0]  # Assuming street name is part of lane ID
        if street not in lanes_by_street:
            lanes_by_street[street] = []
        lanes_by_street[street].append(lane)
    return lanes_by_street


def get_avg_speed_by_street():
    lanes_by_street = get_lanes_by_street()
    avg_speed_by_street = {}
    
    for street, lanes in lanes_by_street.items():
        total_speed = 0
        total_vehicles = 0
        for lane in lanes:
            vehicles = traci.lane.getLastStepVehicleIDs(lane)
            total_vehicles += len(vehicles)
            for vehicle in vehicles:
                total_speed += traci.vehicle.getSpeed(vehicle)
        
        if total_vehicles > 0:
            avg_speed_by_street[street] = total_speed / total_vehicles
        else:
            avg_speed_by_street[street] = 0  # No vehicles in this street
    
    return avg_speed_by_street



## metricsenv
#     vehicle_count = traci.vehicle.getIDCount()
#     vehicle_speeds = [traci.vehicle.getSpeed(veh) for veh in traci.vehicle.getIDList() if traci.vehicle.getSpeed(veh) > 0]
#     average_speed = sum(vehicle_speeds) / len(vehicle_speeds) if vehicle_speeds else 0
#     waiting_time = sum(traci.vehicle.getWaitingTime(veh) for veh in traci.vehicle.getIDList())
#     queue_length = sum(traci.lane.getLastStepHaltingNumber(lane) for lane in traci.lane.getIDList())
#     lane_density = sum(get_lane_density(lane) for lane in traci.lane.getIDList())
#     lane_queue_length = sum(get_lane_queue_length(lane) for lane in traci.lane.getIDList())

#     return {
#         "vehicle_count": vehicle_count,
#         "average_speed": average_speed,
#         "waiting_time": waiting_time,
#         "queue_length": queue_length,
#         "lane_density": lane_density,
#         "lane_queue_length": lane_queue_length
#     }

def collect_metrics(env):
    #queued = sum([traci.lane.getLastStepHaltingNumber(lane) for lane in env.lanes])
    #avg_speed = sum([traci.lane.getLastStepMeanSpeed(lane) for lane in env.lanes]) / len(env.lanes)
    vehicle_count = traci.vehicle.getIDCount()  
    vehicle_speeds = [traci.vehicle.getSpeed(veh) for veh in traci.vehicle.getIDList() if traci.vehicle.getSpeed(veh) > 0]
    avg_speed = sum(vehicle_speeds) / len(vehicle_speeds) if vehicle_speeds else 0
    return {'Vehicle Count': vehicle_count, 'Average Speed': avg_speed}
    #return {'Queue Length': queued, 'Average Speed': avg_speed}



def get_lane_density(lane_id):
    lane_length = traci.lane.getLength(lane_id)
    lane_vehicles = traci.lane.getLastStepVehicleNumber(lane_id)
    return lane_vehicles / lane_length if lane_length > 0 else 0

def get_lane_queue_length(lane_id):
    return traci.lane.getLastStepHaltingNumber(lane_id)