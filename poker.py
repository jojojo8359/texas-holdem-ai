import random
from enum import Enum
from util import suits, ranks


class Action(Enum):
    NONE = 0
    CHECK = 1
    OPEN = 2
    FOLD = 3
    CALL = 4
    RAISE = 5


class Player:
    def __init__(self, game: "PokerGame", id: int):
        self.game: PokerGame = game
        self.id: int = id
        self.bankroll: int = 1000
        self.pocket: list[str] = []

    def draw_pocket(self, num_cards: int):
        for _ in range(num_cards):
            self.pocket.append(self.game.draw_card())

    def bet(self, amount: int):
        if amount > self.bankroll:
            raise ValueError("Cannot bet " + str(amount) + ", player has bankroll of " + str(self.bankroll))
        else:
            current_bet: int = self.game.bets[self.id] if self.id in list(self.game.bets.keys()) else 0
            self.game.bets[self.id] = amount
            self.bankroll -= amount - current_bet

    def do_bet(self, preflop: bool) -> Action:
        print("Base Player class cannot place a bet!")
        return Action.NONE

    def __str__(self) -> str:
        return "Player " + str(self.id) + ": " + ("Active" if self.id in self.game.active_players else "Not Active") + \
            ", Bankroll = " + str(self.bankroll) + ", Pocket Cards = " + str(self.pocket) + ", Current Bet = " + (str(self.game.bets[self.id]) if self.id in list(self.game.bets.keys()) else "No Bet")


class HumanPlayer(Player):
    def __init__(self, game: "PokerGame", id: int):
        super().__init__(game, id)

    def get_action(self, prompt: str) -> Action:
        i: str = input(prompt).strip().upper()
        for action in Action._member_names_[1:]:
            if i == action:
                r = Action[action]
                return r if r is not None else Action["NONE"]
        return Action["NONE"]

    def get_bet_amount(self, min: int, max: int) -> int:
        while True:
            i: str = input("Enter a bet amount: (" + str(min) + "-" + str(max) + ") ").strip()
            try:
                bet: int = int(i)
                if bet < min:
                    print("Bet must be greater than " + str(min) + "!")
                elif bet > max:
                    print("Bet must be less than " + str(max) + "!")
                else:
                    return bet
            except ValueError:
                print("Incorrect bet amount!")

    def do_bet(self, preflop: bool) -> Action:
        # TODO: Move some of this logic into base Player class (get_action, doing the betting, etc.)
        if self.id not in self.game.active_players:
            print("Player " + str(self.id) + " is not playing, skipping...")
            return Action.FOLD
        action: Action = Action.NONE
        choices: str = ""
        valid_actions: list[Action] = []
        if preflop and len(self.game.bets) == 0:
            choices = "(check, open) "
            valid_actions = [Action.CHECK, Action.OPEN]
        else:
            choices = "(fold, call, raise) "
            valid_actions = [Action.FOLD, Action.CALL, Action.RAISE]

        while action == Action.NONE:
            action = self.get_action("Player " + str(self.id) + "'s Turn: " + choices)
            if action not in valid_actions:
                action = Action.NONE
            if action == Action.NONE:
                print("Not a valid action, please try again.")

        game_max_bet: int = max(list(self.game.bets.values())) if len(self.game.bets) != 0 else 0

        if action == Action.CHECK:
            pass
        elif action == Action.OPEN:
            # Ask for bet amount
            self.bet(self.get_bet_amount(1, self.bankroll))
        elif action == Action.FOLD:
            # Do whatever you need to do to fold
            self.game.active_players.remove(self.id)
        elif action == Action.CALL:
            # Bet max amount so far
            self.bet(game_max_bet)
        elif action == Action.RAISE:
            # Ask for bet amount, make sure it's over max game bet
            self.bet(self.get_bet_amount(game_max_bet + 1, self.bankroll))
        return action


class PokerGame:
    def __init__(self, num_players: int):
        self.players: list[Player] = []
        self.active_players: list[int] = []
        self.deck: list[str] = []
        self.bets: dict[int, int] = {}
        self.community: list[str] = []

        self.rebuild_deck()
        for i in range(num_players):
            self.players.append(HumanPlayer(self, i))
            self.active_players.append(i)

    def rebuild_deck(self):
        self.deck = []
        for suit in suits:
            for number in ranks:
                self.deck.append(number + suit)

    def draw_card(self) -> str:
        return self.deck.pop(random.randint(0, len(self.deck) - 1))

    def bet_round(self, preflop: bool):
        bet_status = [Action.NONE for _ in range(len(self.players))]
        for i in range(len(self.players)):
            if i not in self.active_players:
                bet_status[i] = Action.FOLD
        i: int = 0
        print("Bet status: " + str(bet_status))
        while (Action.NONE in bet_status or Action.CHECK in bet_status) and len(self.active_players) > 1:
            self.print_state()
            print("Bet status: " + str(bet_status))
            bet_status[i] = self.players[i].do_bet(preflop)
            if bet_status[i] == Action.OPEN:
                bet_status[i] = Action.RAISE
            if bet_status[i] in [Action.RAISE, Action.OPEN]:
                for index, action in enumerate(bet_status):
                    if index == i:
                        continue
                    if action not in [Action.NONE, Action.FOLD]:
                        bet_status[index] = Action.NONE
            i = (i + 1) % len(self.players)

    def preflop(self):
        for player in self.players:
            player.draw_pocket(2)
        print("Pre-flop cards dealt")
        self.bet_round(True)

    def flop(self):
        for i in range(3):
            self.community.append(self.draw_card())
        print("Flop cards dealt")
        self.bet_round(False)

    def street(self):
        self.community.append(self.draw_card())
        print("Street card dealt")
        self.bet_round(False)

    def __str__(self) -> str:
        return "Game: Active Players = " + str(self.active_players) + ", Community Cards = " + str(self.community)

    def print_state(self) -> None:
        print(self)
        for player in self.players:
            print(player)


if __name__ == "__main__":
    game = PokerGame(4)
    game.print_state()
    game.preflop()
    game.flop()
    game.street()
    game.street()
    game.print_state()

# Winning:
# If general rank is the same between multiple people (i.e. 3 people have Two Pair):
# Look at cards in rank (i.e. one has 2x6 2x7, one has 2x6 2x7, one has 2x6 2x8) - 2x6 2x8 would win here
# Find hand with highest numeric rank: if cards found in rank match someone else, split pot
