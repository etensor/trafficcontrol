from fastapi import APIRouter
from model.training import train_model
from model.environment import TrafficControlEnv
from threading import Thread
import matplotlib.pyplot as plt

# Creating a router instance for model training-related endpoints
model_router = APIRouter()

# Define variables to store selected model and reward function
selected_model = "PPO"
selected_reward_function = "waiting_time"



@model_router.post("/train")
async def train_model_endpoint(timesteps: int):
    """
    Endpoint to train the RL model.
    Args:
        timesteps (int): Number of training steps.
    """
    global selected_model, selected_reward_function

    # Initialize the environment with the selected reward function
    env = TrafficControlEnv(reward_fn=selected_reward_function)

    # Threaded function to run training with Matplotlib visualizing in real time.
    def run_training():
        plt.ion()  # Interactive mode for real-time plotting
        try:
            train_model(selected_model, env, total_timesteps=timesteps)
        finally:
            plt.ioff()  # Turn off interactive mode

    # Start training in a separate thread
    thread = Thread(target=run_training)
    thread.start()

    return {"status": "Training started", "model": selected_model, "reward_function": selected_reward_function}
