# -*- coding: utf-8 -*-

import random
from collections import defaultdict
from copy import deepcopy, copy

from cardclasses import Guard, Priest, Baron, Maid, Prince, King, Countess, Princess, card_dict, Card
from player import Player, PlayerCtl
from playing_mode import PlayingMode
from strategy import clean_cards
from utils import TranspositionTable


class LoveLetterState:
    """
     A state of the game love letter.
    """

    def __init__(self, n, decks=None):
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
        self.decks = decks
        self.tricks_taken_limit = 7

    def get_winner(self):
        winners = [player for player in self.user_ctl.users if player.won_round]
        assert len(winners) == 1
        return winners[0]

    def clone(self, **kwargs):
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
        st.deck = []

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

        st.tricks_taken_limit = self.tricks_taken_limit

        for card, counter in st.used_cards.items():
            card_count[card] -= counter
            assert card_count[card] >= 0

        for card, counter in card_count.items():
            if counter > 0:
                st.deck.extend([card] * counter)

        random.shuffle(st.deck)
        st.user_ctl = self.user_ctl.clone()
        st.real_players = deepcopy(st.real_players)
        st.playerToMove = st.user_ctl.users[st.user_ctl.users.index(self.playerToMove)]

        return st

    def clone_and_randomize(self, **kwargs):
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
                if not kwargs.get('vanilla', False) and st.seen_cards[st.playerToMove][user]:
                    taken_card = random.choice(st.seen_cards[st.playerToMove][user])
                    if taken_card in st.deck:
                        st.playerHands[user].append(taken_card)
                        st.deck.remove(taken_card)
                    else:
                        del st.seen_cards[st.playerToMove][user][:]

        for user in st.user_ctl.users:
            if user != st.playerToMove and not user.lost and not st.playerHands[user]:
                user.take_card(st)

        # select outcard
        st.out_card = st.deck.pop()

        return st

    def add_seen_card(self, _from, to, card):
        if not self.seen_cards[_from][to] or card not in self.seen_cards[_from][to]:
            del self.seen_cards[_from][to][:]
            self.seen_cards[_from][to].append(card)

    def get_moves(self):
        """
        :return: list of available moves for current user 
        """
        available_moves = self.playerHands[self.playerToMove]

        # countess and king or countess and prince are in hand, return move with countess card
        if Countess() in available_moves and (King() in available_moves or Prince() in available_moves):
            return [Countess()]

        return available_moves

    def get_card_deck(self):
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

    def start_new_round(self, first_player=None):
        """
        :param first_player: player(instance of User class) who starts current round. If None, then random player starts round
        :return:  
        """
        self.round += 1
        self.round_over = False

        for user in self.tricksTaken:
            print("{} -> {}".format(user, self.tricksTaken[user]))

        if not hasattr(self, "user_ctl"):
            self.user_ctl = PlayerCtl(self.numberOfPlayers)
            self.user_ctl.shuffle()
        else:
            self.user_ctl.reset()

        self.deck = copy(random.choice(self.decks))
        # remove one card from deck and remember it
        self.out_card = self.deck.pop()
        self.playerHands = {user: [] for user in self.user_ctl.users}
        #  if there is winner in previous round, then he or she starts the next round
        if first_player:
            # place player on first position in player list
            winner_index = self.user_ctl.users.index(first_player)
            # cyclic shift of players
            self.user_ctl.users = self.user_ctl.users[winner_index:] + self.user_ctl.users[:winner_index]

        self.used_cards = defaultdict(int)
        self.currentTrick = []
        self.wrong_guesses = defaultdict(list)
        self.seen_cards = defaultdict(lambda: defaultdict(list))

        for user in self.user_ctl.users:
            user.take_card(self)

        # player who makes move takes second card
        self.playerToMove = self.user_ctl.get_current_player()
        self.playerToMove.take_card(self)

        # print real user hand when bot starts round
        if self.real_players and self.user_ctl.users[0] != self.real_players[0]:
            print("Your new hand is: ", self.playerHands[self.real_players[0]])

    def do_move(self, move, **kwargs):
        """
        Function apply moves for current player and change state (itself)
        :param move: move to make
        :param verbose: simple logging of every action
        :param global_game: in case of simulation algorithm plays until round ends.
        in case of global gamel multiple rounds are played.
        :return: list of messages
        """
        messages = []
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

        if victim:
            assert not self.user_ctl.users[self.user_ctl.users.index(victim)].lost

        # Remove the card from the player's hand
        self.playerHands[self.playerToMove].remove(move)
        assert len(self.playerHands[self.playerToMove]) == 1

        self.used_cards[move] += 1
        # code to refactor
        if move.name == "Prince" and not victim:
            clean_cards(self.playerHands[self.playerToMove][0], self.wrong_guesses[self.playerToMove], self.seen_cards,
                        self.playerToMove)
        messages.extend(move.activate(self, **kwargs))

        # Store the played card in the current trick
        self.currentTrick.append((self.playerToMove, move))

        # If only one player left
        if self.user_ctl.players_left_number() == 1:
            winner = self.user_ctl.get_left_player()
            self.tricksTaken[winner] += 1
            winner.won_round = True

            if self.tricksTaken[winner] == self.tricks_taken_limit:
                self.game_over = True

            self.round_over = True
            if global_game:
                messages.append("Round #{} won by {}".format(self.round, winner))
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
            if self.tricksTaken[winner] == self.tricks_taken_limit:
                self.game_over = True

            self.round_over = True
            if global_game:
                messages.append("Round #{} won by {}".format(self.round, winner))
                print("\n\nRound #{} won by {}".format(self.round, winner))
                self.start_new_round(first_player=winner)
        else:
            # Find the next player
            previous_player = self.playerToMove
            self.playerToMove = self.user_ctl.get_current_player()
            # check that there are more that one player
            assert previous_player != self.playerToMove
            self.playerToMove.take_card(self)

        return messages

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


