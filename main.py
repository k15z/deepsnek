import pickle
from rl import *
from game import Game

agent = DDPGAgent()
fout = open("rewards.csv", "wt")
fout.write("epoch,epsilon,loss,memory,reward\n")

for i in range(32):
    rewards = []
    epsilon = max(0.1, 1.0-i/32.0)
    for _ in range(16):
        reward, _ = agent.play(Game(), epsilon)
        rewards.append(reward)
    loss = agent.train()

    record = (i, epsilon, loss, len(agent.memory.entries), sum(rewards)/len(rewards))
    fout.write(",".join(map(str, record)) + "\n")
    print(*record)

pickle.dump(agent.memory, open("memory.pkl", "wb"))
