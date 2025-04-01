import logging
from typing import Optional

from agents.player import Player
from util import PlayerAction

log = logging.getLogger(__name__)


class HumanPlayer(Player):
    def __init__(self):
        super().__init__("Human Agent")

    def action(self, action_space: list[PlayerAction], observation, info) -> PlayerAction:
        log.info(f"Action space: {action_space}")
        print(f"Current possible actions: {action_space}")
        action: Optional[int] = None
        while action is None:
            s: str = input("Choose an action: ")
            try:
                action = int(s)
            except ValueError:
                print("Please try again.")
                action = None
        return PlayerAction(action)
