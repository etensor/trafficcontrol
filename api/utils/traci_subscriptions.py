from typing import Dict, List
import traci

class SubscriptionManager:
    def __init__(self):
        self._subscribed = False
        
    def subscribe_all(self):
        """Initialize all TraCI subscriptions"""
        if self._subscribed:
            return

        self._subscribed = True
            
        # Traffic Lights
        for tls_id in traci.trafficlight.getIDList():
            traci.trafficlight.subscribe(
                tls_id,
                [
                    traci.constants.TL_RED_YELLOW_GREEN_STATE,
                    traci.constants.TL_PHASE_DURATION,
                    traci.constants.TL_CURRENT_PHASE,
                    traci.constants.TL_NEXT_SWITCH
                ]
            )
        
        # Induction Loops (E1)
        for loop_id in traci.inductionloop.getIDList():
            traci.inductionloop.subscribe(
                loop_id,
                [
                    traci.constants.LAST_STEP_VEHICLE_NUMBER,
                    traci.constants.LAST_STEP_OCCUPANCY,
                    traci.constants.LAST_STEP_MEAN_SPEED
                ]
            )
            
        # Lane Area Detectors (E2)
        for area_id in traci.lanearea.getIDList():
            traci.lanearea.subscribe(
                area_id,
                [
                    traci.constants.LAST_STEP_VEHICLE_NUMBER,
                    traci.constants.LAST_STEP_OCCUPANCY,
                    traci.constants.LAST_STEP_MEAN_SPEED
                ]
            )
            
        


subscription_manager = SubscriptionManager()