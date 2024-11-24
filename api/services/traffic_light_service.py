import traci
import traci.constants

from schemas.models import TrafficLightData

def subscribe_traffic_lights():

    for tls_id in traci.trafficlight.getIDList():
        traci.trafficlight.subscribe(
            tls_id,
            [traci.constants.TL_CURRENT_PHASE,
             traci.constants.TL_RED_YELLOW_GREEN_STATE,
             traci.constants.TL_PHASE_DURATION,          
             traci.constants.TL_SPENT_DURATION,
             traci.constants.TL_NEXT_SWITCH,
             traci.constants.TL_CURRENT_PROGRAM,
             traci.constants.TL_CONTROLLED_LANES
            ]
        )



def get_traffic_lights_data():
    tls_data = {}
    tls_response = {}

    for tls_id in traci.trafficlight.getIDList():
        tls_data[tls_id] = traci.trafficlight.getSubscriptionResults(tls_id)

        tls_response[tls_id] = TrafficLightData(
            id=tls_id,
            red_yellow_green_state=tls_data[tls_id][traci.constants.TL_RED_YELLOW_GREEN_STATE],
            phase_duration=tls_data[tls_id][traci.constants.TL_PHASE_DURATION],
            current_phase=tls_data[tls_id][traci.constants.TL_CURRENT_PHASE],
            spent_duration=tls_data[tls_id][traci.constants.TL_SPENT_DURATION],
            next_switch=tls_data[tls_id][traci.constants.TL_NEXT_SWITCH],
            current_program=tls_data[tls_id][traci.constants.TL_CURRENT_PROGRAM],
            #controlled_lanes=tls_data[tls_id][traci.constants.TL_CONTROLLED_LANES]
        )

    return tls_response