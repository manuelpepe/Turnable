First steps
===========

Installing
***********

You can install Turnable from PyPi with: ::

        pip install -i https://test.pypi.org/simple/ Turnable

.. warning::
    Currently Trunable is only available from TestPyPi. Once the
    first stable version is released it will be moved to the standard PyPi.


Simplest game ever
******************
This is the least amount of lines it requires to run your first game with Turnable:

.. code-block::

    from turnable import build_game

    g = build_game('My New Game', 'My Player Name')
    g.start()

The code above will start a CLI game with the default classes, parameters and distributions.
I


Most basic game
***************

**WIP**


Extending PlayableCharacter
***************************


.. _special-commands:

Special Commands
----------------

Special commands are commands that start with a `:` (colon).
These commands do not use the player turn, for example, `:help`.

You can use this for all types of things, not only showing data to the user or changing settings.
You could, for example, have a custom ``PlayableEntity`` that has an inventory and access to
actions like ``:use 1`` or ``:check 1``.
