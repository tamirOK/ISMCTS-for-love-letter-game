import sys  # We need sys so that we can pass argv to QApplication

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import design  # This file holds our MainWindow and all design related things
from cardclasses import card_dict
# it also keeps events etc that we defined in Qt Designer
from game import LoveLetterState
from playing_mode import PlayingMode


class Game(QThread):
    history_signal = pyqtSignal(str)
    card_label_signal = pyqtSignal(int, str)
    notification_signal = pyqtSignal(bool)
    deck_signal = pyqtSignal(str)
    update_field = pyqtSignal()
    update_info = pyqtSignal(str)
    hide_card = pyqtSignal()
    show_card = pyqtSignal()
    show_turn = pyqtSignal(bool)
    update_count = pyqtSignal(str)

    def __init__(self, form, parent=None):
        self.form = form
        QThread.__init__(self, parent)

    def run(self):
        decks = []

        with open('decks.txt') as f:
            for line in f:
                splitted = line.split()
                decks.append([card_dict[card] for card in splitted])

        state = LoveLetterState(2, decks)
        state.start_new_round()

        mode = PlayingMode(state, "real_player")
        while not state.game_over:
            if state.playerToMove == state.real_players[0]:
                self.show_turn.emit(True)
                self.update_field.emit()
                victim, guess = None, None

                self.update_info.emit("You are {}".format(state.real_players[0]))

                self.show_card.emit()

                self.card_label_signal.emit(0, state.playerHands[state.playerToMove][0].name)
                self.card_label_signal.emit(1, state.playerHands[state.playerToMove][1].name)

                self.history_signal.emit("Your cards are {} and {}".format(state.playerHands[state.playerToMove][0],
                                                                           state.playerHands[state.playerToMove][1]))

                while not self.form.is_selected:
                    QApplication.processEvents()

                if state.playerHands[state.playerToMove][0].name == self.form.card_name:
                    move = state.playerHands[state.playerToMove][0]
                else:
                    move = state.playerHands[state.playerToMove][1]

                if move.name == "Guard":
                    for buttom in self.form.select_victim.findChildren(QRadioButton):
                        if buttom.isChecked():
                            guess = card_dict[str(buttom.text())]
                            break

                self.history_signal.emit("You played with {}".format(move))
                self.update_field.emit()

            else:
                self.show_turn.emit(False)
                self.hide_card.emit()
                move, victim, guess = mode.get_move(0)
                self.card_label_signal.emit(0, state.playerHands[state.playerToMove][0].name)
                self.history_signal.emit("Opponent played with {}".format(move))

            messages = state.do_move(move, verbose=True, global_game=False, victim=victim, guess=guess,
                                     real_player=state.playerToMove == mode.real_player, vanilla=False)

            for message in messages:
                self.history_signal.emit(message)

            self.deck_signal.emit("{} cards in deck".format(len(state.deck)))

            if state.round_over:
                self.history_signal.emit("#" * 40)
                self.history_signal.emit("# " * 15 + "ROUND " + str(state.round) + " " + "#" * 15)
                self.history_signal.emit("#" * 40)
                winner = [user for user in state.user_ctl.users if user.won_round][0]
                if winner == state.real_players[0]:
                    self.update_count.emit("You: {}".format(state.tricksTaken[winner]))
                else:
                    self.update_count.emit("Opponent: {}".format(state.tricksTaken[winner]))
                state.start_new_round(first_player=winner)


class ExampleApp(QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # Explaining super is out of the scope of this article
        # So please google it if you're not familar with it
        # Simple reason why we use it here is that it allows us to
        # access variables, methods etc in the design.py file
        super(self.__class__, self).__init__()
        self.setupUi(self)  # This is defined in design.py file automatically
        # It sets up layout and widgets that are defined
        self.game = Game(self)

        self.game.deck_signal.connect(self.update_deck_info, Qt.QueuedConnection)
        self.game.history_signal.connect(self.update_history, Qt.QueuedConnection)
        self.game.notification_signal.connect(self.show_notification, Qt.QueuedConnection)
        self.game.update_field.connect(self.update_field, Qt.QueuedConnection)
        self.game.card_label_signal.connect(self.update_cards, Qt.QueuedConnection)
        self.game.update_info.connect(self.update_info, Qt.QueuedConnection)
        self.game.hide_card.connect(self.hide_card, Qt.QueuedConnection)
        self.game.show_card.connect(self.show_card, Qt.QueuedConnection)
        self.game.show_turn.connect(self.show_turn, Qt.QueuedConnection)
        self.game.update_count.connect(self.update_player_count, Qt.QueuedConnection)

        self.card1.mouseReleaseEvent = self.make_action
        self.card2.mouseReleaseEvent = self.make_action

        # self.card1.clicked.connect(self.make_action)
        # self.card2.clicked.connect(self.make_action)

        self.is_selected = False
        self.card_name = None
        self.turn_info.setVisible(False)

        self.game.start()

    def hide_card(self):
        self.card2.setVisible(False)

    def show_card(self):
        self.card2.setVisible(True)

    def update_info(self, message):
        self.player_info.setText(message)

    def make_action(self, event):
        print("Hello, world")
        # sender = self.sender()
        # self.is_selected = True
        # self.card_name = sender.text()

    def update_deck_info(self, msg):
        self.deck.setText(msg)

    def update_history(self, msg):
        self.history.addItem(msg)

    def show_notification(self, flag):
        self.notification.setText("Now is your turn")

    def update_field(self):
        self.is_selected = False

    def update_cards(self, index, cardname):
        if index == 0:
            self.card1.setText(cardname)
        else:
            self.card2.setText(cardname)

    def show_turn(self, show):
        self.turn_info.setVisible(show)

    def update_player_count(self, message):
        message = str(message)
        if message.startswith("Opponent"):
            self.opponent_count.setText(message)
        else:
            self.real_player_count.setText(message)

def main():
    app = QApplication(sys.argv)  # A new instance of QApplication
    form = ExampleApp()  # We set the form to be our ExampleApp (design)
    form.show()  # Show the form
    app.exec_()  # and execute the app


if __name__ == '__main__':  # if we're running file directly and not importing it
    main()
