import random


def get_dummy():
    r = random.Random()
    return dict(dummy1=r.random(), dummy2=r.random())
