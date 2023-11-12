import json
import os
import tempfile
import random
import math
from datetime import datetime
from enum import Enum
import copy
import uuid

from kdm import names, constants
from kdm.innovations import InnovationRegistry
from kdm.principles import PrincipleRegistry
from kdm.events import Courage, Understanding, DragonInheritance


with open(os.path.join(constants.RESOURCE_PATH, "survivor.json"), "r", encoding="utf-8") as fh:
    NEW_SURVIVOR_TEMPLATE = json.loads(
        fh.read().replace("’", "'")
    )


class DictWrapper:
    def __getitem__(self, key):
        return self.data[key]
    
    def __setitem__(self, key, value):
        self.data[key] = value
    
    def __delitem__(self, key):
        del self.data[key]
    
    def __contains__(self, key):
        return key in self.data
    
    def __len__(self):
        return len(self.data)


class Scribe(DictWrapper):

    def __init__(self, data: dict):
        self.data = data

    @classmethod
    def load(cls, path: str):
        with open(path, "r", encoding="utf-8") as fh:
            string_data = fh.read()
        
        # Replace "right single quotation marks" with single quotes for ease of use.
        string_data = string_data.replace("’", "'")
        return cls(json.loads(string_data))

    def save(self, out_path=None):
        if out_path is None:
            out_path = tempfile.mktemp()
        
        out_dir = os.path.dirname(out_path)
        os.makedirs(out_dir, exist_ok=True)

        # Encode to JSON string and undo the single quote replacements we're doing on read.
        out_data = json.dumps(self.data)
        out_data.replace("'","’")
        with open(out_path, "w") as fh:
            fh.write(out_data)
        print(f"Saved scribe backup to: {out_path}")


