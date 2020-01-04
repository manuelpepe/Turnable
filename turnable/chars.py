import logging
import random

from enum import Enum

from turnable.command import Command
from turnable.map import Position, parse_directions, InvalidMoveException
from turnable.state import States
from turnable.streams import CommandRequest, CommandResponse


class CharacterStatus(Enum):
    STUNNED = 0
    ONFIRE = 1


class HealthyEntity:
    """ Represents an Entity with health and armor"""
    _logger = logging.getLogger('HealthyEntity')

    BASE_HEALTH = 100
    BASE_ARMOR = 100

    def __init__(self,
                 health: int = BASE_HEALTH,
                 armor: int = BASE_ARMOR):
        self.health = health
        self.max_health = health
        self.armor = armor

    def take_damage(self, damage: int):
        """ Handles health and armor reduction based on incomming damage. """
        leftdmg = damage

        if self.armor:
            leftdmg = damage - self.armor
            self.armor = max(0, self.armor - damage)

        if leftdmg > 0:
            self.health -= leftdmg

        self._logger.debug(f'DMG - {self} received {damage}.')


class Character(HealthyEntity):
    """ Represents base playable character. """
    _logger = logging.getLogger('Character')

    COMMAND_CLASS = Command

    BASE_HEALTH = 100
    BASE_DAMAGE = 10

    def __init__(self,
                 name: str = 'Character',
                 damage: int = BASE_DAMAGE,
                 pos: Position = None,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.game = None
        self.name = name
        self.damage = damage
        self.pos = pos
        self.status_list = []

        self._logger.debug(f'NEW - {self} at {self.pos}.')

    @property
    def actions(self):
        return self.available_actions()

    @actions.setter
    def actions(self, action):
        raise AttributeError("Do not directly set value. If you are sure of what you're doing override "
                             "@actions.setter in subclass.")

    def handle_move(self, resp: CommandResponse) -> bool:  # newpos: Position, delta: bool = True) -> Position:
        """
        Prepares move from action :py:class:`turnable.streams.CommandResponse`.

        It's good practice to make handler functions for every Actions in :py:meth:`~available_actions` that
        takes care of setup, and then defer the actual logic to it's own function.

        For other example see :py:meth:`~handle_attack`.
        """
        hasdir = len(resp.command.matched) == 1
        delta = parse_directions(resp.command.matched[0]) if hasdir else None
        while not delta:
            dir_cmd = Command('(UP|DOWN|LEFT|RIGHT)', 'Direction')
            req = CommandRequest('Enter direction: ', [dir_cmd], self.game.inputstream)
            res = req.send()
            dir_ = res.command.matched[0] if res.command.matched else None
            delta = parse_directions(dir_)
        return self.move(delta, True)

    def move(self, newpos: Position, delta: bool = True) -> bool:
        """ Tries to move character to new position. If delta is True the position
         will be added; otherwise it'll be replaced. """
        oldpos = self.pos.copy() if self.pos else None

        if self.pos and delta:
            self.pos += newpos
        else:
            self.pos = newpos

        try:
            self.game.map.player_pos = self.pos
            self._logger.debug(f'MOV - {self} to {self.pos}.')
            return True
        except InvalidMoveException:
            self._logger.warn(f'MOV - {self} couldn\'t move to {self.pos}')
            self.pos = oldpos
            return False

    def handle_attack(self, resp: CommandResponse):
        """
        Handles attack from :py:class:`turnable.streams.CommandResponse`.

        It's good practice to make handler functions for every Actions in :py:meth:`~available_actions` that
        takes care of setup, and then defer the actual logic to it's own function. Even if the only thing you
        are currently doing is calling the logic function, as in this example, it will make inheritance much easier.

        For other example see :py:meth:`~handle_move`.
        """
        self.attack()

    def attack(self):
        """ Deals damage equal to :py:attr:`~damage` to all enemies targetted by :py:meth:`~target_attack`. """
        enemies = self.target_attack(self.game.room.enemies)
        if type(enemies) != list:
            enemies = [enemies]

        if CharacterStatus.STUNNED not in self.status_list \
                and self.game.state == States.IN_FIGHT:
            for enemy in enemies:
                enemy.take_damage(self.damage)
                self._logger.debug(f'ATT - {self} to {enemy}.')

    def target_attack(self, enemies):
        """ This method is called first in :py:meth:`~attack` to target enemies. """
        return random.choice(enemies)

    def is_alive(self):
        """ Returns if character is alive. """
        return self.health > 0

    def _get_action(self) -> CommandResponse:
        """ This function is called in :py:meth:`~play_turn` to request the following move. """
        req = CommandRequest('Enter action: ', self.actions, self.game.inputstream)
        resp = req.send()
        while not resp or not resp.command:
            resp = req.send(True)
        return resp

    def play_turn(self):
        """ Plays it's turn. You can handle actions here. """
        resp = self._get_action()
        action = resp.command
        getattr(self, action.method)(resp)

    def available_actions(self):
        """
        Returns actions available to the player.

        Actions are added as :py:attr:`~COMMAND_CLASS` which defaults to :py:class:`turnable.command.Command`,
        if you are using a command subclass remember to override the attribute in your subclass.

        .. note::
            If you're adding actions in a subclass and wanna keep the existing ones remember to start with
            ``actions = super().available_actions()``, add your custom actions to the dictionary and return it.
        """
        actions = []
        if self.game.state == States.IN_FIGHT:
            actions.append(self.COMMAND_CLASS('ATK', 'Attack enemies.', 'handle_attack', self))
        else:
            actions.append(self.COMMAND_CLASS('MOV(UP|DOWN|LEFT|RIGHT)', 'Moves between rooms.', 'handle_move', self))

        return actions

    def __str__(self):
        return f'{self.name}(hp={self.health}, ar={self.armor}, dmg={self.damage})'


class Soldier(Character):
    """ Deals single target damage. """

    def target_attack(self, enemies):
        """ Ask player for target. """
        target = None
        if len(enemies) == 1:
            return enemies[0]
        while target is None or target > len(enemies) or target <= 0:
            target = int(input(f'Select target (1-{len(enemies)}.'))
        return enemies[target - 1]


class Mage(Character):
    """ Mage class. Deals damage in area. """
    BASE_MAX_TARGETS = 2
    BASE_DAMAGE = 5

    def __init__(self,
                 *args,
                 max_targets: int = BASE_MAX_TARGETS,
                 **kwargs):
        super().__init__()
        self.max_targets = max_targets

    def target_attack(self, enemies):
        """ Selects :py:attr:`max_targets` targets randomly. """
        choices = []
        while len(choices) < self.max_targets:
            c = random.randint(0, len(enemies) - 1)
            if c not in choices:
                choices.append(c)

        return [enemies[c] for c in choices]
