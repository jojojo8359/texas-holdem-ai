import logging
from util import PlayerAction, Round, suits, ranks, rank_hand
from typing import Optional
from agents.player import Player

import numpy as np

log = logging.getLogger(__name__)


class PokerGame:
    def __init__(self, initial_bankroll: int, small_blind: int, big_blind: int):
        # Game attributes - shouldn't change after initialization
        self.rng: np.random.Generator = np.random.Generator(np.random.PCG64(None))
        self.initial_bankroll: int = initial_bankroll
        self.small_blind: int = small_blind
        self.big_blind: int = big_blind

        # Players should be added before starting a hand, and shouldn't change between hands
        self.players: list[Player] = []

        self.done: bool = False
        self.active_players: list[bool] = []
        self.current_player: Optional[Player] = None
        self.current_player_idx: int = 0
        self.dealer_idx: int = 0

        self.round: Round = Round.PREFLOP
        self.community_pot: int = 0
        self.round_pot: int = 0
        self.player_pots: list[int] = []

        self.deck: list[str] = []
        self.community_cards: list[str] = []

        self.checkers: int = 0
        self.min_call: int = 0

        self.legal_moves: list[PlayerAction] = []

    def set_rng(self, gen: np.random.Generator) -> None:
        """
        Replace the game's random number generator with an external one.

        This is meant to be called when the Gym environment re-seeds its generator.
        """
        self.rng = gen

    def generate_deck(self) -> None:
        """Reset the game's deck to having all 52 cards."""
        self.deck = [rank + suit for suit in suits for rank in ranks]

    def add_players(self, players: list[Player]) -> None:
        """Add a list of players to the game. Players should be `Player` sub-classes."""
        for player in players:
            self.add_player(player)

    def add_player(self, player: Player) -> None:
        """
        Add a "Player" sub-class to the game.

        The player instance will have all of its internal attributes initialized.
        """
        player.bankroll = self.initial_bankroll
        player.actions = []
        player.cards = []
        player.seat = len(self.players)
        self.players.append(player)
        log.debug(f"Player added: {player.name} at seat #{player.seat}, has {player.bankroll} chips in bankroll")

    def draw_card(self) -> str:
        """Draw a random card from the game's deck, remove it, and return it."""
        return self.deck.pop(self.rng.integers(0, len(self.deck)))

    def deal_new_cards(self) -> None:
        """Deal two cards to all active players in the game (as a part of the pre-flop round)."""
        for player in self.players:
            # TODO: Take players who aren't playing into account - if a player has no bankroll left, they can't play and shouldn't be dealt cards
            # Rather - change direct bankroll check into checking active player list directly
            player.cards = []
            if player.bankroll <= 0:
                continue
            for _ in range(2):
                player.cards.append(self.draw_card())
            log.info(f"Player {player.seat} drew {player.cards}")

    def deal_cards_to_table(self, num_cards: int) -> None:
        """Deal a variable number of cards to the table."""
        for _ in range(num_cards):
            self.community_cards.append(self.draw_card())
        log.info(f"Dealer drew {num_cards} card{'s' if num_cards > 1 else ''} to table: {self.community_cards}")

    def start_new_hand(self) -> None:
        """
        Start a new hand of Texas Hold'em, starting with the pre-flop round.

        Also handles resetting the game state to prepare for the new hand.
        """
        if len(self.players) < 2 or len(self.players) > 8:
            raise RuntimeError(f"Cannot start a hand with {len(self.players)} players - must be between 2 and 8. Use add_player() to add a new player to the game.")
        # TODO: Implement game over condition
        # if (game over condition):
        #     self.done = True
        #     self.info("Game over!")
        #     return
        log.info("Starting new hand...")
        self.round = Round.PREFLOP
        self.community_cards = []
        self.community_pot = 0
        # Set current player to the dealer - this way, starting preflop round will advance to the person after dealer (small blind)
        self.current_player_idx = self.dealer_idx
        self.current_player = self.players[self.current_player_idx]
        # TODO: Take into account players that have no bankroll -> reconstruct active players list with checking
        self.active_players = [True] * len(self.players)
        self.player_pots = [0] * len(self.players)
        self.generate_deck()
        self.deal_new_cards()
        self.start_round()

    def end_hand(self) -> None:
        """
        End the current hand of Texas Hold'em. Includes the showdown round..

        Determines the winner of the current hand and manages pots and bankrolls accordingly.
        """
        self.close_pots()
        log.info(f"Final community pot: {self.community_pot}")
        log.info(f"Final community cards: {self.community_cards}")
        self.showdown()
        # Move dealer one position
        # TODO: Take into account players that have no bankroll? -> while loop
        self.dealer_idx = (self.dealer_idx + 1) % len(self.players)

    def start_round(self) -> None:
        """
        Start the current round of betting, after doing the appropriate pre-round actions.

        Before returning, will handle blind bets (pre-flop) and dealing table cards (other rounds).
        """
        self.checkers = 0
        self.min_call = 0
        if self.round == Round.PREFLOP:
            log.info("Starting round: Preflop")
            # Only advance past dealer if not playing with 2 players - this way with 2 players the dealer will bet small blind
            if len(self.players) != 2:
                self.next_player()
            self.process_decision(PlayerAction.SMALL_BLIND)
            self.next_player()
            self.process_decision(PlayerAction.BIG_BLIND)
            # Start preflop betting with dealer
            self.current_player_idx = self.dealer_idx
            self.current_player = self.players[self.current_player_idx]
        elif self.round in [Round.FLOP, Round.TURN, Round.RIVER]:
            log.info(f"Starting round: {'Flop' if self.round == Round.FLOP else ('Turn' if self.round == Round.TURN else 'River')}")
            if self.round == Round.FLOP:
                self.deal_cards_to_table(3)
            elif self.round in [Round.TURN, Round.RIVER]:
                self.deal_cards_to_table(1)
            # Start other betting rounds with small blind (dealer + 1 position clockwise)
            # Do this by setting current player to dealer and then advancing one position - this will take into account folded players
            self.current_player_idx = self.dealer_idx
            self.next_player()
        else:
            log.info("Starting showdown")
            return
        log.info(f"Player {self.current_player_idx} will start betting - starting betting round!")

    def end_round(self) -> None:
        """
        End the current round of betting.

        Will manage player/round/community pots as needed, and then set up the game to run the next round of betting.
        """
        self.close_pots()

        self.round = Round(self.round.value + 1)
        log.info("Round over!")

    def close_pots(self) -> None:
        """
        Do the following to clean up game pots at the end of a betting round:

        - Add the round pot to the community pot.
        - Reset the round pot.
        - Reset individual player pots.
        """
        self.community_pot += self.round_pot
        self.round_pot = 0
        self.player_pots = [0] * len(self.players)

    def next_player(self) -> None:
        """
        Determine the next player and allow them to bet next. Skips inactive players.

        The game must have a current player set before calling this method.

        Will switch rounds if the game's current state allows for it (all players check, one player left to bet, or all players call to same amount).
        """
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
                log.debug("Not all players have bet the same amount, continuing betting...")
                cont = False
                break
        if cont:
            log.info("All players have bet the same amount, moving to next round...")
            self.end_round()
            self.start_round()
            return

        while True:
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
            if self.active_players[self.current_player_idx]:
                break

        # Successful switch
        if not self.current_player:
            # Round should start with a current player (dealer)
            self.current_player_idx = 0
            log.error("No current player - make sure a current player is set before attempting to advance players!")
            log.error("Moving to player 0...")
        self.current_player = self.players[self.current_player_idx]
        log.info(f"Moved to player {self.current_player_idx}")

    def determine_legal_moves(self) -> None:
        """Update the set of legal moves for the current player given the game's state."""
        self.legal_moves = []
        self.legal_moves.append(PlayerAction.FOLD)
        if self.player_pots[self.current_player_idx] == max(self.player_pots):
            self.legal_moves.append(PlayerAction.CHECK)
        else:
            self.legal_moves.append(PlayerAction.CALL)
        if self.current_player:
            if self.current_player.bankroll > 0:
                self.legal_moves.append(PlayerAction.RAISE)
        else:
            log.error("No current player, cannot determine legal moves!")
        self.dump_state()

    def dump_state(self) -> None:
        """Log the game's current state (at debug level). Useful for providing info before a human player's bet."""
        log.debug(f"Current legal moves: {self.legal_moves}")
        log.debug(f"Current player: {self.current_player_idx} (dealer = {self.dealer_idx}, sb = {(self.dealer_idx + 1) % len(self.players)}, bb = {(self.dealer_idx + 2) % len(self.players)})")
        log.debug(f"Active players: {self.active_players}")
        log.debug(f"Player pots: {self.player_pots}")
        log.debug(f"Pots: Round = {self.round_pot} | Community = {self.community_pot} | Min Call = {self.min_call}")
        if self.current_player:
            log.debug(f"Current player cards: {self.current_player.cards + self.community_cards} | Rank = {rank_hand(self.current_player.cards + self.community_cards) if len(self.current_player.cards + self.community_cards) >= 5 else 'Not enough cards to rank'}")

    def process_decision(self, action: PlayerAction) -> None:
        """Process a player's decision by updating the game's state based on the requested player action."""
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
                contribution = min((3 * self.big_blind) + self.min_call, self.current_player.bankroll)
                log.info(f"Player raises (3BB={3*self.big_blind}): contribution = {contribution}")
            self.current_player.bankroll -= contribution
            self.player_pots[self.current_player_idx] += contribution
            self.round_pot += contribution
            if self.player_pots[self.current_player_idx] == max(self.player_pots):
                self.min_call = self.player_pots[self.current_player_idx]
            # TODO: Log players' actions in their own history array, clear when a round starts
        else:
            log.error("No current player, cannot process decision!")

    def action(self) -> Optional[PlayerAction]:
        """
        Request the current player to make a decision given the current set of legal actions, an observation of the game state, and additional info.

        Calls the current player's `action()` method (in the `Player` subclass).
        """
        if self.current_player:
            # TODO: Make this work in the future once observations and info is actually implemented
            # Make sure that observe() is called before action to update the set of legal moves!
            self.observe()
            return self.current_player.action(self.legal_moves, None, self.info())
        else:
            log.error("No current player, cannot take an action!")
            return None

    def observe(self) -> None:
        # TODO: Return something useful
        self.determine_legal_moves()

    def info(self) -> None:
        # TODO: Return something useful
        pass

    def deactivate_current_player(self) -> None:
        """Set the current player to be inactive in the current round."""
        self.active_players[self.current_player_idx] = False
        log.info(f"Player {self.current_player_idx} is now inactive")

    def step(self, action: Optional[PlayerAction]) -> None:
        """Advance the game by one step given an action for the current player to take."""
        if action is None:
            log.error("Cannot step game with action None!")
            raise ValueError("action should not be None")
        self.process_decision(action)
        self.next_player()
        if self.round == Round.SHOWDOWN:
            self.end_hand()
            self.start_new_hand()

    def showdown(self) -> None:
        """Determine the winner of the current round and award them the proper win total."""
        # TODO: Change to handle ties
        winner: int = self.determine_winner()
        log.info(f"Player {winner} wins!")
        self.players[winner].bankroll += self.community_pot
        log.info(f"Winner wins {self.community_pot}, and now has {self.players[winner].bankroll}")

    def determine_winner(self) -> int:
        """Determine the winner of the current round."""
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
