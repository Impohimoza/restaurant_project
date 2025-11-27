from .detector.detector import PersonDetector
from ..data.model import Status, Camera
from ..util.logconf import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


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
        print(person_area)
        
        return round(overlap_area / person_area, 2)
    
    def process_table(self, camera_frame, camera: Camera):
        """Обработка кадра

        Args:
            camera_frame (_type_): кадр с камеры
            camera (Camera): камера
        """
        detection_result = self.detector.detect(camera_frame)
        for tracked_person in detection_result:
            person_box = tracked_person[0]
            
            for table in camera.tables:
                table_box = (table.bbox.x1,
                             table.bbox.y1,
                             table.bbox.x2,
                             table.bbox.y2)
                overlap_percentage = self.get_overlap_percentage(table_box,
                                                                 person_box)
                if overlap_percentage > 0.8:
                    table.status = Status.Await
                else:
                    table.status = Status.Free