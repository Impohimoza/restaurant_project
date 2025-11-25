from rest_framework import serializers
from .models import TableZone, Camera, TableSession


class TableZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableZone
        fields = ['id', 'name', 'x1', 'y1', 'x2', 'y2']


class CameraWithZonesSerializer(serializers.ModelSerializer):
    zones = TableZoneSerializer(many=True)
    
    class Meta:
        model = Camera
        fields = ['id', 'name', 'stream_url', 'zones']


class TableSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableSession
        fields = [
            'id', 'table', 'arrival_time',
            'waiter_first_approach_time', 'bill_closed_time',
            'departure_time', 'cleaning_time',
            'status', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']