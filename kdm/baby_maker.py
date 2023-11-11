import sys
from typing import Union
import kdm
from kdm.scribe import DragonInheritance


MAX_UNDERSTANDING = 9  # Maximum possible understanding for a survivor.
AUGURY_UNDERSTANDING_THRESHOLD = 3  # Required understanding to get a bonus to augury roll.
UNDERSTANDING_EVENTS = [3, 6, 9]  # understanding values that trigger understanding events.


class BabyMaker:

    def __init__(self, settlement) -> None:
        self.settlement = settlement
    
    def save(self, out_path=None):
        self.settlement.save(out_path)
    
    def make_babies(self, endeavor: Union[int,None]=None, father: Union[str,list,None]=None, mother: Union[str,list,None]=None):
        if endeavor is None:
            endeavor = self.settlement["endeavors"]
        if endeavor <= 0:
            print("No endeavor, no babies to make!")
            return

        if father is None:
            father = []
        elif not isinstance(father, list):
            father = [father.lower()]
        else:
            father = [x.lower() for x in father]
        
        if mother is None:
            mother = []
        elif not isinstance(mother, list):
            mother = [mother.lower()]
        else:
            mother = [x.lower() for x in mother]
        
        print(f"Attempting to make babies with {endeavor} endeavor.")
        for i in range(endeavor):
            print(f"Endeavor {endeavor} --> {endeavor-1}")
            endeavor -= 1
            augurer = self.select_augurer(father, mother)
            if self.augur(augurer):
                self.intimacy(*self.select_mates(augurer, father, mother))
    
    def augur(self, survivor):
        roll = kdm.roll()

        bonus = 0
        if survivor["understanding"] >= AUGURY_UNDERSTANDING_THRESHOLD:
            bonus += 1
        
        result = roll + bonus
        print(f"{survivor['name']} augured, roll {roll} + {bonus} (understanding: {survivor['understanding']})")

        if result <= 3:
            self.remove_resource()
            if survivor["understanding"] < MAX_UNDERSTANDING:
                print(f"{survivor['name']} gained 1 understanding ({survivor['understanding']} --> {survivor['understanding']+1})")
                survivor["understanding"] += 1
                if survivor["understanding"] in UNDERSTANDING_EVENTS:
                    self.settlement.understanding_event(survivor)
        elif result <= 7:
            if survivor["survival"] < self.settlement["survivalLimit"]:
                print(f"{survivor['name']} gained 1 survival ({survivor['survival']} --> {survivor['survival'] + 1})")
                survivor["survival"] += 1
        else:
            print(f"{survivor['name']} triggered intimacy.")
            return 1  # trigger intimacy
        return 0  # Do not trigger intimacy

    def select_augurer(self, father, mother):
        def _augur_filter(_x):
            _result = []
            # Is the survivor in our curated list?
            _in_mother = _x["name"].lower() in mother
            _in_father = _x["name"].lower() in father
            _result.append(-int(_in_mother or _in_father))
            
            # If it's in the list, sort by index in the list. Mother & father tie here.
            if _in_mother:
                _result.append(mother.index(_x["name"].lower()))
            elif _in_father:
                _result.append(father.index(_x["name"].lower()))
            else:
                _result.append(sys.maxsize)
            
            # Do they have enough understanding to get the augury bonus?
            _result.append(-int(_x["understanding"] >= AUGURY_UNDERSTANDING_THRESHOLD))

            # Do they have their once in a lifetime re-roll?
            _result.append(-int(_x["reroll"]))

            # Do they have less than the maximum understanding (room to grow)?
            _result.append(-int(_x["understanding"] < MAX_UNDERSTANDING))

            # How close are they to their next understanding event?
            for _epoch in UNDERSTANDING_EVENTS:
                _diff = _epoch - _x["understanding"]
                if _diff > 0:
                    _result.append(_diff)
                    break

            # How much understanding do they have?
            _result.append(-_x["understanding"])

            # Have they reached the survival limit?
            _result.append(-int(_x["survival"] < self.settlement["survivalLimit"]))

            # Males are better for augury, because they are less likely to die in childbirth.
            #  So any survival or understanding gains are more likely to be beneficial.
            _result.append(-int(_x["gender"] == "M"))
        
        candidates = [
            x for x in self.settlement.survivors.values()
            if x["dead"] is False and "destroyedGenitals" not in x["severeInjuries"]
        ]
        if not candidates:
            print("No living, breedable candidates for augury!")
            return
        
        return sorted(candidates, key=_augur_filter)[0]

    def select_mates(self, augurer, father, mother):
        """Return mates in the order (FATHER, MOTHER)"""
        result = [augurer]
        search_gender = "M" if augurer["gender"] == "F" else "F"  # Are we looking for a male or a female?
        curated = father if search_gender == "M" else mother

        def _mate_filter(_x):
            _result = []
            # Is the survivor in our curated list?
            _in_curated = _x["name"].lower() in curated
            _result.append(-int(_in_curated))
            
            # If it's in the list, sort by index in the list.
            if _in_curated:
                _result.append(curated.index(_x["name"].lower()))
            else:
                _result.append(sys.maxsize)
            
            # Do they have their once in a lifetime re-roll?
            _result.append(-int(_x["reroll"]))

            # Prioritize survivors will stat penalties - they might die.
            for _attr in ["MOV", "SPD", "ACC", "LCK", "EVA", "STR"]:
                _result.append(_x["attributes"][_attr])
            
            # Breed people with higher injuries and disorders.
            _result.append(-len(_x["severeInjuries"]))
            _result.append(-len(_x["disorders"]))

            # Other attributes.
            _result.append(_x["courage"])
            _result.append(_x["understanding"])

        candidates = [
            x for x in self.settlement.survivors.values()
            if x["gender"] == search_gender and x["dead"] is False and "destroyedGenitals" not in x["severeInjuries"]
        ]
        if len(candidates) <= 0:
            print(f"No living mates found for: {augurer}")
            return
        
        result.append(sorted(candidates, key=_mate_filter)[0])
        result.sort(key=lambda x: x["gender"] == "F")

        print(
            "Selected mates - "
            f"Father: {result[0]['name']} (und: {result[0]['understanding']}, reroll: {result[0]['reroll']}) "
            f"Mother: {result[1]['name']} (und: {result[1]['understanding']}, reroll: {result[1]['reroll']})"
        )
        return tuple(result)
    
    def intimacy(self, father, mother):
        if self.settlement["campaign"].lower() == "potstars":
            return self.intamacy_potstars(father, mother)
        else:
            raise ValueError(f"Campagin: {self.settlement['campaign']} intimacy rules not implemented.")
    
    def roll_intimacy(self):
        if self.settlement["principles"]["newLife"] == "survivalOfTheFittest":
            rolls = [kdm.roll(), kdm.roll()]
            roll = min(rolls)
            print(f"Rolled: {rolls}, selected {roll} (Survival of the Fittest)")
        elif self.settlement["principles"]["newLife"] == "protectTheYoung":
            rolls = [kdm.roll(), kdm.roll()]
            roll = max(rolls)
            print(f"Rolled: {rolls}, selected {roll} (Protect the Young)")
        else:
            rolls = [kdm.roll()]
            roll = rolls[0]
            print(f"Rolled {roll}")
        return rolls, roll

    def intamacy_potstars(self, father, mother, rolls=None, roll=None):
        new_survivors = []
        if rolls is None:
            rolls, roll = self.roll_intimacy()
        
        if roll == 1:
            if self.settlement["principles"]["newLife"] == "survivalOfTheFittest" and all(x == 1 for x in rolls) and mother["reroll"] and father["reroll"]:
                print("Using both the mother and father's once in a lifetime re-roll so try to survive snake-eyes (Survival of the Fittest).")
                mother["reroll"] = father["reroll"] = False
                return self.intamacy_potstars(father, mother)
            elif self.settlement["principles"]["newLife"] == "survivalOfTheFittest" and not all(x == 1 for x in rolls):
                if mother["reroll"]:
                    mother["reroll"] = False
                    print("Using the mother's once in a lifetime re-roll (Survival of the Fittest).")
                    rolls = [max(rolls), kdm.roll()]
                    return self.intamacy_potstars(father, mother, rolls=rolls, roll=rolls[-1])
                elif father["reroll"]:
                    father["reroll"] = False
                    print("Using the father's once in a lifetime re-roll (Survival of the Fittest).")
                    return self.intamacy_potstars(father, mother, rolls=rolls, roll=rolls[-1])
            else:
                print("No re-rolls available or you rolled snake eyes and did not have 2 re-rolls. Both survivors are killed.")
                self.settlement.kill_survivor(father["id"], "Childbirth.")
                self.settlement.kill_survivor(mother["id"], "Childbirth.")
        elif roll in {2, 3}:
            print("The child perishes in childbirth and the mother's genitals are destroyed.")
            mother["severeInjuries"].append("destroyedGenitals")
            # TODO it says to add "scar" to the mother, which is a dragon trait, but I don't see where to add that in the file
            print(f"MANUALLY ADD Scar Dragon trait to {mother['name']}")
        elif roll in {4, 5}:
            if self.settlement["principles"]["newLife"] == "protectTheYoung":
                print("MANUALLY GIVE new survivor the Noble Surname dragon trait (Protect the Young)")
                # TODO figure out how to do this automatically.
            print("A strong child is born with +1 strength.")
            new_survivors.append(self.settlement.new_survivor(gender="F", strength=1))
        elif roll in {6, 7, 8, 9}:
            dragon_inheritance = []
            if self.settlement["principles"]["newLife"] == "survivalOfTheFittest" and roll in {6, 7}:
                dragon_inheritance.append(self.select_dragon_inheritance(father, mother))
            print("A new survivor with 1 dragon inheritance is born.")
            dragon_inheritance.append(self.select_dragon_inheritance(father, mother, exclude=dragon_inheritance))
            new_survivors.append(self.settlement.new_survivor(gender="F", dragon_inheritance=dragon_inheritance))
        else:
            print("Twins are born! Each with 1 dragon inheritance.")
            new_survivors.append(
                self.settlement.new_survivor(
                    gender="F",
                    dragon_inheritance=self.select_dragon_inheritance(father, mother)
                )
            )

            abilities = None
            if "hovel" in self.settlement["innovations"]:
                favored_roll = kdm.roll()
                if favored_roll <=5:
                    abilities = ["iridescentHide"]
                else:
                    abilities = ["oraclesEye"]
                print(f"The settlement has innovated Hovel, so one of the twins is favored. They rolled {favored_roll}, they gained: {abilities[0]}")
            
            new_survivors.append(
                self.settlement.new_survivor(
                    gender="F",
                    dragon_inheritance=self.select_dragon_inheritance(father, mother),
                    abilities=abilities
                )
            )

    
    def select_dragon_inheritance(self, father, mother, exclude=None):
        candidates = set(DragonInheritance.__members__.values())
        if exclude is not None:
            exclude = set(exclude)
            candidates -= exclude

        if DragonInheritance.UNDERSTANDING in candidates:
            # Always prioritize understanding, because it will help new children augur better.
            understanding = max((father["understanding"], mother["understanding"]))
            if understanding >= 2:
                return DragonInheritance.UNDERSTANDING
        
        # TODO give scores to fighting arts and disorders to choose the best option.
        if DragonInheritance.FIGHTING_ART in candidates:
            arts = father["fightingArts"] + mother["fightingArts"]
            if arts:
                return DragonInheritance.FIGHTING_ART
        if DragonInheritance.COURAGE in candidates:
            courage = max((father["courage"], mother["courage"]))
            if courage >= 2:
                return DragonInheritance.COURAGE
        
        if DragonInheritance.SURNAME in candidates:
            return DragonInheritance.SURNAME
        
        if DragonInheritance.DISORDERS in candidates:
            return DragonInheritance.DISORDERS
        
        return DragonInheritance.NONE
