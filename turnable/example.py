import random

from typing import Callable

from turnable import Game, HookType, build_game
from turnable.chars import PlayableEntity, Entity
from turnable.state import States
from turnable.streams import CommandResponse
from turnable.helpers.text import clear_terminal


class PoisonousCharacter(PlayableEntity):
    """
    Custom Character

    Can poison enemies, poison stacks increasing duration. Has 10% base
    dodge change.
    """
    POISON_TURNS_LEFT_ATT = '_MyGame_poison_left'
    POISON_HOOK_ATT = '_MyGame_poison_hook'
    POISON_DURATION = 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dodge_change = 0.1

    def take_damage(self, damage: int):
        """ Has a chance to not take damage. """
        if random.random() >= self.dodge_change:
            super().take_damage(damage)

    def available_actions(self):
        actions = []
        command = self.COMMAND_CLASS

        if self.game.state == States.IN_FIGHT:
            actions.append(command('POI', 'Poisons enemies, they take 3 damage a turn.', 'handle_poison', self))

        actions.extend(super().available_actions())
        return actions

    def handle_poison(self, resp: CommandResponse):
        """ Poisons all enemies """
        # The name of the attribute that will be injected into the enemy object
        for enemy in self.game.room.enemies:
            self._infect(enemy)

    def _infect(self, enemy: Entity):
        turns_left = getattr(enemy, self.POISON_TURNS_LEFT_ATT, self.POISON_DURATION)
        hook = getattr(enemy, self.POISON_HOOK_ATT, None)

        if hook:
            turns_left = turns_left + self.POISON_DURATION
        else:
            hook = build_poison_hook(self.POISON_HOOK_ATT, self.POISON_TURNS_LEFT_ATT, enemy, 3)
            self.game.add_hook(HookType.ENEMY_TURN_START, hook)

        setattr(enemy, self.POISON_HOOK_ATT, hook)
        setattr(enemy, self.POISON_TURNS_LEFT_ATT, turns_left)


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
            return

        turns_left = getattr(enemy, turns_left_attr)
        if turns_left <= 0:
            game.remove_hook(hook_type, hook_id)
            setattr(enemy, hook_attr, None)
            return

        enemy.take_damage(damage)
        setattr(enemy, turns_left_attr, turns_left - 1)
    return poison_hook


def start_screen(game: Game, hook_type: HookType, hook_id: str):
    """ This is a hook that starts a countdown at the start of the game. """
    clear_terminal()
    print(f"All set.")
    print(f"Welcome, {game.player.name}, to {game.name}.")
    print(f"Press any key to start")
    input()


def main():
    print("""Set up your game. """)
    game_name = input("Choose game name:")
    player_name = input("Choose player name:")

    g = build_game(game_name, player_name)
    g.add_hook(HookType.GAME_START, start_screen)
    g.start()


if __name__ == '__main__':
    main()