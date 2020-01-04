"""
Types of hooks
--------------

Type of hooks are described at :py:class:`HookType`.

How to use hooks
----------------

Using hooks is real simple, all you need is a function that receives an argument called ``game``, which will be
a reference to :py:class:`turnable.game.Game`, and the proper :py:class:`HookType`. Then yu can add a hook
to your Game object such as:

For example, if you wanted to print a message to the screen at the start of the level you would: ::

    from turnable import Game, HookType

    def my_welcome_hook(game):
        print('The game is going to start in 5...')
        for t in range(4, 1):
            print(f'{t}...')
            time.sleep(1)
        print('GET READY...')

    game = Game( ... )
    game.add_hook(HookType.GAME_START, my_welcome_hook)
    game.start()


When to use hooks
-----------------

You can use them for all kinds of fun stuff, there is no rules!

There's only one thing that is tied to hooks, and it is the :py:class:`turnable.stream.BaseOutputStream`.
If you're developing your own UI, you set your own hooks that handle getting the data from the game to
whatever you are using as UI.

For example, you could set a hook that triggers every start of the turn round so you can request the user for input
and show them how their turn played out. ::

    import MyUI
    from turnable import Game, HookType

    def ui_update_hook(game):
        # You can do crazy stuff here like building a data package, serializing it and sending it over the network.
        MyUI.render_from_game(game)

    game = Game( ... )
    game.add_hook(HookType.GAME_START, my_welcome_hook)
    game.start()

"""
from enum import Enum, auto


class HookType(Enum):
    """
    Type of hooks that can be added to the :py:class:`Game` object.

    * ``GAME_START``: At the end of :py:meth:`Game.main_loop`.
    * ``GAME_END``: At the start of :py:meth:`Game.main_loop`.
    * ``LEVEL_START``: At the start of :py:meth:`Game.level_loop`.
    * ``LEVEL_END``: At the end of :py:meth:`Game.level_loop`.
    * ``ROOM_START``: At :py:meth:`Room.start` which is called before the turns are played in :py:meth:`Game.level_loop`.
    * ``ROOM_END``: At :py:meth:`Room.end` which is called after the turns are played in :py:meth:`Game.level_loop`.
    * ``TURN_ROUND_START``: At the start of :py:meth:`Game.play_turn`.
    * ``TURN_ROUND_END``: At the end of :py:meth:`Game.play_turn`.

    """
    GAME_START = auto()
    GAME_END = auto()
    LEVEL_START = auto()
    LEVEL_END = auto()
    ROOM_START = auto()
    ROOM_END = auto()
    BEFORE_PLAYER_MOVE = auto()
    AFTER_PLAYER_MOVE = auto()
    TURN_ROUND_START = auto()
    TURN_ROUND_END = auto()
