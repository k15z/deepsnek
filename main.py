from rl import *
from game import Game

agent = DDPGAgent()

for i in range(10):
    print("-----"*16)
    agent.play(Game(), epsilon=1.0-i/10.0)
    agent.train()
