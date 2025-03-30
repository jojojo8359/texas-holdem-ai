import random
from phevaluator import evaluate_cards
from phevaluator.hash import hash_quinary


def denom_in_hand(denom: str, hand: list[str]) -> list[str]:
    if denom not in denominations:
        raise ValueError("Denomination " + denom + " is not a valid "
                         "denomination")
    result: list[str] = []
    for card in hand:
        if card.find(denom) != -1:
            result.append(card)
    return result


def draw_card(deck: list[str]) -> str:
    return deck.pop(random.randint(0, len(deck) - 1))


def has_royal_flush(hand: list[str]) -> bool:
    aces = denom_in_hand("A", hand)
    kings = denom_in_hand("K", hand)
    queens = denom_in_hand("Q", hand)
    jacks = denom_in_hand("J", hand)
    tens = denom_in_hand("T", hand)
    for suit in suits:
        if "A" + suit in aces and "K" + suit in kings and "Q" + suit in queens\
                and "J" + suit in jacks and "T" + suit in tens:
            return True
    return False


def has_straight_flush(hand: list[str]) -> bool:
    pass


def has_four_of_a_kind(hand: list[str]) -> bool:
    pass


def score_hand(hand: list[str]):
    if has_royal_flush(hand):
        return 22
    elif has_straight_flush(hand):
        return 21
    elif has_four_of_a_kind(hand):
        return 20


if __name__ == "__main__":
    deck: list[str] = generate_deck()
    hand: list[str] = []
    # hand.append(draw_card(deck))
    hand = ["Ah", "Th", "Kc", "Qh", "Jh", "3s", "6h"]
    # 6 5 4 3 2
    # quinary = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
    # print(len(quinary))
    # print(hash_quinary(quinary, 5))
    # print(evaluate_cards("6h", "5d", "4c", "3s", "2h"))
    # print(hand)
    # print(has_royal_flush(hand))
