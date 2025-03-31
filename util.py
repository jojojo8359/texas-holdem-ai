from phevaluator import evaluate_cards
from enum import Enum

suits: list[str] = ["d", "c", "s", "h"]
ranks: list[str] = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J",
                    "Q", "K", "A"]


class PlayerAction(Enum):
    FOLD = 0
    CHECK = 1
    CALL = 2
    RAISE = 3


class Round(Enum):
    PREFLOP = 0
    FLOP = 1
    TURN = 2
    RIVER = 3
    SHOWDOWN = 4


def get_rank(card: str) -> str:
    return card[0]


def get_suit(card: str) -> str:
    return card[1]


def rank_from_str(rank: str) -> int:
    """Convert a rank string (2-A) to an int (2-14)."""
    return ranks.index(rank) + 2


def rank_to_str(rank: int):
    """Convert a rank int (2-14) to a string (2-A)."""
    return ranks[rank - 2]


def get_rank_int(card: str) -> int:
    """Get a card's rank as an integer (2-14) from the full card representation ("Ah")."""
    return rank_from_str(get_rank(card))


def rank_hand(hand: list[str]) -> tuple[str, int]:
    r: int = evaluate_cards(*hand)
    rank = "Unknown Rank"
    if r == 1:
        rank = "Royal Flush"
    elif r <= 10:
        rank = "Straight Flush"
    elif r <= 10 + 156:
        rank = "Four of a Kind"
    elif r <= 10 + 156 + 156:
        rank = "Full House"
    elif r <= 10 + 156 + 156 + 1277:
        rank = "Flush"
    elif r <= 10 + 156 + 156 + 1277 + 10:
        rank = "Straight"
    elif r <= 10 + 156 + 156 + 1277 + 10 + 858:
        rank = "Three of a Kind"
    elif r <= 10 + 156 + 156 + 1277 + 10 + 858 + 858:
        rank = "Two Pair"
    elif r <= 10 + 156 + 156 + 1277 + 10 + 858 + 858 + 2860:
        rank = "One Pair"
    elif r <= 10 + 156 + 156 + 1277 + 10 + 858 + 858 + 2860 + 1277:
        rank = "High Card"
    else:
        pass
    return (rank, r)
