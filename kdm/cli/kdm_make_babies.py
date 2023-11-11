"""
Usage:
    kdm-make-babies <file> [--settlement=SET --endeavor=END --father=FA... --mother=MO... --output-path=OUT]

Options:
    <file>                          Path to the Scribe for KDM backup JSON file containing game data.
    --settlement=SET, -s=SET        Optionally specify the name of the settlement [default: Roshi's Island]
    --endeavor=END, -e=END          Optionally specify an amount of endeavor to use.
    --father=FA, -f=FA              Specify a list of Father candidates.
    --mother=MO, -m=MO              Specify a list of mother candidates.
    --output-path=OUT, -o=OUT       Specify the output data file path to load back into Scribe.
"""
from docopt import docopt
from kdm.scribe import Scribe, Settlement
from kdm.baby_maker import BabyMaker


def main(**kwargs):
    scribe = Scribe.load(kwargs["<file>"])
    settlement = Settlement(scribe, kwargs["--settlement"])
    maker = BabyMaker(settlement)

    endeavor = kwargs["--endeavor"]
    if endeavor is not None:
        endeavor = int(endeavor)
    
    maker.make_babies(endeavor=endeavor, father=kwargs["father"], mother=kwargs["mother"])
    maker.save(kwargs["--output-path"])


if __name__ == "__main__":
    main(**docopt(__doc__))
