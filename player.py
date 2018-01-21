import random


class Player:
    def __init__(self, uid:int, lost:bool=False, defence:bool=False):
        self.uid = uid
        self.lost = lost
        self.defence = defence
        self.won_round = False

    def take_card(self, state):
        state.playerHands[self].append(state.deck.pop())

    def __eq__(self, other):
        return self.uid == getattr(other, 'uid', None)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(self.uid)

    def __repr__(self):
        return "User {0}".format(self.uid)


class PlayerCtl:
    def __init__(self, number_of_players:int, **kwargs):

        if not kwargs.get('skip', False):
            self.users = [Player(uid) for uid in range(1, number_of_players + 1)]
            self.next_player_index = 0

    def add(self, user):
        self.users.append(user)

    def shuffle(self):
        random.shuffle(self.users)

    def get_current_player(self):
        """
        :return: current player to make move
        """
        while self.users[self.next_player_index].lost:
            self.next_player_index += 1
            if self.next_player_index == len(self.users):
                self.next_player_index = 0

        result = self.next_player_index
        self.next_player_index = (self.next_player_index + 1) % len(self.users)
        return self.users[result]

    def __contains__(self, user):
        return user in self.users

    def kill(self, user):
        self.users[self.users.index(user)].lost = True

    def players_left_number(self):
        return len([player for player in self.users if not player.lost])

    def get_victims(self, dealer):
        victims = []
        for user in self.users:
            if not user.defence and user.uid != dealer.uid:
                victims.append(user)
        return victims

    def clone(self):
        """
        clones current user ctl
        :return: deep clone
        """
        cloned = PlayerCtl(len(self.users), skip=True)
        cloned.users = [Player(user.uid, user.lost, user.defence) for user in self.users]
        cloned.next_player_index = self.next_player_index
        return cloned

    def num_users(self):
        return len(self.users)

    def get_left_player(self):
        for player in self.users:
            if not player.lost:
                return player

        raise AssertionError("No players left!")

    def reset(self):
        self.next_player_index = 0
        for user in self.users:
            user.defence = user.lost = user.won_round = False