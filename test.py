from collections import defaultdict

import pytest

from game import LoveLetterState, PlayerCtl, Player
from cardclasses import Guard, King, Priest, Princess, Prince, Countess, Maid
from ismcts import ISMCTS
from strategy import get_guess_card


@pytest.fixture
def init_game():
    game = LoveLetterState(2)

    game.user_ctl = PlayerCtl(game.numberOfPlayers)
    player1, player2 = game.user_ctl.users[0], game.user_ctl.users[1]
    game.playerToMove = game.user_ctl.get_current_player()

    game.playerHands = defaultdict(list)
    game.currentTrick = []
    game.round_over = False
    game.deck = game.get_card_deck()
    return dict(locals())


def test_guard_when_card_is_known(init_game):
    """
    testing move with guard when opponent's card is known
    """
    game, player1, player2 = init_game['game'], init_game['player1'], init_game['player2']

    game.deck.remove(Guard())
    game.deck.remove(Guard())
    game.deck.remove(King())
    game.deck.remove(Priest())

    game.playerHands[player1].extend([Guard(), King()])
    game.playerHands[player2].append(Priest())

    game.seen_cards[player1][player2].append(Priest())

    assert ISMCTS(game, itermax=1000) == (Guard(), player2, Priest())


def test_not_playing_with_princess(init_game):
    """
    testing making move with second card if first one is Princess
    """
    game, player1, player2 = init_game['game'], init_game['player1'], init_game['player2']

    game.deck.remove(Princess())
    game.deck.remove(King())
    game.deck.remove(Priest())
    game.deck.remove(Guard())

    game.playerHands[player1].extend([Princess(), King()])
    game.playerHands[player2].append(Priest())

    assert ISMCTS(game, itermax=1000) == (King(), None, None)


def test_king_when_card_is_known(init_game):
    game, player1, player2 = init_game['game'], init_game['player1'], init_game['player2']

    game.playerHands[player1].extend([Princess(), King()])
    game.playerHands[player2].append(Priest())

    game.deck.append(Guard())

    game.deck.remove(Guard())
    game.deck.remove(Princess())
    game.deck.remove(King())
    game.deck.remove(Priest())

    game.do_move(King())

    assert ISMCTS(game, itermax=100) == (Guard(), player1, Priest())


def test_prince_when_pricess_is_known(init_game):
    game, player1, player2 = init_game['game'], init_game['player1'], init_game['player2']

    game.playerHands[player1].extend([Prince(), King()])
    game.playerHands[player2].append(Princess())
    game.seen_cards[player1][player2].append(Princess())

    game.deck.remove(Guard())
    game.deck.remove(Prince())
    game.deck.remove(King())
    game.deck.remove(Princess())

    assert(ISMCTS(game, itermax=100)[0] == Prince())


def test_priest_and_guard(init_game):
    game, player1, player2 = init_game['game'], init_game['player1'], init_game['player2']

    game.playerHands[player1].extend([King(), Guard()])
    game.seen_cards[player1][player2].append(Princess())

    game.deck.remove(Guard())
    game.deck.remove(Maid())
    game.deck.remove(King())
    game.deck.remove(Princess())

    game.playerHands[player2].append(Princess())

    game.do_move(King())
    assert game.seen_cards[player1][player2] == [Guard()]
