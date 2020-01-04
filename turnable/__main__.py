#!/usr/bin/python3
"""
Runs the most barebones version of the game, which is the logger on debug mode outputting to stdout.
"""
import os
import sys
import logging

sys.path.insert(0, os.path.abspath('.'))

from turnable.chars import Character
from turnable.map import Map
from turnable.game import Game
from turnable.streams import TextInputStream, TextOutputStream


def main():
    instream = TextInputStream()
    ostream = TextOutputStream()
    player = Character('player_name')
    map_ = Map()
    game = Game('Turnable', [player], map_, instream, ostream   )
    game.start()


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    main()
