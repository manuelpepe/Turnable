from __future__ import annotations

import sys
import logging

from turnable.command import Command

from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from turnable.game import Game


class StreamException(Exception):
    pass


class BaseInputStream:
    """
    An input stream knows how to acquire input from the player.
    In a CLI interface it might read from stdin, while in a network interface it might read from a socket.
    """

    def request(self, request: CommandRequest) -> CommandResponse:
        """ Handles :py:class:`CommandRequest` and builds an appropiate :py:class:`CommandResponse`. """
        raise NotImplementedError()


class BaseOutputStream:
    """
    An output stream knows how to send info to the user, and in which format.
    """
    def send(self, game: Game):
        """ Handles how the information gets to the player. """
        raise NotImplementedError()


class CommandRequest:
    """ Represents a request for user input. Part of the **Command Series** that allows for CLI gameplay. """

    _logger = logging.getLogger('turnable.streams.CommandRequest')

    def __init__(self, label: str, commands: list = None, instream: BaseInputStream = None):
        self.label = label
        self.commands = commands or []
        self.stream = instream
        self.retried = False

    def get_command(self, tag: str) -> Optional[Command]:
        """ Returns :py:class:`turnable.command.Command` based on tag. """
        for cmd in self.commands:
            if cmd.is_valid_input(tag):
                return cmd
        return None

    def send(self, retry: bool = False) -> CommandResponse:
        """ Sends request through :py:attr:`~stream`. """
        if retry and not self.retried:
            self.label = f"Invalid command.\n{self.label}"
            self.retried = True
        return self.stream.request(self)


class CommandResponse:
    """ Represents the response built from a request and user input. """

    def __init__(self, request: CommandRequest, command: str):
        self.rawdata = command.strip()
        self.request = request
        self.command = request.get_command(self.rawdata)
        self.is_special = self.rawdata and self.rawdata[0] == ':'


class TextInputStream(BaseInputStream):
    """
    Input stream for CLI gameplay.
    It utilizes :py:class:`CommandResponse` and :py:class:`CommandRequest`, so it is a **Command** interface
    class, just that ``CommandTextInputStream`` seemed harsher.

    Performs basic :py:func:`input` calls.
    """
    def __init__(self, stdout=sys.stdout):
        self.stdout = stdout

    def request(self, request: CommandRequest) -> CommandResponse:
        input_ = input(request.label)
        return CommandResponse(request, input_)


class TextOutputStream(BaseOutputStream):
    """
    Output stream for CLI gameplay.
    """
    def send(self, game: Game):
        player = game.player
        room = game.room
        template = f"""
{room.__class__.__name__}
{'=' * len(room.__class__.__name__)}
Position: X={room.pos.x} Y={room.pos.y}

Player
======
Health: {player.health}
Armor: {player.armor}
Damage: {player.damage}
Position: X={player.pos.x} Y={player.pos.y}
"""
        if hasattr(room, 'enemies'):
            template += """
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

