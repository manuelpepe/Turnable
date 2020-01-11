"""
You can use classes and functions in this module to build a CLI interface for your game.
These classes are used by default when constructing your game object with :py:func:`turnable.build_game`.
"""

import os
import sys

from turnable import BaseInputStream, Game
from turnable.streams import CommandRequest, CommandResponse, BaseOutputStream


def clear_terminal():
    """ Sends a system call to clear the terminal. """
    os.system('cls' if os.name == 'nt' else 'clear')


class TextInputStream(BaseInputStream):
    """
    Input stream for CLI gameplay.

    Performs :py:func:`input` calls for user input.
    """
    def __init__(self, stdout=sys.stdout):
        self.stdout = stdout

    def request(self, request: CommandRequest) -> CommandResponse:
        input_ = input(request.label)
        return CommandResponse(request, input_)


class TextOutputStream(BaseOutputStream):
    """ Output stream for CLI gameplay. """

    def __init__(self, *args, clear: bool = True, **kwargs):
        """ *clear* indicates if the terminal should be clerared before each send. """
        super().__init__(*args, **kwargs)
        self.clear = clear

    def send(self, game: Game):
        if self.clear:
            clear_terminal()

        player = game.player
        room = game.room
        template = f"""{player.name}
{'=' * len(player.name)}
Health: {player.health}
Armor: {player.armor}
Damage: {player.damage}
Position: X={player.pos.x} Y={player.pos.y}

{room.__class__.__name__}
{'=' * len(room.__class__.__name__)}
Position: X={room.pos.x} Y={room.pos.y}
"""
        if hasattr(room, 'enemies'):
            template += f"""
Enemies
======="""
            for enemy in room.enemies:
                template += f"""
* {enemy.__class__.__name__}
Health: {enemy.health}
Armor: {enemy.armor}
Damage: {enemy.damage}
"""
        print(template)

