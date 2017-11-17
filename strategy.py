from collections import defaultdict
from random import choice

from cardclasses import Guard, Priest, Baron, Maid, Prince, King, Countess, Princess


def buid_move_matrix():
    """
    :return: matrix with optimal moves for all possible states
    """
    move_matrix = defaultdict(lambda: defaultdict(lambda: None))
    guard = Guard()
    priest = Priest()
    baron = Baron()
    maid = Maid()
    prince = Prince()
    king = King()
    countess = Countess()
    princess = Princess()

    move_matrix[guard][guard] = guard
    move_matrix[guard][priest] = priest
    move_matrix[guard][baron] = guard
    move_matrix[guard][maid] = guard
    move_matrix[guard][prince] = guard
    move_matrix[guard][king] = guard
    move_matrix[guard][countess] = guard
    move_matrix[guard][princess] = guard

    move_matrix[priest][guard] = priest
    move_matrix[priest][priest] = priest
    move_matrix[priest][baron] = priest
    move_matrix[priest][maid] = priest
    move_matrix[priest][prince] = priest
    move_matrix[priest][king] = priest
    move_matrix[priest][countess] = priest
    move_matrix[priest][princess] = priest

    move_matrix[baron][guard] = guard
    move_matrix[baron][priest] = priest
    move_matrix[baron][baron] = baron
    move_matrix[baron][maid] = baron
    move_matrix[baron][prince] = baron
    move_matrix[baron][king] = baron
    move_matrix[baron][countess] = baron
    move_matrix[baron][princess] = baron

    move_matrix[maid][guard] = guard
    move_matrix[maid][priest] = priest
    move_matrix[maid][baron] = baron
    move_matrix[maid][maid] = maid
    move_matrix[maid][prince] = maid
    move_matrix[maid][king] = maid
    move_matrix[maid][countess] = maid
    move_matrix[maid][princess] = maid

    move_matrix[prince][guard] = guard
    move_matrix[prince][priest] = priest
    move_matrix[prince][baron] = baron
    move_matrix[prince][maid] = maid
    move_matrix[prince][prince] = prince
    move_matrix[prince][king] = prince
    move_matrix[prince][countess] = countess
    move_matrix[prince][princess] = prince

    move_matrix[king][guard] = guard
    move_matrix[king][priest] = priest
    move_matrix[king][baron] = baron
    move_matrix[king][maid] = maid
    move_matrix[king][prince] = prince
    move_matrix[king][countess] = countess
    move_matrix[king][princess] = king

    move_matrix[countess][guard] = guard
    move_matrix[countess][priest] = priest
    move_matrix[countess][baron] = baron
    move_matrix[countess][maid] = maid
    move_matrix[countess][prince] = countess
    move_matrix[countess][king] = countess
    move_matrix[countess][princess] = countess

    move_matrix[princess][guard] = guard
    move_matrix[princess][priest] = priest
    move_matrix[princess][baron] = baron
    move_matrix[princess][maid] = maid
    move_matrix[princess][prince] = prince
    move_matrix[princess][king] = king
    move_matrix[princess][countess] = countess

    return move_matrix


move_matrix = None


def clean_wrong_guesses(move, wrong_guesses):
    """
    Cleans wrong guesses made by other opponents if move is not in wrong_guesses
    :param move: current move
    :param wrong_guesses: list of wrong_guesses
    :return:
    """


def clean_cards(move, wrong_guesses, seen_cards, player_to_move):
    for player in seen_cards:
        if move in seen_cards[player][player_to_move]:
            seen_cards[player][player_to_move].remove(move)

    if not move in wrong_guesses:
        wrong_guesses.clear()


def remove_seen_card(seen_cards, current_player, card):
    for player in seen_cards:
        if card in seen_cards[player][current_player]:
            seen_cards[player][current_player].remove(card)


def get_guess_card(current_player, seen_cards):
    # attack with guard if player knows card
    for player in seen_cards[current_player]:
        if len(seen_cards[current_player][player]) == 2:
            print(current_player, player, seen_cards[current_player][player])
        assert len(seen_cards[current_player][player]) <= 1

        if seen_cards[current_player][player] and not player.lost and not player.defence:
            for guess in seen_cards[current_player][player]:
                if guess.name != "Guard":
                    return player, guess
    return None, None


def get_optimal_move(current_player, available_moves, used_cards, wrong_guesses, users, seen_cards):

    # if only one card is available, make move with the card
    if len(available_moves) == 1:
        return available_moves[0], None, None

    maid = Maid()
    guard = Guard()
    princess = Princess()
    priest = Priest()
    baron = Baron()

    victim, guess = get_guess_card(current_player, seen_cards)
    # for player in seen_cards[current_player]:
    #     if seen_cards[current_player][player] and not player.lost and not player.defence:
    #         victim = player
    #         guess = seen_cards[current_player][player][0]
    #         break

    if guard in available_moves and victim:
        return guard, victim, guess

    # if player knows card of victim and can make move with baron
    if victim:
        if baron == available_moves[0] and available_moves[1] > seen_cards[current_player][victim][0]:
            return baron, victim, None
        elif baron == available_moves[1] and available_moves[0] > seen_cards[current_player][victim][0]:
            return baron, victim, None

    # if priest and guard in hand, make move with priest
    if guard in available_moves and priest in available_moves:
        return priest, None, None

    watched_cards = []
    for player in seen_cards:
        if not player.lost:
            for card in seen_cards[player][current_player]:
                watched_cards.append(card)

    available_moves.sort()

    # if one of current player's cards were seen by priest
    if available_moves[0] in watched_cards:
        remove_seen_card(seen_cards, current_player, available_moves[0])
        return available_moves[0], None, None

    if available_moves[1] in seen_cards and available_moves[1] != Princess():
        if available_moves[0] == maid:
            return maid, None, None
        else:
            remove_seen_card(seen_cards, current_player, available_moves[1])
            return available_moves[1], None, None

    return available_moves[0], None, None

    global move_matrix
    if not move_matrix:
        move_matrix = buid_move_matrix()

    assert move_matrix[available_moves[0]][available_moves[1]] == move_matrix[available_moves[1]][available_moves[0]]
    return move_matrix[available_moves[0]][available_moves[1]]