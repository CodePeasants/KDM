import json
import os
import tempfile
import random
from datetime import datetime
from enum import Enum
import copy
import uuid

from kdm import names


with open(os.path.abspath("../resources/survivor.json"), "r", encoding="utf-8") as fh:
    NEW_SURVIVOR_TEMPLATE = json.loads(
        fh.read().replace("’", "'")
    )


class Scribe:

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
            fh.wrte(out_data)
        print(f"Saved scribe backup to: {out_path}")


class Settlement:
    """
    scribe = Scribe.load("file-path.json")
    settlement = Settlement(scribe, "Roshi's Island")
    """

    def __init__(self, parent: Scribe, name: str) -> None:
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

        if self.data["principles"]["death"] == "graves":
            end = 2 if self.data["departing"] else 1  # 2 if in hunt or encounter, 1 if in settlement.
            self.data["endeavors"] += end
            print(f"Principle Death: Graves - Added {end} endeavor.")
        elif self.data["principles"]["death"] == "cannibalize":
            print("Principle Death: Cannibalize - Adding 2 random basic resources.")
            self.add_random_resource()
            self.add_random_resource()
        else:
            print(
                "Principle Death event triggered! You need to pick one and manually apply the "
                "benefits of any subsequent deaths!"
            )

    def add_random_resource(self, resource_type="Basic"):
        # TODO - get the actual counts of each card type in the physical deck, so I can weight
        #  the probabilities of drawing each item accordingly. Also refactor this to support
        #  adding multiple resources, so I can modify the weight of each item in the pool
        #  for each subsequent selection, based on removing one of the previously selected item.
        choices = list(self.data["storage"]["resources"][resource_type].keys())
        selected = random.choice(choices)
        self.data["storage"]["resources"][resource_type][selected] += 1
        print("Added 1 {} to settlement storage".format(selected))
    
    def new_survivor(self, father=None, mother=None, name=None, gender="F", strength=0, dragon_inheritance=None) -> dict:
        new_survivor = copy.deepcopy(NEW_SURVIVOR_TEMPLATE)
        new_survivor["id"] = str(uuid.uuid4())
        new_survivor["key"] = new_survivor["id"]
        
        if name is None:
            name = names.get_name(gender=gender, exclude=[x["name"] for x in self.survivors.values()])
        new_survivor["name"] = name

        new_survivor["gender"] = gender
        new_survivor["settlement"] = self.id
        new_survivor["parents"] = {
            "father": father["id"] if father else None,
            "mother": mother["id"] if mother else None
        }

        # TODO - Automatically gets everything from settlement innovations.
        # TODO - Apply dragon inheritances.
        new_survivor["attributes"] = {
            "MOV": 5,
            "STR": strength,
            "EVA": 0,
            "ACC": 0,
            "LCK": 0,
            "SPD": 0
        }
        # new_survivor["courage"] =
        # new_survivor["understanding"] =
        # new_survivor["fightingArts"] = [{"id": "oratorOfDeath"}, ...]
        # new_survivor["disorders"] = [{"id": "verminObsession"}, ...]
        # new_survivor["abilities"] = [{"id": "prepared"}, ...]
        # Dragon traits / constellations?

        self.parent["survivors"][self.id][new_survivor["id"]] = new_survivor
        self.data["population"] += 1
        return new_survivor

    def understanding_event(self, survivor):
        # TODO
        pass


class DragonInheritance(Enum):
    """Dragon inheritances for intimacy in people of the stars."""
    NONE = -1  # Do not pick one!
    COURAGE = 0  # Half of one parent's courage rounded down.
    UNDERSTANDING = 1  # Half of one parent's understanding rounded down.
    FIGHTING_ART = 2  # One of a parent's fighting arts.
    DISORDERS = 3  # All of all parent's disorders.
    SURNAME = 4  # One parent's surname.
