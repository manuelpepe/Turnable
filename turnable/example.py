import logging
import random
from typing import Callable

import time

from turnable import Game, HookType, build_game
from turnable.chars import PlayableEntity, Entity
from turnable.state import States
from turnable.streams import TextInputStream, TextOutputStream, CommandResponse
from turnable.map import Map
from turnable.rooms import FightRoom


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class FlyingPoisonousCharacter(PlayableEntity):
    """
    Custom Character

    Can poison enemies, poison stacks increasing duration. Has 10% base
    dodge change.
    """
    POISON_DURATION = 2

    def __init__(self, *args, **kwargs):
        super(FlyingPoisonousCharacter, self).__init__(*args, **kwargs)
        self.flying = False  # Add new control attribute, used for flying action.
        self.fly_start = 0
        self.dodge_change = 0.1

    def take_damage(self, damage: int):
        if random.random() >= self.dodge_change:
            super().take_damage(damage)

    def available_actions(self):
        actions = []
        command = self.COMMAND_CLASS

        if self.game.state == States.IN_FIGHT:
            actions.append(command('POI', 'Poisons enemies, they take 3 damage a turn.', 'handle_poison', self))
            actions.append(command('FLY', 'Start flying, you cannot take damage for 2 turns.', 'handle_fly', self))

        actions.extend(super().available_actions())
        return actions

    def handle_fly(self, resp: CommandResponse):
        self.flying = not self.flying

    def handle_poison(self, resp: CommandResponse):
        """ Poisons all enemies """
        # The name of the attribute that will be injected into the enemy object
        turns_left_attr = '_MyGame_poison_left'
        hook_attr = '_MyGame_poison_hook'

        for enemy in self.game.room.enemies:
            turns_left = getattr(enemy, turns_left_attr, 0)
            hook = getattr(enemy, hook_attr, None)

            if hook:
                # If already poisoned only increase turns.
                turns_left = turns_left + self.POISON_DURATION
                setattr(enemy, turns_left_attr, turns_left)
                continue

            hook = build_poison_hook(hook_attr, turns_left_attr, enemy, 3)
            setattr(enemy, turns_left_attr, self.POISON_DURATION)
            setattr(enemy, hook_attr, hook)
            self.game.add_hook(HookType.ENEMY_TURN_START, hook)


def build_poison_hook(hook_attr: str, turns_left_attr: str, enemy: Entity, damage: int) -> Callable:
    """
    This functions BUILDS the hook function that is added to the game.

    We can use this builder pattern when we want to keep references to certain things. In this
    case we save a reference to the *enemy* that is poisoned, how much *damage* is the poison dealing and
    how many *turns* will it last.
    """

    def poison_hook(game: Game, hook_type: HookType, hook_id: str):
        """
        This is the actual hook function that gets added with ``game.add_hook``.
        We set a counter attribute in the enemy that tells us when to stop doing damage to it.
        """
        if not enemy or not enemy.is_alive():
            # Check the enemy is still alive
            return

        turns_left = getattr(enemy, turns_left_attr)
        if turns_left <= 0:
            game.remove_hook(hook_type, hook_id)
            setattr(enemy, hook_attr, None)
            return

        enemy.take_damage(damage)
        setattr(enemy, turns_left_attr, turns_left - 1)
    return poison_hook


def my_welcome_hook(game: Game, hook_type: HookType, hook_id: str):
    """ This is a hook that starts a countdown at the start of the game. """
    print('The game is going to start in...')
    for t in range(5, 0, -1):
        print(f'{t}...')
        time.sleep(0.1)
    print('GO!')
    time.sleep(0.5)
    game.remove_hook(hook_type, hook_id)


def main():
    FightRoom.ENEMY_DIST = FightRoom.SAMPLE_DIST
    g = build_game('My Game', 'Player Name', FlyingPoisonousCharacter, Map, TextInputStream, TextOutputStream)
    g.add_hook(HookType.GAME_START, my_welcome_hook)
    g.start()


if __name__ == '__main__':
    main()