import random
from agents.player import Player
from util import PlayerAction


class RandomPlayer(Player):
    def __init__(self):
        super().__init__("Random Agent")

    def action(self, action_space: list[PlayerAction], observation, info) -> PlayerAction:
        return random.choice(action_space)
