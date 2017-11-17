# -*- coding: utf-8 -*-

from collections import defaultdict
from copy import deepcopy
import random
from typing import List, Tuple

from cardclasses import Guard, Priest, Baron, Maid, Prince, King, Countess, Princess, card_dict, Card
from ismcts import ISMCTS
from player import Player, PlayerCtl
from strategy import clean_cards


class LoveLetterState:
    """
     A state of the game love letter.
    """

    def __init__(self, n: str) -> None:
        """ Initialise the game state which are constant during the game. 
            n is the number of players (from 2 to 4).
        """
        self.numberOfPlayers = n
        self.used_cards = defaultdict(int)  # Stores the cards that have been played already in this round
        self.tricksTaken = defaultdict(int)  # Number of tricks taken by each player
        self.round = 0
        self.game_over = False
        self.wrong_guesses = defaultdict(list)
        self.seen_cards = defaultdict(lambda: defaultdict(list))
        self.real_players = []

    def select_outcard(self) -> 'Card':
        """
        Choosing outcard with uniform probability
        :return: out_card
        """
        unique_cards = list(set(self.deck))
        return random.choice(unique_cards)

    def get_winner(self):
        winner = self.user_ctl.users[0] if self.user_ctl.users[0].won_round else self.user_ctl.users[1]
        assert winner
        return winner

    def clone(self) -> 'LoveLetterState':
        """ Create a deep clone of this game state.
        """
        st = LoveLetterState(self.numberOfPlayers)
        st.round = self.round
        st.playerHands = defaultdict(list)
        st.used_cards = deepcopy(self.used_cards)
        st.currentTrick = deepcopy(self.currentTrick)
        st.tricksTaken = deepcopy(self.tricksTaken)
        st.seen_cards = deepcopy(self.seen_cards)
        st.round_over = self.round_over
        st.wrong_guesses = deepcopy(self.wrong_guesses)
        st.game_over = self.game_over
        st.deck = st.get_card_deck()

        for card, counter in st.used_cards.items():
            for _ in range(counter):
                st.deck.remove(card)

        random.shuffle(st.deck)
        st.user_ctl = self.user_ctl.clone()
        st.playerToMove = st.user_ctl.users[st.user_ctl.users.index(self.playerToMove)]

        return st

    def clone_and_randomize(self) -> 'LoveLetterState':
        """ Create a deep clone of this game state, randomizing any information not visible to the specified observer player.
        """
        st = self.clone()
        assert len(self.playerHands[self.playerToMove]) == 2
        # assign same card for current user
        st.playerHands[st.playerToMove] = deepcopy(self.playerHands[self.playerToMove])
        # remove current player's cards from deck
        for card in self.playerHands[self.playerToMove]:
            st.deck.remove(card)

        # assign random cards for other users
        for user in st.user_ctl.users:
            if user != st.playerToMove and not user.lost:
                if st.seen_cards[st.playerToMove][user]:
                    taken_card = random.choice(st.seen_cards[st.playerToMove][user])
                    st.playerHands[user].append(taken_card)
                    st.deck.remove(taken_card)
                else:
                    user.take_card(st)

        # select outcard
        st.out_card = st.deck.pop()

        return st

    def add_seen_card(self, _from, to, card):
        if not self.seen_cards[_from][to] or self.seen_cards[_from][to][-1] != card:
            self.seen_cards[_from][to].append(card)

    def get_moves(self) -> List[Card]:
        """
        :return: list of available moves for current user 
        """
        available_moves = self.playerHands[self.playerToMove]

        # countess and king or countess and prince are in hand, return move with countess card
        if Countess() in available_moves and (King() in available_moves or Prince() in available_moves):
            return [Countess()]

        return available_moves

    def get_card_deck(self) -> List[Card]:
        """ Construct a standard deck of 16 cards.
        """
        return [Princess(),
                Countess(),
                King(),
                Prince(),
                Prince(),
                Maid(),
                Maid(),
                Baron(),
                Baron(),
                Priest(),
                Priest(),
                Guard(),
                Guard(),
                Guard(),
                Guard(),
                Guard()]

    def start_new_round(self, first_player: 'Player'=None) -> None:
        """
        :param first_player: player(instance of User class) who starts current round. If None, then random player starts round 
        :return:  
        """
        self.round += 1
        self.round_over = False

        if not hasattr(self, "user_ctl"):
            self.user_ctl = PlayerCtl(self.numberOfPlayers)
            self.user_ctl.shuffle()
        else:
            self.user_ctl.reset()

        self.deck = self.get_card_deck()
        random.shuffle(self.deck)
        # remove one card from deck and remember it
        self.out_card = self.deck.pop()
        self.playerHands = {user: [] for user in self.user_ctl.users}
        #  if there is winner in previous round, then he or she starts the next round
        if first_player:
            # place player on first position in player list
            for index, user in enumerate(self.user_ctl.users):
                if index > 0 and user == first_player:
                    self.user_ctl.users[index], self.user_ctl.users[0] = self.user_ctl.users[0], user
                    break

        self.used_cards = defaultdict(int)
        self.currentTrick = []
        self.wrong_guesses = defaultdict(list)
        self.seen_cards = defaultdict(lambda: defaultdict(list))

        for user in self.user_ctl.users:
            user.take_card(self)

        # player who makes move takes second card
        self.playerToMove = self.user_ctl.get_current_player()
        self.playerToMove.take_card(self)

        if self.real_players and self.user_ctl.users[0] != self.real_players[0]:
            print("Your new hand is: ", self.playerHands[self.real_players[0]])

    def do_move(self, move: 'Card', **kwargs) -> None:
        """
        Function apply moves for current player and change state (itself)
        :param move: move to make
        :param verbose: simple logging of every action
        :param global_game: in case of simulation algorithm plays until round ends.
        in case of global gamel multiple rounds are played.
        :return: 
        """

        assert move

        global_game = kwargs.get('global_game', False)
        victim = kwargs.get('victim')

        if not 'verbose' in kwargs:
            kwargs['verbose'] = False

        # deactivate action of defense from previous move
        if self.playerToMove.defence:
            self.playerToMove.defence = False

        old_wrong_guesses = self.wrong_guesses[self.playerToMove]
        clean_cards(move, self.wrong_guesses[self.playerToMove], self.seen_cards, self.playerToMove)
        if move not in old_wrong_guesses:
            assert not old_wrong_guesses

        left_players = [player for player in self.user_ctl.users
                        if not player.defence and self.playerToMove != player and not player.lost]

        if not victim:
            victim = random.choice(left_players) if left_players else None
            kwargs['victim'] = victim

        # Remove the card from the player's hand
        self.playerHands[self.playerToMove].remove(move)
        assert len(self.playerHands[self.playerToMove]) == 1

        self.used_cards[move] += 1
        # code to refactor
        if move.name == "Prince" and not victim:
            clean_cards(self.playerHands[self.playerToMove][0], self.wrong_guesses[self.playerToMove], self.seen_cards, self.playerToMove)
        move.activate(self, **kwargs)
        
        # Store the played card in the current trick
        self.currentTrick.append((self.playerToMove, move))

        # If only one player left
        if self.user_ctl.players_left_number() == 1:
            winner = self.user_ctl.get_left_player()
            self.tricksTaken[winner] += 1
            winner.won_round = True

            if self.tricksTaken[winner] == 4:
                self.game_over = True

            self.round_over = True
            if global_game:
                print("\n\nRound #{} won by {}".format(self.round, winner))
                self.start_new_round(first_player=winner)

        # deck is empty, so game is over
        elif len(self.deck) == 0:
            for player in self.user_ctl.users:
                assert len(self.playerHands[player]) <= 1

            def played_card_sum(player):
                result = 0
                for moved_player, card in self.currentTrick:
                    if moved_player == player:
                        result += card.value
                return result

            cards = [(player, self.playerHands[player], played_card_sum(player))
                     for player in self.user_ctl.users
                     if not player.lost]

            cards.sort(key=lambda item: (item[1], item[2]), reverse=True)

            winner = cards[0][0]
            winner.won_round = True
            self.tricksTaken[winner] += 1
            if self.tricksTaken[winner] == 4:
                self.game_over = True

            self.round_over = True
            if global_game:
                print("\n\nRound #{} won by {}".format(self.round, winner))
                self.start_new_round(first_player=winner)
        else:
            # Find the next player
            previous_player = self.playerToMove
            self.playerToMove = self.user_ctl.get_current_player()

            # check that there are more that one player
            assert previous_player != self.playerToMove
            self.playerToMove.take_card(self)

    def get_result(self, player):
        """ Get the game result from the viewpoint of player. 
        """
        return 1 if player.won_round else 0

    def take_card_from_deck(self):
        self.playerHands[self.playerToMove].append(self.deck.pop())

    def check_move(self, move, available_moves):

        # do not allow to make move with princess card
        while move == Princess():
            move = random.choice(available_moves)
        return move

    def __repr__(self):
        """ Return a human-readable representation of the state
        """
        current_player = self.playerToMove
        result = "Round %i" % self.round
        result += " | %s: " % current_player
        # result += ",".join(str(card) for card in self.playerHands[current_player])
        # result += " | Tricks: %i" % self.tricksTaken[self.user_ctl.users[self.playerToMove]]
        result += " | Trick: ["
        result += ",".join(("%s:%s" % (player, card)) for (player, card) in self.currentTrick)
        result += "]"
        return result


def get_single_player_move(state: 'LoveLetterState') -> Tuple[Card, Player, Card]:
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

    # if maid is selected, activate it on player (Rationality assumption)
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


def play_game():
    """ 
    Play a sample game between 4 ISMCTS players.
    """
    state = LoveLetterState(2)
    state.start_new_round()
    real_player = state.user_ctl.users[0]
    state.real_players.append(real_player)
    # take card from deck
    print("You are {}".format(real_player))
    print("Your hand is: [", ",".join(str(card) for card in state.playerHands[real_player]), "]")
    while not state.game_over:
        victim, guess = None, None

        if state.playerToMove == real_player:
            move, victim, guess = get_single_player_move(state)
            print("You play with {}".format(move))
        else:
            print("\n", state)
            move, victim, guess = ISMCTS(rootstate=state, itermax=4000, verbose=False)
            # print "Best Move: " + str(m) + "\n"
        state.do_move(move, verbose=True, global_game=True, victim=victim, guess=guess,
                      real_player=True)

    for player in state.user_ctl.users:
        if state.tricksTaken[player] == 4:
            print("Player " + str(player) + " wins the game!")


if __name__ == "__main__":
    play_game()