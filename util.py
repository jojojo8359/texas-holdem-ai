import logging
from phevaluator import evaluate_cards
from enum import Enum


class ColoredFormatter(logging.Formatter):
    white: str = "\x1b[38;20m"
    grey: str = "\x1b[90;20m"
    yellow: str = "\x1b[33;20m"
    red: str = "\x1b[31;20m"
    bold_red: str = "\x1b[31;1m"
    reset: str = "\x1b[0m"
    fmt: str = "%(levelname)s:%(name)s:%(funcName)s: %(message)s"

    FORMATS: dict[int, str] = {
        logging.DEBUG: grey + fmt + reset,
        logging.INFO: white + fmt + reset,
        logging.WARNING: yellow + fmt + reset,
        logging.ERROR: red + fmt + reset,
        logging.CRITICAL: bold_red + fmt + reset
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt: str = self.FORMATS.get(record.levelno, self.grey + "UNKNOWN:%(name)s:%(funcName)s: %(message)s" + self.reset)
        formatter: logging.Formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


suits: list[str] = ["d", "c", "s", "h"]
ranks: list[str] = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J",
                    "Q", "K", "A"]


class PlayerAction(Enum):
    FOLD = 0
    CHECK_CALL = 1
    RAISE = 2
    SMALL_BLIND = 3
    BIG_BLIND = 4


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


# TODO: Write card pretty conversions


def rank_hand(hand: list[str]) -> tuple[str, int, int]:
    r: int = evaluate_cards(*hand)
    rank = "Unknown Rank"
    rank_index = 0
    if r == 1:
        rank = "Royal Flush"
        rank_index = 10
    elif r <= 10:
        rank = "Straight Flush"
        rank_index = 9
    elif r <= 10 + 156:
        rank = "Four of a Kind"
        rank_index = 8
    elif r <= 10 + 156 + 156:
        rank = "Full House"
        rank_index = 7
    elif r <= 10 + 156 + 156 + 1277:
        rank = "Flush"
        rank_index = 6
    elif r <= 10 + 156 + 156 + 1277 + 10:
        rank = "Straight"
        rank_index = 5
    elif r <= 10 + 156 + 156 + 1277 + 10 + 858:
        rank = "Three of a Kind"
        rank_index = 4
    elif r <= 10 + 156 + 156 + 1277 + 10 + 858 + 858:
        rank = "Two Pair"
        rank_index = 3
    elif r <= 10 + 156 + 156 + 1277 + 10 + 858 + 858 + 2860:
        rank = "One Pair"
        rank_index = 2
    elif r <= 10 + 156 + 156 + 1277 + 10 + 858 + 858 + 2860 + 1277:
        rank = "High Card"
        rank_index = 1
    else:
        pass
    return (rank, r, rank_index)

# TODO: Write Monte-Carlo equity simulation
