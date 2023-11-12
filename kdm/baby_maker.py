import random
from typing import Union
from kdm.events import Augury, Intimacy


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
            intimacy_bonus=0
        ):
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
        result = []
        while self.settlement["endeavors"] or self.settlement.temp_endeavor:
            print("-"*20)
            if random.uniform(0, 1) >= male_chance:
                new_gender = "F"
            else:
                new_gender = "M"

            if self.settlement['endeavors']:
                print(f"Endeavor {self.settlement['endeavors']} --> {self.settlement['endeavors']}")
                self.settlement['endeavors'] -= 1
                augury = Augury.select_augurer(self.settlement, father, mother, augury_bonus)
                if augury.augury():
                    intimacy = Intimacy.select_mates(self.settlement, initiator=augury.survivor, father=father, mother=mother, bonus=intimacy_bonus)
                    new_survivors = intimacy.intimacy(gender=new_gender)
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
                        new_survivors = intimacy.intimacy(gender=new_gender)
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
            for survivor in result:
                print(survivor["name"], survivor["gender"], f"Re-roll: {survivor['reroll']}")
    
    

    
    