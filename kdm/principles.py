"""Apply principle bonuses to newborn survivors like so:

for principle_key in settlement["principles"].values():
    if not principle_key:
        continue
    principle = PrincipleRegistry[principle_key]
    principle.newborn(survivor)
"""
import kdm
from kdm.events import Understanding

class PrincipleRegistry(type):
    principles = {}

    def __new__(cls, name, bases, dct):
        klass = super().__new__(cls, name, bases, dct)
        cls.principles[klass.KEY] = klass
        return klass

class Principle(metaclass=PrincipleRegistry):
    KEY = None

    def newborn(self, survivor, settlement):
        pass

    def death(self, settlement):
        pass


class Barbaric(Principle):
    KEY = "barbaric"

    def newborn(self, survivor, settlement):
        super().newborn(survivor, settlement)
        survivor["attributes"]["STR"] += 1
        print("Principle Barbaric added +1 strength.")


class Cannibalize(Principle):
    KEY = "cannibalize"

    def death(self, settlement):
        super().death(settlement)
        resource = settlement.add_random_resource()
        print(f"Principle Cannibalize - added {resource} to settlement storage.")


class Graves(Principle):
    KEY = "graves"

    def newborn(self, survivor, settlement):
        super().newborn(survivor, settlement)
        Understanding(survivor, settlement).give(1)
        print(f"Principle Graves - gained 1 understanding.")

    def death(self, settlement):
        super().death(settlement)
        if settlement["departing"]:
            gain = 2
        else:
            gain = 1
        settlement["endeavors"] += gain
        print(f"Principle Graves - gained {gain} endeavor.")


class SurvivalOfTheFittest(Principle):
    KEY = "survivalOfTheFittest"

    def newborn(self, survivor, settlement):
        super().newborn(survivor, settlement)
        survivor["attributes"]["STR"] += 1
        survivor["attributes"]["EVA"] += 1
        print(f"Principle Survival of the Fittest - gained 1 strength and evasion.")
    
    def intimacy_roll(self):
        rolls = [kdm.roll(), kdm.roll()]
        roll = min(rolls)
        print(f"(Survival of the Fittest) Rolled: {rolls}, selected {roll}")
        return rolls, roll


class ProtectTheYoung(Principle):
    KEY = "protectTheYoung"

    def intimacy_roll(self):
        rolls = [kdm.roll(), kdm.roll()]
        roll = max(rolls)
        print(f"(Protect the Young) Rolled: {rolls}, selected {roll}")
        return rolls, roll
