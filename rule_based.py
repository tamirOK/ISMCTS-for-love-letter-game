#coding=utf-8

import random

from cardclasses import Guard, Princess, Priest, Prince, Baron, Maid, Countess, King, card_dict
from strategy import get_guess_card


def get_move(state, ismcts=False):
    # TODO: fix multiple opponents case (selecting opponents)
    cards = state.playerHands[state.playerToMove]
    victim, guess = None, None
    maid = Maid()
    guard = Guard()
    princess = Princess()
    priest = Priest()
    baron = Baron()
    prince = Prince()
    king = King()
    countess = Countess()
    opponent = [player for player in state.user_ctl.users if player != state.playerToMove][0]
    twin_cards = [priest, baron, maid, priest]

    victim, guess = get_guess_card(state.user_ctl.users, state.playerToMove, state.seen_cards)

    card_count = {
        Princess(): 1,
        Countess(): 1,
        King(): 1,
        Prince(): 2,
        Maid(): 2,
        Baron(): 2,
        Priest(): 2,
        Guard(): 5,
    }
    # substract used cards
    for card, counter in state.used_cards.items():
        card_count[card] -= counter
        assert card_count[card] >= 0

    # substract cards in hand
    for card in state.playerHands[state.playerToMove]:
        card_count[card] -= 1
        assert card_count[card] >= 0

    def play_guard():
        """
        Selects probable guess when playing with Guard
        :return: probable guess card
        """
        available_cards = sorted([(counter, card) for card, counter in card_count.items() if card != guard], reverse=True)
        most_probable_cards = [card for counter, card in available_cards if counter == available_cards[0][0]]
        return random.choice(most_probable_cards)

    def get_probability(player_card):
        c = 0
        if card_count[player_card] > 0:
            for card in twin_cards:
                if card_count[card] == 2 or (card_count[card] == 1 and card in cards):
                    c += 1
            return 1 / c

        for card, counter in card_count.items():
            if counter > 0 or card in cards:
                c += 1

        return 1 / c

    def lose_with_baron(card):
        """
        Will the current player lose the game if he makes move with Baron
        :param card:
        :return:
        """
        if card != baron:
            return False
        if cards[0] == baron:
            if guess and cards[1] <= guess:
                return True
            if cards[1] <= baron:
                return True

        if cards[1] == baron:
            if guess and cards[0] <= guess:
                return True
            if cards[0] <= baron:
                return True

        return False

    # follow the rules about Countess
    if countess in cards:
        if king in cards:
            return king, None, None
        if prince in cards:
            return prince, None, None

    # if player has guard and knows an opponent's card
    if guard in cards and victim:
        return guard, victim, guess

    # if player knows an opponent's card and has a greater card
    if baron in cards and victim:
        if cards[0] == baron and cards[1] > guess:
            return baron, victim, None
        if cards[1] == baron and cards[0] > guess:
            return baron, victim, None

    # play with prince if player holds the princess
    if guess == princess and prince in cards:
        return prince, victim, None

    # make last move with minimal card
    if sum(card_count.values()) <= 2:
        card = min(cards)
        if card == guard:
            guess = play_guard()
        return min(cards), victim, guess

    # do not play with princess
    if cards[0] == princess:
        if cards[1] == guard:
            guess = play_guard()
        return cards[1], victim, guess

    # do not play with princess
    try:
        if cards[1] == princess:
            if cards[0] == guard:
                guess = play_guard()
            return cards[0], victim, guess
    except:
        import pdb
        pdb.set_trace()

    # if both cards are same, play any of them
    for card in card_dict.values():
        if cards.count(card) == 2:
            if card == guard:
                guess = play_guard()
            assert guess != guard
            return card, victim, guess

    # return seen card by an opponent if any
    for card in cards:
        # TODO: когда мы не видели карту, но нашего барона видели, а вторая карта слишком маленькая
        if not ismcts and card != guard and card in state.seen_cards[opponent][state.playerToMove] and card_count[guard] > 0 and not lose_with_baron(card):
            return card, victim, guess

    # Guard and Priest
    if not ismcts and guard in cards and priest in cards:
        return priest, victim, guess

    # check if twin card has high prob to be guessed
    for card in twin_cards:
        # TODO: когда мы не видели карту, но нашего барона видели, а вторая карта слишком маленькая
        if not ismcts and card in cards and get_probability(card) >= 0.5 and card_count[guard] > 0 and not lose_with_baron(card):
            return card, victim, guess

    # return nothing for ismcts algorithm
    if ismcts:
        return [None] * 3

    card = min(cards)
    if card == guard:
        guess = play_guard()
    if lose_with_baron(card):
        card = max(cards)
    return card, victim, guess
