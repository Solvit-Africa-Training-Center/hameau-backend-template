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
