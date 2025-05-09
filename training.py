import logging
import time
import gymnasium as gym
from util import ColoredFormatter
from agents.random_player import RandomPlayer
from agents.q import QPlayer
# from agents.human_player import HumanPlayer
from gym_env.env import TexasHoldemEnv  # noqa: F401

import numpy as np
import random
from collections import defaultdict
from util import PlayerAction


if __name__ == "__main__":
    log = logging.getLogger()
    log.setLevel(logging.WARNING)
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    ch.setFormatter(ColoredFormatter())
    log.addHandler(ch)

    env = gym.make('TexasHoldem-v0', render_mode="human", initial_bankroll=100, small_blind=2, big_blind=5, players=[QPlayer(), RandomPlayer(), RandomPlayer(), RandomPlayer()])

    action_size = env.action_space.n  # type: ignore
    qtable = defaultdict(lambda: np.zeros(action_size))

    learning_rate = 0.1
    discount_rate = 0.5
    epsilon = 0.5
    decay_rate = 0.005

    num_episodes = 3000
    max_steps = 200

    episodes_won = 0

    for episode in range(num_episodes):
        state, info = env.reset()
        done = False

        log.error("Starting episode " + str(episode))
        for s in range(max_steps):
            if random.uniform(0, 1) < epsilon:
                action = random.choice(info['legal_moves']).value
            else:
                action = np.argmax(qtable[state])  # type: ignore

            log.info("Chosen action is " + str(PlayerAction(action)))

            new_state, reward, done, truncated, info = env.step(PlayerAction(action))

            qtable[state][action] = qtable[state][action] + learning_rate * (float(reward) + discount_rate * np.max(qtable[new_state]) - qtable[state][action])

            state = new_state

            if done or truncated:
                if float(reward) > 0.0:
                    episodes_won += 1
                break

        epsilon = np.exp(-decay_rate * episode)

    log.error("Training finished!")
    log.error(f"Agent won: {episodes_won}/{num_episodes} episodes")
    input()

    # env.close()

    # env = gym.make('TexasHoldem-v0', render_mode="human", initial_bankroll=100, small_blind=2, big_blind=5, players=[QPlayer(), RandomPlayer(), RandomPlayer(), RandomPlayer()])

    # state, info = env.reset()
    # done = False
    # rewards = 0

    log.error("Trained agent is now playing...")

    # trained_episodes = 2000
    episodes_won = 0

    for episode in range(num_episodes):
        state, info = env.reset()
        done = False
        rewards = 0

        for s in range(max_steps):
            if state in qtable:
                action = np.argmax(qtable[state])
                if PlayerAction(action) not in info['legal_moves']:
                    new_action = random.choice(info['legal_moves']).value
                    # log.error(f"Q-value {PlayerAction(action)} not legal for round, choosing {PlayerAction(new_action)} instead...")
                    action = new_action
            else:
                action = random.choice(info['legal_moves']).value
            # log.error(f"Legal moves are {info['legal_moves']}")
            # log.error("Chosen action is " + str(PlayerAction(action)))
            new_state, reward, done, truncated, info = env.step(PlayerAction(action))
            # env.render()
            rewards += float(reward)
            # log.error(f"Current reward: {rewards}")
            state = new_state
            if done or truncated:
                if float(reward) > 0.0:
                    episodes_won += 1
                break
    log.error("Playing finished!")
    log.error(f"Agent won: {episodes_won}/{num_episodes} episodes")

    time.sleep(5)
    env.close()
    # print(qtable)

    # env.reset()
    # env.step(None)
    # time.sleep(5)
