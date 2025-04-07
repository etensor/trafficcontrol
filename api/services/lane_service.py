from typing import Dict, List
import traci
from pydantic import BaseModel

class LaneMetrics(BaseModel):
    queue: int
    density: float
    waiting_time: float
    vehicle_count: int

class DirectionMetrics(BaseModel):
    total_queue: int
    avg_density: float
    total_waiting: float
    total_vehicles: int
    lanes: Dict[str, LaneMetrics]

def get_lanes_by_direction() -> Dict[str, List[str]]:
    """Group lanes by their cardinal direction"""
    directions = {'N': [], 'S': [], 'E': [], 'W': []}
    for lane in traci.lane.getIDList():
        if lane.startswith('N'): directions['N'].append(lane)
        elif lane.startswith('S'): directions['S'].append(lane)
        elif lane.startswith('E'): directions['E'].append(lane)
        elif lane.startswith('W'): directions['W'].append(lane)
    return directions



def get_detailed_directional_metrics() -> Dict[str, DirectionMetrics]:
    directions = get_lanes_by_direction()
    metrics = {}
    
    for direction, lanes in directions.items():
        dir_metrics = DirectionMetrics(
            total_queue=0,
            avg_density=0,
            total_waiting=0,
            total_vehicles=0,
            lanes={}
        )
        
        total_density = 0
        for lane in lanes:
            vehicle_count = traci.lane.getLastStepVehicleNumber(lane)
            lane_length = traci.lane.getLength(lane)
            
            lane_data = LaneMetrics(
                queue=traci.lane.getLastStepHaltingNumber(lane),
                density=vehicle_count / lane_length if lane_length > 0 else 0,
                waiting_time=sum(
                    traci.vehicle.getWaitingTime(veh) 
                    for veh in traci.lane.getLastStepVehicleIDs(lane)
                ),
                vehicle_count=vehicle_count
            )
            
            dir_metrics.lanes[lane] = lane_data
            dir_metrics.total_queue += lane_data.queue
            dir_metrics.total_waiting += lane_data.waiting_time
            total_density += lane_data.density
            dir_metrics.total_vehicles += vehicle_count
        
        dir_metrics.avg_density = total_density / len(lanes) if lanes else 0
        metrics[direction] = dir_metrics
        
    return metrics



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




def get_detailed_lane_data():
    lanes = traci.lane.getIDList()
    return {
        lane_id: {
            "queue": traci.lane.getLastStepHaltingNumber(lane_id),
            "density": traci.lane.getLastStepVehicleNumber(lane_id)/traci.lane.getLength(lane_id),
            "waiting_time": sum(
                traci.vehicle.getWaitingTime(veh) 
                for veh in traci.lane.getLastStepVehicleIDs(lane_id)
            )
        }
        for lane_id in lanes
    }



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




