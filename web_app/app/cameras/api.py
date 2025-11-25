from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from .models import Camera, TableZone, TableSession
from .serializers import CameraWithZonesSerializer, TableSessionSerializer


# Получение всех камер с зонами столов
@api_view(['GET'])
def cameras_with_zones(request):
    cameras = Camera.objects.prefetch_related('zones').all()
    serializer = CameraWithZonesSerializer(cameras, many=True,
                                           context={'request': request})
    return Response(serializer.data)


# Запись прихода посетителя
@api_view(['POST'])
def record_arrival(request):
    """
    POST data: {"table_id": 1, "arrival_time": "2025-11-25T12:34:56Z"}
    arrival_time optional -> now used
    """
    table_id = request.data.get('table_id')
    
    table = get_object_or_404(TableZone, id=table_id)
    
    arrival_time = request.data.get('arrival_time')
    if arrival_time:
        arrival_time = parse_datetime(arrival_time)
    else:
        arrival_time = timezone.now()
    
    session = TableSession.objects.create(
        table=table,
        arrival_time=arrival_time,
        status='open'
    )
    serializer = TableSessionSerializer(session)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# Запись времени первичного подхода официанта
@api_view(['POST'])
def record_waiter_approach(request, session_id=None):
    """
    POST to /api/session/<id>/waiter_approach/ or with {"session_id":..}
    body may contain 'waiter_first_approach_time'
    """
    
    sid = session_id or request.data.get('session_id')
    session = get_object_or_404(TableSession, id=sid)
    
    t = request.data.get('waiter_first_approach_time')
    if t:
        t = parse_datetime(t)
    else:
        t = timezone.now()
    
    session.waiter_first_approach_time = t
    if session.status == 'open':
        session.status = 'served'
    session.save()
    
    serializer = TableSessionSerializer(session)
    return Response(serializer.data)


# Запись закрытия счета
@api_view(['POST'])
def record_bill_closed(request, table_id=None):
    """
    body:
    {
        "table_id": 1,
        "bill_closed_time": "...",
    }
    """
    tid = table_id or request.data.get('table_id')
    if not tid:
        return Response({"error": "table_id is required"}, status=400)
    
    session = TableSession.objects.filter(
        table_id=tid,
        status__in=["open", "served"]
    ).order_by("-created_at").first()
    
    if not session:
        return Response({"error": "Active session not found for this table"},
                        status=404)
    
    t = request.data.get('bill_closed_time')
    if t:
        t = parse_datetime(t)
    else:
        t = timezone.now()
    
    session.status = 'closed'
    session.save()

    serializer = TableSessionSerializer(session)
    return Response(serializer.data)


# Получение информации о счете
@api_view(['GET'])
def get_bill_info(request, session_id):
    session = get_object_or_404(TableSession, id=session_id)
    return Response({
        "session_id": session.id,
        "bill_closed_time": session.bill_closed_time,
        "status": session.status
    })


# Запись ухода посетителя
@api_view(['POST'])
def record_departure(request, session_id=None):
    sid = session_id or request.data.get('session_id')
    session = get_object_or_404(TableSession, id=sid)
    
    t = request.data.get('departure_time')
    if t:
        from django.utils.dateparse import parse_datetime
        t = parse_datetime(t)
    else:
        t = timezone.now()
        
    session.departure_time = t
    if session.status != 'closed':
        session.status = 'closed'
    session.save()
    
    serializer = TableSessionSerializer(session)
    return Response(serializer.data)


# Запись времени уборки стола
@api_view(['POST'])
def record_cleaning(request, session_id=None):
    sid = session_id or request.data.get('session_id')
    session = get_object_or_404(TableSession, id=sid)
    
    t = request.data.get('cleaning_time')
    if t:
        from django.utils.dateparse import parse_datetime
        t = parse_datetime(t)
    else:
        t = timezone.now()

    session.cleaning_time = t
    session.status = 'cleaned'
    session.save()
    
    serializer = TableSessionSerializer(session)
    return Response(serializer.data)


@api_view(["GET"])
def api_monitor_camera(request, camera_id):
    camera = get_object_or_404(Camera, id=camera_id)
    tables = TableZone.objects.filter(camera=camera)

    now = timezone.now()
    data = []

    for t in tables:
        session = (
            TableSession.objects
            .filter(table=t, status__in=["open", "served", "closed"])
            .order_by("-created_at")
            .first()
        )

        status = session.status if session else "free"

        wait_first = None
        wait_clean = None

        if session:
            if session.status == "open" and not session.waiter_first_approach_time:
                wait_first = (now - session.arrival_time).seconds

            if session.status == "closed" and not session.cleaning_time:
                wait_clean = (
                    (now - session.departure_time).seconds
                    if session.departure_time else None
                )

        data.append({
            "id": t.id,
            "name": t.name,

            # координаты
            "x1": t.x1,
            "y1": t.y1,
            "width": t.x2 - t.x1,
            "height": t.y2 - t.y1,

            # сессии
            "status": status,
            "arrival_time": session.arrival_time.strftime("%H:%M") if session else None,
            "bill_closed_time": session.bill_closed_time.strftime("%H:%M") if session and session.bill_closed_time else None,
            "wait_first": wait_first,
            "wait_clean": wait_clean,
        })

    return Response({"tables": data})
