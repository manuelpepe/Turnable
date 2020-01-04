from typing import Callable

from turnable.game import Game
from turnable.hooks import HookType
from turnable.map import Map
from turnable.streams import BaseInputStream


def build_game(game_name: str,
               player_name: str,
               player_class: Callable,
               map_class: Callable,
               instream_class: Callable[[], BaseInputStream],
               outstream_class: Callable = None) -> Game:
    player = player_class(player_name)
    map_ = map_class()
    instream = instream_class()
    outstream = outstream_class() if outstream_class else None

    return Game(game_name, player, map_, instream, outstream)
