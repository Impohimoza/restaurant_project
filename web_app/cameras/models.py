from django.db import models


class Camera(models.Model):
    name = models.CharField(max_length=100)
    stream_url = models.CharField(max_length=500)
    
    def __str__(self):
        return self.name


class TableZone(models.Model):
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE,
                               related_name='zones')
    name = models.CharField(max_length=100)
    
    x1 = models.IntegerField()
    y1 = models.IntegerField()
    x2 = models.IntegerField()
    y2 = models.IntegerField()
    
    def __str__(self):
        return f"{self.name} ({self.camera.name})"