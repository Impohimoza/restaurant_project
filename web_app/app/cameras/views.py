import base64
import json

import cv2
from django.shortcuts import render, get_object_or_404, redirect
from django.http import StreamingHttpResponse, JsonResponse
from django.utils import timezone

from .models import Camera, TableZone, TableSession


CAMERA_DEFAULT_WIDTH = 1080
CAMERA_DEFAULT_HEIGHT = 720


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
                   b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

    return StreamingHttpResponse(
        generate(),
        content_type="multipart/x-mixed-replace; boundary=frame"
    )


def monitor_camera(request, camera_id):
    camera = get_object_or_404(Camera, id=camera_id)
    tables = TableZone.objects.filter(camera=camera)

    tables_data = []

    for t in tables:
        # --- активная сессия стола ---
        session = (
            TableSession.objects
            .filter(table=t, status__in=["open", "served", "closed"])
            .order_by("-created_at")
            .first()
        )

        status = session.status if session else "free"

        # --- вычисления времени ---
        now = timezone.now()

        wait_first = None
        wait_clean = None

        if session:
            # ожидает первичного подхода официанта
            if session.status == "open" and not session.waiter_first_approach_time:
                wait_first = (now - session.arrival_time).seconds

            # ожидает уборку стола
            if session.status == "closed" and not session.cleaning_time:
                wait_clean = (now - session.departure_time).seconds if session.departure_time else None

        tables_data.append({
            "name": t.name,

            # координаты
            "x1_scaled": int(t.x1),
            "y1_scaled": int(t.y1),
            "width_scaled": int(t.x2 - t.x1),
            "height_scaled": int(t.y2 - t.y1),

            # данные сессии
            "status": status,
            "session": session,
            "wait_first": wait_first,
            "wait_clean": wait_clean,
        })

    return render(request, "monitor.html", {
        "camera": camera,
        "tables": tables_data,
    })
