from enum import Enum
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

from model.rewards import reward_composite, reward_maximize_speed, reward_minimize_queue_length, reward_minimize_waiting_time

class ModelType(str, Enum):
    DQN = "DQN"
    PPO = "PPO"

class RewardFunction(str, Enum):
    MINIMIZE_QUEUE = "minimize_queue"
    MINIMIZE_WAITING = "minimize_waiting"
    MAXIMIZE_SPEED = "maximize_speed"
    HYBRID = "hybrid"

class ConfigRequest(BaseModel):
    model_type: ModelType
    reward_function: RewardFunction

config_router = APIRouter()

@config_router.post("/configdeprec", tags=["Configuration"])
async def configure_model(config: ConfigRequest):
    global srl_env, selected_model, reward_function

    # Set the reward function based on the request
    if config.reward_function == RewardFunction.MINIMIZE_QUEUE:
        reward_function = reward_minimize_queue_length
    elif config.reward_function == RewardFunction.MINIMIZE_WAITING:
        reward_function = reward_minimize_waiting_time
    elif config.reward_function == RewardFunction.MAXIMIZE_SPEED:
        reward_function = reward_maximize_speed
    elif config.reward_function == RewardFunction.HYBRID:
        reward_function = reward_composite
    else:
        raise HTTPException(status_code=400, detail="Invalid reward function specified")

    # Set the model type
    if config.model_type == ModelType.DQN:
        selected_model = "DQN"
    elif config.model_type == ModelType.PPO:
        selected_model = "PPO"
    else:
        raise HTTPException(status_code=400, detail="Invalid model type specified")

    # Update the SRL environment with new reward function
    srl_env.reward_function = reward_function

    return {"status": "Configuration updated successfully"}


@config_router.post("/configure", tags= ["Configuration"])
async def configure_training(model_name: str, reward_function: str):
    """
    Endpoint to configure model training.
    Args:
        model_name (str): Type of model ('PPO' or 'DQN').
        reward_function (str): Reward function ('queue_length', 'waiting_time', 'speed', 'hybrid').
    """
    global selected_model, selected_reward_function

    if model_name not in ["PPO", "DQN"]:
        return {"status": "error", "message": "Invalid model_name. Choose 'PPO' or 'DQN'."}

    if reward_function not in ["queue_length", "waiting_time", "speed", "hybrid"]:
        return {"status": "error", "message": "Invalid reward_function. Choose 'queue_length', 'waiting_time', 'speed', or 'hybrid'."}

    selected_model = model_name
    selected_reward_function = reward_function

    return {"status": "Configuration updated", "model": selected_model, "reward_function": selected_reward_function}

