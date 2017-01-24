from tqdm import tqdm
from game import Game

g = Game()
while not g.ready(): pass
while not g.is_over():
    g.do_action(float(input()))
