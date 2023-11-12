"""
Usage:
    kdm-make-babies <file> [--settlement=SET --father=FA... --mother=MO... --output-path=OUT --male-chance=MC --augury-bonus=AB --intimacy-bonus=IB]

Options:
    <file>                          Path to the Scribe for KDM backup JSON file containing game data.
    --settlement=SET, -s=SET        Optionally specify the name of the settlement [default: Roshi's Island]
    --father=FA, -f=FA              Specify a list of Father candidates.
    --mother=MO, -m=MO              Specify a list of mother candidates.
    --output-path=OUT, -o=OUT       Specify the output data file path to load back into Scribe.
    --male-chance=MC, -c=MC         Chance that new babies will be male (number from 0-1 ) [default: 0.1]
    --augury-bonus=AB, -a=AB        Bonus to augury rolls. [default: 0]
    --intimacy-bonus=IB, -i=IB      Bonus to intimacy rolls. [default: 0]
"""
from docopt import docopt
from kdm.scribe import Scribe, Settlement
from kdm.baby_maker import BabyMaker


def main(**kwargs):
    scribe = Scribe.load(kwargs["<file>"])
    settlement = Settlement(scribe, kwargs["--settlement"])
    maker = BabyMaker(settlement)
    
    maker.make_babies(
        father=kwargs["father"],
        mother=kwargs["mother"],
        male_chance=float(kwargs["--male-chance"]),
        augury_bonus=int(kwargs["--augury-bonus"]),
        intimacy_bonus=int(kwargs["--intimacy-bonus"])
    )

    maker.save(kwargs["--output-path"])


if __name__ == "__main__":
    main(**docopt(__doc__))
