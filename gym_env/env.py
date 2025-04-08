from typing import Optional
import logging

import numpy as np
import pygame

import gymnasium as gym
from gymnasium import spaces

from poker import PokerGame
from util import PlayerAction, rank_hand, Round, suits, ranks
from agents.player import Player
# from agents.human_player import HumanPlayer

log = logging.getLogger(__name__)


class TexasHoldemEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 60}

    def __init__(self, initial_bankroll: int, small_blind: int, big_blind: int, players: list[Player], render_mode: Optional[str] = None):
        self.game = PokerGame(initial_bankroll, small_blind, big_blind)
        self.add_players(players)
        self.master_deck = [rank + suit for suit in suits for rank in ranks]
        self.window_size = (768, 512)
        self.action_space = spaces.Discrete(len(PlayerAction) - 2)
        self.observation_space = spaces.Dict(
            {
                "num_players": spaces.Discrete(1, start=len(self.game.players)),
                "current_player": spaces.Discrete(len(self.game.players), start=0),
                "bankrolls": spaces.Box(low=0, high=2**63 - 2, shape=(len(self.game.players),), dtype=np.int64),
                "player_cards": spaces.Box(low=0, high=51, shape=(2,), dtype=np.int64),
                "table_cards": spaces.Box(low=-1, high=51, shape=(5,), dtype=np.int64),
                "current_hand_rank": spaces.Discrete(7463, start=1),
                "player_pots": spaces.Box(low=0, high=2**63 - 2, shape=(len(self.game.players),), dtype=np.int64),
                "active_players": spaces.Box(low=0, high=1, shape=(len(self.game.players),), dtype=np.int64),
                "round_contributions": spaces.Box(low=0, high=2**63 - 2, shape=(len(self.game.players),), dtype=np.int64),
                "round_pot": spaces.Box(low=0, high=2**63 - 2, shape=(1,), dtype=np.int64),
                "community_pot": spaces.Box(low=0, high=2**63 - 2, shape=(1,), dtype=np.int64),
                "round": spaces.Discrete(len(Round)),
                "legal_moves": spaces.Box(low=0, high=1, shape=(len(PlayerAction) - 2,), dtype=np.int64)
            }
        )
        self.observation = {}

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        self.window: Optional[pygame.Surface] = None
        self.clock = None
        self.table_image = pygame.image.load("sprites/png/table.png")
        self.table_image = pygame.transform.scale_by(self.table_image, 5.0)
        self.cards_spritesheet = pygame.image.load("sprites/png/Card_Sheet.png")
        self.cards: list[pygame.Surface] = []
        for y in range(0, 128, 32):
            for x in range(0, 416, 32):
                card_image = pygame.Surface((32, 32), pygame.SRCALPHA)
                card_image.blit(self.cards_spritesheet, (0, 0), (x, y, x + 32, y + 32))
                self.cards.append(card_image)
        one_of_one_bottom = pygame.Rect(320, 384, 128, 128)
        one_of_one_top = pygame.Rect(320, 0, 128, 128)
        left = pygame.Rect(0, 192, 128, 128)
        right = pygame.Rect(640, 192, 128, 128)
        one_of_two_top = pygame.Rect(220, 0, 128, 128)
        two_of_two_top = pygame.Rect(420, 0, 128, 128)
        one_of_two_bottom = pygame.Rect(220, 384, 128, 128)
        two_of_two_bottom = pygame.Rect(420, 384, 128, 128)
        one_of_three_top = pygame.Rect(170, 0, 128, 128)
        two_of_three_top = pygame.Rect(320, 0, 128, 128)
        three_of_three_top = pygame.Rect(470, 0, 128, 128)
        one_of_three_bottom = pygame.Rect(170, 384, 128, 128)
        two_of_three_bottom = pygame.Rect(320, 384, 128, 128)
        three_of_three_bottom = pygame.Rect(470, 384, 128, 128)

        self.player_offsets = [
            [pygame.Rect(0, 0, 0, 0)], [pygame.Rect(0, 0, 0, 0)],
            [one_of_one_bottom, one_of_one_top],
            [one_of_one_bottom, left, right],
            [one_of_one_bottom, left, one_of_one_top, right],
            [one_of_one_bottom, left, one_of_two_top, two_of_two_top, right],
            [one_of_two_bottom, left, one_of_two_top, two_of_two_top, right, two_of_two_bottom],
            [one_of_two_bottom, left, one_of_three_top, two_of_three_top, three_of_three_top, right, two_of_two_bottom],
            [two_of_three_bottom, one_of_three_bottom, left, one_of_three_top, two_of_three_top, three_of_three_top, right, three_of_three_bottom]
        ]

    def _get_obs(self) -> None:
        self.game.determine_legal_moves()
        self.observation = {
            "num_players": len(self.game.players),
            "current_player": self.game.current_player_idx,
            "bankrolls": np.array([player.bankroll for player in self.game.players]),
            "player_cards": np.array([self.master_deck.index(card) for card in (self.game.current_player.cards if self.game.current_player else [])]),
            "table_cards": [self.master_deck.index(card) for card in self.game.community_cards],
            "current_hand_rank": rank_hand((self.game.current_player.cards if self.game.current_player else []) + self.game.community_cards)[1] if len(self.game.community_cards) >= 3 else 7463,
            "player_pots": np.array(self.game.player_pots),
            "active_players": np.array([int(player) for player in self.game.active_players]),
            "round_contributions": np.array([player.round_contribution for player in self.game.players]),
            "round_pot": np.array([self.game.round_pot]),
            "community_pot": np.array([self.game.community_pot]),
            "round": self.game.round.value,
            "legal_moves": np.array([1 if PlayerAction(i) in self.game.legal_moves else 0 for i in range(len(PlayerAction) - 2)])
        }
        self.observation["table_cards"] = np.array((self.observation["table_cards"] + 5 * [-1])[:5])
        self.game.dump_state()
        log.debug(f"Observation: {self.observation}")
        self.render()

    def _get_info(self) -> dict:
        return {}

    def add_players(self, players: list[Player]) -> None:
        """Add a list of players to the game. Players should be `Player` sub-classes."""
        for player in players:
            self.add_player(player)

    def add_player(self, player: Player) -> None:
        """
        Add a "Player" sub-class to the game.

        The player instance will have all of its internal attributes initialized.
        """
        player.bankroll = self.game.initial_bankroll
        player.actions = []
        player.cards = []
        player.seat = len(self.game.players)
        self.game.players.append(player)
        log.debug(f"Player added: {player.name} at seat #{player.seat}, has {player.bankroll} chips in bankroll")
        self.observation_space = spaces.Dict(
            {
                "num_players": spaces.Discrete(1, start=len(self.game.players)),
                "current_player": spaces.Discrete(len(self.game.players), start=0),
                "bankrolls": spaces.Box(low=0, high=2**63 - 2, shape=(len(self.game.players),), dtype=np.int64),
                "player_cards": spaces.Box(low=0, high=51, shape=(2,), dtype=np.int64),
                "table_cards": spaces.Box(low=-1, high=51, shape=(5,), dtype=np.int64),
                "current_hand_rank": spaces.Discrete(7463, start=1),
                "player_pots": spaces.Box(low=0, high=2**63 - 2, shape=(len(self.game.players),), dtype=np.int64),
                "active_players": spaces.Box(low=0, high=1, shape=(len(self.game.players),), dtype=np.int64),
                "round_contributions": spaces.Box(low=0, high=2**63 - 2, shape=(len(self.game.players),), dtype=np.int64),
                "round_pot": spaces.Box(low=0, high=2**63 - 2, shape=(1,), dtype=np.int64),
                "community_pot": spaces.Box(low=0, high=2**63 - 2, shape=(1,), dtype=np.int64),
                "round": spaces.Discrete(len(Round)),
                "legal_moves": spaces.Box(low=0, high=1, shape=(len(PlayerAction) - 2,), dtype=np.int64)
            }
        )

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):  # type: ignore
        super().reset(seed=seed)
        self.game.set_rng(self.np_random)
        self.game.reset()
        self._get_obs()
        return (self.observation, {})

    def step(self, action: Optional[PlayerAction] = None):
        if action is None and self.game.current_player and self.game.current_player.autoplay:
            while self.game.current_player.autoplay and not self.game.done:
                action = self.game.action(self.observation, self._get_info())
                self.game.do_step(action)
                self._get_obs()
        else:
            if action is not None:
                self.game.do_step(action)
                self._get_obs()
            else:
                raise RuntimeError("Cannot step game with action None when a non-autoplay agent is playing!")
        # Observation, reward, terminated, truncated, info
        return (self.observation, 0, self.game.done, False, self._get_info())

    def render(self):
        if self.render_mode in ["human", "rgb_array"]:
            return self._render_frame()

    def _render_frame(self):
        if self.window is None and self.render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode(self.window_size)
        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()
        canvas = pygame.Surface(self.window_size)
        canvas.fill((255, 255, 255))

        # Draw state using pygame.draw.*
        canvas.blit(self.table_image, self.table_image.get_rect(center=canvas.get_rect().center).move(0, -7))

        # Community card rect
        # pygame.draw.rect(canvas, (0, 0, 0), (canvas.get_rect().centerx - 80, canvas.get_rect().centery - 16, 160, 32))
        card_offset: int = 0
        for card in self.game.community_cards:
            self._draw_card(self.master_deck.index(card), canvas, pygame.Rect(canvas.get_rect().centerx - 80 + card_offset, canvas.get_rect().centery - 16, 0, 0))
            card_offset += 32

        font = pygame.font.Font(pygame.font.get_default_font(), 14)
        for idx, player in enumerate(self.game.players):
            name = font.render(player.name + " (" + str(player.seat) + ")", True, (0, 0, 0), None)
            bankroll = font.render("BR: " + str(player.bankroll), True, (0, 0, 0), None)
            bet = font.render("Bet: " + str(player.round_contribution), True, (0, 0, 0), None)
            rank = font.render("Rank: " + (rank_hand(player.cards + self.game.community_cards)[0] if len(self.game.community_cards) + len(player.cards) >= 5 and self.game.active_players[idx] else "N/A"), True, (0, 0, 0), None)

            canvas.blit(name, self.player_offsets[len(self.game.players)][idx])
            canvas.blit(bankroll, self.player_offsets[len(self.game.players)][idx].move(0, 14))
            canvas.blit(bet, self.player_offsets[len(self.game.players)][idx].move(0, 28))
            canvas.blit(rank, self.player_offsets[len(self.game.players)][idx].move(0, 42))

            card_offset: int = 0
            for card in player.cards:
                self._draw_card(self.master_deck.index(card), canvas, self.player_offsets[len(self.game.players)][idx].move(card_offset, 56))
                card_offset += 32

        round = font.render(self.game.round.name, True, (255, 255, 255), None)
        canvas.blit(round, round.get_rect(center=canvas.get_rect().center).move(0, -30))
        pots = font.render(str(self.game.round_pot) + " | " + str(self.game.community_pot), True, (255, 255, 255), None)
        canvas.blit(pots, pots.get_rect(center=canvas.get_rect().center).move(0, 30))

        if self.render_mode == "human":
            if self.window is not None:
                self.window.blit(canvas, canvas.get_rect())
                pygame.event.pump()
                pygame.display.update()

            if self.clock is not None:
                self.clock.tick(self.metadata["render_fps"])
        else:
            return np.transpose(np.array(pygame.surfarray.pixels3d(canvas)), axes=(1, 0, 2))

    def _draw_card(self, card_index: int, canvas: pygame.Surface, position: pygame.Rect):
        canvas.blit(self.cards[card_index], position)
