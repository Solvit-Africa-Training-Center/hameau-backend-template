import uuid

from django.db import models

class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='team/')
    position = models.CharField(max_length=255)
    linkedin_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Team"
        verbose_name_plural = "Teams"
        
    def __str__(self):
        return str(self.full_name)
