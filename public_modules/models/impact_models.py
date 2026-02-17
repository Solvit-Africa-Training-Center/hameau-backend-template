from django.db import models
import uuid
from accounts.models import TimeStampedModel
from .gallery_models import GalleryCategory, GalleryMedia


class ImpactStatistic(TimeStampedModel):
   
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, help_text="e.g., Children Supported")
    value = models.CharField(max_length=100, help_text="e.g., 500+")
    description = models.CharField(max_length=300, blank=True, help_text="")
    order = models.IntegerField(default=0, help_text="Display order on the page")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "impact_statistics"
        ordering = ["order"]
        verbose_name = "Impact Statistic"
        verbose_name_plural = "Impact Statistics"

    def __str__(self):
        return f"{self.title}: {self.value}"


class ContactInfo(TimeStampedModel):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255, help_text="Primary contact email")
    phone = models.CharField(max_length=20, help_text="Primary contact phone number")
    address = models.TextField(help_text="Full address")
    
    is_active = models.BooleanField(default=True, help_text="Display on website")

    class Meta:
        db_table = "contact_info"
        verbose_name = "Contact Information"
        verbose_name_plural = "Contact Information"

    def __str__(self):
        return f"Contact Info - {self.email}"


class ContactMessage(TimeStampedModel):
    """Model for storing contact form submissions from the public site"""
    PENDING = "PENDING"
    VIEWED = "VIEWED"
    RESPONDED = "RESPONDED"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (VIEWED, "Viewed"),
        (RESPONDED, "Responded"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100, help_text="First name of the sender")
    last_name = models.CharField(max_length=100, help_text="Last name of the sender")
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=300, help_text="Reason for contact")
    message = models.TextField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=PENDING
    )
    admin_notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "contact_messages"
        ordering = ["-created_on"]
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.subject}"
    
    @property
    def fullname(self):
        
        return f"{self.first_name} {self.last_name}".strip()
