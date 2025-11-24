from django.urls import path

from . import views

urlpatterns = [
    path("cameras/", views.camera_list, name='cameras'),
    path("cameras/<int:camera_id>/edit/", views.edit_zones, name="edit_zones"),
    path("tables/monitor/<int:camera_id>/", views.monitor_camera, name="monitor_camera"),
    path("stream/<int:camera_id>/", views.stream_camera, name="stream_camera"),
    
]
