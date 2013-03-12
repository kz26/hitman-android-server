import os
import random

PATH = os.path.dirname(os.path.realpath(__file__))

adjectives = []
with open(os.path.join(PATH, 'adjectives.txt'), 'r') as f:
    for line in f:
        l = line.rstrip()
        if l:
            adjectives.append(l)

nouns = []
with open(os.path.join(PATH, 'nouns.txt'), 'r') as f:
    for line in f:
        l = line.rstrip()
        if l:
            nouns.append(l)

def gen_kill_code():
    return random.choice(adjectives).lower() + " " + random.choice(nouns).lower()
