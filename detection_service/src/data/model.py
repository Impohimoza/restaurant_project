from collections import namedtuple
from enum import Enum

import cv2

BboxCord = namedtuple('BboxCord', 'x1, y1, x2, y2')
Status = Enum('Status', [('Free', 0), ('Await', 1)])


class Table:
    def __init__(self, table_id: int, x1: int, y1: int, x2: int, y2: int):
        self.id = table_id
        self.people_at_the_table = dict()
        self.bbox = BboxCord(x1, y1, x2, y2)
        self.status = Status.Free
    
    def set_status_free(self):
        self.status = Status.Free
    
    def set_status_await(self):
        if self.status == Status.Free:
            self.status = Status.Await


class Camera:
    def __init__(self, camera_id: int, stream_url: str, zones: list):
        self.id = camera_id
        self.cap = cv2.VideoCapture(stream_url)
        
        self.tables = self._initTables(zones)
    
    def _initTables(self, zones: list) -> list[Table]:
        tables_list = []
        for zone in zones:
            tables_list.append(Table(
                zone['id'],
                zone['x1'],
                zone['y1'],
                zone['x2'],
                zone['y2'],
            ))
        return tables_list