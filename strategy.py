from collections import defaultdict

import random

from cardclasses import Guard, Priest, Baron, Maid, Prince, King, Countess, Princess


def clean_cards(move, wrong_guesses, seen_cards, player_to_move):

    if move.max_count > 1:
        for player in seen_cards:
            if move in seen_cards[player][player_to_move]:
                seen_cards[player][player_to_move].remove(move)
    else:
        # remove non-twin card all player's seen card
        for p1 in seen_cards:
            for p2 in seen_cards:
                if move in seen_cards[p1][p2]:
                    seen_cards[p1][p2].remove(move)

    if move not in wrong_guesses:
        del wrong_guesses[:]


def get_guess_card(users, current_player, seen_cards):
    # attack with guard if player knows opponent's card and opponent is not lost or under Maid defence
    for player in seen_cards[current_player]:
        if player != current_player and seen_cards[current_player][player] and not users[users.index(player)].lost and not users[users.index(player)].defence:
            for guess in seen_cards[current_player][player]:
                if guess.name != "Guard":
                    return player, guess
    return None, None


def get_optimal_move(current_player, available_moves, used_cards, wrong_guesses, users, seen_cards, hand, cards_left, real_players, **kwargs):

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
        princess: 1,
        Countess(): 1,
        king: 1,
        prince: 2,
        maid: 2,
        baron: 2,
        priest: 2,
        guard: 5,
    }
    # remove already used cards from cards counter
    for card, counter in used_cards.items():
        card_count[card] -= counter
        assert card_count[card] >= 0
    # remove cards in hand from cards counter
    for card in hand:
        card_count[card] -= 1
        assert card_count[card] >= 0

    available_moves.sort()
    left_players = [player for player in users if not player.lost and player != current_player]

    opponent = random.choice(left_players) or None

    # AI plays against single human player
    if real_players and real_players[0] != current_player and not real_players[0].defence and not real_players[0].lost:
        opponent = real_players[0]

    # build list of cards that were seen in player's hand
    watched_cards = []
    for player in seen_cards:
        if not users[users.index(player)].lost:
            for card in seen_cards[player][current_player]:
                watched_cards.append(card)

    # try:
    #     assert all(card in kwargs.get('playerHands')[current_player] for card in watched_cards)
    # except AssertionError:
    #     import pdb
    #     pdb.set_trace()
    #     raise

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

    victim, guess = get_guess_card(users, current_player, seen_cards)

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
            return baron, opponent, None

    # if priest and guard in hand, make move with priest
    if guard in available_moves and priest in available_moves:
        return priest, opponent, None

    # if one of current player's cards was seen by priest
    if available_moves[0] in watched_cards and used_cards[guard] < 5:
        return available_moves[0], opponent, None

    # if one of current player's cards was seen by priest
    if available_moves[1] in watched_cards and available_moves[1] != Princess() and used_cards[guard] < 5:
        if available_moves[0] == maid:
            return maid, None, None
        else:
            return available_moves[1], opponent, None

    # guard or maid
    if maid in available_moves and guard in available_moves:
        if cards_left <= 2:
            return guard, opponent, None
        else:
            return maid, None, None

    return available_moves[0], opponent, None