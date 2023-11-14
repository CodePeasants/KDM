"""
Usage:
    kdm-stats <mode> [--iterations=IT --endeavor=EN]

Options:
    <mode>                          What to evaluate (e.g. safe_reroll, risky_reroll)
    --iterations=IT, -i=IT          How many iterations to check with [default: 1000]
    --endeavor=EN, -e=EN            How much endeavor to use for each iteration [default: 10]
"""
from docopt import docopt
from kdm import stats


def main(**kwargs):
    mode = kwargs["<mode>"].lower()
    iters = int(kwargs["--iterations"])
    endeavor = int(kwargs["--endeavor"])

    if mode in {"safe", "safe_reroll", "safe_rerolls"}:
        stats.safe_reroll(iters=iters, endeavor=endeavor)
    elif mode in {"risk", "risky", "risky_reroll", "risky_rerolls"}:
        stats.risky_reroll(iters=iters, endeavor=endeavor)
    else:
        raise ValueError(f"{mode} mode not recognized!")


if __name__ == "__main__":
    main(**docopt(__doc__))
