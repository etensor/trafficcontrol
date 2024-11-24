import traci 


def collect_metrics():
    vehicle_count = traci.vehicle.getIDCount()
    vehicle_speeds = [traci.vehicle.getSpeed(veh) for veh in traci.vehicle.getIDList() if traci.vehicle.getSpeed(veh) > 0]
    avg_speed = sum(vehicle_speeds) / len(vehicle_speeds) if vehicle_speeds else 0

    return {
        "vehicle_count": vehicle_count,
        "average_speed": avg_speed
    }

