"""
Helpers for random dictionary words
"""

import random 

class RandomWord:
    """Produce random words from the dictionary."""

    def __init__(self):
        self.words = []
        with open('/usr/share/dict/words') as w:
            for word in w:
                self.words.append(word.strip())

    def choice(self):
        return random.choice(self.words)


randword = RandomWord()
