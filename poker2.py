import logging
from util import PlayerAction, Round, suits, ranks, rank_hand
from typing import Optional
from agents.player import Player
from agents.random_player import RandomPlayer
from agents.human_player import HumanPlayer

import numpy as np

log = logging.getLogger(__name__)


class PokerGame:
    def __init__(self, initial_bankroll: int, small_blind: int, big_blind: int):
        self.gen: np.random.Generator = np.random.Generator(np.random.PCG64(None))

        self.initial_bankroll: int = initial_bankroll
        self.small_blind: int = small_blind
        self.big_blind: int = big_blind

        self.players: list[Player] = []
        self.active_players: list[bool] = []
        self.current_player: Optional[Player] = None
        self.current_player_idx: int = 0

        self.round: Round = Round.PREFLOP
        self.community_pot: int = 0
        self.round_pot: int = 0
        self.player_pots: list[int] = []

        self.deck: list[str] = []
        self.community_cards: list[str] = []

        self.folders: list[bool] = []
        self.raisers: list[bool] = []
        self.checkers: int = 0
        self.min_call: int = 0

        self.legal_moves: list[PlayerAction] = []

    def set_gen(self, gen: np.random.Generator) -> None:
        self.gen = gen

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

    def draw_card(self):
        return self.deck.pop(self.gen.integers(0, len(self.deck)))

    def deal_new_cards(self):
        for player in self.players:
            player.cards = []
            if player.bankroll <= 0:
                continue
            for _ in range(2):
                player.cards.append(self.draw_card())
            log.info(f"Player {player.seat} drew {player.cards}")

    def deal_cards_to_table(self, num_cards: int):
        for _ in range(num_cards):
            self.community_cards.append(self.draw_card())
        log.info(f"Dealer drew {num_cards} card{'s' if num_cards > 1 else ''} to table: {self.community_cards}")

    def start_new_hand(self) -> None:
        log.info("Starting new hand...")
        self.round = Round.PREFLOP
        self.community_cards = []
        self.generate_deck()
        self.deal_new_cards()
        self.start_round()

    def end_hand(self) -> None:
        self.close_pots()
        log.info(f"Final community pot: {self.community_pot}")
        log.info(f"Final community cards: {self.community_cards}")
        self.determine_and_award_winner()

    def start_round(self):
        # TODO: Reset betting data
        self.checkers = 0
        self.min_call = 0
        if self.round == Round.PREFLOP:
            log.info("Starting round: Preflop")
            self.next_player()
            self.process_decision(PlayerAction.SMALL_BLIND)
            self.next_player()
            self.process_decision(PlayerAction.BIG_BLIND)
            self.next_player()
        elif self.round in [Round.FLOP, Round.TURN, Round.RIVER]:
            log.info(f"Starting round: {'Flop' if self.round == Round.FLOP else ('Turn' if self.round == Round.TURN else 'River')}")
            if self.round == Round.FLOP:
                self.deal_cards_to_table(3)
            elif self.round in [Round.TURN, Round.RIVER]:
                self.deal_cards_to_table(1)
            self.next_player()
        else:
            log.info("Starting showdown")
            return
        log.info("Betting has started!")

    def end_round(self):
        self.close_pots()

        self.round = Round(self.round.value + 1)
        log.info("Round over!")

    def close_pots(self):
        self.community_pot += self.round_pot
        self.round_pot = 0
        self.player_pots = [0] * len(self.players)

    def next_player(self):
        log.debug("next_player called")
        alive: int = self.active_players.count(True)
        if alive < 2:
            log.info("One player remains in hand, skipping to showdown...")
            self.round = Round.SHOWDOWN
            return

        if self.checkers == alive:
            log.info("All players have checked, moving to next round...")
            self.end_round()
            self.start_round()
            return

        cont: bool = True
        for index, pot in enumerate(self.player_pots):
            if not self.active_players[index]:
                continue
            if pot != max(self.player_pots) or pot == 0:
                log.info("Not all players have bet the same amount, continuing betting...")
                cont = False
                break
        if cont:
            log.info("All players have bet the same amount, moving to next round...")
            self.end_round()
            self.start_round()
            # TODO: Check that betting leaves off at the right point when ending the round here
            return

        while True:
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
            if self.active_players[self.current_player_idx]:
                break

        # Successful switch
        if not self.current_player:
            self.current_player_idx = 0
            log.info("No current player, set to 0")
        self.current_player = self.players[self.current_player_idx]
        log.info(f"Moved to player {self.current_player_idx}")

    def determine_legal_moves(self):
        self.legal_moves = []
        if self.player_pots[self.current_player_idx] == max(self.player_pots):
            self.legal_moves.append(PlayerAction.CHECK)
        else:
            self.legal_moves.append(PlayerAction.CALL)
            self.legal_moves.append(PlayerAction.FOLD)
        if self.current_player:
            if self.current_player.bankroll >= 3 * self.big_blind - self.player_pots[self.current_player_idx]:
                self.legal_moves.append(PlayerAction.RAISE)
        else:
            log.error("No current player, cannot determine legal moves!")
        log.debug(f"Current legal moves: {self.legal_moves}")
        log.info(f"Active players: {self.active_players}")
        log.info(f"Player pots: {self.player_pots}")
        log.info(f"Round pot: {self.round_pot}")
        log.info(f"Min call: {self.min_call}")
        log.info(f"Community pot: {self.community_pot}")

    def process_decision(self, action: PlayerAction):
        if action not in [PlayerAction.SMALL_BLIND, PlayerAction.BIG_BLIND] and action not in self.legal_moves:
            log.error(f"Action {action} is not a legal move ({self.legal_moves})!")

        contribution: int = 0
        # Check against action and set contribution accordingly
        if self.current_player:
            if action == PlayerAction.SMALL_BLIND:
                contribution = min(self.small_blind, self.current_player.bankroll)
                log.info(f"Player bet small blind ({self.small_blind}): contribution = {contribution}")
            elif action == PlayerAction.BIG_BLIND:
                contribution = min(self.big_blind, self.current_player.bankroll)
                log.info(f"Player bet big blind ({self.big_blind}): contribution = {contribution}")
            elif action == PlayerAction.FOLD:
                self.deactivate_current_player()
                log.info("Player folds")
            elif action == PlayerAction.CALL:
                contribution = min(self.min_call - self.player_pots[self.current_player_idx], self.current_player.bankroll)
                log.info(f"Player calls ({self.min_call}): contribution = {contribution}")
            elif action == PlayerAction.CHECK:
                self.checkers += 1
                log.info("Player checks: contribution = 0")
            elif action == PlayerAction.RAISE:
                contribution = min((3 * self.big_blind), self.current_player.bankroll)
                log.info(f"Player raises (3BB={3*self.big_blind}): contribution = {contribution}")
            self.current_player.bankroll -= contribution
            self.player_pots[self.current_player_idx] += contribution
            self.round_pot += contribution
            if self.player_pots[self.current_player_idx] == max(self.player_pots):
                self.min_call = self.player_pots[self.current_player_idx]
        else:
            log.error("No current player, cannot process decision!")

    def action(self) -> Optional[PlayerAction]:
        if self.current_player:
            # TODO: Make this work in the future once observations and info is actually implemented
            self.observe()
            return self.current_player.action(self.legal_moves, None, self.info())
        else:
            log.error("No current player, cannot take an action!")
            return None

    def observe(self):
        self.determine_legal_moves()

    def info(self):
        pass

    def deactivate_current_player(self):
        self.active_players[self.current_player_idx] = False
        log.info(f"Player {self.current_player_idx} is now inactive")

    def step(self, action: Optional[PlayerAction]) -> bool:
        if action is None:
            log.error("Cannot step game with action None!")
            raise ValueError("action should not be None")
        self.process_decision(action)
        self.next_player()
        if self.round == Round.SHOWDOWN:
            self.end_hand()
            self.start_new_hand()
            return False
        return True

    def determine_and_award_winner(self):
        # TODO: Change to handle ties
        winner: int = self.determine_winner()
        log.info(f"Player {winner} wins!")
        self.award_winner(winner)

    def determine_winner(self) -> int:
        ranks: list[int] = [0] * len(self.players)
        for index, player in enumerate(self.players):
            if self.active_players[index]:
                log.info(f"Player {index}'s cards: {player.cards}")
                all_cards: list[str] = player.cards.copy()
                all_cards.extend(self.community_cards)
                ranks[index] = rank_hand(all_cards)[1]
            else:
                ranks[index] = 7463
        # TODO: Check for ties, change return type to tuple/list
        return ranks.index(min(ranks))

    def award_winner(self, winner_index: int) -> None:
        self.players[winner_index].bankroll += self.community_pot
        log.info(f"Winner wins {self.community_pot}, and now has {self.players[winner_index].bankroll}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(name)s:%(funcName)s: %(message)s")
    game = PokerGame(1000, 5, 10)
    # game.add_players([RandomPlayer() for _ in range(4)])
    # game.add_players([RandomPlayer(), RandomPlayer(), HumanPlayer(), RandomPlayer()])
    game.add_players([HumanPlayer() for _ in range(4)])
    game.start_new_hand()
    cont: bool = True
    while cont is True:
        action: Optional[PlayerAction] = game.action()
        if action is not None:
            cont = game.step(action)
