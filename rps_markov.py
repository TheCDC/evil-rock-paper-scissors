#!/usr/bin/env python3

# rock paper scissors game which models the player as a markov chain
# and uses it to predict their next move
import pymarkoff
import random
import pprint
# possible moves

throw_types = [
    "R",
    "S",
    "P",
]
throw_to_name = {"R": "Rock", "P": "Paper", "S": "Scissors"}
# what beats what/does X beat Y?
beats = {
    "R": "S",
    "S": "P",
    "P": "R",
}
beaten_by = {beats[i]: i for i in beats.keys()}

# game loop needs to always ask a player for a throw
# initially, there is no history of throws
# let the player make an arbitrary number of throws at the beginning
# before beginning to model them.

class QuitError(Exception):
    pass

def user_move():
    response = ''
    while True:
        try:
            response = input("What's your move? [r,p,s] or q to quit\n>>>").strip().upper()
        except:
            raise QuitError("Interrupted")
        if response == 'Q':
            raise QuitError("Quit requested")
        if not response in throw_types:
            print("That's not a valid move...")
        else:
            break
    return response


def pc_choose(samples, brain):
    try:
        prev = samples[-1]
        # print("Trying to predict based on", prev)
        predicted_player_move = brain.get_next(prev)
        # print("Prediction made!")
        return beaten_by[predicted_player_move[0]]
    except ValueError:
        # print("Not enough data.")
        pass
    except IndexError:
        # print("Not enough samples.")
        pass
    return random.choice(throw_types)

brain = pymarkoff.Markov(orders=(0, 1), discrete_mode=False)

min_sample_size = 10
player_score = 0
pc_score = 0
player_name = input("What is your name?\n>>>").strip()
try:
    with open("rps_markov_samples/" + player_name + ".txt") as f:
        samples = eval(f.read())
except (FileNotFoundError, SyntaxError):
    samples = []
while True:

    pc_choice = pc_choose(samples, brain)
    try:
        player_choice = user_move()
    except QuitError as e:
        with open("rps_markov_samples/" + player_name + ".txt", 'w') as f:
            f.write(pprint.pformat(samples))
        print("Have a nice day!")
        quit()

    samples.append((player_choice, pc_choice))
    brain.feed([samples[-3:]])
    # print(dict(brain))
    # print(samples)
    print("You threw {}, the computer threw {}.".format(
        *[throw_to_name[i] for i in [player_choice, pc_choice]]))

    if beats[pc_choice] == player_choice:
        print("The computer wins!")
        pc_score += 1
    elif beats[player_choice] == pc_choice:
        print("You win!")
        player_score += 1
    elif pc_choice == player_choice:
        print("Draw!")
    print("Scores: PC: {}, You: {}".format(pc_score, player_score))
s
