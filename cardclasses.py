# -*- coding: utf-8 -*-
card_names = ['Princess', 'Countess', 'King', 'Prince', 'Maid', 'Baron', 'Priest', 'Guard']


class Card:
    value = None
    need_victim = False
    need_guess = False
    owner = None

    def activate(self, game):
        game.used_cards.append(self.owner.card)

    def __eq__(self, other):
        return self.name == other

    def __le__(self, other):
        return self.value <= other.value

    def __ge__(self, other):
        return self.value >= other.value

    def __lt__(self, other):
        return self.value < other.value

    def __gt__(self, other):
        return self.value > other.value


class Princess(Card):
    name = 'Princess'
    value = 8

    def activate(self, game):
        #game.bot.send_message(game.group_chat, '@{} сбрасывает Принцессу и проигрывает.'.format(self.owner.name))
        #game.bot.send_message(self.owner.uid, '@{} сбрасывает Принцессу и проигрывает.'.format(self.owner.name),
        #                      reply_markup=markup)
        super(Card, self).activate()
        game.users.kill(self.owner)


class Countess(Card):
    name = 'Countess'
    value = 7

    def activate(self, game):
        pass
        # TODO: не забыть сбросить графиню
        #markup = types.ReplyKeyboardRemove(selective=False)
        #game.bot.send_message(game.group_chat, '@{} сбрасывает Графиню.'.format(self.owner.name))
        #game.bot.send_message(self.owner.uid, '@{} сбрасывает Графиню.'.format(self.owner.name), reply_markup=markup)


class King(Card):
    name = 'King'
    value = 6
    need_victim = True

    def activate(self, game):
        super(Card, self).activate()
        if game.card_without_action:
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

            game.dealer.card.owner = game.victim
            game.victim.card.owner = game.dealer
            game.dealer.card, game.victim.card = game.victim.card, game.dealer.card
            

class Prince(Card):
    name = 'Prince'
    value = 5
    need_victim = True

    def activate(self, game):
        super(Card, self).activate()
        game.used_cards.append(game.victim.card)
        if game.victim.card.name == 'Princess':
            # game.bot.send_message(game.group_chat,
            #                       '@{0} использует Принца против @{1}. '
            #                       '@{1} сбрасывает Принцессу и проигрывает.'.format(self.owner.name, game.victim.name))
            # game.bot.send_message(self.owner.uid,
            #                       '@{0} использует Принца против @{1}. '
            #                       '@{1} сбрасывает Принцессу и проигрывает.'.format(self.owner.name, game.victim.name),
            #                       reply_markup=markup)
            game.users.kill(game.victim)
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
            game.deck.append(game.first_card)

        game.victim.take_card(game.deck)


class Maid(Card):
    name = 'Maid'
    value = 4

    def activate(self, game):
        super(Card, self).activate()
        # game.bot.send_message(game.group_chat, '@{} защищен Служанкой в течение круга.'.format(self.owner.name))
        # game.bot.send_message(self.owner.uid, '@{} защищен Служанкой в течение круга.'.format(self.owner.name),
        #                       reply_markup=markup)
        self.owner.defence = True


class Baron(Card):
    name = 'Baron'
    value = 3
    need_victim = True

    def activate(self, game):
        super(Card, self).activate()
        if game.card_without_action:
            pass
            # game.bot.send_message(game.group_chat,
            #                       '@{} использует Барона впустую, так как все защищены.'.format(
            #                           self.owner.name))
            # game.bot.send_message(self.owner.uid,
            #                       '@{} использует Барона впустую, так как все защищены.'.format(
            #                           self.owner.name),
            #                       reply_markup=markup)
        else:
            if self.owner.card > game.victim.card:
                # game.bot.send_message(game.group_chat,
                #                       '@{0} использует Барона против @{1} и выигрывает. '
                #                       'У @{1} оказалась карта "{2}"'.format(self.owner.name,
                #                                                             game.victim.name, game.victim.card.name))
                # game.bot.send_message(self.owner.uid,
                #                       '@{0} использует Барона против @{1} и выигрывает. '
                #                       'У @{1} оказалась карта "{2}"'.format(self.owner.name,
                #                                                             game.victim.name, game.victim.card.name),
                #                       reply_markup=markup)
                game.used_cards.append(game.victim.card)
                game.users.kill(game.victim)
            elif self.owner.card < game.victim.card:
                # game.bot.send_message(game.group_chat,
                #                       '@{0} использует Барона против @{1}, но проигрывает. '
                #                       'у {0} оказалась карта "{2}"'.format(self.owner.name,
                #                                                            game.victim.name, self.owner.card.name))
                # game.bot.send_message(self.owner.uid,
                #                       '@{0} использует Барона против @{1}, но проигрывает. '
                #                       'у {0} оказалась карта "{2}"'.format(self.owner.name,
                #                                                            game.victim.name, self.owner.card.name),
                #                       reply_markup=markup)
                game.used_cards.append(self.owner.card)
                game.users.kill(self.owner)
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

    def activate(self, game):
        super(Card, self).activate()
        if game.card_without_action:
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

    def activate(self, game):
        super(Card, self).activate()
        if game.card_without_action:
            pass
            # game.bot.send_message(game.group_chat,
            #                       '@{} использует Стражницу впустую, так как все защищены.'.format(
            #                           self.owner.name))
            # game.bot.send_message(self.owner.uid,
            #                       '@{} использует Стражницу впустую, так как все защищены.'.format(
            #                           self.owner.name),
            #                       reply_markup=markup)
        else:
            if game.victim.card.name == game.guess:
                # game.bot.send_message(game.group_chat,
                #                       '@{} использует Стражницу и угадывает что у @{} {}.'.format(self.owner.name,
                #                                                                                   game.victim.name,
                #                                                                                   game.guess))
                # game.bot.send_message(self.owner.uid,
                #                       '@{} использует Стражницу и угадывает что у @{} {}.'.format(self.owner.name,
                #                                                                                   game.victim.name,
                #                                                                                   game.guess),
                #                       reply_markup=markup)
                game.used_cards.append(game.victim.card)
                game.users.kill(game.victim)
            else:
                pass
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