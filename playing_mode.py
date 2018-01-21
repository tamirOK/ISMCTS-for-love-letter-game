from typing import List, Tuple

from cardclasses import Guard, Priest, Baron, Maid, Prince, King, Countess, Princess, card_dict, Card
from ismcts import Smart_ISMCTS, ISMCTS
from player import Player
from uct import Determinized_UCT


class PlayingMode:

    @staticmethod
    def __get_single_player_move(state: 'LoveLetterState') -> Tuple[Card, Player, Card]:
        """
        User selects card and victim.
        :param state:
        :return: Move that user selected, victim that user selected, and card to guess (for Guard only)
        """
        card = None

        print("\nNow is your turn, {}. Choose card to move:".format(state.playerToMove))
        print("[", " ".join(str(card) for card in state.get_moves()), "]")

        # deactivate defense from previous move
        state.playerToMove.defence = False

        move_index = int(input())
        move = state.get_moves()[move_index]

        # simple case when player does not need to select victim
        if move == Countess():
            return move, None, card

        # if maid is selected, activate it on player
        if move == Maid():
            return move, state.playerToMove, card

        print("Now select victim")
        left_players = [player for player in state.user_ctl.users
                        if not player.defence and not player.lost]
        print(left_players)
        victim_index = int(input())

        if move == Guard():
            print("Select card to guess:")
            selected_card = str(input())
            card = card_dict[selected_card]

        return move, left_players[victim_index], card

    def __init__(self, state, mode):
        self.state = state

        if mode == "real_player":
            self.real_player = self.state.user_ctl.users[0]
            self.state.real_players.append(self.real_player)
            self.get_data = self.__play_with_real_payer
            self.smart_ismcts = Smart_ISMCTS()

            print("You are {}".format(self.real_player))
            print("Your hand is: [", ",".join(str(card) for card in self.state.playerHands[self.real_player]), "]")

        elif mode == "compare_bots":
            self.smart_ismcts = Smart_ISMCTS()
            self.plain_ismct = ISMCTS()
            self.uct = Determinized_UCT()
            self.get_data = self.__compare_bots

            self.player1 = self.state.user_ctl.users[0]
            self.player2 = self.state.user_ctl.users[1]

            print("{} plays using smart ISMCTS".format(self.player2))
            print("{} plays using determinized UCT".format(self.player1))

    def __play_with_real_payer(self, iterations):
        if self.state.playerToMove == self.real_player:
            move, opponent, guess_card = self.__get_single_player_move(self.state)
            print("You play with {}".format(move))
            return move, opponent, guess_card
        else:
            return self.smart_ismcts.get_move(rootstate=self.state, itermax=1000)

    def __compare_bots(self, iterations):
        if self.state.playerToMove == self.player1:
            return self.uct.get_move(rootstate=self.state, itermax=iterations)
        else:
            return self.smart_ismcts.get_move(rootstate=self.state, itermax=1000)

    def get_move(self, iterations):
        return self.get_data(iterations)