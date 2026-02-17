from django.db import models
import uuid
from accounts.models import TimeStampedModel


class TeamMember(TimeStampedModel):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=200, help_text="Job title or role")
   #bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to=" ", blank=True, null=True)
    order = models.IntegerField(default=0, help_text="Display order on the page")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "team_members"
        ordering = ["order"]
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"