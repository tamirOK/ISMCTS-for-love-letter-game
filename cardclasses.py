# -*- coding: utf-8 -*-

import random


class Card:
    value = None
    name = None
    max_count = 0

    def __eq__(self, other):
        return self.name == getattr(other, 'name', None)

    def __le__(self, other):
        return self.value <= other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __lt__(self, other):
        return self.value < other.value

    def __gt__(self, other):
        return self.value > other.value

    def __str__(self):
        return str(self.name)

    def __hash__(self):
        return hash(str(self.name))


class Princess(Card):
    name = 'Princess'
    path = 'static/princess.gif'
    value = 8
    max_count = 1

    def activate(self, game, victim, verbose, **kwargs):
        messages = []
        if verbose:
            messages.append("{} makes move with Princess and leaves game".format(game.playerToMove))
            print("{} makes move with Princess and leaves game".format(game.playerToMove))
        game.user_ctl.kill(game.playerToMove)

        return messages


class Countess(Card):
    name = 'Countess'
    path = 'static/countess.gif'
    value = 7
    max_count = 1

    def activate(self, game, victim, verbose, **kwargs):
        messages = []
        if verbose:
            messages.append("{} makes move with Countess".format(game.playerToMove))
            print("{} makes move with Countess".format(game.playerToMove))

        return messages


class King(Card):
    name = 'King'
    path = 'static/king.gif'
    value = 6
    max_count = 1

    def activate(self, game, victim, verbose, **kwargs):
        messages = []
        if not victim or victim == game.playerToMove:
            # if there is no victim, nothing happens
            if verbose:
                messages.append("{} plays King to itself".format(game.playerToMove))
                print("{} plays King to itself".format(game.playerToMove))
        else:
            if verbose:
                messages.append("{} makes move with King against {}".format(game.playerToMove, victim))
                print("{} makes move with King against {}".format(game.playerToMove, victim))

            # exchanging with cards with victim
            current_player = game.playerToMove
            card1 = game.playerHands[current_player].pop()
            card2 = game.playerHands[victim].pop()

            assert len(game.playerHands[current_player]) == 0
            assert len(game.playerHands[victim]) == 0

            for player in game.user_ctl.users:
                if card1 in game.seen_cards[player][current_player] and not player.lost:
                    game.seen_cards[player][current_player].remove(card1)

                if card2 in game.seen_cards[player][victim] and not player.lost:
                    game.seen_cards[player][victim].remove(card2)

            game.add_seen_card(victim, current_player, card2)
            game.add_seen_card(current_player, victim, card1)
            # exchange with cards
            game.playerHands[victim].append(card1)
            game.playerHands[current_player].append(card2)

            if kwargs.get('real_player', False):
                messages.append("Your new card is {}".format(card2))
                print("Your new card is {}".format(card2))

        return messages


class Prince(Card):
    name = 'Prince'
    path = 'static/prince.gif'
    value = 5
    max_count = 2

    def activate(self, game, victim, verbose, **kwargs):
        messages = []

        if victim:
            card = game.playerHands[victim].pop()

            for player in game.user_ctl.users:
                if card in game.seen_cards[player][victim]:
                    game.seen_cards[player][victim].remove(card)

            assert (len(game.playerHands[victim]) == 0)
            game.used_cards[card] += 1

            assert game.used_cards[card] <= card.max_count

            if verbose:
                messages.append("{} makes move with Prince against {}".format(game.playerToMove, victim))
                messages.append("{} drops {}".format(victim, card))

                print("{} makes move with Prince against {}".format(game.playerToMove, victim))
                print("{} drops {}".format(victim, card))

            if card == Princess():
                game.user_ctl.kill(victim)
                if verbose:
                    messages.append("{} drops {} and leaves game".format(victim, card))
                    print("{} drops {} and leaves game".format(victim, card))

            # if deck is empty, take additional 16-th card and put in deck
            if len(game.deck) == 0:
                assert game.out_card
                game.deck.append(game.out_card)
                game.out_card = None

            victim.take_card(game)
        else:
            # apply prince card to itself
            current_player = game.playerToMove
            card = game.playerHands[current_player].pop()

            assert len(game.playerHands[current_player]) == 0
            game.used_cards[card] += 1

            assert game.used_cards[card] <= card.max_count

            if card.name != "Princess":
                if len(game.deck) == 0:
                    assert game.out_card
                    game.deck.append(game.out_card)
                    game.out_card = None
                current_player.take_card(game)

            else:
                game.user_ctl.kill(current_player)

            if verbose:
                if card.name != "Princess":
                    messages.append("{} drops {} and takes new one".format(current_player, card))
                    print("{} drops {} and takes new one".format(current_player, card))
                else:
                    messages.append("{} drops {} and loses round".format(current_player, card))
                    print("{} drops {} and loses round".format(current_player, card))

        return messages


class Maid(Card):
    name = 'Maid'
    path = 'static/maid.gif'
    value = 4
    max_count = 2

    def activate(self, game, victim, verbose, **kwargs):
        # It is assumed that all players play optimally, thus player applies defense to itself
        messages = []
        game.playerToMove.defence = True
        if verbose:
            messages.append("{} applied defense(Maid) to itself".format(game.playerToMove))
            print("{} applied defense(Maid) to itself".format(game.playerToMove))

        return messages


