from turnable.hooks import HookType


class Room:
    TYPES = []

    def __init__(self, pos, game):
        self.pos = pos
        self.game = game
        self.is_done = False
        self.description = 'An empty room'

    def effect(self):
        pass

    def get_possible_actions(self):
        pass

    def start(self):
        self.game.trigger_hook(HookType.ROOM_START)

    def end(self):
        self.game.trigger_hook(HookType.ROOM_END)


class BaseRewardRoom(Room):
    """ This will do something good for the player. """


class BaseDangerRoom(Room):
    """ A dangerous room. """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enemies = []


class FightRoom(BaseDangerRoom):
    """ Room with enemies that require KILLIN'. """


class BossRoom(BaseDangerRoom):
    """ Room with a BIG enemy. """


class AdvanceLevelRoom(Room):
    """ Allows player to advance to the next level. """
    def start(self):
        self.game.advance_level = True
