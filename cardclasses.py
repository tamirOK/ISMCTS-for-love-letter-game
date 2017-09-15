# -*- coding: utf-8 -*-

import random


class Card:
    value = None
    need_victim = False
    need_guess = False
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
        return self.name


class Princess(Card):
    name = 'Princess'
    value = 8

    def activate(self, game, victim, verbose):
        #game.bot.send_message(game.group_chat, '@{} сбрасывает Принцессу и проигрывает.'.format(self.owner.name))
        #game.bot.send_message(self.owner.uid, '@{} сбрасывает Принцессу и проигрывает.'.format(self.owner.name),
        #                      reply_markup=markup)
        if verbose:
            print("{} makes move with Princess and leaves game".format(game.user_ctl.users[game.playerToMove]))
        game.user_ctl.kill(game.user_ctl.users[game.playerToMove])


class Countess(Card):
    name = 'Countess'
    value = 7

    def activate(self, game, victim, verbose):
        pass
        # TODO: не забыть сбросить графиню
        #markup = types.ReplyKeyboardRemove(selective=False)
        #game.bot.send_message(game.group_chat, '@{} сбрасывает Графиню.'.format(self.owner.name))
        #game.bot.send_message(self.owner.uid, '@{} сбрасывает Графиню.'.format(self.owner.name), reply_markup=markup)


class King(Card):
    name = 'King'
    value = 6
    need_victim = True

    def activate(self, game, victim, verbose):
        if not victim:
            pass
            # game.bot.send_message(game.group_chat,
            #                       '@{} использует Короля впустую, так как все защищены.'.format(
            #                           self.owner.name))
            # game.bot.send_message(self.owner.uid,
            #                       '@{} использует Короля впустую, так как все защищены.'.format(
            #                           self.owner.name),
            #                       reply_markup=markup)
            
        else:
            # game.bot.send_message(game.group_chat,
            #                       '@{} использует Короля чтобы обменяться с @{} картами.'.format(self.owner.name,
            #                                                                                       game.victim.name))
            # game.bot.send_message(self.owner.uid,
            #                       '@{} использует Короля чтобы обменяться с @{} картами.'.format(self.owner.name,
            #                                                                                       game.victim.name),
            #                       reply_markup=markup)

            # game.bot.send_message(game.dealer.uid, 'Вы получили карту "{}" от @{}'.format(game.victim.card.name,
            #                                                                               game.victim.name))
            # game.bot.send_message(game.victim.uid, 'Вы получили карту "{}" от @{}'.format(game.dealer.card.name,
            #                                                                               game.dealer.name))

            if verbose:
                print "{} makes move with King agains {}".format(game.user_ctl.users[game.playerToMove], victim)

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
    need_victim = True

    def activate(self, game, victim, verbose):
        if victim:
            card = game.playerHands[victim].pop()
            assert(len(game.playerHands[victim]) == 0)
            game.used_cards.append(card)
            if verbose:
                print("{} makes move with Prince against {}".format(game.user_ctl.users[game.playerToMove], victim))
                print("{} drops {}".format(victim, card))
            if card == 'Princess':
                # game.bot.send_message(game.group_chat,
                #                       '@{0} использует Принца против @{1}. '
                #                       '@{1} сбрасывает Принцессу и проигрывает.'.format(self.owner.name, game.victim.name))
                # game.bot.send_message(self.owner.uid,
                #                       '@{0} использует Принца против @{1}. '
                #                       '@{1} сбрасывает Принцессу и проигрывает.'.format(self.owner.name, game.victim.name),
                #                       reply_markup=markup)

                game.user_ctl.kill(victim)
                if verbose:
                    print("{} drops {} and leaves game".format(victim, card))
                return

            # game.bot.send_message(game.group_chat,
            #                       '@{0} использует Принца против @{1}. У @{1} был(а) {2}.'.format(self.owner.name,
            #                                                                                        game.victim.name,
            #                                                                                        game.victim.card.name))
            # game.bot.send_message(self.owner.uid,
            #                       '@{0} использует Принца против @{1}. У @{1} был(а) {2}.'.format(self.owner.name,
            #                                                                                        game.victim.name,
            #                                                                                        game.victim.card.name),
            #                       reply_markup=markup)
            if len(game.deck) == 0:
                assert game.out_card
                game.deck.append(game.out_card)
                game.out_card = None

            victim.take_card(game)
        else:
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

    def activate(self, game, victim, verbose):
        # game.bot.send_message(game.group_chat, '@{} защищен Служанкой в течение круга.'.format(self.owner.name))
        # game.bot.send_message(self.owner.uid, '@{} защищен Служанкой в течение круга.'.format(self.owner.name),
        #                       reply_markup=markup)
        game.user_ctl.users[game.playerToMove].defence = True
        if verbose:
            print("{} applied defense(Maid) to itself".format(game.user_ctl.users[game.playerToMove]))


