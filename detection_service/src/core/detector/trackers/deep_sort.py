from deep_sort_realtime.deepsort_tracker import DeepSort


class Tracker:
    tracker = None
    tracks = None

    def __init__(self):
        self.tracker = DeepSort(
            max_age=100,
            n_init=8,
            max_iou_distance=0.3,
            max_cosine_distance=0.4,
            nms_max_overlap=1.0,
            nn_budget=100,
            embedder="mobilenet",
            half=True,
            bgr=True,
            embedder_gpu=True,
            embedder_model_name=None,
            embedder_wts=None,
            polygon=False,
            today=None
        )
        
        self.tracks = []

    def update(self, frame, detections):
        """
        Обновление трекера с новыми детекциями
        
        Args:
            frame: кадр изображения (numpy array)
            detections: список детекций в формате [[x1, y1, x2, y2, score],...]
        """
        
        if len(detections) == 0:
            # Если детекций нет, просто обновляем треки
            self.tracks = []
            return

        # Конвертируем детекции в формат для DeepSort
        detections_for_tracker = []
        for det in detections:
            bbox = det[:4]
            confidence = det[4]
            detections_for_tracker.append((bbox, confidence, "object"))
        
        # Обновляем трекер
        tracks = self.tracker.update_tracks(detections_for_tracker,
                                            frame=frame)
        
        # Обновляем наши треки
        self.update_tracks(tracks, bbox)

    def update_tracks(self, tracks, detections):
        """
        Обновление внутреннего списка треков
        
        Args:
            tracks: список треков из DeepSort
        """
        updated_tracks = []
        
        for i, track in enumerate(tracks):
            if not track.is_confirmed():
                continue
                
            track_id = track.track_id
            
            bbox = map(int, track.to_tlbr())
            
            updated_tracks.append(Track(track_id, bbox))
        
        self.tracks = updated_tracks


class Track:
    def __init__(self, track_id, bbox):
        """
        Класс для представления трека
        
        Args:
            track_id: идентификатор трека
            bbox: bounding box в формате [x1, y1, x2, y2]
        """
        self.track_id = track_id
        self.bbox = bbox