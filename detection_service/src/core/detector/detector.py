import os

from ultralytics import YOLO
import numpy as np


class PersonDetector:
    def __init__(self, conf_thresh=0.5):
        self.model = YOLO(os.getenv('YOLO_DETECTOR_PATH'))
        self.conf_thresh = conf_thresh
    
    def get_results(self, results: list):
        """Функция для обработки ответа модели

        Args:
            results (list): результат работы модели

        Returns:
            _type_: bounding boxes людей в кадре
        """
        detection_list = []
        for result in results[0]:
            class_id = result.boxes.cls.cpu().numpy().astype(int)
            if class_id == 0:
                bbox = result.boxes.xyxy.cpu().numpy()
                merged_detection = (
                    bbox[0][0],
                    bbox[0][1],
                    bbox[0][2],
                    bbox[0][3],)
                detection_list.append(merged_detection)
        return detection_list
    
    def detect(self, frame: np.ndarray):
        """Функция для инференса модели

        Args:
            frame (np.ndarray): кадр

        Returns:
            _type_: bounding boxes людей в кадре
        """
        results = self.model.predict(frame,
                                     conf=self.conf_thresh,
                                     verbose=False)
        
        detections_list = self.get_results(results)
        return detections_list
        