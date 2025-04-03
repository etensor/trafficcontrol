import gymnasium as gym
from gymnasium import spaces
import numpy as np
import traci
from .rewards import reward_minimize_waiting_time, reward_minimize_queue_length, reward_maximize_speed, reward_composite


class TrafficControlEnv(gym.Env):
    lanes_by_street = {
            "E": ["E_0", "E_1", "E_2"],
            "N": ["N_0", "N_1", "N_2"],
            "S": ["S_0", "S_1", "S_2"],
            "W": ["W_0", "W_1", "W_2"]
        }
    
    def __init__(self, sumo_cfg="escenario/osm2.sumocfg", reward_fn = reward_minimize_waiting_time):
        super(TrafficControlEnv, self).__init__()
        
        self.phases = [
            "N+S",
            "E+W",
            "N",
            "E",
            "S",
            "W"
        ]

        self.reward_function = reward_fn
        self.sumo_cfg = sumo_cfg
        


        # let traci not fail
        if not traci.isLoaded():
            traci.start(["sumo", "-c", self.sumo_cfg])

        
        # Initialize e1 and e2 sensors (these represent the induction loops and lane area detectors)
        self.e1_sensors = traci.inductionloop.getIDList()  # All E1 induction loop sensors
        self.e2_sensors = traci.lanearea.getIDList()  # All E2 lane area detectors

        # Observation Space
        self.observation_space = spaces.Dict({
            "traffic_lights": spaces.Dict({
                "phase": spaces.Discrete(len(self.phases)),
                "duration": spaces.Box(low=0, high=100, shape=(1,))
            }),
            "lanes": spaces.Dict({
                "queue_length": spaces.Box(low=0, high=50, shape=(len(self.lanes_by_street) * 3,)),
                "waiting_time": spaces.Box(low=0, high=1, shape=(len(self.lanes_by_street) * 3,))
            }),
            "sensors": spaces.Dict({
                "e1": spaces.Box(low=0, high=1, shape=(len(self.e1_sensors),)),
                "e2": spaces.Box(low=0, high=1, shape=(len(self.e2_sensors),))
            })
        })


        # Action Space -> 3 actions per TLS
        #       #spaces.Discrete(3)
        self.action_space = spaces.Tuple((
            spaces.Discrete(len(self.phases)),        # Phase index
            spaces.Discrete(5)  # E.g., -2, -1, 0, +1, +2 for duration change
        ))
        
        # = spaces.Dict({
        #     "tls_0": spaces.Discrete(3),
        #     "tls_1": spaces.Discrete(3),
        #     "tls_2": spaces.Discrete(3),
        #     "tls_3": spaces.Discrete(3)
        # })

    def reset(self):
        # if traci.isLoaded():
        #     traci.close()  # Close existing connection
        # traci.start(["sumo", "-c", self.sumo_cfg])
        # traci.simulationStep()
        obs = self.get_observation()
        return obs
    

    def get_observation(self):
        # Collect and normalize all data needed for the observation
        # Get data from WebSocket or directly from SUMO subscriptions
        observation = {
            "traffic_lights": {
                "phase": traci.trafficlight.getPhase("semaforos"),
                "duration": traci.trafficlight.getPhaseDuration("semaforos"),
            },
            "lanes": {
                "queue_length": np.array([
                    traci.lane.getLastStepHaltingNumber(lane_id)
                    for direction in self.lanes_by_street.values()
                    for lane_id in direction
                ]),
                "waiting_time": np.array([
                    sum(traci.vehicle.getAccumulatedWaitingTime(veh_id)
                        for veh_id in traci.lane.getLastStepVehicleIDs(lane_id))
                    for direction in self.lanes_by_street.values()
                    for lane_id in direction
                ]),
            },
            "sensors": {
                "e1_sensors": np.array([
                    traci.inductionloop.getLastStepVehicleNumber(sensor_id)
                    for sensor_id in self.e1_sensors if sensor_id.startswith(tuple(self.lanes_by_street.keys()))
                ]),
                "e2_sensors": np.array([
                    traci.lanearea.getLastStepVehicleNumber(sensor_id)
                    for sensor_id in self.e2_sensors if sensor_id.startswith(tuple(self.lanes_by_street.keys()))
                ]),
            },
        }
        return observation
    

    
    def step(self, action):
        self.apply_action(action)
        traci.simulationStep()

        # Get new observation
        observation = self.get_observation()

        # Calculate reward
        # if self.reward_function == "queue_length":
        #     reward = reward_minimize_queue_length(observation)
        # elif self.reward_function == "waiting_time":
        #     reward = reward_minimize_waiting_time(observation)
        # elif self.reward_function == "speed":
        #     reward = reward_maximize_speed(observation)
        # elif self.reward_function == "hybrid":
        #     reward = reward_composite(observation)
        # else:
        #     raise ValueError(f"Unknown reward function: {self.reward_function}")
        reward = self.calculate_reward(observation)

        # Return Gym-like step results
        done = traci.simulation.getMinExpectedNumber() == 0
        return observation, reward, done, {}
    


    def calculate_reward(self, state):
        return self.reward_function(state)

    


        # def apply_action(self, action):
        #     if isinstance(action, tuple):
        #         phase, duration_change = action
        #         if 0 <= phase < len(self.phases):  # Ensure valid phase
        #             traci.trafficlight.setPhase("semaforos", phase)
        #         if duration_change != 0:  # Modify phase duration
        #             current_duration = traci.trafficlight.getPhaseDuration("semaforos")
        #             new_duration = max(1, current_duration + duration_change)  # Avoid zero/negative duration
        #             traci.trafficlight.setPhaseDuration("semaforos", new_duration)
        #     elif isinstance(action, int):  # Single-phase action
        #         if action in range(len(self.phases)):
        #             traci.trafficlight.setPhase("semaforos", action)
        #     else:
        #         raise ValueError("Invalid action type provided!")
    
    def apply_action(self, action):
        """
        Applies the action to control the traffic lights.
        :param action: The action to be applied. Example:
                    - 0: Do nothing
                    - 1..n: Switch to Phase n
                    - n+1: Extend current phase
                    - n+2: Reduce current phase
        """
        current_phase = traci.trafficlight.getPhase("semaforos")

        # Total phases
        total_phases = len(self.phases)  # Define phases list somewhere

        if action == 0:
            # Do nothing
            pass
        elif 1 <= action <= total_phases:
            # Switch to a specific phase
            traci.trafficlight.setPhase("semaforos", action - 1)
        elif action == total_phases + 1:
            # Extend the current phase duration
            traci.trafficlight.setPhaseDuration(
                "semaforos", traci.trafficlight.getPhaseDuration("semaforos") + 5
            )
        elif action == total_phases + 2:
            # Reduce the current phase duration (minimum of 5 seconds)
            new_duration = max(
                5, traci.trafficlight.getPhaseDuration("semaforos") - 5
            )
            traci.trafficlight.setPhaseDuration("semaforos", new_duration)
        
