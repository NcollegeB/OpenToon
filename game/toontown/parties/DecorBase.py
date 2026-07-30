# This module provides shared decor behavior and data used by related implementations in party
# scheduling, activities, decorations, and services.

class DecorBase:

    def __init__(self, decorId, x, y, h):
        self.decorId = decorId
        self.x = x
        self.y = y
        self.h = h

    def __str__(self):
        string = 'decorId=%d ' % self.decorId
        string += '(%d,%d,%d) ' % (self.x, self.y, self.h)
        return string

    def __repr__(self):
        return self.__str__()
