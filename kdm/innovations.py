"""Apply innovation bonuses to newborn survivors like so:

for innovation_key in settlement["innovations"]:
    innovation = InnovationRegistry[innovation_key]
    innovation.newborn(survivor, settlement)
"""
import copy
from kdm.events import Age, Courage, Understanding


class InnovationRegistry(type):
    innovations = {}

    def __new__(cls, name, bases, dct):
        klass = super().__new__(cls, name, bases, dct)
        cls.innovations[klass.KEY] = klass
        return klass

class Innovation(metaclass=InnovationRegistry):
    KEY = None

    def newborn(self, survivor, settlement):
        pass


class Bloodline(Innovation):
    KEY = "bloodline"

    def newborn(self, survivor, settlement):
        super().newborn(survivor, settlement)
        abilities = []
        for parent in survivor["parents"].values():
            abilities.extend([x["id"] for x in parent["abilities"]])
        
        for ability in ("iridescentHide", "pristine", "oraclesEye"):
            if ability in abilities:
                print(f"Bloodline - Inherited {ability} ability.")
                break
        
        proficiencies = [x.get("weaponProfieiency", {}) for x in survivor["parents"].values()]
        proficiencies.sort(key=lambda x: -x.get("rank", 0))
        if proficiencies[0]:
            if survivor.get("weaponProficiency", {}).get("rank", 0) < proficiencies[0]["rank"]:
                survivor["weaponProficiency"] = copy.deepcopy(proficiencies[0])
                print (f"Bloodline - inherited weapon proficiency {proficiencies[0]['rank']} with {proficiencies[0]['weapon']}")


class ClanOfDeath(Innovation):
    KEY = "clanOfDeath"

    def newborn(self, survivor, settlement):
        super().newborn(survivor, settlement)
        print("Clan of Death adding +1 strength, accuracy and evasion.")
        for stat in ("STR", "ACC", "EVA"):
            survivor["attributes"][stat] += 1


class Empire(Innovation):
    KEY = "empire"

    def newborn(self, survivor, settlement):
        super().newborn(survivor, settlement)
        survivor["attributes"]["STR"] += 1
        abilitites = {x["id"] for x in survivor["abilitites"]}
        if "pristine" not in abilitites:
            survivor["abilities"].append({"id": "pristine"})
        for stat in ("STR", "ACC", "EVA"):
            survivor["attributes"][stat] += 1
        print("Empire - gained 1 strength and the Pristine ability.")


class Family(Innovation):
    KEY = "family"

    def newborn(self, survivor, settlement):
        super().newborn(survivor, settlement)
        father = survivor["parents"]["father"]
        mother = survivor["parents"]["mother"]
        print(f"MANUAL: Parents ({father['name'], mother['name']} may give themselves a surname if they do not have one.")
        print(f"MANUAL: Their child {survivor['name']} inherits one of their surnames.")
        proficiencies = sorted([father.get("weaponProficiency", {}), mother.get("weaponProficiency", {})], key=lambda x: -x.get("rank", 0))
        if proficiencies[0]:
            survivor["weaponProficiency"] = copy.deepcopy(proficiencies[0])
            print(f"{survivor['name']} inherited {survivor['weaponProficiency']['rank']} ranks of {survivor['weaponProficiency']['weapon']} weapon proficiency.")


class RadiatingOrb(Innovation):
    KEY = "radiatingOrb"

    def newborn(self, survivor, settlement):
        super().newborn(survivor, settlement)
        if survivor["survival"] < settlement["survivalLimit"]:
            survivor["survival"] += 1
        print("Radiating Orb - gained 1 survival.")

class Saga(Innovation):
    KEY = "saga"

    def newborn(self, survivor, settlement):
        super().newborn(survivor, settlement)
        print("Saga adding 2 courage, 2 understanding and 2 XP.")
        Courage(survivor, settlement).give(2)
        Understanding(survivor, settlement).give(2)
        Age(survivor, settlement).give(2)
