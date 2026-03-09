import uuid

from django.db import models


class Work(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    icon = models.ImageField(upload_to='work/')
    
    class Meta:
        verbose_name = "Work"
        verbose_name_plural = "Work"
        
    def __str__(self):
        return self.title