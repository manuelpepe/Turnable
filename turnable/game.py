"""
The Game module contains the :py:class:`Game`, which is the core of any Turnable application.


"""
import logging

import turnable.rooms as rooms

from turnable.hooks import HookType
from turnable.map import Position, Map
from turnable.chars import Character
from turnable.state import States
from turnable.streams import BaseInputStream, BaseOutputStream, CommandRequest

from typing import List, Any, Callable, Optional


class InvalidPlayerException(Exception):
    pass


def endgame_all_dead(game):
    return all(not p.is_alive() for p in game.players)


def endgame_one_dead(game):
    return any(not p.is_alive() for p in game.players)


class Game:
    """
    Main game object. It handles game loops and basic logic.
    It's also in charge of sending data to the outputstream.
    """
    logger = logging.getLogger('turnable.Game')

    def __init__(self,
                 name: str,
                 players: List[Character],
                 map_: Map,
                 inputstream: BaseInputStream,
                 outputstream: Optional[BaseOutputStream],
                 endgame_condition: Callable = endgame_all_dead):
        self.name = name
        self.players = players
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

    @property
    def players(self):
        return self.__players

    @players.setter
    def players(self, players: List[Character]):
        for player in players:
            if not isinstance(player, Character):
                raise InvalidPlayerException
            player.game = self
        self.__players = players

    @property
    def map(self):
        return self.__map

    @map.setter
    def map(self, map_: Map):
        self.__map = map_
        self.__map.game = self

    def add_hook(self, type_: HookType, callback: Callable[['Game'], Any]):
        """ Adds a hook callback. The callback must accept a single :py:class:`Game` argument. """
        if not self.hooks.get(type_):
            self.hooks[type_] = []
        self.hooks[type_].append(callback)

    def trigger_hook(self, type_: HookType):
        """ Executes hook passing a refence to the :py:class:`Game` object. """
        hooks = self.hooks.get(type_) or []
        for hook in hooks:
            hook(self)

    def start(self):
        """ Start game. """
        self.state = States.START
        self.is_done = False
        self.map.reset()
        self.main_loop()

    def main_loop(self):
        """
        Handles the main loop of the game.
        While the game is not done it will keep advancing levels and calling :py:meth:`~level_loop`.
        """
        self.trigger_hook(HookType.GAME_START)
        while not self.is_done:
            for player in self.players:
                player.move(Position(0, 0), False)
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
            self.room.start()
            self.play_turn()
            self.room.end()

            endgame = self.check_endgame_conditions()
            if endgame:
                self.endgame(endgame)

    def update_state(self):
        """ Automatically updates game state. """
        if isinstance(self.room, rooms.FightRoom) and not self.room.is_done:
            self.state = States.IN_FIGHT
        elif isinstance(self.room, rooms.FightRoom) and self.room.is_done:
            self.state = States.IN_FIGHT_ROOM_DONE

    def play_turn(self):
        """
        Handles game turn.
        Player moves first, then enemies (if any). Game state gets updated accordingly.
        """
        self.trigger_hook(HookType.TURN_ROUND_START)
        self.update_state()

        for player in self.players:
            player.play_turn()

        if isinstance(self.room, rooms.BaseDangerRoom) and self.room.enemies:
            for enemy in self.room.enemies:
                enemy.play_turn()

        self.update_state()
        self.trigger_hook(HookType.TURN_ROUND_END)

    def check_endgame_conditions(self):
        return self.endgame_condition(self)

    def endgame(self, state):
        """ Ends game. """
        self.trigger_hook(HookType.GAME_END)
        self.is_done = True
        self.state = state
