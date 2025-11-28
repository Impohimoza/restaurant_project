import time
import os

import asyncio
from dotenv import load_dotenv

from .detector.detector import PersonDetector
from ..data.model import Status, Camera, Table
from ..util.logconf import logging
from ..api.async_client import api_client


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
load_dotenv()

TABLE_TIME_FREE = int(os.getenv('TABLE_TIME_FREE'))


class TableProcessor:
    def __init__(self):
        self.detector = PersonDetector(conf_thresh=0.75)
        self._pending_requests = set()
        self._table_locks = {}
        self._active_sessions = set()
    
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
            if table.id not in self._table_locks:
                self._table_locks[table.id] = asyncio.Lock()
            
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
            
            should_start_session = False
            for time_at_table in table.people_at_the_table.values():
                print(time.time() - time_at_table)
                if time.time() - time_at_table >= TABLE_TIME_FREE:
                    should_start_session = True
                    break  # Достаточно одного человека для смены статуса
            
            if (should_start_session and (table.id not in self._active_sessions)):
                asyncio.create_task(
                    self._start_table_session(table)
                )
            break
    
    async def _start_table_session(self, table: Table):
        """Асинхронная отправка запроса на начало сессии стола

        Args:
            table (Table): Стол для которого начинается сессия
        """
        table_id = table.id
        
        self._active_sessions.add(table_id)
        try:
            async with self._table_locks[table.id]:
                if table.status == Status.Free:
                    print(1)
                    task = asyncio.create_task(
                        api_client.start_table_session(table=table)
                    )
                    
                    self._pending_requests.add(task)
                    
                    try:
                        success = await task
                        if success:
                            log.debug(f"Table {table.id} status changed to Await")
                        else:
                            log.warning(f"Failed to start session for table {table.id}")
                    except Exception as e:
                        log.error(f"Error starting session for table {table.id}: {e}")
        except Exception as e:
            log.error(f"Error starting session for table {table_id}: {e}")
        finally:
            self._pending_requests.discard(task)

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