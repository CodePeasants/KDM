"""Just some utility scripts to help evaluate the likelyhoods of some outcomes via brute force."""
import sys
import os
from contextlib import contextmanager
from copy import deepcopy
from tqdm import tqdm
from kdm.scribe import Settlement
from kdm.baby_maker import BabyMaker


SETTLEMENT = settlement = Settlement.load()


def safe_reroll(iters=1000, endeavor=10):
    result = []
    for _ in tqdm(range(iters)):
        with NoPrint():
            settlement = deepcopy(SETTLEMENT)
            settlement["endeavors"] = endeavor
            maker = BabyMaker(settlement)
            new_survivors = maker.make_babies(risky_rerolls=False)
            result.append(len(new_survivors))
    
    avg = sum(result) / len(result)
    print(f"Safe re-roll chances with {endeavor} endeavor and {iters} iterations: {avg}")


def risky_reroll(iters=1000, endeavor=10):
    result = []
    for _ in tqdm(range(iters)):
        with NoPrint():
            settlement = deepcopy(SETTLEMENT)
            settlement["endeavors"] = endeavor
            maker = BabyMaker(settlement)
            new_survivors = maker.make_babies(risky_rerolls=True)
            result.append(len(new_survivors))
    
    avg = sum(result) / len(result)
    print(f"Risky re-roll chances with {endeavor} endeavor and {iters} iterations: {avg}")


@contextmanager
def NoPrint():
    original_stdout = sys.stdout
    sys.stdout=open(os.devnull, "w")
    yield
    sys.stdout = original_stdout