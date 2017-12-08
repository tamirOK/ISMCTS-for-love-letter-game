from collections import defaultdict

import random

from cardclasses import Guard, Priest, Baron, Maid, Prince, King, Countess, Princess

move_matrix = None


def clean_cards(move, wrong_guesses, seen_cards, player_to_move):
    for player in seen_cards:
        if move in seen_cards[player][player_to_move]:
            seen_cards[player][player_to_move].remove(move)

    if not move in wrong_guesses:
        wrong_guesses.clear()


def get_guess_card(current_player, seen_cards):
    # attack with guard if player knows card
    victim = None
    for player in seen_cards[current_player]:
        if player != current_player and seen_cards[current_player][player] and not player.lost and not player.defence:
            for guess in seen_cards[current_player][player]:
                victim = player
                if guess.name != "Guard":
                    return player, guess
    return victim, None


def get_optimal_move(current_player, available_moves, used_cards, wrong_guesses, users, seen_cards, hand, cards_left, **kwargs):

    # if only one card is available, make move with the card
    if len(available_moves) == 1:
        return available_moves[0], None, None

    if kwargs.get('random', False):
        return random.choice(available_moves), None, None

    maid = Maid()
    guard = Guard()
    princess = Princess()
    priest = Priest()
    baron = Baron()
    prince = Prince()
    king = King()

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

    for card, counter in used_cards.items():
        card_count[card] -= counter
        assert card_count[card] >= 0

    for card in hand:
        card_count[card] -= 1
        assert card_count[card] >= 0

    available_moves.sort()
    opponent = users[0] if users[0] != current_player else users[1]

    watched_cards = []
    for player in seen_cards:
        if not player.lost:
            for card in seen_cards[player][current_player]:
                watched_cards.append(card)

    if opponent.defence:

        if guard in available_moves and priest in available_moves:
            if card_count[guard] > 0 and cards_left <= 1:
                return guard, None, None
            else:
                return priest, None, None

        if guard in available_moves and maid in available_moves:
            if card_count[guard] > 0:
                if maid in watched_cards:
                    return maid, None, None
            if cards_left <= 1:
                return guard, None, None
            else:
                return maid, None, None

        if prince in available_moves and card_count[guard] > 0 and prince in watched_cards:
            return prince, None, None

        if king in available_moves and card_count[guard] > 0 and king in watched_cards:
                return king, None, None

        return available_moves[0], None, None

    victim, guess = get_guess_card(current_player, seen_cards)

    # if player knows victim card and has guard in hand
    if guard in available_moves and guess:
        return guard, victim, guess

    # if player knows card of victim and can make move with Baron
    if victim:
        if baron == available_moves[0] and available_moves[1] > seen_cards[current_player][victim][0]:
            return baron, victim, None
        elif baron == available_moves[1] and available_moves[0] > seen_cards[current_player][victim][0]:
            return baron, victim, None
        # if players knows that victim holds Princess and has Prince
        elif princess in seen_cards[current_player][victim] and prince in available_moves:
            return prince, victim, None

    # decide when to play with baron
    if baron in available_moves:
        second_card = available_moves[0] if available_moves[0] != baron else available_moves[1]
        left_card_counter, gt_card_counter = 0, 0

        for card, counter in card_count.items():
            left_card_counter += counter
            if card < second_card:
                gt_card_counter += counter

        if gt_card_counter / left_card_counter >= 0.6:
            return baron, None, None

    # if priest and guard in hand, make move with priest
    if guard in available_moves and priest in available_moves:
        return priest, None, None

    # if one of current player's cards was seen by priest
    if available_moves[0] in watched_cards and used_cards[guard] < 5:
        return available_moves[0], None, None

    # if one of current player's cards was seen by priest
    if available_moves[1] in watched_cards and available_moves[1] != Princess() and used_cards[guard] < 5:
        if available_moves[0] == maid:
            return maid, None, None
        else:
            return available_moves[1], None, None

    # guard or maid
    if maid in available_moves and guard in available_moves:
        if cards_left <= 2:
            return guard, None, None
        else:
            return maid, None, None

    return available_moves[0], None, None