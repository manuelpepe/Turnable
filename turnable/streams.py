import sys
from typing import Optional

from turnable.command import Command


class StreamException(Exception):
    pass


class RequestInputException(StreamException):
    pass


class BaseRequest:
    """ Represents a request for user input. """
    pass


class BaseResponse:
    """ Represents the response built from a request and user input. """
    pass


class CommandRequest(BaseRequest):
    """ Represents a request for user input. Part of the **Command Series** that allows for CLI gameplay. """

    def __init__(self, label: str, commands: list = None, stream: 'BaseInputStream' = None):
        self.label = label
        self.commands = commands or []
        self.stream = stream
        self.retried = False

    def get_command(self, tag: str) -> Optional[Command]:
        """ Returns :py:class:`turnable.command.Command` based on tag. """
        for cmd in self.commands:
            if cmd.is_valid_input(tag):
                return cmd
        return None

    def send(self, retry: bool = False) -> 'CommandResponse':
        """ Sends request through :py:attr:`~stream`. """
        if retry and not self.retried:
            self.label = f"Try again.\n{self.label}"
            self.retried = True
        return self.stream.request(self)


class CommandResponse(BaseResponse):
    """ Represents the response built from a request and user input. """

    def __init__(self, request: CommandRequest, command: str):
        self.request = request
        self.command = request.get_command(command)
        self.rawdata = command


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
    It might use an :py:class:`CommandResponse` but that's up to the implementer.
    """
    def send(self, *args, **kwargs):
        """ Handles how the information gets to the player. """
        raise NotImplementedError()


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
    def send(self, text):
        print(text)
