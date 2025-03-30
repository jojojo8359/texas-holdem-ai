from util import rank_hand


if __name__ == "__main__":
    # Royal Flush - 7 cards
    # hand = ["Ah", "Th", "Kh", "Qh", "Jh", "3s", "6h"]

    # Royal Flush - 5 cards
    # hand = ["Ah", "Th", "Kh", "Qh", "Jh"]

    # Straight - 5 cards
    # hand = ["Ah", "Th", "Kh", "Qh", "Jc"]

    # High Card - 5 cards
    # hand = ["Tc", "4h", "7d", "Qc", "2s"]

    # Pair - 5 cards
    # hand = ["Kc", "Kh", "7d", "2c", "5s"]

    # Straight - 5 cards
    # hand = ["3c", "4h", "5d", "6c", "7s"]
    # hand = ["Ac", "2h", "3d", "4c", "5s"]

    hand = ["Js", "3h", "6d", "5d", "6s", "7s", "7c"]
    rank_hand(hand)

    hand = ["Ad", "Td", "6d", "5d", "6s", "7s", "7c"]
    rank_hand(hand)

    hand = ["9s", "Ah", "6d", "5d", "6s", "8s", "8c"]
    rank_hand(hand)
