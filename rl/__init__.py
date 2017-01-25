from .ddpg import *
from .memory import *
from random import random

class Agent:

    def __init__(self):
        pass

    def play(self, game):
        while not game.ready(): pass
        while not game.is_over():
            state = game.get_state()
            game.do_action(random() - 0.5)
            print(game.get_score())

    def train(self):
        pass

class DDPGAgent(Agent):

    def __init__(self):
        self.ddpg = DDPG([100, 100, 3], 1)
        self.memory = Memory()

    def play(self, game, epsilon):
        total_reward = 0.0
        while not game.ready(): pass
        while not game.is_over():
            pscore = game.get_score()
            state = game.get_state()
            action = self.ddpg.get_actions(np.array([state]))[0]
            if random() < epsilon:
                action[0] = random() * 2.0 - 1.0
            game.do_action(action[0])
            nscore = game.get_score()
            reward = nscore - pscore
            nstate = game.get_state()
            terminal = game.is_over()
            self.memory.remember(state, action, reward, nstate, terminal)
            total_reward += reward
        return total_reward, len(self.memory.entries)

    def train(self):
        samples = self.memory.sample(N=False)
        S, A, R, NS, T = map(np.array, zip(*samples))
        return self.ddpg.fit(S, A, R, NS, T).history["loss"][0]
