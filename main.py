from util import rank_hand


if __name__ == "__main__":
    # Royal Flush - 7 cards
    hand = ["Ah", "Th", "Kh", "Qh", "Jh", "3s", "6h"]

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

    # hand = ["Js", "3h", "6d", "5d", "6s", "7s", "7c"]
    # rank_hand(hand)

    # hand = ["Ad", "Td", "6d", "5d", "6s", "7s", "7c"]
    # rank_hand(hand)

    # hand = ["9s", "Ah", "6d", "5d", "6s", "8s", "8c"]
    # hand = ["Ad", "2d", "3d", "4d", "5d", "7d", "9d"]
    # hand = ["2d", "2c", "2h", "2s", "3d"]
    # hand = ["2d", "2c", "2h", "3s", "3d"]
    # hand = ["Ad", "Kd", "Qd", "Jd", "9d"]
    # hand = ["2d", "3d", "4d", "5d", "7d"]
    # hand = ["2d", "3h", "4c", "5s", "As"]
    # hand = ["As", "Ad", "Ac", "Ks", "Qd"]
    # hand = ["2s", "2d", "2c", "3s", "4d"]
    # hand = ["As", "Ad", "Kc", "Ks", "Qd"]
    # hand = ["2s", "2d", "3c", "3s", "4d"]
    print(rank_hand(hand))
