from copy import deepcopy

from strategy import get_guess_card
from collections import defaultdict
from rule_based import get_move


class Minimax:
    INF = 1 << 30

    @staticmethod
    def get_move(state):
        # print(state.playerHands[state.playerToMove])
        move, victim, guess = get_move(state, ismcts=True)

        if move:
            return move, victim, guess

        move_counter = defaultdict(int)
        moves = state.get_moves()

        for _ in range(201):
            rootstate = state.clone_and_randomize()
            value, move = Minimax._minimax(rootstate, True, -Minimax.INF, Minimax.INF, 1)
            move_counter[move] += 1

        # from pprint import pprint
        # pprint(move_counter)

        result_move = max(moves, key=lambda item: move_counter[item])
        victim, guess = None, None

        if result_move.name == "Guard":
            victim, guess = get_guess_card(state.user_ctl.users, state.playerToMove, state.seen_cards)

        return result_move, victim, guess

    @staticmethod
    def _minimax(state, is_maximizing_player, alpha, beta, depth):
        if state.round_over:
            try:
                assert len([1 for user in state.user_ctl.users if user.lost]) == 1 or not state.deck
            except AssertionError:
                import pdb
                pdb.set_trace()
            if not state.deck:
                def played_card_sum(player):
                    result = 0
                    for moved_player, card in state.currentTrick:
                        if moved_player == player:
                            result += card.value
                    return result

                cards = [(player, state.playerHands[player], played_card_sum(player))
                         for player in state.user_ctl.users
                         if not player.lost]

                cards.sort(key=lambda item: (item[1], item[2]), reverse=True)

                winner = cards[0][0]

                if winner == state.playerToMove:
                    if is_maximizing_player:
                        return depth - 100, None
                    else:
                        return 100 - depth, None
                else:
                    if is_maximizing_player:
                        return 100 - depth, None
                    else:
                        return depth - 100, None

            if is_maximizing_player:
                return depth - 100, None
            else:
                return 100 - depth, None

        if is_maximizing_player:
            best_value = -Minimax.INF
        else:
            best_value = Minimax.INF
        previous_move = None
        best_move = None

        for move in state.get_moves():
            if move == previous_move:
                continue
            previous_move = move
            victim, guess = None, None

            if move.name == "Guard":
                victim, guess = get_guess_card(state.user_ctl.users, state.playerToMove, state.seen_cards)

            state_copy = deepcopy(state)

            state_copy.do_move(move, victim=victim, guess=guess)

            value, _ = Minimax._minimax(state_copy, not is_maximizing_player, alpha, beta,depth + 1)

            if is_maximizing_player:
                if best_value < value:
                    best_value = value
                    best_move = move
                alpha = max(alpha, best_value)
            else:
                if best_value > value:
                    best_value = value
                    best_move = move
                beta = min(beta, best_value)

            if beta <= alpha:
                break

        return best_value, best_move
