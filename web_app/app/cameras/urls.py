from django.urls import path

from . import views, api

urlpatterns = [
    path("cameras/", views.camera_list, name='cameras'),
    path("cameras/<int:camera_id>/edit/", views.edit_zones, name="edit_zones"),
    path("tables/monitor/<int:camera_id>/", views.monitor_camera, name="monitor_camera"),
    path("stream/<int:camera_id>/", views.stream_camera, name="stream_camera"),
    
    path('api/cameras-with-zones/', api.cameras_with_zones, name='api_cameras_with_zones'),
    path('api/arrival/', api.record_arrival, name='api_record_arrival'),
    path('api/session/<int:session_id>/waiter-approach/', api.record_waiter_approach, name='api_waiter_approach'),
    path('api/session/<int:table_id>/bill-closed/', api.record_bill_closed, name='api_bill_closed'),
    path('api/session/<int:session_id>/bill-info/', api.get_bill_info, name='api_bill_info'),
    path('api/session/<int:session_id>/departure/', api.record_departure, name='api_departure'),
    path('api/session/<int:session_id>/cleaning/', api.record_cleaning, name='api_cleaning'),
    path('api/monitor/<int:camera_id>/', api.api_monitor_camera, name='api_monitor_camera'),
]
