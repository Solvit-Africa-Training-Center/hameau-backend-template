from django.db import models
from accounts.models import User
import uuid
from accounts.models import TimeStampedModel, SoftDeleteModel


class GalleryCategory(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=70)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "gallery_categories"
        ordering = ["name"]
        verbose_name = "Gallery Category"
        verbose_name_plural = "Public Modules"

    def __str__(self):
        return self.name


class GalleryMedia(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        GalleryCategory, on_delete=models.CASCADE, related_name="media_items"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    media_url = models.FileField(upload_to="media_gallery/")
    is_public = models.BooleanField(default=True)
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="uploaded_media",
    )

    class Meta:
        db_table = "gallery_media"
        ordering = ["title", "created_on"]
        verbose_name = "Public Modules"
        verbose_name_plural = "Gallery Media Items"

    def __str__(self):
        return self.title


class TeamMember(TimeStampedModel, SoftDeleteModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    job_title = models.CharField(max_length=200)
    image = models.ImageField(upload_to="team_members/")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "team_members"
        ordering = ["name", "created_on"]
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"

    def __str__(self):
        return self.name


class ContactMessage(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=255)
    phone_number = models.CharField(max_length=20)
    message = models.TextField()

    class Meta:
        db_table = "contact_messages"
        ordering = ["-created_on"]
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

    def __str__(self):
        return f"{self.name} ({self.email})"


class SuccessStory(TimeStampedModel, SoftDeleteModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(upload_to="success_stories/")
    title = models.CharField(max_length=255)
    body = models.TextField()
    location = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "success_stories"
        ordering = ["-created_on"]
        verbose_name = "Success Story"
        verbose_name_plural = "Success Stories"

    def __str__(self):
        return self.title
