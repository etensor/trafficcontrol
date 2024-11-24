import traci

def get_len_lanes():
    return len(traci.len.getIDList())


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

        avg_speed_by_street[street] = total_speed / total_vehicles if total_vehicles > 0 else 0



def get_lane_density(laneid):
    lane_length = traci.lane.getLength(laneid)
    lane_vehicles = traci.lane.getLastStepVehicleNumber(laneid)
    return lane_vehicles / lane_length if lane_length > 0 else 0


def get_lane_queue_length(laneid):
    return traci.lane.getLastStepHaltingNumber(laneid) # number of vehicles in the lane that are not moving




