import sys
from enum import Enum
from functools import partial
import kdm


class Age:
    MAX = 16
    EVENTS = (2, 6, 10, 15, 16)

    def __init__(self, survivor, settlement):
        self.survivor = survivor
        self.settlement = settlement

        self.map = {
            2: self.weapon_proficiency,
            6: self.improved_reflexes,
            10: self.enhanced_senses,
            15: None,
            16: None
        }
    
    def give(self, amount):
        if self.survivor["xp"] >= self.MAX:
            print(f"{self.survivor['name']} is already at the maximum age.")
            return
        
        starting = self.survivor["xp"]
        self.survivor["xp"] += amount
        
        for threshold in sorted(list(self.map.keys())):
            if starting >= threshold:
                continue

            if self.survivor["xp"] >= threshold:
                fnc = self.map[threshold]
                if fnc is None:
                    print(f"MANUAL: later age events are not implemented. Do them manually for {self.survivor['name']}")
                else:
                    fnc()
    
    def weapon_proficiency(self):
        rolls = [kdm.roll(), kdm.roll()]
        roll = sum(rolls)
        msg = f"Age event Weapon Proficiency - rolled {rolls} = {roll}: "
        if roll <= 2:
            self.survivor["attributes"]["EVA"] += 1
            msg += "gained 1 evasion."
        elif roll <= 6:
            self.survivor["attributes"]["STR"] += 1
            msg += "gained 1 strength."
        elif roll <= 15:
            fighting_art = self.settlement.add_random_fighting_art(self.survivor)
            msg += f"gained {fighting_art}"
        elif roll <= 19:
            self.survivor["attributes"]["ACC"] += 1
            msg += "gained 1 accuracy."
        else:
            self.survivor["attributes"]["LCK"] += 1
            msg += "gained 1 luck."
        print(msg)

    def improved_reflexes(self):
        rolls = [kdm.roll(), kdm.roll()]
        roll = sum(rolls)
        msg = f"Age event Improved Reflexes - rolled {rolls} = {roll}: "
        if roll <= 2:
            self.survivor["attributes"]["MOV"] += 1
            msg += "gained 1 movement."
        elif roll <= 6:
            fighting_art = self.settlement.add_random_fighting_art(self.survivor)
            msg += f"gained {fighting_art}"
        elif roll <= 15:
            self.survivor["attributes"]["STR"] += 1
            msg += "gained 1 strength."
        elif roll <= 19:
            fighting_art = self.settlement.add_random_fighting_art(self.survivor)
            msg += f"gained {fighting_art}"
        else:
            self.survivor["attributes"]["SPD"] += 1
            msg += "gained 1 speed."
        print(msg)

    def enhanced_senses(self):
        rolls = [kdm.roll(), kdm.roll()]
        roll = sum(rolls)
        msg = f"Age event Enhanced Senses - rolled {rolls} = {roll}: "
        if roll <= 2:
            self.survivor["attributes"]["SPD"] += 1
            msg += "gained 1 speed."
        elif roll <= 6:
            self.survivor["attributes"]["MOV"] += 1
            msg += "gained 1 movement."
        elif roll <= 15:
            fighting_art = self.settlement.add_random_fighting_art(self.survivor)
            msg += f"gained {fighting_art}"
        elif roll <= 19:
            fighting_art_1 = self.settlement.add_random_fighting_art(self.survivor)
            fighting_art_2 = self.settlement.add_random_fighting_art(self.survivor)
            msg += f"gained {fighting_art_1} and {fighting_art_2}"
        else:
            self.survivor["attributes"]["STR"] += 3
            msg += "gained 3 strength."
        print(msg)
    

