import math
from time import time

import cv2
import numpy as np

from .util.logconf import logging
from .data.model import Camera, Status
from .core.table_processor import TableProcessor

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

COLOR_DICT = {Status.Free: (0, 255, 0),
              Status.Await: (0, 0, 255)}


class VideoStreamProcessor:
    def __init__(self, cameras_data: list[dict], monitor: bool):
        self.cameras = self._initCameras(cameras_data)
        self.processor = TableProcessor()
        self.monitor = monitor
    
    def _initCameras(self, cameras_data: dict) -> list[Camera]:
        """Инициация камер

        Args:
            cameras_data (dict): Информация о камерах со столами

        Returns:
            list[Camera]: Список инициализированных камер
        """
        cameras_list = []
        for camera in cameras_data:
            cameras_list.append(Camera(
                camera['id'],
                camera['stream_url'],
                camera['zones']
            ))
        
        return cameras_list

    def show_monitor(self, frames: list, fps: float, dsize: tuple):
        """Функция для мониторинга камер

        Args:
            frames (list): Кадры с камер
            dsize (tuple): Resize размер
        """
        cols = math.ceil(math.sqrt(len(frames)))
        rows = math.ceil(len(frames) / cols)
        height, width = dsize
        
        grid = np.zeros((height * rows, width * cols, 3), dtype=np.uint8)
        
        for i, frame in enumerate(frames):
            if frame is not None:
                resize_frame = cv2.resize(frame, (width, height))
            else:
                resize_frame = np.zeros((height, width, 3), dtype=np.uint8)
            row = i // cols
            col = i % cols
            
            start_height = row * height
            end_height = (row + 1) * height
            start_width = col * width
            end_width = (col + 1) * width
            grid[start_height:end_height, start_width:end_width] = resize_frame
        
        cv2.putText(
            grid,
            f'FPS: {int(fps)}',
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (0, 255, 0),
            2)
        
        cv2.imshow('Camera Monitor', grid)
    
    def draw_bounding_boxes(self, frame: np.ndarray, camera: Camera):
        """Отображение столов на камерах

        Args:
            frame (np.ndarray): кадр
            camera (Camera): камера

        Returns:
            np.ndarray: кадр с помеченными столами
        """
        for table in camera.tables:
            cv2.rectangle(
                frame,
                (table.bbox.x1, table.bbox.y1),
                (table.bbox.x2, table.bbox.y2),
                COLOR_DICT[table.status],
                2
            )
        return frame
        
    def run(self):
        """Запуск видеопотока

        Raises:
            Exception: Проверка на работу всех камер
        """
        log.info('Запуск видеопотока ...')
        
        fps_count = []
        fps = 0
        while True:
            start_time = time()
            frames = []
            for camera in self.cameras:
                ret, frame = camera.cap.read()
                if not ret:
                    raise Exception(
                        f'Изображение на камере {camera.id} не доступно')
                self.processor.process_table(frame, camera)
                frame = self.draw_bounding_boxes(frame, camera)
                frames.append(frame)
            
            end_time = time()
            fps_now = 1 / np.round(end_time - start_time, 2)
            fps_count.append(fps_now)
            if len(fps_count) == 30:
                fps = np.mean(fps_count)
                fps_count = []
            
            if self.monitor:
                self.show_monitor(frames, fps, (360, 540))
            
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        for camera in self.cameras:
            camera.cap.release()
        cv2.destroyAllWindows()