from typing import Callable

from turnable.map import Map
from turnable.game import Game
from turnable.chars import PlayableEntity
from turnable.hooks import HookType
from turnable.rooms import FightRoom
from turnable.streams import BaseInputStream, BaseOutputStream
from turnable.helpers.text import TextInputStream, TextOutputStream


def build_game(game_name: str,
               player_name: str,
               player_class: Callable = PlayableEntity,
               map_class: Callable = Map,
               instream: BaseInputStream = TextInputStream,
               outstream: BaseOutputStream = TextOutputStream) -> Game:

    FightRoom.ENEMY_DIST = FightRoom.DEFAULT_DIST
    Map.ROOM_DIST = Map.DEFAULT_DIST

    player = player_class(player_name)
    map_ = map_class()

    return Game(game_name, player, map_, instream(), outstream())
