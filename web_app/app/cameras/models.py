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


class TableSession(models.Model):
    """
    Сессия обслуживания одного стола
    """
    table = models.ForeignKey('TableZone', on_delete=models.CASCADE,
                              related_name='sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    
    arrival_time = models.DateTimeField(null=True, blank=True)
    
    waiter_first_approach_time = models.DateTimeField(null=True, blank=True)
    
    bill_closed_time = models.DateTimeField(null=True, blank=True)
    
    departure_time = models.DateTimeField(null=True, blank=True)
    
    cleaning_time = models.DateTimeField(null=True, blank=True)
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('served', 'Served'),
        ('closed', 'Closed'),
        ('cleaned', 'Cleaned'),
    ]
    status = models.CharField(max_length=16, choices=STATUS_CHOICES,
                              default='open')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Session #{self.id} table={self.table.name}"
    