import logging
from util import Round, suits, ranks
from typing import Optional
from agents.player import Player
from agents.random_player import RandomPlayer

import numpy as np

log = logging.getLogger(__name__)


class PokerGame:
    def __init__(self, initial_bankroll: int):
        self.initial_bankroll = initial_bankroll

        self.players: list[Player] = []
        self.active_players: list[bool] = []
        self.current_player: Optional[Player] = None

        self.round: Round = Round.PREFLOP
        self.community_pot: int = 0
        self.round_pot: int = 0
        self.player_pots: list[int] = []

        self.deck: list[str] = []
        self.community_cards: list[str] = []

    def generate_deck(self) -> None:
        self.deck = [rank + suit for suit in suits for rank in ranks]

    def add_players(self, players: list[Player]) -> None:
        for player in players:
            self.add_player(player)

    def add_player(self, player: Player) -> None:
        player.bankroll = self.initial_bankroll
        player.actions = []
        player.cards = []
        player.seat = len(self.players)
        self.players.append(player)
        self.active_players = [True] * len(self.players)
        self.player_pots = [0] * len(self.players)
        log.info(f"Player added: {player.name} at seat #{player.seat}, has {player.bankroll} chips in bankroll")

    def draw_card(self, gen: np.random.Generator):
        return self.deck.pop(gen.integers(0, len(self.deck)))

    def deal_new_cards(self, gen: np.random.Generator):
        for player in self.players:
            player.cards = []
            if player.bankroll <= 0:
                continue
            for _ in range(2):
                player.cards.append(self.draw_card(gen))
            log.info(f"Player {player.seat} drew {player.cards}")

    def deal_cards_to_table(self, gen: np.random.Generator, num_cards: int):
        for _ in range(num_cards):
            self.community_cards.append(self.draw_card(gen))
        log.info(f"Dealer drew {num_cards} card{'s' if num_cards > 1 else ''} to table: {self.community_cards}")

    def start_new_hand(self, gen: np.random.Generator) -> None:
        self.round = Round.PREFLOP
        self.community_cards = []
        self.generate_deck()
        self.deal_new_cards(gen)
        self.start_round()

    def start_round(self):
        pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    game = PokerGame(1000)
    game.add_players([RandomPlayer() for _ in range(4)])
    game.start_new_hand(np.random.Generator(np.random.PCG64(None)))
