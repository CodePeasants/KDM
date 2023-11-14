import os

ROOT_PATH = os.path.dirname(__file__)
RESOURCE_PATH = os.path.join(ROOT_PATH, "resources")
TEST_DATA_PATH = os.path.join(RESOURCE_PATH, "scribe_backup.json")

# Constellations for people of the stars are stored as a 4x4 matrix of booleans
#  in survivor data. This is a mapping to access the correct index with a
#  semantic name.
POTSTARS_CONSTELLATION_MAP = {
    "max_understanding": (0, 0),
    "destined_disorder": (0, 1),
    "fated_blow_art": (0, 2),
    "pristine_ability": (0, 3),
    "reincarnated_surname": (1, 0),
    "frozen_start_secret_art": (1, 1),
    "iridescent_hide_ability": (1, 2),
    "champions_rite_art": (1, 3),
    "scar": (2, 0),
    "noble_surname": (2, 1),
    "weapon_mastery": (2, 2),
    "1_accuracy": (2, 3),
    "oracles_eye_ability": (3, 0),
    "unbreakable_art": (3, 1),
    "3_strength": (3, 2),
    "max_courage": (3, 3)
}

WEAPON_PROFICIENCY_RANK = 3  # How much weapon preficiency is required to gain proficiency.
WEAPON_MASTRY_RANK = 8  # How much weapon preficiency is required to gain mastery.