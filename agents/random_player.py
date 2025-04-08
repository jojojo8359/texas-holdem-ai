import logging
import random

from agents.player import Player
from util import PlayerAction

log = logging.getLogger(__name__)
log.propagate = True


class RandomPlayer(Player):
    def __init__(self):
        super().__init__("Random Agent", True)

    def action(self, action_space: list[PlayerAction], observation, info) -> PlayerAction:
        log.info(f"Action space: {action_space}")
        return random.choice(action_space)
