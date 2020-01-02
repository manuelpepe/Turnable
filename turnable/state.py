from enum import Enum


class States(Enum):
    START = 0
    IN_EMPTY_ROOM = 1
    IN_REWARD_ROOM = 2
    IN_FIGHT_ROOM_BEFORE_FIGHT = 3
    IN_FIGHT = 4
    IN_FIGHT_ROOM_AFTER_FIGHT = 5
    LOST = 6
    WON = 7
