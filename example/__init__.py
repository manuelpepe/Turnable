import logging
import os
import sys

sys.path.insert(0, os.path.abspath('.'))

from turnable import Game
from turnable.chars import Character
from turnable.inputstream import TextInputStream
from turnable.map import Map, Position

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


class MyCharacter(Character):
    def move(self, newpos: Position, delta: bool = True) -> Position:
        self._logger.info('This is happening BEFORE MOVING!')
        super().move(newpos, delta)
        self._logger.info('This is happening AFTER MOVING!')
        if delta:
            self._logger.info('This only happens on delta moves (not level start).')


def main():
    player = MyCharacter('Player')
    map_ = Map()
    instream = TextInputStream()
    g = Game('My Game', player, map_, instream)
    g.start()


if __name__ == '__main__':
    main()