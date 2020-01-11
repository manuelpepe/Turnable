import random
from typing import Tuple

from turnable.chars import Entity, AIEntity
from turnable.hooks import HookType


class Room:
    TYPES = []

    def __init__(self, pos, game):
        self.pos = pos
        self.game = game
        self.is_done = False
        self.has_ended = False
        self.has_started = False
        self.description = 'An empty room'

    def start(self):
        """ Sets started flag and triggers :py:attr:`HookType.ROOM_START`. """
        if not self.has_started:
            self.has_started = True
            self.game.trigger_hook(HookType.ROOM_START)

    def play_turn(self):
        raise NotImplementedError()

    def end(self):
        """ Sets started flag and triggers :py:attr:`HookType.ROOM_END`. """
        if not self.has_ended:
            self.has_ended = True
            self.game.trigger_hook(HookType.ROOM_END)


class BaseDangerRoom(Room):
    """ A dangerous room. """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enemies = []
        self.create_enemies()

    def play_turn(self):
        self.is_done = all(not e.is_alive() for e in self.enemies)

    def create_enemies(self):
        raise NotImplementedError()


class BaseRewardRoom(Room):
    """ This will do something good for the player. """
    def play_turn(self):
        pass


class EmptyRoom(Room):
    def play_turn(self):
        pass


class FightRoom(BaseDangerRoom):
    """ Room with enemies that require KILLIN'. """
    ENEMY_DIST = None
    DEFAULT_DIST = [
        (AIEntity, 1),
    ]

    @classmethod
    def set_enemy_dist(cls, dist: Tuple[Entity, float]):
        cls.ENEMY_DIST = dist

    def play_turn(self):
        self.game.trigger_hook(HookType.ENEMY_TURN_START)
        dead = []
        for ix, enemy in enumerate(self.enemies):
            if not enemy.is_alive():
                dead.append(ix)
                continue

            enemy.play_turn()

        for ix in dead:
            self.enemies.pop(ix)

        self.game.trigger_hook(HookType.ENEMY_TURN_END)
        super().play_turn()

    def create_enemies(self):
        """ Creates a random amount of enemies in the room. """
        if not self.ENEMY_DIST:
            raise ValueError('You must initialize ENEMY_DIST. Import turnable.rooms.FightRoom and '
                             'call FightRoom.set_enemy_dist(your_dist).')

        amount = random.randint(1, 3)
        for c in range(amount):
            en = self._get_enemy()(pos=self.pos)
            en.game = self.game
            self.enemies.append(en)

    def _get_enemy(self):
        return random.choices(
            [class_ for class_, weight in self.ENEMY_DIST],
            [weight for class_, weight in self.ENEMY_DIST]
        )[0]


class BossRoom(BaseDangerRoom):
    """ Room with a BIG enemy. """

    def create_enemies(self):
        pass


class AdvanceLevelRoom(Room):
    """ Allows player to advance to the next level. """

    def play_turn(self):
        pass

    def start(self):
        self.game.advance_level = True
