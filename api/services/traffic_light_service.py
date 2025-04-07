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



PHASE_DIRECTIONS = {
    0: "Norte - Sur",
    2: "Este - Oeste",
    4: "Norte - Sur Diagonal",
    6: "Este - Oeste Diagonal"
}


def get_traffic_lights_data() -> Dict[str, dict]:
    tls_response = {}

    for tls_id in traci.trafficlight.getIDList():
        try:
            tls_data = traci.trafficlight.getSubscriptionResults(tls_id)
            phase_idx = tls_data.get(traci.constants.TL_CURRENT_PHASE, 0)
            if not tls_data:
                continue

            # Create TrafficLightData instance
            tl_data = TrafficLightData(
                id=tls_id,
                red_yellow_green_state=tls_data.get(traci.constants.TL_RED_YELLOW_GREEN_STATE, "unknown"),
                phase_duration=tls_data.get(traci.constants.TL_PHASE_DURATION, 0.0),
                current_phase=phase_idx,
                spent_duration=tls_data.get(traci.constants.TL_SPENT_DURATION, 0.0),
                next_switch=tls_data.get(traci.constants.TL_NEXT_SWITCH, 0.0),
                current_program=tls_data.get(traci.constants.TL_CURRENT_PROGRAM, "unknown"),
                phase_name=PHASE_DIRECTIONS.get(phase_idx, "Unknown Phase")
            )
            
            # Convert to dictionary immediately
            tls_response[tls_id] = tl_data.model_dump()
            
        except Exception as e:
            logger.error(f"Error processing traffic light {tls_id}: {str(e)}")
            continue

    return tls_response


def get_phase_info(tls_id: str) -> dict:
    program = traci.trafficlight.getAllProgramLogics(tls_id)[0]
    current_phase = traci.trafficlight.getPhase(tls_id)
    return {
        "current_phase": current_phase,
        "phase_name": PHASE_DIRECTIONS.get(current_phase, "Unknown"),
        "phase_duration": traci.trafficlight.getPhaseDuration(tls_id),
        "next_phases": [
            {
                "index": (current_phase + i) % len(program.phases),
                "name": PHASE_DIRECTIONS.get((current_phase + i) % len(program.phases), "Unknown")
            } 
            for i in range(1, 3)  # Show next 2 phases
        ]
    }