class Settlement(DictWrapper):
    """
    scribe = Scribe.load("file-path.json")
    settlement = Settlement(scribe, "Roshi's Island")
    """
    fighting_arts = None

    def __init__(self, parent: Scribe, name: str) -> None:
        self.temp_endeavor = {}
        self.parent = parent
        self.name = name
        candidates = []
        for data in parent["settlements"].values():
            if data["name"].lower() == name.lower():
                candidates.append(data)
        
        if not candidates:
            raise ValueError(f"Settlement named: {name} not found. ({[x['name'] for x in parent['settlements']]})")
        
        if len(candidates) > 1:
            candidates.sort(reverse=True, key=lambda x: x["ly"])
            print(f"{len(candidates)} settlements found with the same name. Selecting the one at the highest lantern year ({candidates[0]['id']}).")
        self.data = candidates[0]
        
        self.id = data["id"]
        self.survivors = parent["survivors"][self.id]

        # Load my list of fighting arts.
        if self.fighting_arts is None:
            arts_path = os.path.join(constants.RESOURCE_PATH, "fighting_arts.json")
            with open(arts_path, "r", encoding="utf-8") as fh:
                self.__class__.fighting_arts = json.load(fh)
    
    @property
    def expansions(self):
        """List of expansions this settlement is using."""
        return list(k for k, v in self.data["expansions"].items() if v == "all")

    @staticmethod
    def can_mate(survivor):
        return survivor["dead"] is False and "destroyedGenitals" not in survivor["severeInjuries"]

    def get_parents(self, survivor):
        result = []
        father_id = survivor["parents"].get("father")
        if father_id:
            result.append(self.survivors[father_id])
        else:
            result.append(None)

        mother_id = survivor["parents"].get("mother")
        if mother_id:
            result.append(self.survivors[mother_id])
        else:
            result.append(None)
        return tuple(result)

    def save(self, out_path=None):
        self.parent.save(out_path)
    
    def kill_survivor(self, id, cause=""):
        """Kill of a survivor.
        
        Args:
            id: ID of the survivor to kill.
            cause: Cause of death.
        """
        self.survivors[id]["dead"] = True
        self.survivors[id]["causeOfDeath"] = cause
        self.survivors[id]["timeOfDeath"] = int(datetime.utcnow().timestamp() * 1000)
        self.data["population"] -= 1
        self.data["deathCount"] += 1

        # Apply principle effects.
        for principle_key in self["principles"].values():
            if not principle_key:
                continue
            principle = PrincipleRegistry.principles.get(principle_key)
            if principle:
                principle().death(self)
            else:
                print(f"Principle: {principle_key} not implemented.")

    def add_random_resource(self, resource_type="Basic"):
        # TODO - get the actual counts of each card type in the physical deck, so I can weight
        #  the probabilities of drawing each item accordingly. Also refactor this to support
        #  adding multiple resources, so I can modify the weight of each item in the pool
        #  for each subsequent selection, based on removing one of the previously selected item.
        choices = list(self.data["storage"]["resources"][resource_type].keys())
        selected = random.choice(choices)
        self.data["storage"]["resources"][resource_type][selected] += 1
        print("Added 1 {} to settlement storage".format(selected))
    
    def remove_resource(self):
        total_resources = 0
        for resource_type in self.data["storage"]["resources"].values():
            for resource, count in resource_type.items():
                total_resources += count
        print(f"MANUAL: Remove 1 resource from settlement storage.")

    def add_random_fighting_art(self, survivor):
        expansions = self.expansions
        candidates = []
        for expansion, arts in self.fighting_arts["fighting_arts"].items():
            if expansion in expansions:
                candidates.extend(arts)
        
        existing = {x["id"] for x in survivor["fightingArts"]}
        candidates = set(candidates) - existing
        choice = random.choice(list(candidates))
        survivor["fightingArts"].append({"id": choice})
        print(f"Added random fighting art: {choice} to {survivor['name']}.")
        return choice

    def new_survivor(self, father=None, mother=None, name=None, gender="F", strength=0, dragon_inheritance=None, abilities=None) -> dict:
        if dragon_inheritance is None:
            dragon_inheritance = []
        elif not isinstance(dragon_inheritance, (list, tuple)):
            dragon_inheritance = [dragon_inheritance]

        new_survivor = copy.deepcopy(NEW_SURVIVOR_TEMPLATE)
        new_survivor["id"] = str(uuid.uuid4())
        new_survivor["key"] = new_survivor["id"]
        
        if name is None:
            name = names.get_name(gender=gender, exclude=[x["name"] for x in self.survivors.values()])
        print(f"New survivor's name is: {name}")
        new_survivor["name"] = name

        new_survivor["gender"] = gender
        new_survivor["settlement"] = self.id
        new_survivor["parents"] = {
            "father": father["id"] if father else None,
            "mother": mother["id"] if mother else None
        }
        new_survivor["attributes"] = {
            "MOV": 5,
            "STR": strength,
            "EVA": 0,
            "ACC": 0,
            "LCK": 0,
            "SPD": 0
        }

        # Apply bonuses from principles.
        for principle_key in self.data["principles"].values():
            if not principle_key:
                continue
            principle = PrincipleRegistry.principles.get(principle_key)
            if principle:
                principle().newborn(new_survivor, self)

        # Apply bonuses from innovations.
        for innovation_key in self.data["innovations"]:
            innovation = InnovationRegistry.innovations.get(innovation_key)
            if innovation:
                innovation().newborn(new_survivor, self)
        
        # Add abilitites passed in.
        abilities = abilities if abilities else []
        owned_abilitites = {x["id"] for x in new_survivor["abilities"]}
        for ability in abilities:
            if ability not in owned_abilitites:
                new_survivor["abilities"].append({"id": ability})

        # Apply dragon inheritances.
        for inheritance in dragon_inheritance:
            if inheritance == DragonInheritance.NONE:
                continue
            elif inheritance == DragonInheritance.COURAGE:
                courage = int(math.floor(float(max(father["courage"], mother["courage"])) / 2.0))
                Courage(new_survivor, self).give(courage)
                print(f"Dragon Inheritance - Courage: +{courage}")
            elif inheritance == DragonInheritance.UNDERSTANDING:
                understanding = int(math.floor(float(max(father["understanding"], mother["understanding"])) / 2.0))
                Understanding(new_survivor, self).give(understanding)
                print(f"Dragon Inheritance - Understanding: +{understanding}")
            elif inheritance == DragonInheritance.FIGHTING_ART:
                print("Dragon Inheritance - Fighting Art")
                owned = {x["id"] for x in new_survivor["fightingArts"]}
                selected = False
                for parent in (father, mother):
                    if selected:
                        break
                    for fighting_art in parent["fightingArts"]:
                        if fighting_art["id"] not in owned:
                            new_survivor["fightingArts"].append(fighting_art)
                            selected = True
                            break
                if not selected:
                    print(
                        f"MANUAL: {new_survivor['name']} was supposed to get a fighting art as a Dragon Inheritance from their "
                        f"parents ({father['name']}, {mother['name']}), but a new unique are was not able to be selected!"
                    )
            elif inheritance == DragonInheritance.DISORDERS:
                unique_disorders = {x["id"] for x in father["disorders"] + mother["disorders"] + new_survivor["disorders"]}
                new_survivor["disorders"] = [{"id": x} for x in unique_disorders]
                print(f"Dragon Inheritance - Disorders: {unique_disorders}")
            elif inheritance == DragonInheritance.SURNAME:
                print(f"MANUAL: Dragon Inheritance - Surname: {new_survivor['name']} should inherit the surname of a parent ({father['name']}, {mother['name']})")
        # new_survivor["abilities"] = [{"id": "prepared"}, ...]
        # Dragon traits / constellations?

        self.parent["survivors"][self.id][new_survivor["id"]] = new_survivor
        self.data["population"] += 1
        return new_survivor



