import os

import numpy as np
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
import cv2


class PersonDetector:
    def __init__(self,
                 conf_thresh=0.5,
                 max_age=50,
                 n_init=3,
                 max_cosine_distance=0.2):
        self.model = YOLO(os.getenv('YOLO_DETECTOR_PATH'))
        self.tracker = DeepSort(
            max_age=max_age,
            n_init=n_init,
            max_cosine_distance=max_cosine_distance,
            nms_max_overlap=0.8
        )
        self.conf_thresh = conf_thresh
    
    def get_results(self, results: list, frame):
        """Функция для обработки ответа модели

        Args:
            results (list): результат работы модели
            frame (np.ndarray): кадр

        Returns:
            _type_: bounding boxes людей в кадре
        """
        detection_list = []
        # for result in results[0]:
        #     class_id = result.boxes.cls.cpu().numpy().astype(int)
        #     if class_id == 0:
        #         bbox = result.boxes.xyxy.cpu().numpy()
        #         merged_detection = (
        #             bbox[0][0],
        #             bbox[0][1],
        #             bbox[0][2],
        #             bbox[0][3],)
        #         detection_list.append(merged_detection)
        # return detection_list
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                conf = box.conf[0].cpu().numpy()
                cls = int(box.cls[0].cpu().numpy())
                
                detection_list.append(([x1, y1, x2, y2], conf, cls))
        
        tracks = self.tracker.update_tracks(detection_list, frame=frame)
        
        tracked_list = []
        for i, track in enumerate(tracks):
            if not track.is_confirmed():
                continue
            
            track_id = track.track_id
            x1, y1, x2, y2 = detection_list[i][0]
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            
            tracked_list.append(([x1, y1, x2, y2], track_id))
        return tracked_list
    
    def detect(self, frame: np.ndarray):
        """Функция для инференса модели

        Args:
            frame (np.ndarray): кадр

        Returns:
            _type_: bounding boxes людей в кадре
        """
        results = self.model.predict(frame,
                                     conf=self.conf_thresh,
                                     verbose=False,
                                     classes=[0])
        
        tracked_list = self.get_results(results, frame)
        return tracked_list
        