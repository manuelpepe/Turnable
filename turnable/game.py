"""
The Game module contains the :py:class:`Game`, which is the core of any Turnable application.


"""
import uuid
import logging
import hashlib

from turnable.hooks import HookType
from turnable.map import Position, Map
from turnable.rooms import BaseDangerRoom, FightRoom
from turnable.chars import Entity, PlayableEntity
from turnable.state import States
from turnable.streams import BaseInputStream, BaseOutputStream

from typing import Any, Callable, Optional


class InvalidPlayerException(Exception):
    pass


def endgame_player_dead(game):
    return not game.player.is_alive()


class Game:
    """
    Main game object. It handles game loops and basic logic.
    It's also in charge of sending data to the outputstream.

    At the moment Turnable only supports single user play. You must
    pass an instance of a :py:class:`PlayableEntity` as the *player* param.

    *map_* receives an instance of :py:class:turnable.map.Map:

    *name* is not used meaningfully yet.
    """
    logger = logging.getLogger('turnable.Game')

    def __init__(self,
                 name: str,
                 player: PlayableEntity,
                 map_: Map,
                 inputstream: BaseInputStream,
                 outputstream: Optional[BaseOutputStream],
                 endgame_condition: Callable = endgame_player_dead):
        self.name = name
        self.player = player
        self.map = map_
        self.map.game = self
        self.inputstream = inputstream
        self.outputstream = outputstream
        self.endgame_condition = endgame_condition

        self.hooks = {}
        self.is_done = False
        self.state = None
        self.room = None
        self.advance_level = False
        self.turn = 0

    @property
    def player(self) -> PlayableEntity:
        return self.__player

    @player.setter
    def player(self, player: PlayableEntity):
        if not isinstance(player, PlayableEntity):
            raise InvalidPlayerException
        player.game = self
        self.__player = player

    @property
    def map(self):
        return self.__map

    @map.setter
    def map(self, map_: Map):
        self.__map = map_
        self.__map.game = self

    def add_hook(self, type_: HookType, callback: Callable[['Game'], Any]):
        """ Adds a hook callback. The callback must accept a single :py:class:`Game` argument. """
        typelist = self.hooks.setdefault(type_, {})
        id = str(uuid.uuid4())
        while id in typelist.keys():
            id = str(uuid.uuid4())
        self.hooks[type_][id] = callback

    def remove_hook(self, type_: HookType, id: str):
        if type_ in self.hooks.keys():
            if self.hooks[type_].get(id):
                self.hooks[type_][id] = None
            else:
                raise RuntimeError(f'No such hook {id}')

    def trigger_hook(self, type_: HookType):
        """ Executes hook passing a refence to the :py:class:`Game` object. """
        hooks = self.hooks.get(type_) or {}
        for id, hook in hooks.items():
            if hook is not None:
                hook(self, type_, id)

    def start(self):
        """ Start game. """
        self.state = States.START
        self.is_done = False
        self.turn = 0
        self.map.reset()
        self.main_loop()

    def main_loop(self):
        """
        Handles the main loop of the game.
        While the game is not done it will keep advancing levels and calling :py:meth:`~level_loop`.
        """
        self.trigger_hook(HookType.GAME_START)
        while not self.is_done:
            self.player.move(Position(0, 0), False)
            self.level_loop()
            self.map.next_level()
        self.trigger_hook(HookType.GAME_END)

    def level_loop(self):
        """
        Handles the level loop.
        While the player is alive and the level is not finished it will keep calling :py:meth:`play_turn`.
        """
        # self.advance_level will be set to True on AdvanceLevelRoom.start()
        self.trigger_hook(HookType.LEVEL_START)
        self.advance_level = False
        while not self.advance_level:
            self.room = self.map.get_player_room()
            self.notify_state()
            self.play_turns()

    def update_state(self):
        """ Automatically updates game state. """
        if isinstance(self.room, FightRoom) and not self.room.is_done:
            self.state = States.IN_FIGHT
        elif isinstance(self.room, FightRoom) and self.room.is_done:
            self.state = States.IN_FIGHT_ROOM_DONE

    def play_turns(self):
        """
        Handles game turn.
        Player moves first, then enemies (if any). Game state gets updated accordingly.
        """
        self.update_state()
        self.trigger_hook(HookType.TURN_ROUND_START)
        if not self.room.has_started:
            self.room.start()

        self.logger.debug(f'Player at {self.room.__class__.__name__}.')
        self.player.play_turn()
        self.room.play_turn()

        self.trigger_hook(HookType.TURN_ROUND_END)
        if self.room.is_done:
            self.room.end()
        endgame = self.check_endgame_conditions()
        if endgame:
            self.endgame(endgame)
        self.update_state()
        self.notify_state()

    def notify_state(self):
        self.outputstream.send(self)

    def check_endgame_conditions(self):
        return self.endgame_condition(self)

    def endgame(self, state):
        """ Ends game. """
        self.trigger_hook(HookType.GAME_END)
        self.is_done = True
        self.state = state
