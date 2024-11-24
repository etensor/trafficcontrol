import traci

from schemas.models import InductionLoopData, LaneAreaData


def subscribe_e1_sensors():
    try:
        for loop_id in traci.inductionloop.getIDList():
            traci.inductionloop.subscribe(
                loop_id, 
                [traci.constants.LAST_STEP_VEHICLE_NUMBER, 
                 traci.constants.LAST_STEP_OCCUPANCY,
                 traci.constants.LAST_STEP_MEAN_SPEED]
            )
    except Exception as e:
        print(f"Error subscribing to E1 sensors: {e}")



def subscribe_e2_sensors():
    try:
        for e2id in traci.lanearea.getIDList():
            traci.lanearea.subscribe(e2id,
            [
                traci.constants.LAST_STEP_VEHICLE_NUMBER,
                traci.constants.LAST_STEP_MEAN_SPEED,
                traci.constants.LAST_STEP_OCCUPANCY
            ])
    except Exception as e:
        print(f"Error subscribing to E2 sensors: {e}")



def get_e1_sensors_data():
    e1dict = {}
    for e1_id in traci.inductionloop.getIDList():
        results = traci.inductionloop.getSubscriptionResults(e1_id)
        if results:
            e1dict[e1_id] = InductionLoopData(
                id = e1_id,
                vehicle_count = results[traci.constants.LAST_STEP_VEHICLE_NUMBER],
                occupancy = results[traci.constants.LAST_STEP_OCCUPANCY],
                mean_speed = results[traci.constants.LAST_STEP_MEAN_SPEED]
            )
        else:
            print(f"No subscription result for E1_{e1_id}")

    return e1dict



def get_e2_sensors_data():
    e2dict = {}
    for e2_id in traci.lanearea.getIDList():
        results = traci.lanearea.getSubscriptionResults(e2_id)
        if results:
            e2dict[e2_id] = LaneAreaData(
                id = e2_id,
                vehicle_count = results[traci.constants.LAST_STEP_VEHICLE_NUMBER],
                occupancy = results[traci.constants.LAST_STEP_OCCUPANCY],
                mean_speed = results[traci.constants.LAST_STEP_MEAN_SPEED]
            )
        else: print(f"No subscription result for E2_{e2_id}")

    return e2dict



def aggregate_e2_sensor_data_per_edge():
    edge_data = {}

    edges = {
        'W': ['E2_W0', 'E2_W1', 'E2_W2'],
        'E': ['E2_E0', 'E2_E1', 'E2_E2'],
        'N': ['E2_N0', 'E2_N1', 'E2_N2'],
        'S': ['E2_S0', 'E2_S1', 'E2_S2']
    }

    for edge, lanes in edges.items():
        total_vehicles = 0
        total_speed = 0
        total_occupancy = 0
        lane_count = len(lanes)

        for lane in lanes:
            sensor_data = traci.lanearea.getSubscriptionResults(lane)
            if sensor_data:
                total_vehicles += sensor_data[traci.constants.LAST_STEP_VEHICLE_NUMBER]
                total_speed += sensor_data[traci.constants.LAST_STEP_MEAN_SPEED]
                total_occupancy += sensor_data[traci.constants.LAST_STEP_OCCUPANCY]

        if lane_count > 0:
            edge_data[edge] = {
                "edge_id": edge,
                "vehicle_count": total_vehicles,
                "mean_speed": total_speed / lane_count if lane_count else 0,
                "occupancy": total_occupancy / lane_count if lane_count else 0
            }
    return edge_data