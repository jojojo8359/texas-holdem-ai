import logging

from agents.player import Player

log = logging.getLogger(__name__)
log.propagate = True


class QPlayer(Player):
    def __init__(self):
        super().__init__("Q-Learning Agent", False)