class Baron(Card):
    name = 'Baron'
    path = 'static/baron.gif'
    value = 3
    max_count = 2

    def activate(self, game, victim, verbose, **kwargs):
        messages = []
        if not victim or victim == game.playerToMove:
            if verbose:
                messages.append("{} plays Baron to itself".format(game.playerToMove))
                print("{} plays Baron to itself".format(game.playerToMove))
        else:
            owner = game.playerToMove

            assert len(game.playerHands[owner]) == 1
            assert len(game.playerHands[victim]) == 1

            if game.playerHands[owner][0] > game.playerHands[victim][0]:
                # current player kicks out victim
                game.used_cards[game.playerHands[victim][0]] += 1

                assert game.used_cards[game.playerHands[victim][0]] <= game.playerHands[victim][0].max_count
                game.user_ctl.kill(victim)

                if verbose:
                    messages.append("{} kicks out {} via Baron. Victim's card is {}".format(owner, victim,
                                                                                            game.playerHands[victim][
                                                                                                0]))
                    print("{} kicks out {} via Baron. Opponents's card is {}".format(owner, victim,
                                                                                  game.playerHands[owner][0]))
            elif game.playerHands[owner][0] < game.playerHands[victim][0]:
                # victim kicks out current player
                game.used_cards[game.playerHands[owner][0]] += 1

                assert game.used_cards[game.playerHands[owner][0]] <= game.playerHands[owner][0].max_count

                game.user_ctl.kill(owner)
                if verbose:
                    messages.append("{} kicks out {} via Baron. Current player's card is {}".format(victim, owner,
                                                                                                    game.playerHands[
                                                                                                        owner][0]))
                    print("{} kicks out {} via Baron. Oppenent's card is {}".format(victim, owner,
                                                                                          game.playerHands[victim][0]))
            else:
                # nothing happens if cards are equal
                game.add_seen_card(owner, victim, game.playerHands[victim][0])
                game.add_seen_card(victim, owner, game.playerHands[owner][0])

                if verbose:
                    messages.append("Equal cards, nothing happens")
                    print("Equal cards, nothing happens")

        return messages


class Priest(Card):
    name = 'Priest'
    path = 'static/priest.gif'
    value = 2
    max_count = 2

    def activate(self, game, victim, verbose, **kwargs):
        messages = []
        if not victim or victim == game.playerToMove:
            if verbose:
                messages.append("{} plays Priest to itself".format(game.playerToMove))
                print("{} plays Priest to itself".format(game.playerToMove))
        else:
            current_player = game.playerToMove
            victims_card = game.playerHands[victim][0]
            game.add_seen_card(current_player, victim, victims_card)
            if verbose:
                messages.append("{} plays Priest against {}".format(game.playerToMove, victim))
                print("{} plays Priest against {}".format(game.playerToMove, victim))
            if kwargs.get('real_player', False):
                messages.append("{} card is {}".format(victim, victims_card))
                print("{} card is {}".format(victim, victims_card))

        return messages


class Guard(Card):
    name = 'Guard'
    path = 'static/guard.gif'
    value = 1
    max_count = 5

    def activate(self, game, victim, verbose, **kwargs):
        messages = []

        victim_card = kwargs.get('guess', None)
        if not victim or victim == game.playerToMove:
            if verbose:
                messages.append("{} plays Guard to itself".format(game.playerToMove))
                print("{} plays Guard to itself".format(game.playerToMove))
        else:
            card_count = {
                Princess(): 1,
                Countess(): 1,
                King(): 1,
                Prince(): 2,
                Maid(): 2,
                Baron(): 2,
                Priest(): 2,
            }

            if not victim_card:
                # remove already played cards from candidates
                for card, counter in game.used_cards.items():
                    # ignore guard because it cannot be guessed
                    if card.name != 'Guard':
                        card_count[card] -= counter
                        assert card_count[card] >= 0

                for card in game.playerHands[game.playerToMove]:
                    if card.name != 'Guard':
                        card_count[card] -= 1
                        assert card_count[card] >= 0

                if kwargs.get('vanilla', False):
                    possible_cards = []

                    for card in card_count:
                        for _ in range(card_count[card]):
                            possible_cards.append(card)

                    victim_card = random.choice(possible_cards)
                else:
                    # ignore cards that were guessed incorrectly
                    for card in game.wrong_guesses[victim]:
                        if card.name != 'Guard':
                            card_count[card] -= 1

                    if game.currentTrick and game.currentTrick[-1][1].name == "Countess":
                        if card_count[Prince()] > 0:
                            victim_card = Prince()
                        elif card_count[King()] > 0:
                            victim_card = King()

                    available_cards = sorted([(counter, card) for card, counter in card_count.items()], reverse=True)
                    most_probable_cards = [card for counter, card in available_cards if
                                           counter == available_cards[0][0]]
                    if not victim_card:
                        victim_card = random.choice(most_probable_cards)

            assert victim_card

            if victim_card in game.playerHands[victim]:
                game.used_cards[victim_card] += 1
                assert game.used_cards[victim_card] <= victim_card.max_count
                game.user_ctl.kill(victim)
                if verbose:
                    messages.append(
                        "{} kicks out {} via Guard with guess {}".format(game.playerToMove, victim, victim_card))
                    print("{} kicks out {} via Guard with guess {}".format(game.playerToMove, victim, victim_card))
            else:
                game.wrong_guesses[victim].append(victim_card)
                if verbose:
                    messages.append(
                        "{} doesn't kick out {} via Guard with guess {}".format(game.playerToMove, victim, victim_card))
                    print(
                        "{} doesn't kick out {} via Guard with guess {}".format(game.playerToMove, victim, victim_card))

        return messages


card_dict = {
    'Princess': Princess(),
    'Countess': Countess(),
    'King': King(),
    'Priest': Priest(),
    'Maid': Maid(),
    'Baron': Baron(),
    'Guard': Guard(),
    'Prince': Prince(),
}
