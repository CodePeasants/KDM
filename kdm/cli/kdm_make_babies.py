"""
Usage:
    kdm-make-babies [<file> --settlement=SET --father=FA... --mother=MO... --output-path=OUT --male-chance=MC --augury-bonus=AB --intimacy-bonus=IB --safe-rerolls --use-juice]

Options:
    <file>                          Path to the Scribe for KDM backup JSON file containing game data.
    --settlement=SET, -s=SET        Optionally specify the name of the settlement [default: Roshi's Island]
    --father=FA, -f=FA              Specify a list of Father candidates.
    --mother=MO, -m=MO              Specify a list of mother candidates.
    --output-path=OUT, -o=OUT       Specify the output data file path to load back into Scribe.
    --male-chance=MC, -c=MC         Chance that new babies will be male (number from 0-1 ) [default: 0.1]
    --augury-bonus=AB, -a=AB        Bonus to augury rolls. [default: 0]
    --intimacy-bonus=IB, -i=IB      Bonus to intimacy rolls. [default: 0]
    --safe-rerolls, -r              Don't use once in a lifetime re-roll on 2 or 3 for intamcy, only 1 (20% fewer children).
    --use-juice, -u                 Use up love juice resources to trigger intimacy.
"""
from docopt import docopt
import os
from kdm.scribe import Scribe, Settlement
from kdm.baby_maker import BabyMaker
from kdm import constants


def main(**kwargs):
    if not (data_path := kwargs["<file>"]):
        data_path = os.path.join(constants.RESOURCE_PATH, "scribe_backup.json")
        print(f"No Scribe data file provided, using test file: {data_path}")

    scribe = Scribe.load(data_path)
    settlement = Settlement(scribe, kwargs["--settlement"])
    maker = BabyMaker(settlement)
    
    maker.make_babies(
        father=kwargs["--father"],
        mother=kwargs["--mother"],
        male_chance=float(kwargs["--male-chance"]),
        augury_bonus=int(kwargs["--augury-bonus"]),
        intimacy_bonus=int(kwargs["--intimacy-bonus"]),
        risky_rerolls=not kwargs["--safe-rerolls"],
        use_love_juice=kwargs["--use-juice"]
    )
    maker.save(kwargs["--output-path"])


if __name__ == "__main__":
    main(**docopt(__doc__))
