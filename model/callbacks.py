from stable_baselines3.common.callbacks import BaseCallback
import matplotlib.pyplot as plt
import numpy as np


class RTPlotCallback(BaseCallback):
    def __init__(self, verbose=0):
        super(RTPlotCallback, self).__init__(verbose)
        self.rewards = []
        #self.fig, self.ax = plt.subplots()
        #self.x_data, self.y_data = [], []
        #self.line, = self.ax.plot(self.x_data, self.y_data, 'r-')
    

    def _on_step(self) -> bool:
        reward = self.locals['rewards'][0]
        self.rewards.append(reward)
        if len(self.rewards) % 100 == 0:
            self.plot_rewards()
        
        return True
    

    def plot_rewards(self):
        plt.figure(figsize=(10, 5))
        plt.plot(np.arange(len(self.rewards)), self.rewards, label='Rewards')
        plt.xlabel('Episode')
        plt.ylabel('Reward')
        plt.title('Training Progress')
        plt.legend()
        plt.show(block=False)
        plt.pause(0.001)  # Pause to allow for real-time plot updates