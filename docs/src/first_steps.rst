First steps
===========

Installing
***********

You can install Turnable from PyPi with: ::

        pip install -i https://test.pypi.org/simple/ Turnable

.. warning::
    Currently Trunable is only available from TestPyPi. Once the
    first stable version is released it will be moved to the standard PyPi.


Simplest game example
*********************

This is the least amount of lines it requires to run your first game with Turnable:

.. code-block::

    from turnable import build_game

    g = build_game('My New Game', 'My Player Name')
    g.start()

The code above will start a CLI game with the default classes, parameters and distributions.

Making your own PlayableEntity
******************************

The :py:class:`turnable.PlayableEntity` represents an entity that can be played by the player.
You can extend the this class and pass it as *player_class* to `turnable.build_game`.
For example, this is an implementation of a player that has a 30% dodge change: ::

    class Ninja(PlayableEntity):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.dodge_change = 0.3

        def take_damage(self, damage: int):
            if random.random() >= self.dodge_change:
                super().take_damage(damage)

    g = build_game('My New Game', 'My Player Name', player_class=Ninja)
    g.start()

.. note::
    For more examples of PlayableEntity implementations see :ref:`playable-entity-implementations`.


Adding new actions
------------------

You can add your own actions that a player can make.
To add an action you have to:

#. Extend :py:meth:`turnable.chars.PlayableEntity.available_actions`

    a. Build your own list of :py:class:`turnable.streams.CommandRequest`.
    b. Extend it with ``super().available_actions()``.
    c. Return the extended list.
#. Implement your own ``handle_<action>(resp: CommandResponse)``.

.. note::
    If you are using your own :py:class:`turnable.streams.BaseRequest` class, you'll need to change the default
    class  in :py:attr:`turnable.chars.PlayableEntity.COMMAND_CLASS`.

    For more information, see :ref:`implementing-your-own-baserequest`.

For example, here we implement a fairly straight forward AoE attack.

.. code-block::

    class Mage(PlayableEntity):
        def available_actions(self):
            actions = []
            command = self.COMMAND_CLASS  # We use the configured command request class.

            if self.game.state == States.IN_FIGHT:
                actions.append(command('AREA', 'Deals damage to all enemies.', 'handle_area', self))

            # Add actions made available by parent
            actions.extend(super().available_actions())
            return actions

        def handle_area(self, resp: CommandResponse):
            for enemy in self.game.room.enemies:
                enemy.take_damage(self.damage)

.. _special-commands:

Special Commands
----------------

Special commands are commands that start with a `:` (colon).
These commands do not use the player turn, for example, `:help`.

You can use this for all types of things, not only showing data to the user or changing settings.
You could, for example, have a custom ``PlayableEntity`` that has an inventory and access to
actions like ``:use 1`` or ``:check 1``.
