import time
import os

from .detector.detector import PersonDetector
from ..data.model import Status, Camera, Table
from ..util.logconf import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

TABLE_TIME_FREE = int(os.getenv('TABLE_TIME_FREE'))


class TableProcessor:
    def __init__(self):
        self.detector = PersonDetector(conf_thresh=0.75)
    
    def get_overlap_percentage(self, bbox1, bbox2) -> float:
        """Получения процента перекрытия боксов

        Args:
            bbox1 (_type_): бокс 1
            bbox2 (_type_): бокс 2

        Returns:
            float: доля перекрытия
        """
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        x_overlap = max(0, min(x2_1, x2_2) - max(x1_1, x1_2))
        
        y_overlap = max(0, min(y2_1, y2_2) - max(y1_1, y1_2))
        
        overlap_area = x_overlap * y_overlap
        
        person_area = (x2_2 - x1_2) * (y2_2 - y1_2)
        
        return round(overlap_area / person_area, 2)
    
    def work_with_free_table(self, tables: list[Table], persons: list):
        """Функция для работы со свободными столами

        Args:
            tables (list[Table]): Список столов
            persons (list): Список людей на кадре
        """
        for table in tables:
            table_box = (table.bbox.x1,
                         table.bbox.y1,
                         table.bbox.x2,
                         table.bbox.y2)
            person_at_table = set()
            for person in persons:
                person_box = person[0]
                overlap_percentage = self.get_overlap_percentage(table_box,
                                                                 person_box)
                if overlap_percentage > 0.7:
                    person_at_table.add(person[1])
                    table.people_at_the_table[person[1]] = \
                        table.people_at_the_table.get(person[1], time.time())
            
            table.people_at_the_table = \
                {k: v for k, v in table.people_at_the_table.items()
                 if (k in person_at_table) or (time.time() - v < 10)}
            
            for time_at_table in table.people_at_the_table.values():
                print(time.time() - time_at_table)
                if time.time() - time_at_table >= TABLE_TIME_FREE:
                    table.status = Status.Await
                        
    def process_table(self, camera_frame, camera: Camera):
        """Обработка кадра

        Args:
            camera_frame (_type_): кадр с камеры
            camera (Camera): камера
        """
        detection_result = self.detector.detect(camera_frame)
        
        free_table = []
        for table in camera.tables:
            if table.status == Status.Free:
                free_table.append(table)
        
        self.work_with_free_table(free_table, detection_result)