class Understanding:
    MAX = 9
    EVENTS = (3, 9)

    def __init__(self, survivor, settlement):
        self.survivor = survivor
        self.settlement = settlement

        self.map = {
            3: self.awake,
            9: None
        }
    
    def give(self, amount):
        starting = self.survivor["understanding"]
        if self.survivor["understanding"] >= self.MAX:
            print(f"{self.survivor['name']} already has maximum understanding.")
            return
        
        self.survivor["understanding"] += amount
        
        for threshold in sorted(list(self.map.keys())):
            if starting >= threshold:
                continue

            if self.survivor["understanding"] >= threshold:
                fnc = self.map[threshold]
                if fnc is None:
                    print(f"MANUAL: later understanding events are not implemented. Do them manually for {self.survivor['name']}")
                else:
                    fnc()

    def awake(self):
        roll = kdm.roll()
        print(f"{self.survivor['name']} rolled a {roll} on the Awake understanding event.")
        if roll <= 3:
            if self.settlement["departing"]:
                print("Detected hunt phase, giving +1 strength and evasion tokens.")
                self.survivor["tempAttributes"]["STR"] += 1
                self.survivor["tempAttributes"]["EVA"] += 1
            else:
                print("Detected settlement phase, giving +2 endeavor only {} can use - will re-invest automatically.")
                if self.survivor["id"] not in self.settlement.temp_endeavor:
                    self.settlement.temp_endeavor[self.survivor["id"]] = 2
                else:
                    self.settlement.temp_endeavor[self.survivor["id"]] += 2
        elif roll <= 7:
            self.survivor["attributes"]["EVA"] += 1
            fighting_art = self.settlement.add_random_fighting_art(self.survivor)
            print(f"Gained +1 permanent evasion and {fighting_art} fighting art.")
            print("MANUAL: You must manually add the noble surname.")  
        else:
            self.survivor["attributes"]["EVA"] += 1
            if {"id": "championsRite"} not in self.survivor["fightingArts"]:
                self.survivor["fightingArts"].append({"id": "championsRite"})
            print("+1 permanent evasion and champions right fighting art added.")


class Courage:
    MAX = 9
    EVENTS = (3, 9)

    def __init__(self, survivor, settlement):
        self.survivor = survivor
        self.settlement = settlement

        self.map = {
            3: self.awake,
            9: None
        }
    
    def give(self, amount):
        starting = self.survivor["courage"]
        if self.survivor["courage"] >= self.MAX:
            print(f"{self.survivor['name']} already has maximum courage.")
            return
        
        self.survivor["courage"] += amount
        
        for threshold in sorted(list(self.map.keys())):
            if starting >= threshold:
                continue

            if self.survivor["courage"] >= threshold:
                fnc = self.map[threshold]
                if fnc is None:
                    print(f"MANUAL: later courage events are not implemented. Do them manually for {self.survivor['name']}")
                else:
                    fnc()

    def awake(self):
        roll = kdm.roll()
        print(f"{self.survivor['name']} rolled a {roll} on the Awake courage event.")
        if roll <= 3:
            if self.settlement["departing"]:
                self.survivor["survival"] = self.settlement["survivalLimit"]
                print("Hunt phase detected, gained survival up to the limit.")
            else:
                print("Settlement phase detected, triggering intimacy with +1 bonus to roll result.")
                if self.settlement.can_mate(self.survivor):
                    intimacy = Intimacy.select_mates(initiator=self.survivor, bonus=1)
                    intimacy.intimacy()
                else:
                    intimacy = Intimacy.select_mates(bonus=1)
                    intimacy.intimacy()
        elif roll <= 7:
            self.survivor["attributes"]["STR"] += 1
            fighting_art = self.settlement.add_random_fighting_art(self.survivor)
            print(f"Added +1 permanent strength and the {fighting_art} fighting art.")
            print("MANUAL: You must add the Reincarnated surname.")
        else:
            self.survivor["attributes"]["ACC"] += 1
            if {"id": "unbreakable"} not in self.survivor["fightingArts"]:
                self.survivor["fightingArts"].append({"id": "unbreakable"})
            print("Added +1 permanent accuracy and the Unbreakable fighting art.")