def compare(decks):
    table = TranspositionTable()
    with open('ismcts_vs_ismcts__200.txt', 'w') as out:

        for iterations in (50, 100, 200, 500, 1000, 2000, 4000):
            winner_counter = defaultdict(int)
            game_number = 1

            for plays in range(game_number):
                state = LoveLetterState(2, decks)
                state.start_new_round()
                mode = PlayingMode(state, "compare_bots", show_logs=False)

                while not state.game_over:
                    try:
                        assert len(state.playerHands[state.playerToMove]) == 2
                    except:
                        import pdb
                        pdb.set_trace()
                    move, victim, guess = mode.get_move(iterations)
                    # table.write(state, move, victim, guess)
                    state.do_move(move, verbose=False, global_game=True, victim=victim, guess=guess,
                                  real_player=state.playerToMove == mode.real_player, vanilla=False)

                # determine a winner
                for player in state.user_ctl.users:
                    if state.tricksTaken[player] == state.tricks_taken_limit:
                        # print("Player " + str(player) + " wins the game!")
                        winner_counter[player.algorithm] += 1

            assert (sum(winner_counter.values()) == game_number)

            out.write("{} iterations\n".format(iterations))

            for algorithm, won_count in winner_counter.items():
                out.write("{} - {}\n".format(algorithm, won_count))
            out.write("\n")

            print("Iterations - {}".format(iterations, ))
            print(winner_counter)

    print("Done")
    # table.close()


def play_game():
    """ 
    Play a sample game between 2-4 ISMCTS players.
    """
    decks = []

    # use decks specified in advance
    with open('decks.txt') as f:
        for line in f:
            splitted = line.split()
            decks.append([card_dict[card] for card in splitted])
    # state = LoveLetterState(2, decks)
    # state.start_new_round()

    compare(decks)

    # mode = PlayingMode(state, "real_player")
    # while not state.game_over:
    #     print("\n", state)
    #     move, victim, guess = mode.get_move(0)
    #     state.do_move(move, verbose=True, global_game=True, victim=victim, guess=guess,
    #                   real_player=state.playerToMove == mode.real_player, vanilla=False)
    #
    # # determine a winner
    # for player in state.user_ctl.users:
    #     if state.tricksTaken[player] == state.tricks_taken_limit:
    #         print("Player " + str(player) + " wins the game!")


if __name__ == "__main__":
    play_game()
