import cv2

from .table import Table


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