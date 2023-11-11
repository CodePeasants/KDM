"""
Usage:
    kdm-cache-names [--number=N --country=C...]

Options:
    --number=N, -n=N                 Specify how many names from each gender and country you want to cache [default: 200]
    --country=C, -c=C               Specify the 2-digit country names to use.
"""
from docopt import docopt
from kdm import names


def main(**kwargs):
    names.cache_names(count=int(kwargs["--number"]), countries=kwargs["--country"] or None)


if __name__ == "__main__":
    main(**docopt(__doc__))
