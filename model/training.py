from stable_baselines3 import DQN, PPO
from model.environment import TrafficControlEnv
from model.callbacks import RTPlotCallback


callback = RTPlotCallback()


def train_model(model_type: str, env: TrafficControlEnv, total_timesteps: int = 12000):
    if model_type == "DQN":
        model = DQN("MlpPolicy", env, verbose=1, tensorboard_log="./tensorboard_logs/")
    elif model_type == "PPO":
        model = PPO("MlpPolicy", env, verbose=1, tensorboard_log="./tensorboard_logs/")
    else:
        raise ValueError("Invalid model type (?) Use 'DQN' or 'PPO'.")

    model.learn(total_timesteps=total_timesteps, callback=callback)
    return model



