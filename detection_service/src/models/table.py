from collections import namedtuple
from enum import Enum


BboxCord = namedtuple('BboxCord', 'x1, y1, x2, y2')
Status = Enum('Status', [('Free', 0)])


class Table:
    def __init__(self, table_id: int, x1: int, y1: int, x2: int, y2: int):
        self.id = table_id
        self.bbox = BboxCord(x1, y1, x2, y2)
        self.status = Status.Free