import random


def roll(sides=10):
    return random.randint(1, sides)


class RollResult:

    def __init__(self, result, sides=10, bonuses=None):
        self.result = result
        self.sides = sides
        self.bonuses = bonuses or []
    

class RollBonus:

    def __init__(self, value, reason):
        self.value = value
        self.reason = reason