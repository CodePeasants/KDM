import os
from kdm.scribe import Scribe, Settlement
from kdm.baby_maker import BabyMaker
from kdm import constants


def test_make_babies():
    test_path = os.path.join(constants.RESOURCE_PATH, "scribe_backup.json")
    scribe = Scribe.load(test_path)
    settlement = Settlement(scribe, "Roshi's Island")

    settlement['endeavors'] = 1000
    maker = BabyMaker(settlement)
    maker.make_babies()
