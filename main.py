import pickle
from rl import *
from game import Game

agent = DDPGAgent()
agent.memory = pickle.load(open("memory.pkl", "rb"))
print([agent.train() for _ in range(10)])

fout = open("rewards.csv", "wt")
fout.write("epoch,epsilon,loss,memory,reward\n")

for i in range(10):
    epsilon = max(0.1, 0.5-i/10.0)

    total_rewards = []
    actual_rewards = []
    for _ in range(16):
        total_reward, actual_reward = agent.play(Game(), epsilon)
        total_rewards.append(total_reward)
        actual_rewards.append(actual_reward)
    actual_rewards = sum(actual_rewards) / len(actual_rewards)
    total_rewards = sum(total_rewards) / len(total_rewards)
    loss = agent.train()

    record = (i, epsilon, loss, len(agent.memory.entries), total_rewards, actual_rewards)
    fout.write(",".join(map(str, record)) + "\n")
    print(*record)

    pickle.dump(agent.memory, open("memory.pkl", "wb"))