class Baron(Card):
    name = 'Baron'
    value = 3
    need_victim = True

    def activate(self, game, victim, verbose):
        if not victim:
            pass
            # game.bot.send_message(game.group_chat,
            #                       '@{} использует Барона впустую, так как все защищены.'.format(
            #                           self.owner.name))
            # game.bot.send_message(self.owner.uid,
            #                       '@{} использует Барона впустую, так как все защищены.'.format(
            #                           self.owner.name),
            #                       reply_markup=markup)
        else:
            owner = game.user_ctl.users[game.playerToMove]

            assert len(game.playerHands[owner]) == 1
            assert len(game.playerHands[victim]) == 1

            if game.playerHands[owner][0] > game.playerHands[victim][0]:
                # game.bot.send_message(game.group_chat,
                #                       '@{0} использует Барона против @{1} и выигрывает. '
                #                       'У @{1} оказалась карта "{2}"'.format(self.owner.name,
                #                                                             game.victim.name, game.victim.card.name))
                # game.bot.send_message(self.owner.uid,
                #                       '@{0} использует Барона против @{1} и выигрывает. '
                #                       'У @{1} оказалась карта "{2}"'.format(self.owner.name,
                #                                                             game.victim.name, game.victim.card.name),
                #                       reply_markup=markup)
                game.used_cards.append(game.playerHands[victim][0])
                game.user_ctl.kill(victim)
                if verbose:
                    print("{} kicks out {} via Baron".format(owner, victim))
            elif game.playerHands[owner][0] < game.playerHands[victim][0]:
                # game.bot.send_message(game.group_chat,
                #                       '@{0} использует Барона против @{1}, но проигрывает. '
                #                       'у {0} оказалась карта "{2}"'.format(self.owner.name,
                #                                                            game.victim.name, self.owner.card.name))
                # game.bot.send_message(self.owner.uid,
                #                       '@{0} использует Барона против @{1}, но проигрывает. '
                #                       'у {0} оказалась карта "{2}"'.format(self.owner.name,
                #                                                            game.victim.name, self.owner.card.name),
                #                       reply_markup=markup)
                game.used_cards.append(game.playerHands[owner][0])
                game.user_ctl.kill(owner)
                if verbose:
                    print("{} kicks out {} via Baron".format(victim, owner))
            else:
                pass
                # game.bot.send_message(game.group_chat,
                #                       'Похоже, у @{} и @{} одинаковые карты... '
                #                       'Барон уходит впустую.'.format(self.owner.name, game.victim.name))
                # game.bot.send_message(self.owner.uid,
                #                       'Похоже, у @{} и @{} одинаковые карты... '
                #                       'Барон уходит впустую.'.format(self.owner.name, game.victim.name),
                #                       reply_markup=markup)


class Priest(Card):
    name = 'Priest'
    value = 2
    need_victim = True

    def activate(self, game, victim, verbose):
        if verbose:
            print("{} plays Priest".format(game.user_ctl.users[game.playerToMove]))
        if not victim:
            pass
            # game.bot.send_message(game.group_chat,
            #                       '@{} использует Священника впустую, так как все защищены.'.format(
            #                           self.owner.name))
            # game.bot.send_message(self.owner.uid,
            #                       '@{} использует Священника впустую, так как все защищены.'.format(
            #                           self.owner.name),
            #                       reply_markup=markup)
        else:
            pass
            # TODO: Обработать случай
            # game.bot.send_message(game.group_chat,
            #                       '@{} сбрасывает Священника и смотрит карту @{}.'.format(self.owner.name,
            #                                                                               game.victim.name))
            # game.bot.send_message(self.owner.uid,
            #                       '@{} сбрасывает Священника и смотрит карту @{}.'.format(self.owner.name,
            #                                                                               game.victim.name),
            #                       reply_markup=markup)
            # game.bot.send_message(self.owner.uid,
            #                       '@{} показывает Вам свою карту. У него(нее) {}.'.format(game.victim.name,
            #                                                                               game.victim.card.name))


class Guard(Card):
    name = 'Guard'
    value = 1
    need_victim = True
    need_guess = True

    def activate(self, game, victim, verbose):
        if not victim:
            pass
            # game.bot.send_message(game.group_chat,
            #                       '@{} использует Стражницу впустую, так как все защищены.'.format(
            #                           self.owner.name))
            # game.bot.send_message(self.owner.uid,
            #                       '@{} использует Стражницу впустую, так как все защищены.'.format(
            #                           self.owner.name),
            #                       reply_markup=markup)
            if verbose:
                print("{} plays Guard to itself".format(game.user_ctl.users[game.playerToMove]))
        else:
            available_cards = [
                card
                for card in game.get_card_deck()
                if card not in game.used_cards and card not in game.playerHands[game.user_ctl.users[game.playerToMove]]
            ]
            card = random.choice(available_cards) if available_cards else None
            if card and card in game.playerHands[victim]:
                # game.bot.send_message(game.group_chat,
                #                       '@{} использует Стражницу и угадывает что у @{} {}.'.format(self.owner.name,
                #                                                                                   game.victim.name,
                #                                                                                   game.guess))
                # game.bot.send_message(self.owner.uid,
                #                       '@{} использует Стражницу и угадывает что у @{} {}.'.format(self.owner.name,
                #                                                                                   game.victim.name,
                #                                                                                   game.guess),
                #                       reply_markup=markup)
                game.used_cards.append(card)
                game.user_ctl.kill(victim)
                if verbose:
                    print("{} kicks out {} via Guard".format(game.user_ctl.users[game.playerToMove], victim))
            else:
                pass
                if verbose:
                    print "{} doesn't kick out {} via Guard with guess {}".format(game.user_ctl.users[game.playerToMove], victim, card)
                # game.bot.send_message(game.group_chat,
                #                       '@{} использует Стражницу, предполагая '
                #                       'что у @{} {}, но не угадывает.'.format(self.owner.name,
                #                                                               game.victim.name,
                #                                                               game.guess))
                # game.bot.send_message(self.owner.uid,
                #                       '@{} использует Стражницу, предполагая '
                #                       'что у @{} {}, но не угадывает.'.format(self.owner.name,
                #                                                               game.victim.name,
                #                                                               game.guess),
                #                       reply_markup=markup)