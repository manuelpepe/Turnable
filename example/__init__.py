import logging
import sys
import time
from random import choice

from turnable import Game, HookType
from turnable.chars import Character
from turnable.streams import TextInputStream
from turnable.map import Map, Position

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


class MyCharacter(Character):
    """ This character screams when moving! """
    SCREAMS = ['OHHH!', 'AHHH!', 'OMG!']

    def move(self, newpos: Position, delta: bool = True) -> Position:
        moved = super().move(newpos, delta)
        if moved:
            self._logger.info(choice(self.SCREAMS))


def my_welcome_hook(game):
    """ This is a hook that launchs a countdown at the start of the game. """
    game.logger.info('The game is going to start in...')
    for t in range(5, 0, -1):
        game.logger.info(f'{t}...')
        time.sleep(0.5)
    game.logger.info('GO!')
    time.sleep(0.5)


def main():
    player = MyCharacter('Player')
    map_ = Map()
    instream = TextInputStream()

    g = Game('My Game', [player], map_, instream, None)
    g.add_hook(HookType.GAME_START, my_welcome_hook)
    g.start()


if __name__ == '__main__':
    main()