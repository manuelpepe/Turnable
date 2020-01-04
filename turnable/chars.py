import logging
import random

from enum import Enum

from turnable.command import Command
from turnable.map import Position
from turnable.geometry import parse_directions
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

    def is_alive(self):
        """ Returns if entity has health left. """
        return self.health > 0


class Entity(HealthyEntity):
    """
    Represents base entity for both AI (enemies) and not-AI characters Entities.
    Most of the time you shouldn't need to directly inherit from this class.
    """
    _logger = logging.getLogger('Entity')

    COMMAND_CLASS = Command
    TURN_START_HOOK = None
    TURN_END_HOOK = None

    BASE_HEALTH = 100
    BASE_DAMAGE = 10

    def __init__(self,
                 name: str = 'Entity',
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

        self._logger.debug(f'Created {self} at {self.pos}.')

    @property
    def actions(self):
        return self.available_actions()

    @actions.setter
    def actions(self, action):
        raise AttributeError("Do not directly set value. If you are sure of what you're doing override "
                             "@actions.setter in subclass.")

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
        raise NotImplementedError('Implement this in your subclass')  # return random.choice(enemies)

    def get_action(self) -> CommandResponse:
        """
        This method defines what action is the Entity playing in it's turn.

        For a Playable character you might request the input to the user, whilst
        for an AI character you'd run some algorithm (or random.randint() :D)
        """
        raise NotImplementedError('This should be implemented in subclasses.')

    def play_turn(self):
        """
        Plays turn and triggers appropiate hooks.
        You can change the hooks triggered overriding :py:attr:`~TURN_START_HOOK` and :py:attr:`~TURN_END_HOOK`.

        By default, `Entity` enables the :ref:`special-commands` feature.
        """
        if self.TURN_START_HOOK:
            self.game.trigger_hook(self.TURN_START_HOOK)

        resp = self.get_action()
        while resp.is_special:
            self._act_on_response(resp)
            resp = self.get_action()

        self._act_on_response(resp)
        if self.TURN_END_HOOK:
            self.game.trigger_hook(self.TURN_END_HOOK)

    def _act_on_response(self, resp):
        """
        Takes a :py:class:`turnable.stream.CommandResponse` as *resp* and calls
        the method defined in ``resp.command.method``, passing the same *resp* as a parameter.
        """
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
        return actions

    def __str__(self):
        return f'{self.name}(hp={self.health}, ar={self.armor}, dmg={self.damage})'


class PlayableEntity(Entity):
    """
    .. _playable-entity:

    Entity that represents a human player.
    """
    def available_actions(self):
        """ Adds move action as a Playable character should be able to move between rooms. """
        actions = super().available_actions()

        if self.game.state != States.IN_FIGHT:
            actions.append(self.COMMAND_CLASS('MOV(UP|DOWN|LEFT|RIGHT)', 'Moves between rooms.', 'handle_move', self))

        actions.append(self.COMMAND_CLASS(':HELP', 'Shows available commands.', 'handle_help', self))
        return actions

    def get_action(self) -> CommandResponse:
        """ Sends out the request for the next move and retries if command is invalid. """
        req = CommandRequest('Enter action: ', self.actions, self.game.inputstream)
        resp = req.send()
        while not resp or not resp.command:
            resp = req.send(True)
        return resp

    def handle_help(self, resp: CommandResponse):
        self._logger.debug('Actions:')
        for cmd in self.actions:
            self._logger.debug(f'{cmd.tag} - {cmd.help}')

    def handle_move(self, resp: CommandResponse) -> bool:  # newpos: Position, delta: bool = True) -> Position:
        """
        Prepares move from action :py:class:`turnable.streams.CommandResponse`.

        It's good practice to make handler functions for every Actions in :py:meth:`~available_actions` that
        takes care of setup, and then defer the actual logic to it's own function.

        For other example see :py:meth:`~handle_attack`.
        """
        self._logger.debug('Handling move')
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
        tmppos = self.pos + newpos if delta else newpos
        if self.game.map.is_valid(tmppos):
            self._logger.debug(f'Moving {self} to {tmppos}.')
            self.pos = tmppos
            return True
        self._logger.debug(f'{self} couldn\'t move to {self.pos}')
        return False

    def target_attack(self, enemies):
        """ Ask player for target. """
        target = None
        if len(enemies) == 1:
            return enemies[0]
        while target is None or target > len(enemies) or target <= 0:
            target = int(input(f'Select target (1-{len(enemies)}).'))
        return enemies[target - 1]


class AIEntity(Entity):
    """ For now it can only attack. """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('health', 20)
        kwargs.setdefault('armor', 20)
        super().__init__(*args, **kwargs)

    def get_action(self) -> CommandResponse:
        req = CommandRequest('Not used', self.actions)
        return CommandResponse(req, 'atk')

    def target_attack(self, enemies):
        self._logger.debug('AIEntity ATTACKING')
        return self.game.player


class Soldier(PlayableEntity):
    """ Deals single target damage. """

    def target_attack(self, enemies):
        """ Ask player for target. """
        target = None
        if len(enemies) == 1:
            return enemies[0]
        while target is None or target > len(enemies) or target <= 0:
            target = int(input(f'Select target (1-{len(enemies)}.'))
        return enemies[target - 1]


class Mage(PlayableEntity):
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
