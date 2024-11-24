import traci


def get_vehicle_count():
    return traci.vehicle.getIDCount()


def get_average_speed():
    vehicle_ids = traci.vehicle.getIDList()
    speeds = [traci.vehicle.getSpeed(veh_id) for veh_id in vehicle_ids]
    if speeds:
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
    lanes_by_street = {
        "N": [],
        "S": [],
        "W": [],
        "E": []
    }
    
    # Get all lanes in the network
    lanes = traci.lane.getIDList()
    
    # Group lanes by street direction (N, S, W, E)
    for lane in lanes:
        if lane.startswith("N"):
            lanes_by_street["N"].append(lane)
        elif lane.startswith("S"):
            lanes_by_street["S"].append(lane)
        elif lane.startswith("W"):
            lanes_by_street["W"].append(lane)
        elif lane.startswith("E"):
            lanes_by_street["E"].append(lane)

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
            avg_speed_by_street[street] = 0  # No vehicles on this street
    
    return avg_speed_by_street