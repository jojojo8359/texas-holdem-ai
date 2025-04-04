from poker import PokerGame
import logging
from util import PlayerAction, ColoredFormatter
from typing import Optional
# from agents.random_player import RandomPlayer
from agents.human_player import HumanPlayer


if __name__ == "__main__":
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(ColoredFormatter())
    log.addHandler(ch)
    # logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(name)s:%(funcName)s: %(message)s")

    game = PokerGame(1000, 5, 10)
    # game.add_players([RandomPlayer() for _ in range(4)])
    # game.add_players([RandomPlayer(), RandomPlayer(), HumanPlayer(), RandomPlayer()])
    game.add_players([HumanPlayer() for _ in range(4)])
    game.start_new_hand()
    while not game.done:
        action: Optional[PlayerAction] = game.action()
        if action is not None:
            game.step(action)
