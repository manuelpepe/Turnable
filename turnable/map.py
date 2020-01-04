#!/bin/usr/python3
import logging
import random
from typing import Tuple
from math import floor

from turnable.geometry import Position
from turnable.rooms import FightRoom, Room, EmptyRoom


class Map:
    """
    Contains the map grid and logic.
    As is, generates a 2d grid of (:py:attr:`Map.BASE_MAP_SIZE` + :py:attr:`self.level`.
    """
    _logger = logging.getLogger('turnable.map.Map')
    BASE_MAP_SIZE = 6
    ROOM_DIST = [
        (FightRoom, 0.3),
        (EmptyRoom, 0.7),
    ]

    def __init__(self):
        self.game = None
        self.grid = None
        self.player_pos = None
        self.level = 0

    def is_valid(self, pos: Position):
        return 0 <= pos.x < len(self.grid[0]) and 0 <= pos.y < len(self.grid)

    def reset(self) -> Tuple[int, int]:
        """ Returns :py:attr:`self.level` to 1 and regenerates grid. """
        self.level = 1
        return self._generate_grid()

    def next_level(self) -> Tuple[int, int]:
        """ Increments level and generates new grid. """
        self.level += 1
        size = (self.BASE_MAP_SIZE + self.level,) * 2
        return self._generate_grid(*size)

    def get_player_room(self):
        """ Return room in player position. """
        return self.grid[self.game.player.pos.x][self.game.player.pos.y]

    def get_start_pos(self):
        """ Returns starting room. Starting room will always be an :py:class:`room.EmptyRoom`. """
        return Position(floor(len(self.grid[0]) / 2), floor(len(self.grid) / 2))

    def _generate_grid(self, x: int = BASE_MAP_SIZE, y: int = BASE_MAP_SIZE) -> Tuple[int, int]:
        """
        Generates X by Y grid and returns (X, Y) as tuple.

        Steps:
        # Create grid
        # Position enemies
        """
        self.grid = self._generate_grid_skeleton(x, y)
        return x, y

    def _generate_grid_skeleton(self, x: int, y: int) -> list:
        """
        Creates and returns grid skeleton.
        """
        grid = []
        for x_ in range(x):
            grid.append([])
            for y_ in range(y):
                room = self._get_next_room()(Position(x_, y_), self.game)
                grid[x_].append(room)
        return grid

    def _get_next_room(self):
        """
        Generates next room based on weights defined in :py:attr:`~ROOM_DIST`
        """
        return random.choices(
            [class_ for class_, weight in self.ROOM_DIST],
            [weight for class_, weight in self.ROOM_DIST]
        )[0]
