import numpy as np
import traci

# Reward function for minimizing queue length
def reward_minimize_queue_length(observation):
    queue_lengths = observation["lanes"]["queue_length"]
    return -np.sum(queue_lengths)  # Negative reward for longer queues

# Reward function for minimizing waiting time
def reward_minimize_waiting_time(observation):
    waiting_times = observation["lanes"]["waiting_time"]
    return -np.sum(waiting_times)  # Negative reward for more waiting time

# Reward function for maximizing average speed
def reward_maximize_speed(observation):
    lane_speeds = [
        traci.lane.getLastStepMeanSpeed(lane_id)
        for direction in observation["lanes"]
        for lane_id in direction
    ]
    return np.mean(lane_speeds)  # Reward for higher average speed


# Reward function for hybrid approach (weighted combination)
def reward_composite(observation, weights=None):
    if weights is None:
        weights = {"queue_length": 0.5, "waiting_time": 0.3, "speed": 0.2}

    queue_penalty = weights["queue_length"] * -np.sum(observation["lanes"]["queue_length"])
    waiting_time_penalty = weights["waiting_time"] * -np.sum(observation["lanes"]["waiting_time"])
    speed_reward = weights["speed"] * np.mean(observation["sensors"]["e2_sensors"])

    return queue_penalty + waiting_time_penalty + speed_reward

    # if weights is None:
    #     weights = {"queue_length": 0.5, "waiting_time": 0.3, "speed": 0.2}
    
    # queue_penalty = weights["queue_length"] * -np.sum(observation["lanes"]["queue_length"])
    # waiting_time_penalty = weights["waiting_time"] * -np.sum(observation["lanes"]["waiting_time"])
    # speed_reward = weights["speed"] * np.mean([
    #     traci.lane.getLastStepMeanSpeed(lane_id)
    #     for lane_id in observation["lanes"]
    # ])
    
    # return queue_penalty + waiting_time_penalty + speed_reward