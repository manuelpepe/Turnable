#!/usr/bin/python3
import os
import sys
import logging

sys.path.insert(0, os.path.abspath('.'))

from turnable.chars import Character
from turnable.map import Map
from turnable.game import Game
from turnable.streams import TextInputStream, TextOutputStream

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


def main():
    instream = TextInputStream()
    ostream = TextOutputStream()
    player = Character('player_name')
    map_ = Map()
    game = Game('Turnable', [player], map_, instream, ostream   )
    game.start()


if __name__ == '__main__':
    main()
