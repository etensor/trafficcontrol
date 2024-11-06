# from stable_baselines3.common.callbacks import BaseCallback
# from stable_baselines3.common.logger import Logger

# from utils.traci_api import collect_metrics

# class TensorBoardCallback(BaseCallback):
#     def __init__(self, verbose=0):
#         super(TensorBoardCallback, self).__init__(verbose)

#     def _on_step(self) -> bool:
#         metrics = collect_metrics(env)
#         for key, value in metrics.items():
#             if isinstance(value, dict):
#                 for sub_key, sub_value in value.items():
#                     self.logger.record(f"{key}/{sub_key}", sub_value)
#             else:
#                 self.logger.record(key, value)
#         return True
    