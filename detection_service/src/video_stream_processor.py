import math

import cv2
import numpy as np

from .models.camera import Camera
from .util.logconf import logging

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class VideoStreamProcessor:
    def __init__(self, cameras_data: list[dict], debug: bool):
        self.cameras = self._initCameras(cameras_data)
        self.debug = debug
    
    def _initCameras(self, cameras_data) -> list[Camera]:
        cameras_list = []
        for camera in cameras_data:
            cameras_list.append(Camera(
                camera['id'],
                camera['stream_url'],
                camera['zones']
            ))
        
        return cameras_list

    def show_monitor(self, frames: list, dsize: tuple):
        cols = math.ceil(math.sqrt(len(frames)))
        rows = math.ceil(len(frames) / cols)
        height, width = dsize
        
        grid = np.zeros((height * rows, width * cols, 3), dtype=np.uint8)
        
        for i, frame in enumerate(frames):
            resize_frame = cv2.resize(frame, (width, height))
            row = i // cols
            col = i % cols
            
            start_height = row * height
            end_height = (row + 1) * height
            start_width = col * width
            end_width = (col + 1) * width
            grid[start_height:end_height, start_width:end_width] = resize_frame
        
        cv2.imshow('Camera Monitor', grid)
        
    def run(self):
        log.info('Запуск видеопотока ...')
        
        while True:
            frames = []
            for camera in self.cameras:
                ret, frame = camera.cap.read()
                if not ret:
                    break
                frames.append(frame)
            
            if self.debug:
                self.show_monitor(frames, (320, 540))
            
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        for camera in self.cameras:
            camera.cap.release()
        cv2.destroyAllWindows()