from typing import Optional, Any

import numpy as np
import pygame

import gymnasium as gym
from gymnasium import spaces

from poker2 import PlayerAction, Round


class TexasHoldemEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    def __init__(self, render_mode: Optional[str] = None):
        self.window_size = 512
        self.action_space = spaces.Discrete(len(PlayerAction))

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        self.window: Optional[pygame.Surface] = None
        self.clock = None

    # TODO: Fill in return type
    def reset(self, seed: Optional[int] = None, options: Optional[dict[str, Any]] = None):
        super().reset(seed=seed)

    def render(self):
        if self.render_mode == "rgb_array":
            return self._render_frame()

    def _render_frame(self):
        if self.window is None and self.render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode((self.window_size, self.window_size))
        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()
        canvas = pygame.Surface((self.window_size, self.window_size))
        canvas.fill((255, 255, 255))

        # Draw state using pygame.draw.*

        if self.render_mode == "human":
            if self.window is not None:
                self.window.blit(canvas, canvas.get_rect())
                pygame.event.pump()
                pygame.display.update()

            if self.clock is not None:
                self.clock.tick(self.metadata["render_fps"])
        else:
            return np.transpose(np.array(pygame.surfarray.pixels3d(canvas)), axes=(1, 0, 2))
