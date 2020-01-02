from typing import Optional, Any
import re


class Command:
    def __init__(self, tag: str, help: str, method: Optional[str] = None, owner: Optional[object] = None):
        """
        Tag can be a regex and matched groups will be saved into :py:attr:`self.matched`.
        For example, the tag ``MOV(UP|DOWN|LEFT|RIGHT)`` will match
        """
        self.tag = tag
        self.help = help
        self.method = method
        self.owner = owner
        self.matched = None

    def is_valid_input(self, input_):
        m = re.match(self.tag, input_.upper())
        if m:
            self.matched = m.groups()
            return True
        return False

