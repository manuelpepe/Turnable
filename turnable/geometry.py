class Position:
    """ Represents an (X, Y) position. """
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def copy(self) -> 'Position':
        return Position(self.x, self.y)

    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __radd__(self, other):
        return Position(self.x + other.x, self.y + other.y)

    def __str__(self):
        return f'(x={self.x}, y={self.y})'

    def __eq__(self, other):
        return other.x == self.x and other.y == self.y


def parse_directions(dir_: str):
    """
    Returns delta position based on string representation.

    Valid Inputs:
    * up
    * down
    * left
    * right
    """
    if dir_ == 'UP':
        return Position(0, 1)
    if dir_ == 'DOWN':
        return Position(0, -1)
    if dir_ == 'LEFT':
        return Position(-1, 0)
    if dir_ == 'RIGHT':
        return Position(1, 0)
    return None