class Augury:
    UNDERSTANDING_BONUS = 3  # Required understanding to get a bonus to augury roll.

    def __init__(self, settlement, survivor, bonus=0):
        self.settlement = settlement
        self.survivor = survivor

        self.bonus = bonus
        self.roll = None

    def augury(self):
        self.roll = kdm.roll()

        if self.survivor["understanding"] >= self.UNDERSTANDING_BONUS:
            self.bonus += 1
        
        result = self.roll + self.bonus
        print(f"{self.survivor['name']} augured, roll {self.roll} + {self.bonus} (understanding: {self.survivor['understanding']})")

        if result <= 3:
            self.settlement.remove_resource()
            if self.survivor["understanding"] < Understanding.MAX:
                Understanding(self.survivor, self.settlement).give(1)
        elif result <= 7:
            if self.survivor["survival"] < self.settlement["survivalLimit"]:
                print(f"{self.survivor['name']} gained 1 survival ({self.survivor['survival']} --> {self.survivor['survival'] + 1})")
                self.survivor["survival"] += 1
        else:
            print(f"{self.survivor['name']} triggered intimacy.")
            return 1  # trigger intimacy
        return 0  # Do not trigger intimacy

    @classmethod
    def select_augurer(cls, settlement, father, mother, bonus=0):
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
            _result.append(-int(_x["understanding"] >= Augury.UNDERSTANDING_BONUS))

            # Do they have their once in a lifetime re-roll?
            _result.append(-int(_x["reroll"]))

            # Do they have less than the maximum understanding (room to grow)?
            _result.append(-int(_x["understanding"] < Understanding.MAX))

            # How close are they to their next understanding event?
            for _epoch in Understanding.EVENTS:
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
        
        candidates = [x for x in settlement.survivors.values() if settlement.can_mate(x)]
        if not candidates:
            print("No living, breedable candidates for augury!")
            return
        
        return cls(sorted(candidates, key=_augur_filter)[0], settlement, bonus=bonus)


