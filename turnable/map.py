#!/bin/usr/python3
from typing import Tuple
from math import floor

from turnable.rooms import Room


class InvalidMoveException(Exception):
    pass


class Position:
    """ Represents an (X, Y) position. """
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __iadd__(self, other):
        return self.__add__(other)

    def __str__(self):
        return f'(x={self.x}, y={self.y})'


def parse_directions(dir_: str):
    """
    Returns delta position based on string representation.

    Valid Inputs:
    * up
    * down
    * left
    * right
    """
    if dir_ == 'UP':
        return Position(1, 0)
    if dir_ == 'DOWN':
        return Position(-1, 0)
    if dir_ == 'LEFT':
        return Position(0, -1)
    if dir_ == 'RIGHT':
        return Position(0, 1)
    return None


class Map:
    """
    Contains the map grid and logic.
    As is, generates a 2d grid of (:py:attr:`Map.BASE_MAP_SIZE` + :py:attr:`self.level`.
    """
    BASE_MAP_SIZE = 6

    def __init__(self):
        self.game = None
        self.grid = None
        self.player_pos = None
        self.level = 0

    @property
    def player_pos(self):
        """ Returns player position. This is updated on :py:meth:`turnable.chars.Character.move`. """
        return self.__player_pos

    @player_pos.setter
    def player_pos(self, pos):
        """ Tests new player position is inside grid bounds. """
        if pos is None:
            self.__player_pos = pos
            return

        if pos.x < 0 or pos.y < 0 or pos.x > len(self.grid[0]) - 1 or pos.y > len(self.grid) - 1:
            raise InvalidMoveException('Player position out of range.')

        self.__player_pos = pos

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
        return self.grid[self.player_pos.x][self.player_pos.y]

    def get_start_pos(self):
        """ Returns starting room. Starting room will always be an :py:class:`room.EmptyRoom`. """
        return Position(floor(len(self.grid[0]) / 2), floor(len(self.grid) / 2))

    def _generate_grid(self, x: int = BASE_MAP_SIZE, y: int = BASE_MAP_SIZE) -> Tuple[int, int]:
        """ Generates X by Y grid and returns (X, Y) as tuple. """
        self.grid = []
        for x_ in range(x):
            self.grid.append([])
            for y_ in range(y):
                room = Room(Position(x_, y_), self.game)
                self.grid[x_].append(room)
        return x, y
