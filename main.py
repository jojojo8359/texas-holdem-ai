import logging
import time
import gymnasium as gym
from util import ColoredFormatter
from agents.random_player import RandomPlayer
# from agents.human_player import HumanPlayer
from gym_env.env import TexasHoldemEnv  # noqa: F401


if __name__ == "__main__":
    log = logging.getLogger()
    log.setLevel(logging.WARNING)
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(ColoredFormatter())
    log.addHandler(ch)

    env = gym.make('TexasHoldem-v0', render_mode="human", initial_bankroll=100, small_blind=2, big_blind=5, players=[RandomPlayer() for _ in range(8)])
    env.reset()
    env.step(None)
    time.sleep(5)
