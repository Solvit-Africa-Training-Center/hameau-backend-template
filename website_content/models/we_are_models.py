import uuid

from django.db import models


class WeAre(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()


    class Meta:
        verbose_name = "We Are"
        verbose_name_plural = "We Are"
        
    def __str__(self):
        return str(self.title)
    
