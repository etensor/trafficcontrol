import datetime
import numpy as np
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Optional

class TrafficLightData(BaseModel):
    id: str
    current_phase: str | int | None = None# Phase -> "rrrGGGrrrGGG" | len(phase) R uniq(states)
    red_yellow_green_state: str
    phase_duration: Optional[float] = None  # Time remaining in the current phase
    spent_duration: Optional[float] = None  # Time spent in current phase
    next_switch: Optional[float] = None  # Time for the next switch
    current_program: Optional[str] = None  # Current traffic light program
    #controlled_lanes: Optional[List[str]] = []  # Lanes c


class TrafficLightsSubscritionData(BaseModel):
    traffic_lights: Dict[str, TrafficLightData]



class LaneData(BaseModel):
    id: str
    density: float #lane density
    queue: float #lane queue
    waiting_time: float # accumulated per lane



## Aggregated
class EdgeSensorData(BaseModel):
    edge_id: str # -> W, E, N, S
    vehicle_count: int # total vehicles in the edge
    mean_speed: float # mean speed of vehicles accross all lanes
    occupancy: float # mean occupancy


class EdgeData(BaseModel):
    incoming_lanes: Dict[str, LaneData]
    outgoing_lanes: Dict[str, LaneData]


class LaneSubscriptionData(BaseModel):
    edges: Dict[str, LaneData]




class InductionLoopData(BaseModel):
    id: str
    vehicle_count: int # 16
    occupancy: float # 19
    mean_speed: float # 17  <- fields


class LaneAreaData(BaseModel):
    id: str
    vehicle_count: int
    occupancy: float
    mean_speed: float # mismo orden 16,19,17



class SensorSubscriptionData(BaseModel):
    e1_sensors: Dict[str, InductionLoopData]
    e2_sensors: Dict[str, LaneAreaData]
    e2_aggregated: Dict[str, EdgeSensorData]


## context subscription
#vehicle subscription

class VehicleData(BaseModel):
    id: str
    speed: float
    position: float # relative to lane
    lane: str # lane id where the vehicle is on


class VehicleContextSubscriptionData(BaseModel):
    vehicles: Dict[str, VehicleData]




# ws 
class WebSocketResponse(BaseModel):
    traffic_lights: Optional[Dict[str, dict]] = None
    
    # Add Pydantic config for JSON serialization
    model_config = ConfigDict(
        json_encoders={
            np.ndarray: lambda v: v.tolist(),
            datetime.datetime: lambda v: v.isoformat()
        }
    )

    lanes: Optional[Dict[str, List[str]]] = None
    e1_sensors: Optional[Dict[str, InductionLoopData]] = None
    e2_sensors: Optional[Dict[str, LaneAreaData]] = None
    e2_aggregated: Optional[Dict[str, EdgeSensorData]] = None
    vehicles: int
    timestamp: float
    observation: Optional[Dict] = None
    message: Optional[str] = None



# config
class SimulationStartConfig(BaseModel):
    gui_mode: bool = Field(False, description="Launch SUMO with GUI visualization")
    step_length: float = Field(1.0, gt=1, le=500, 
                            description="Simulation step length in seconds (1-500)") # unsure of this
    training_mode: bool = Field(False, description="Initialize RL training environment")

class SimulationRunConfig(BaseModel):
    timestep: float = Field(16.7, gt=5, le=5000.0, 
                          description="Time between steps in milliseconds (5-5000)") # of this too