class Intimacy:

    def __init__(self, father, mother, settlement, bonus=0):
        self.father = father
        self.mother = mother
        self.settlement = settlement

        self.rolls = None
        self.roll = None
        self.bonus = bonus

    @property
    def roll_total(self):
        roll = self.roll if self.roll else 0
        return roll + self.bonus

    def roll_intimacy(self):
        from kdm.principles import PrincipleRegistry

        life_principle_key = self.settlement["principles"]["newLife"]
        if life_principle_key and life_principle_key in PrincipleRegistry.principles:
            life_principle = PrincipleRegistry.principles[life_principle_key]()
            self.rolls, self.roll = life_principle.roll_intimacy()
        else:
            roll = kdm.roll()
            self.roll = roll
            self.rolls = [roll]

    def intimacy(self, gender="F"):
        if self.settlement["campaign"].lower() == "potstars":
            return self.intamacy_potstars(gender=gender)
        else:
            raise ValueError(f"Campagin: {self.settlement['campaign']} intimacy rules not implemented.")

    def intamacy_potstars(self, gender="F"):
        new_survivors = []
        if not self.roll:
            self.roll()

        survival_fittest = self.settlement["principles"]["newLife"] == "survivalOfTheFittest"
        
        if self.roll_total == 1:
            if survival_fittest:
                re_rolling = False
                if self.mother["reroll"]:
                    self.mother["reroll"] = False
                    re_rolling = True
                    print("Using the self.mother's once in a lifetime re-roll (Survival of the Fittest).")
                elif self.father["reroll"]:
                    self.father["reroll"] = False
                    re_rolling = True
                    print("Using the self.father's once in a lifetime re-roll (Survival of the Fittest).")

                if re_rolling:
                    self.rolls = [max(self.rolls), kdm.roll()]
                    return self.intamacy_potstars(gender=gender)

            print("No re-rolls available or you rolled snake eyes and did not have 2 re-rolls. Both survivors are killed.")
            self.settlement.kill_survivor(self.father["id"], "Childbirth.")
            self.settlement.kill_survivor(self.mother["id"], "Childbirth.")
        elif self.roll_total in {2, 3}:
            print("The child perishes in childbirth and the self.mother's genitals are destroyed.")
            self.mother["severeInjuries"].append("destroyedGenitals")
            # TODO it says to add "scar" to the self.mother, which is a dragon trait, but I don't see where to add that in the file
            print(f"MANUAL: Add Scar Dragon trait to {self.mother['name']}")
        elif self.roll_total in {4, 5}:
            if self.settlement["principles"]["newLife"] == "protectTheYoung":
                print("MANUAL: Give new survivor the Noble Surname dragon trait (Protect the Young)")
                # TODO figure out how to do this automatically.
            print("A strong child is born with +1 strength.")
            new_survivors.append(self.settlement.new_survivor(gender=gender, strength=1))
        elif self.roll_total in {6, 7, 8, 9}:
            dragon_inheritance = []
            if survival_fittest and self.roll_total in {6, 7}:
                dragon_inheritance.append(self.select_dragon_inheritance(self.father, self.mother))
            print("A new survivor with 1 dragon inheritance is born.")
            dragon_inheritance.append(self.select_dragon_inheritance(self.father, self.mother, exclude=dragon_inheritance))
            new_survivors.append(self.settlement.new_survivor(gender=gender, dragon_inheritance=dragon_inheritance))
        else:
            print("Twins are born! Each with 1 dragon inheritance.")
            new_survivors.append(
                self.settlement.new_survivor(
                    gender=gender,
                    dragon_inheritance=self.select_dragon_inheritance(self.father, self.mother)
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
                    gender=gender,
                    dragon_inheritance=self.select_dragon_inheritance(self.father, self.mother),
                    abilities=abilities
                )
            )
        
        return new_survivors
    
    def select_dragon_inheritance(self, exclude=None):
        candidates = set(DragonInheritance.__members__.values())
        if exclude is not None:
            exclude = set(exclude)
            candidates -= exclude

        # If newborns can inherit at least 3 courage, they have a 30% chance of immediately triggering
        #  another intimacy event with +1 to roll results.
        if DragonInheritance.COURAGE in candidates and max(self.father["courage"], self.mother["courage"]) >= 6:
            return DragonInheritance.COURAGE

        if DragonInheritance.UNDERSTANDING in candidates:
            # Understanding will help new children augur better.
            understanding = max((self.father["understanding"], self.mother["understanding"]))
            if understanding >= 2:
                return DragonInheritance.UNDERSTANDING
        
        # TODO give scores to fighting arts and disorders to choose the best option.
        if DragonInheritance.FIGHTING_ART in candidates:
            arts = self.father["fightingArts"] + self.mother["fightingArts"]
            if arts:
                return DragonInheritance.FIGHTING_ART
        if DragonInheritance.COURAGE in candidates:
            courage = max((self.father["courage"], self.mother["courage"]))
            if courage >= 2:
                return DragonInheritance.COURAGE
        
        if DragonInheritance.SURNAME in candidates:
            return DragonInheritance.SURNAME
        
        if DragonInheritance.DISORDERS in candidates:
            return DragonInheritance.DISORDERS
        
        return DragonInheritance.NONE

    @classmethod
    def select_mates(cls, settlement, initiator=None, father=None, mother=None, bonus=0):
        """Return mates in the order (FATHER, MOTHER)"""
        if initiator is not None:
            result = [initiator]
            # Are we looking for a male or a female?
            search_genders = ["M"] if initiator["gender"] == "F" else ["F"]
        else:
            result = []
            search_genders = ["M", "F"]

        def _mate_filter(curated, _x):
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

            # If a survivor has 6 or more courage and their child inherits half
            #  with a dragon inheritance, there's a whopping 30% chance to trigger
            #  another intimacy event with +1 to roll results, from the courage event!
            _result.append(-int(_x["courage"] >= 6))

            # Prioritize survivors will stat penalties - they might die.
            for _attr in ["MOV", "SPD", "ACC", "LCK", "EVA", "STR"]:
                _result.append(_x["attributes"][_attr])
            
            # Breed people with higher injuries and disorders.
            _result.append(-len(_x["severeInjuries"]))
            _result.append(-len(_x["disorders"]))

            # Other attributes.
            _result.append(_x["understanding"])
            _result.append(_x["courage"])

        for search_gender in search_genders:
            candidates = [
                x for x in settlement.survivors.values()
                if x["gender"] == search_gender and settlement.can_mate(x)
            ]
            if len(candidates) <= 0:
                print("No living mates found!")
                return
        
            curated_candidates = father if search_gender == "M" else mother
            curated_candidates = curated_candidates if curated_candidates is not None else []
            result.append(sorted(candidates, key=partial(_mate_filter, curated_candidates))[0])
        result.sort(key=lambda x: x["gender"] == "F")

        print(
            "Selected mates - "
            f"Father: {result[0]['name']} (und: {result[0]['understanding']}, reroll: {result[0]['reroll']}) "
            f"Mother: {result[1]['name']} (und: {result[1]['understanding']}, reroll: {result[1]['reroll']})"
        )
        return cls(father, mother, settlement, bonus=bonus)


class DragonInheritance(Enum):
    """Dragon inheritances for intimacy in people of the stars."""
    NONE = -1  # Do not pick one!
    COURAGE = 0  # Half of one parent's courage rounded down.
    UNDERSTANDING = 1  # Half of one parent's understanding rounded down.
    FIGHTING_ART = 2  # One of a parent's fighting arts.
    DISORDERS = 3  # All of all parent's disorders.
    SURNAME = 4  # One parent's surname.
