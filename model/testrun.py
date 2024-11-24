import numpy as np
from model.environment import TrafficControlEnv

# Initialize environment
env = TrafficControlEnv()
obs = env.reset()
print("Initial Observation:", obs)

# Step through environment with random actions for testing
for _ in range(10):
    action = env.action_space.sample()  # Random action
    obs, reward, done, info = env.step(action)
    print("Observation:", obs)
    print("Reward:", reward)
    if done:
        break
env.close()
