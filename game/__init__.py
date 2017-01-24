"""
This module provides a Game class which spawns instances of the electron app and provides an simple
interface for experimenting with reinforcement learning algorithms.
"""

from os import path
from io import BytesIO
from time import sleep
from requests import get
from random import randint
from scipy.misc import imread
from subprocess import Popen, DEVNULL

CWD = path.dirname(path.abspath(__file__))

def request(url, num_tries=10):
    response = None
    for _ in range(num_tries):
        try: response = get(url, timeout=1.0)
        except: sleep(1.0)
        if response != None: break
    return response

class Game:

    def __init__(self):
        self.reset()

    def reset(self):
        self.over = False
        self.state = False
        self.score = 0.0
        self.port = str(randint(3001, 9999))
        self.path = "http://localhost:" + self.port
        Popen("electron app -p " + self.port + " -w", shell=True, cwd=CWD, stdout=DEVNULL)

    def ready(self):
        status = request(self.path + "/ready")
        if status == None:
            self.reset()
            return False
        return status.text == "true"

    def is_over(self):
        if not self.over:
            self.over = request(self.path + "/done").text == "true"
        return self.over

    def get_state(self):
        if not self.over:
            response = request(self.path + "/state")
            self.state = imread(BytesIO(response.content))
        assert type(self.state) != type(False)
        return self.state

    def get_score(self):
        if not self.over:
            response = request(self.path + "/score")
            self.score = int(response.text)
        return self.score

    def do_action(self, action):
        if action > 1.0: action = 1.0
        if action < -1.0: action = -1.0
        command = "left" if action < 0 else "right"
        duration = str(int(abs(action * 1000.0)))
        request(self.path + "/action/" + command + "/" + duration)
