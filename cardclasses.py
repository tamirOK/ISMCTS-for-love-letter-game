# -*- coding: utf-8 -*-

import random


class Card:
    value = None
    name = None

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
    value = 8

    def activate(self, game, victim, verbose, **kwargs):
        if verbose:
            print("{} makes move with Princess and leaves game".format(game.user_ctl.users[game.playerToMove]))
        game.user_ctl.kill(game.user_ctl.users[game.playerToMove])


class Countess(Card):
    name = 'Countess'
    value = 7

    def activate(self, game, victim, verbose, **kwargs):
        if verbose:
            print("{} makes move with Counterss".format(game.user_ctl.users[game.playerToMove]))
        # TODO: не забыть сбросить графиню


class King(Card):
    name = 'King'
    value = 6

    def activate(self, game, victim, verbose, **kwargs):
        if not victim:
            # if there is no victim, nothing happens
            pass
        else:
            if verbose:
                print("{} makes move with King against {}".format(game.user_ctl.users[game.playerToMove], victim))

            # exchanging with cards with victim
            current_player = game.user_ctl.users[game.playerToMove]
            card1 = game.playerHands[current_player].pop()
            card2 = game.playerHands[victim].pop()

            assert len(game.playerHands[current_player]) == 0
            assert len(game.playerHands[victim]) == 0

            game.playerHands[victim].append(card1)
            game.playerHands[current_player].append(card2)


class Prince(Card):
    name = 'Prince'
    value = 5

    def activate(self, game, victim, verbose, **kwargs):
        if victim:
            card = game.playerHands[victim].pop()
            assert(len(game.playerHands[victim]) == 0)
            game.used_cards.append(card)
            if verbose:
                print("{} makes move with Prince against {}".format(game.user_ctl.users[game.playerToMove], victim))
                print("{} drops {}".format(victim, card))
            if card == Princess():
                game.user_ctl.kill(victim)
                if verbose:
                    print("{} drops {} and leaves game".format(victim, card))
                return

            # if deck is empty, take additional 16-th card and put in deck
            if len(game.deck) == 0:
                assert game.out_card
                game.deck.append(game.out_card)
                game.out_card = None

            victim.take_card(game)
        else:
            # apply prince card to itself
            current_player = game.user_ctl.users[game.playerToMove]
            card = game.playerHands[current_player].pop()

            assert len(game.playerHands[current_player]) == 0
            game.used_cards.append(card)

            if len(game.deck) == 0:
                game.deck.append(game.out_card)
            current_player.take_card(game)

            if verbose:
                print("{} drops {} and takes new one".format(current_player, card))


class Maid(Card):
    name = 'Maid'
    value = 4

    def activate(self, game, victim, verbose, **kwargs):
        # It is assumed that all players play optimally, thus player applies defense to itself
        game.user_ctl.users[game.playerToMove].defence = True
        if verbose:
            print("{} applied defense(Maid) to itself".format(game.user_ctl.users[game.playerToMove]))


class Baron(Card):
    name = 'Baron'
    value = 3

    def activate(self, game, victim, verbose, **kwargs):
        if not victim:
            pass
        else:
            owner = game.user_ctl.users[game.playerToMove]

            assert len(game.playerHands[owner]) == 1
            assert len(game.playerHands[victim]) == 1

            if game.playerHands[owner][0] > game.playerHands[victim][0]:
                # current player kicks out victim
                game.used_cards.append(game.playerHands[victim][0])
                game.user_ctl.kill(victim)

                if verbose:
                    print("{} kicks out {} via Baron".format(owner, victim))
            elif game.playerHands[owner][0] < game.playerHands[victim][0]:
                # victim kicks out current player
                game.used_cards.append(game.playerHands[owner][0])
                game.user_ctl.kill(owner)
                if verbose:
                    print("{} kicks out {} via Baron".format(victim, owner))
            else:
                # nothing happens if cards are equal
                pass


class Priest(Card):
    name = 'Priest'
    value = 2

    def activate(self, game, victim, verbose, **kwargs):
        if verbose:
            print("{} plays Priest".format(game.user_ctl.users[game.playerToMove]))
        if not victim:
            pass
        else:
            pass
            # TODO: add knowledge about opponent's cards


class Guard(Card):
    name = 'Guard'
    value = 1

    def activate(self, game, victim, verbose, **kwargs):
        victim_card = kwargs.get('victim_card', None)
        if not victim:
            pass
            if verbose:
                print("{} plays Guard to itself".format(game.user_ctl.users[game.playerToMove]))
        else:
            if not victim_card:
                available_cards = [
                    card
                    for card in game.get_card_deck()
                    if card not in game.used_cards and card not in game.playerHands[game.user_ctl.users[game.playerToMove]]
                        and card.name != "Guard"
                ]
                victim_card = random.choice(available_cards) if available_cards else None

            if victim_card and victim_card in game.playerHands[victim]:
                game.used_cards.append(victim_card)
                game.user_ctl.kill(victim)
                if verbose:
                    print("{} kicks out {} via Guard".format(game.user_ctl.users[game.playerToMove], victim))
            else:
                pass
                if verbose:
                    print("{} doesn't kick out {} via Guard with guess {}".format(game.user_ctl.users[game.playerToMove], victim, victim_card))