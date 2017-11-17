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
            print("{} makes move with Princess and leaves game".format(game.playerToMove))
        game.user_ctl.kill(game.playerToMove)


class Countess(Card):
    name = 'Countess'
    value = 7

    def activate(self, game, victim, verbose, **kwargs):
        if verbose:
            print("{} makes move with Countess".format(game.playerToMove))


class King(Card):
    name = 'King'
    value = 6

    def activate(self, game, victim, verbose, **kwargs):
        if not victim or victim == game.playerToMove:
            # if there is no victim, nothing happens
            if verbose:
                print("{} plays King to itself".format(game.playerToMove))
        else:
            if verbose:
                print("{} makes move with King against {}".format(game.playerToMove, victim))

            # exchanging with cards with victim
            current_player = game.playerToMove
            card1 = game.playerHands[current_player].pop()
            card2 = game.playerHands[victim].pop()

            assert len(game.playerHands[current_player]) == 0
            assert len(game.playerHands[victim]) == 0

            if card2 in game.seen_cards[current_player][victim]:
                game.seen_cards[current_player][victim].remove(card2)

            if card1 in game.seen_cards[victim][current_player]:
                game.seen_cards[victim][current_player].remove(card1)

            game.add_seen_card(victim, current_player, card2)
            game.add_seen_card(current_player, victim, card1)
            # exchange with cards
            game.playerHands[victim].append(card1)
            game.playerHands[current_player].append(card2)


class Prince(Card):
    name = 'Prince'
    value = 5

    def activate(self, game, victim, verbose, **kwargs):
        if victim:
            card = game.playerHands[victim].pop()

            if card in game.seen_cards[game.playerToMove][victim]:
                game.seen_cards[game.playerToMove][victim].remove(card)

            assert(len(game.playerHands[victim]) == 0)
            game.used_cards[card] += 1
            if verbose:
                print("{} makes move with Prince against {}".format(game.playerToMove, victim))
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
            current_player = game.playerToMove
            card = game.playerHands[current_player].pop()

            assert len(game.playerHands[current_player]) == 0
            game.used_cards[card] += 1

            if card.name != "Princess":
                if len(game.deck) == 0:
                    game.deck.append(game.out_card)
                current_player.take_card(game)

            else:
                game.user_ctl.kill(current_player)

            if verbose:
                if card.name != "Princess":
                    print("{} drops {} and takes new one".format(current_player, card))
                else:
                    print("{} drops {} and loses round".format(current_player, card))


class Maid(Card):
    name = 'Maid'
    value = 4

    def activate(self, game, victim, verbose, **kwargs):
        # It is assumed that all players play optimally, thus player applies defense to itself
        game.playerToMove.defence = True
        if verbose:
            print("{} applied defense(Maid) to itself".format(game.playerToMove))


class Baron(Card):
    name = 'Baron'
    value = 3

    def activate(self, game, victim, verbose, **kwargs):
        if not victim or victim == game.playerToMove:
            if verbose:
                print("{} plays Baron to itself".format(game.playerToMove))
        else:
            owner = game.playerToMove

            assert len(game.playerHands[owner]) == 1
            assert len(game.playerHands[victim]) == 1

            if game.playerHands[owner][0] > game.playerHands[victim][0]:
                # current player kicks out victim
                game.used_cards[game.playerHands[victim][0]] += 1
                game.user_ctl.kill(victim)

                if verbose:
                    print("{} kicks out {} via Baron".format(owner, victim))
            elif game.playerHands[owner][0] < game.playerHands[victim][0]:
                # victim kicks out current player
                game.used_cards[game.playerHands[owner][0]] += 1
                game.user_ctl.kill(owner)
                if verbose:
                    print("{} kicks out {} via Baron".format(victim, owner))
            else:
                # nothing happens if cards are equal
                game.add_seen_card(owner, victim, game.playerHands[victim][0])
                game.add_seen_card(victim, owner, game.playerHands[owner][0])

                if verbose:
                    print("Equal cards, nothing happens")


class Priest(Card):
    name = 'Priest'
    value = 2

    def activate(self, game, victim, verbose, **kwargs):
        if verbose:
            print("{} plays Priest".format(game.playerToMove))
        if not victim or victim == game.playerToMove:
            if verbose:
                print("{} plays Priest to itself".format(game.playerToMove))
        else:
            current_player = game.playerToMove
            victims_card = game.playerHands[victim][0]
            game.add_seen_card(current_player, victim, victims_card)
            # game.seen_cards[current_player][victim].append(victims_card)
            if kwargs.get('real_player', False):
                print("{} card is {}".format(victim, victims_card))
            # TODO: add knowledge about opponent's cards


class Guard(Card):
    name = 'Guard'
    value = 1

    def activate(self, game, victim, verbose, **kwargs):
        victim_card = kwargs.get('guess', None)
        if not victim or victim == game.playerToMove:
            if verbose:
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

                for card, counter in game.used_cards.items():
                    # ignore guard because it cannot be guessed
                    if card.name != 'Guard':
                        card_count[card] -= counter

                for card in game.playerHands[game.playerToMove] + game.wrong_guesses[game.playerToMove]:
                    if card.name != 'Guard':
                        card_count[card] -= 1

                for player, card in game.currentTrick:
                    if player == victim and card.name == "Countess":
                        if card_count[King()] > 0:
                            victim_card = King()
                        elif card_count[Prince()] > 0:
                            victim_card = Prince()

                available_cards = sorted([(counter, card) for card, counter in card_count.items()], reverse=True)
                # victim_card = random.choice(available_cards) if available_cards else None
                if not victim_card:
                    victim_card = available_cards[0][1]

            assert(victim_card)

            if victim_card in game.playerHands[victim]:
                game.used_cards[victim_card] += 1
                game.user_ctl.kill(victim)
                if verbose:
                    print("{} kicks out {} via Guard".format(game.playerToMove, victim))
            else:
                game.wrong_guesses[victim].append(victim_card)
                if verbose:
                    print("{} doesn't kick out {} via Guard with guess {}".format(game.playerToMove, victim, victim_card))


card_dict = {
    'princess': Princess(),
    'countess': Countess(),
    'king': King(),
    'priest': Priest(),
    'maid': Maid(),
    'baron': Baron(),
    'guard': Guard(),
    'prince': Prince(),
}
