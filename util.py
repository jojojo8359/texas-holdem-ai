suits: list[str] = ["d", "c", "s", "h"]
ranks: list[str] = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J",
                    "Q", "K", "A"]


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


# TODO: Cite
def evaluate_rank_by_highest_cards(cards: list[str],
                                   excludeCardValue: int = -1,
                                   excludeCardValue2: int = -1,
                                   limitCheck: int = 7,
                                   normalize: float = 433175.0):
    i: int = 0
    sum: float = 0
    fixedSize: int = len(cards) - 1
    for j in range(fixedSize, -1, -1):
        cardValue: int = get_rank_int(cards[j])
        if cardValue == excludeCardValue or cardValue == excludeCardValue2:
            continue
        normalizedValue: int = cardValue - 2
        sum += normalizedValue * (13 ** (fixedSize - i - 1))
        if i == limitCheck - 1:
            break
        i += 1
    return sum / normalize


def rank_hand(hand: list[str]) -> tuple[str, float, list[str]]:
    # Assuming for now that a "hand" is 7 cards, for pocket + table
    hand.sort(key=lambda card: ranks.index(card[0]))
    print(hand)
    dupCount: int = 1
    seqCount: int = 1
    seqCountMax: int = 1
    maxCardValue: int = -1
    # dupValue: int = -1
    seqMaxValue: int = -1
    currCardValue: int = -1
    nextCardValue: int = -1
    # currCardSuit: str = ""
    # nextCardSuit: str = ""
    # Check for Highest Card, Pair, 2 Pair, Three of a Kind, Four of a Kind
    handSize = len(hand)
    maxCardValue = get_rank_int(hand[handSize - 1])
    duplicates: list[list[int]] = []
    rankCards: list[str] = []
    rankName: str = ""
    rank: float = 0.0
    for i in range(handSize - 1):
        currCardValue = get_rank_int(hand[i])
        # currCardSuit = get_suit(hand[i])
        nextCardValue = get_rank_int(hand[i + 1])
        # nextCardSuit = get_suit(hand[i + 1])
        # Check for duplicates
        if currCardValue == nextCardValue:
            dupCount += 1
            # dupValue = currCardValue
        elif dupCount > 1:
            duplicates.append([dupCount, currCardValue])
            dupCount = 1

        if currCardValue + 1 == nextCardValue:
            seqCount += 1
        elif currCardValue != nextCardValue:
            if seqCount > seqCountMax:
                seqCountMax = seqCount
                seqMaxValue = currCardValue
            seqCount = 1

    if seqCount > seqCountMax:
        seqCountMax = seqCount
        seqMaxValue = nextCardValue

    if dupCount > 1:
        duplicates.append([dupCount, nextCardValue])

    rankName = ""
    rank = 0.0
    rankCards = []

    # Check for Royal Flush (rank 900)
    if get_rank(hand[handSize - 1]) == "A" and get_rank(hand[handSize - 2]) == "K" and\
            get_rank(hand[handSize - 3]) == "Q" and get_rank(hand[handSize - 4]) == "J" and\
            get_rank(hand[handSize - 5]) == "T" and\
            get_suit(hand[handSize - 1]) == get_suit(hand[handSize - 2]) and\
            get_suit(hand[handSize - 1]) == get_suit(hand[handSize - 3]) and\
            get_suit(hand[handSize - 1]) == get_suit(hand[handSize - 4]) and\
            get_suit(hand[handSize - 1]) == get_suit(hand[handSize - 5]):
        rankName = "Royal Flush"
        rank = 900
        rankCards.extend(hand[(handSize - 5):])
    else:
        # Check for Straight Flush (rank [800, 900))
        for suit in suits:
            suitCards = [card for card in hand if get_suit(card) == suit]
            if len(suitCards) >= 5:
                counter: int = 1
                lastValue: int = -1
                for i in range(len(suitCards) - 1):
                    if get_rank_int(suitCards[i]) + 1 == get_rank_int(suitCards[i + 1]):
                        counter += 1
                        lastValue = get_rank_int(suitCards[i + 1])
                        rankCards.append(suitCards[i])
                    else:
                        counter = 1
                        rankCards.clear()
                if counter >= 5:
                    rankName = "Straight Flush"
                    rank = 800 + lastValue / 14 * 99
                elif counter == 4 and lastValue == 5 and get_rank_int(suitCards[len(suitCards) - 1]) == 14:
                    rankName = "Straight Flush"
                    rank = 835.3571
        if rankName == "":
            duplicates.sort(key=lambda x: x[0])
            if len(duplicates) > 0 and duplicates[0][0] == 4:
                rankName = "Four of a kind"
                rank = 700 + duplicates[0][1] / 14 * 50 + evaluate_rank_by_highest_cards(hand, duplicates[0][1], -1, 1)
                for suit in suits:
                    rankCards.append(rank_to_str(duplicates[0][1]) + suit)
            # Check for Full House (rank [600, 700))
            elif len(duplicates) > 2 and duplicates[0][0] == 3 and duplicates[1][0] == 2 and duplicates[2][0] == 2:
                rankName = "Full House"
                maxTmpValue = max(duplicates[1][1], duplicates[2][1])
                rank = 600 + duplicates[0][1] + maxTmpValue / 14
                for i in range(3):
                    rankCards.append(rank_to_str(duplicates[0][1]))
                for i in range(2):
                    rankCards.append(rank_to_str(maxTmpValue))
            elif len(duplicates) > 1 and ((duplicates[0][0] == 3 and duplicates[1][0] == 2) or (duplicates[1][0] == 3 and duplicates[0][0] == 2)):
                rankName = "Full House"
                rank = 600 + duplicates[0][1] + duplicates[1][1] / 14
                for i in range(3):
                    rankCards.append(rank_to_str(duplicates[0][1] if duplicates[0][0] == 3 else duplicates[1][1]))
                for i in range(2):
                    rankCards.append(rank_to_str(duplicates[1][1] if duplicates[1][0] == 2 else duplicates[0][1]))
            elif len(duplicates) > 1 and duplicates[0][0] == 3 and duplicates[1][0] == 3:
                rankName = "Full House"
                rank1: float = 600 + duplicates[0][1] + duplicates[1][1] / 14
                rank2: float = 600 + duplicates[1][1] + duplicates[0][1] / 14
                if rank1 > rank2:
                    rank = rank1
                    for i in range(3):
                        rankCards.append(rank_to_str(duplicates[0][1]))
                    for i in range(2):
                        rankCards.append(rank_to_str(duplicates[1][1]))
                else:
                    rank = rank2
                    for i in range(3):
                        rankCards.append(rank_to_str(duplicates[1][1]))
                    for i in range(2):
                        rankCards.append(rank_to_str(duplicates[0][1]))
            else:
                # Check for Flush (rank [500, 600))
                for suit in suits:
                    suitCards = [card for card in hand if get_suit(card) == suit]
                    suitCardsLen: int = len(suitCards)
                    if suitCardsLen >= 5:
                        suitCardsResult = suitCards[(suitCardsLen - 5):]
                        rankName = "Flush"
                        rank = 500 + evaluate_rank_by_highest_cards(suitCardsResult)
                        rankCards.clear()
                        rankCards.extend(suitCardsResult)
                        break
                if rankName == "":
                    # Check for Straight (rank [400, 500))
                    if seqCountMax >= 5:
                        rankName = "Straight"
                        rank = 400 + seqMaxValue / 14 * 99
                        for i in range(seqMaxValue, seqMaxValue - seqCountMax, -1):
                            rankCards.append(rank_to_str(i))
                    elif seqCountMax == 4 and seqMaxValue == 5 and maxCardValue == 14:
                        rankName = "Straight"
                        rank = 435.3571
                        rankCards.append("A")
                        for i in range(2, 6):
                            rankCards.append(rank_to_str(i))
                    # Check for Three of a kind (rank [300, 400))
                    elif len(duplicates) > 0 and duplicates[0][0] == 3:
                        rankName = "Three of a kind"
                        rank = 300 + duplicates[0][1] / 14 * 50 + evaluate_rank_by_highest_cards(hand, duplicates[0][1])
                        for i in range(3):
                            rankCards.append(rank_to_str(duplicates[0][1]))
                    # Check for Two Pairs (rank [200, 300))
                    elif len(duplicates) > 1 and duplicates[0][0] == 2 and duplicates[1][0] == 2:
                        rankName = "Two Pairs"
                        # print(duplicates)
                        if len(duplicates) > 2 and duplicates[2][0] == 2:
                            threePairsValues = [duplicates[0][1], duplicates[1][1], duplicates[2][1]]
                            threePairsValues.sort(reverse=True)
                            rank = 200 + ((threePairsValues[0] ** 2) / 392 + (threePairsValues[1] ** 2) / 392) * 50 + \
                                evaluate_rank_by_highest_cards(hand, threePairsValues[0], threePairsValues[1])
                            rankCards.append(rank_to_str(threePairsValues[0]))
                            rankCards.append(rank_to_str(threePairsValues[1]))
                        else:
                            # print(evaluate_rank_by_highest_cards(hand, duplicates[0][1], duplicates[1][1]))
                            rank = 200 + (((duplicates[0][1] ** 2) / 392) + ((duplicates[1][1] ** 2) / 392)) * 50 + \
                                evaluate_rank_by_highest_cards(hand, duplicates[0][1], duplicates[1][1])
                            for i in range(2):
                                rankCards.append(rank_to_str(duplicates[0][1]))
                            for i in range(2):
                                rankCards.append(rank_to_str(duplicates[1][1]))
                    # Check for One Pair (rank [100, 200))
                    elif len(duplicates) > 0 and duplicates[0][0] == 2:
                        rankName = "Pair"
                        rank = 100 + duplicates[0][1] / 14 * 50 + \
                            evaluate_rank_by_highest_cards(hand, duplicates[0][1], -1, 3)
                        for i in range(2):
                            rankCards.append(rank_to_str(duplicates[0][1]))
                    # Otherwise, it's a High Card (rank [0, 100))
                    else:
                        rankName = "High Card"
                        rank = evaluate_rank_by_highest_cards(hand, -1, -1, 5)
                        rankCards.append(rank_to_str(maxCardValue))
    print(rankName + ", rank = " + str(rank) + ", cards = " + str(rankCards))
    return (rankName, rank, rankCards)
