import base64
import json

import cv2
from django.shortcuts import render, get_object_or_404, redirect
from django.http import StreamingHttpResponse

from .models import Camera, TableZone


CAMERA_DEFAULT_WIDTH = 1920
CAMERA_DEFAULT_HEIGHT = 1080

VIDEO_W = 1080
VIDEO_H = 720
CAMERA_W = CAMERA_DEFAULT_WIDTH
CAMERA_H = CAMERA_DEFAULT_HEIGHT


def camera_list(request):
    cameras = Camera.objects.all()
    return render(request, "camera_list.html", {"cameras": cameras})


def edit_zones(request, camera_id):
    camera = get_object_or_404(Camera, id=camera_id)

    if request.method == "POST":
        TableZone.objects.create(
            camera=camera,
            name=request.POST["name"],
            x1=request.POST["x1"],
            y1=request.POST["y1"],
            x2=request.POST["x2"],
            y2=request.POST["y2"],
        )
        return redirect("cameras") 

    cap = cv2.VideoCapture(camera.stream_url)
    ret, frame = cap.read()
    cap.release()

    _, jpeg = cv2.imencode('.jpg', frame)
    frame_base64 = base64.b64encode(jpeg).decode()

    tables = TableZone.objects.filter(camera=camera)
    tables_json = json.dumps([
        {"name": t.name, "x1": t.x1, "y1": t.y1, "x2": t.x2, "y2": t.y2}
        for t in tables
    ])
    return render(request, "edit_zones.html", {
        "camera": camera,
        "frame": frame_base64,
        "tables_json": tables_json
    })


def stream_camera(request, camera_id):
    cam = get_object_or_404(Camera, id=camera_id)
    cap = cv2.VideoCapture(cam.stream_url)

    def generate():
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            _, jpeg = cv2.imencode('.jpg', frame)
            frame_bytes = jpeg.tobytes()
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" +
                   frame_bytes + b"\r\n")

    return StreamingHttpResponse(
        generate(),
        content_type="multipart/x-mixed-replace; boundary=frame"
    )


def monitor_camera(request, camera_id):
    camera = get_object_or_404(Camera, id=camera_id)
    tables = TableZone.objects.filter(camera=camera)

    # Масштаб относительно оригинального разрешения камеры
    scale_x = VIDEO_W / CAMERA_W
    scale_y = VIDEO_H / CAMERA_H

    tables_data = []
    for t in tables:
        tables_data.append({
            "name": t.name,
            "x1_scaled": int(t.x1 * scale_x),
            "y1_scaled": int(t.y1 * scale_y),
            "width_scaled": int((t.x2 - t.x1) * scale_x),
            "height_scaled": int((t.y2 - t.y1) * scale_y),
        })

    return render(request, "monitor.html", {
        "camera": camera,
        "tables": tables_data,
    })
