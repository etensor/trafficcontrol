import numpy as np
from sumo_rl.environment.observations import ObservationFunction
import gymnasium as gym
import traci

class CustomObservationFunction(ObservationFunction):
    def __init__(self, traffic_signal):
        super().__init__(traffic_signal)
        self.traffic_signal = traffic_signal  # Ensure traffic_signal is set

    def _compute_observations(self):
        observations = {}
        for ts in self.traffic_signals:
            observation = self.observation_class(ts).compute_observation()
            if observation is None:
                print(f"No observation for traffic signal {ts.id}")
                observation = np.zeros(self.observation_space.shape)  # Provide a fallback observation
            observations[ts.id] = observation.copy()  # Copy is safe now
        return observations


    def compute_observation(self):
        try:
            # Actual observation computation logic here
            # Example:
            phase_id = [1 if self.traffic_signal.green_phase == i else 0 for i in range(self.traffic_signal.num_green_phases)]
            total_queued = self.traffic_signal.get_total_queued()
            observation = np.array(phase_id + [total_queued], dtype=np.float32)
            return observation
        except Exception as e:
            print(f"Failed to compute observation: {e}")
            return None


    def observation_space(self):
        num_metrics = 2  # Number of additional metrics (total queued and average speed)
        total_space = self.traffic_signal.num_green_phases + num_metrics
        return gym.spaces.Box(low=np.zeros(total_space, dtype=np.float32), high=np.inf*np.ones(total_space, dtype=np.float32))

