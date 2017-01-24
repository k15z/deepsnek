from random import sample

class Memory:

    def __init__(self):
        self.entries = []

    def sample(self, N):
        N = min(len(self.entries), N)
        return sample(self.entries, N)

    def remember(self, state, action, reward, nstate, terminal):
        self.entries.append([state, action, reward, nstate, terminal])
