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


def get_optimal_move(available_moves, used_cards, wrong_guesses, users, seen_cards):

    return choice(available_moves)
    global move_matrix
    if not move_matrix:
        move_matrix = buid_move_matrix()

    if len(available_moves) == 1:
        return moves[0]
    assert move_matrix[available_moves[0]][available_moves[1]] == move_matrix[available_moves[1]][available_moves[0]]
    return move_matrix[available_moves[0]][available_moves[1]]