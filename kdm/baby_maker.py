import random
from typing import Union
from kdm.events import Augury, Intimacy
from tabulate import tabulate


class BabyMaker:

    def __init__(self, settlement) -> None:
        self.settlement = settlement
    
    def save(self, out_path=None):
        self.settlement.save(out_path)
    
    def make_babies(
            self,
            father: Union[str,list,None]=None,
            mother: Union[str,list,None]=None,
            male_chance=0,
            augury_bonus=0,
            intimacy_bonus=0,
            risky_rerolls=True,
            use_love_juice=True
        ):
        if self.settlement["endeavors"] <= 0:
            print("No endeavor, no babies to make!")
            return []

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
        
        result = []
        if use_love_juice:
            juices = self.settlement["storage"]["resources"]["Basic"]["loveJuice"]
            if juices:
                print(f"Using {juices} love juice resources to trigger intimacy events.")
                for i in range(juices):
                    intimacy = Intimacy.select_mates(self.settlement, father=father, mother=mother, bonus=intimacy_bonus)
                    if intimacy is not None:
                        print("-"*20)
                        if random.uniform(0, 1) >= male_chance:
                            new_gender = "F"
                        else:
                            new_gender = "M"
                        self.settlement["storage"]["resources"]["Basic"]["loveJuice"] -= 1
                        new_survivors = intimacy.intimacy(gender=new_gender, risky_rerolls=risky_rerolls)
                        result.extend(new_survivors)
                    else:
                        print("Could not find a pair of mates! Stopped consuming love juice.")
                        break
        
        print(f"Attempting to make babies with {self.settlement['endeavors']} endeavor.")
        while self.settlement["endeavors"] or self.settlement.temp_endeavor:
            print("-"*20)
            if random.uniform(0, 1) >= male_chance:
                new_gender = "F"
            else:
                new_gender = "M"

            if self.settlement['endeavors']:
                print(f"Endeavor {self.settlement['endeavors']} --> {self.settlement['endeavors'] - 1}")
                self.settlement['endeavors'] -= 1
                augury = Augury.select_augurer(self.settlement, father, mother, augury_bonus)
                if augury.augury():
                    intimacy = Intimacy.select_mates(self.settlement, initiator=augury.survivor, father=father, mother=mother, bonus=intimacy_bonus)
                    if intimacy is not None:
                        new_survivors = intimacy.intimacy(gender=new_gender, risky_rerolls=risky_rerolls)
                        result.extend(new_survivors)
            else:
                candidate_id = list(self.settlement.temp_endeavor.keys())[0]
                candidate = self.settlement.survivors[candidate_id]
                if self.settlement.can_mate(candidate):
                    self.settlement.temp_endeavor[candidate_id] -= 1
                    if self.settlement.temp_endeavor[candidate_id] <= 0:
                        self.settlement.temp_endeavor.pop(candidate_id)
                    if Augury(self.settlement, candidate, augury_bonus).augury():
                        intimacy = Intimacy.select_mates(self.settlement, initiator=candidate, father=father, mother=mother, bonus=intimacy_bonus)
                        if intimacy is not None:
                            new_survivors = intimacy.intimacy(gender=new_gender, risky_rerolls=risky_rerolls)
                            result.extend(new_survivors)
                else:
                    if self.settlement.temp_endeavor[candidate_id] > 0:
                        print(
                            f"MANUAL: {candidate['name']} has {self.settlement.temp_endeavor[candidate_id]} endeavor that only they can use "
                            "remaining, but they cannot mate. You can spend this manually."
                        )
                    self.settlement.temp_endeavor.pop(candidate_id)
        
        print("="*20)
        print(f"COMPLETE: {len(result)} new survivors created!")
        if result:
            headers = ["Name", "Gender", "Reroll", "MOV", "STR", "EVA", "ACC", "LCK", "Cour", "Und", "XP", "Prof", "Surv"]
            table = [[
                x['name'],
                x['gender'],
                self.settlement.has_reroll(x),
                x['attributes']['MOV'],
                x['attributes']['STR'],
                x['attributes']['EVA'],
                x['attributes']['ACC'],
                x['attributes']['LCK'],
                x['courage'],
                x['understanding'],
                x['xp'],
                x.get('weaponProficiency', {}).get('rank', 0),
                x['survival']
            ] for x in result]
            print(tabulate(table, headers=headers))
        return result
    