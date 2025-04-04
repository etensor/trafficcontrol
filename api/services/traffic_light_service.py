from typing import Dict
import traci
import traci.constants

from api.utils import logger
from schemas.models import TrafficLightData

def subscribe_traffic_lights():
    try:
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
    except Exception as e:
        print(f"Error subscribing to traffic lights: {e}")




def get_traffic_lights_data() -> Dict[str, dict]:
    tls_response = {}

    for tls_id in traci.trafficlight.getIDList():
        try:
            tls_data = traci.trafficlight.getSubscriptionResults(tls_id)
            if not tls_data:
                continue

            # Create TrafficLightData instance
            tl_data = TrafficLightData(
                id=tls_id,
                red_yellow_green_state=tls_data.get(traci.constants.TL_RED_YELLOW_GREEN_STATE, "unknown"),
                phase_duration=tls_data.get(traci.constants.TL_PHASE_DURATION, 0.0),
                current_phase=tls_data.get(traci.constants.TL_CURRENT_PHASE, -1),
                spent_duration=tls_data.get(traci.constants.TL_SPENT_DURATION, 0.0),
                next_switch=tls_data.get(traci.constants.TL_NEXT_SWITCH, 0.0),
                current_program=tls_data.get(traci.constants.TL_CURRENT_PROGRAM, "unknown")
            )
            
            # Convert to dictionary immediately
            tls_response[tls_id] = tl_data.model_dump()
            
        except Exception as e:
            logger.error(f"Error processing traffic light {tls_id}: {str(e)}")
            continue

    return tls_response