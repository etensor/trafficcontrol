from pydantic import BaseModel
from typing import List, Dict, Optional


class TrafficLightData(BaseModel):
    id: str
    current_phase: int
    time_remaining: float


## A dict will have to suffice nicely?...
# class LaneData(BaseModel):
#     id: str
#     name: Optional[str]
#     vehicles_count: int
#     avg_speed: float


class SensorData(BaseModel):
    id: str
    vehicle_count: Optional[int]
    occupancy: float
    mean_speed: float


# ws 
class WebSocketResponse(BaseModel):
    #traffic_lights: Dict[str,TrafficLightData]
    #lanes: Dict[str, Dict[str, List[str]]]
    #sensors: Dict[str,SensorData]
    timestamp: float
    traffic_lights: Dict[str,TrafficLightData]
    lanes: Dict[str, List[str]]
    sensors: Optional[Dict[str,Dict[str,str]]]
