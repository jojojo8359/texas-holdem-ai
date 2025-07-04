import logging
from util import PlayerAction

log = logging.getLogger(__name__)
log.propagate = True


class Player:
    def __init__(self, name: str, autoplay: bool):
        self.bankroll: int = 0
        self.name: str = name
        self.seat: int = 0
        self.actions: list[PlayerAction] = []  # Records the player's historical actions
        self.cards: list[str] = []
        self.round_contribution: int = 0
        self.autoplay: bool = autoplay
        log.debug(f"New Player {self.name} initialized")

    def action(self, action_space: list[PlayerAction], observation, info) -> PlayerAction:
        return PlayerAction.CHECK_CALL
