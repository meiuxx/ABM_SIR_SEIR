from enum import Enum

"""file to avoid circular import"""

class State(Enum):
    SUSCEPTIBLE = 0
    INFECTED = 1
    RECOVERED = 2
    DEAD = 3
    EXPOSED = 4