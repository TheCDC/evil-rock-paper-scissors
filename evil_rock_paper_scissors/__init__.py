#!/usr/bin/env python3

# rock paper scissors game which models the player as a markov chain
# and uses it to predict their next move
import pymarkoff
import random
import enum


class Throws(enum.Enum):
    """Represents possible moves in rock, paper, scissors."""
    rock = 'Rock'
    paper = 'Paper'
    scissors = 'Scissors'

    def __len__(self):
        # necessary to define for Markov model.
        return 1


# what beats what/does X beat Y?
beats = {
    Throws.rock: Throws.scissors,
    Throws.scissors: Throws.paper,
    Throws.paper: Throws.rock,
}
beaten_by = {beats[i]: i for i in beats.keys()}


class QuitError(Exception):
    pass


class Player:
    """Represents a player in the Game."""

    def __init__(self, name, decision_function):
        self.name = name
        self.decision_function = decision_function

    def move(self, other_previous_move):
        return self.decision_function(other_previous_move)


def create_ai():
    """Return the AI decision function."""
    # instantiate the markov model
    memory_length = 3
    brain = pymarkoff.Markov(
        [], orders=tuple(range(memory_length)), discrete=False)
    samples = list()

    def decision(other_previous_move):
        # don't record null moves
        if other_previous_move is not None:
            samples.append(other_previous_move)
        # update the model
        brain.feed([samples[-memory_length:]])
        # make a move based onthe model
        my_move = pc_choose(samples, brain)
        return my_move

    return decision


class Game:
    """Represent the game state."""

    def __init__(self, player_one: Player, player_two: Player):
        self.players = [player_one, player_two]
        self.previous_moves = [None, None]
        self.scores = [0 for _ in self.players]
        self.draws = 0

    def advance(self):
        # leat each player make a move based on their opponent's previous move
        moves = [
            player.move(self.previous_moves[(index + 1) % 2])
            for index, player in enumerate(self.players)
        ]
        # record the new moves
        self.previous_moves = moves
        # determin the winner
        if beats[moves[0]] == moves[1]:
            self.scores[0] += 1
            return (self.players[0], moves[0])
        elif beats[moves[1]] == moves[0]:
            self.scores[1] += 1
            return (self.players[1], moves[1])
        elif moves[0] == moves[1]:
            self.draws += 1
            return (None, None)
        else:
            raise ValueError('This should never happen.')


def random_move(other_previous_move=None):

    return random.choice(list(Throws))


def user_move(other_previous_move=None):
    """Ask a user for their move.
    Sanitizes input."""
    response = ''
    chosen = False
    while not chosen:
        try:
            response = input(
                "What's your move? (r)ock, (p)aper, (s)cissors, or q to quit\n>>>"
            ).strip().upper()
        except (KeyboardInterrupt, EOFError):
            raise QuitError("Interrupted")
        if response == 'Q':
            raise QuitError("Quit requested")
        for t in Throws:
            m = t.name[0].upper()
            if m == response:
                user_throw = t
                chosen = True
                break
        else:
            print("That's not a valid move...")

    return user_throw


def pc_choose(samples, brain):
    """Return the ai's next move based on
    markov model of previous moves."""
    try:
        prev = samples[-1]
        predicted_player_move = brain.get_next((prev, ))
        return beaten_by[predicted_player_move]
    except pymarkoff.InvalidStateError:
        # this error occurs when the latest moves haven't yet been seen

        pass
    except IndexError:
        # this error occurs on early moves because there aren't enough samples.
        # so do nothing
        pass
    return random.choice(list(Throws))


def same_choose():
    choice = random.choice(list(Throws))

    def wrapped(*args):
        return choice

    return wrapped


human_player = Player('Human', user_move)
random_player = Player('Rando', random_move)
lazy_player = Player('Lazy', same_choose())
ai_player = Player('PC', create_ai())


def main():

    print("Welcome to Evil Rock Paper Scissors")

    g = Game(human_player, ai_player)
    while True:

        try:
            winner = g.advance()
            if winner[0] is not None:
                print(
                    f'The winner is {winner[0].name}, who threw {winner[1].name}'
                )
            else:
                print('Draw!')
            print('Scores:', ','.join(
                f'{p.name}: {s}' for p, s in zip(g.players, g.scores)),
                  'Draws:', g.draws)
        except (QuitError, KeyboardInterrupt):

            print()
            print("Have a nice day!")
            # print(dict(brain))
            quit()


if __name__ == '__main__':
    main()
