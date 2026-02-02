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
        verbose_name_plural = "Gallery Categories"

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
        ordering = ["title","created_on"]
        verbose_name = "Gallery Media"
        verbose_name_plural = "Gallery Media Items"

    def __str__(self):
        return self.title


class Donor(TimeStampedModel, SoftDeleteModel):
    INDIVIDUAL = "INDIVIDUAL"
    ORGANIZATION = "ORGANIZATION"
    ANONYMOUS = "ANONYMOUS"

    DONOR_TYPE_CHOICES = [
        (INDIVIDUAL, "Individual"),
        (ORGANIZATION, "Organization"),
        (ANONYMOUS, "Anonymous"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fullname = models.CharField(max_length=200)
    email = models.EmailField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    donor_type = models.CharField(max_length=50, choices=DONOR_TYPE_CHOICES, blank=True)

    class Meta:
        db_table = "donors"
        ordering = ["fullname"]
        verbose_name = "Donor"
        verbose_name_plural = "Donors"

    def __str__(self):
        return self.fullname


class Donation(TimeStampedModel):
    CASH = "CASH"
    MOBILE_MONEY = "MOBILE_MONEY"
    BANK_TRANSFER = "BANK_TRANSFER"
    CREDIT_CARD = "CREDIT_CARD"

    PAYMENT_METHOD_CHOICES = [
        (CASH, "Cash"),
        (MOBILE_MONEY, "Mobile Money"),
        (BANK_TRANSFER, "Bank Transfer"),
        (CREDIT_CARD, "Credit Card"),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donor = models.ForeignKey(
        Donor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="donations",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="RWF")
    donation_purpose = models.CharField(max_length=200, blank=True)
    payment_method = models.CharField(
        max_length=50, choices=PAYMENT_METHOD_CHOICES, blank=True
    )
    donation_date = models.DateTimeField(auto_now_add=True)
    receipt_image = models.ImageField(
        upload_to="donations_receipts/", null=True, blank=True
    )
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "donations"
        ordering = ["donation_date"]
        verbose_name = "Donation"
        verbose_name_plural = "Donations"

    def __str__(self):
        donor_name = self.donor.fullname if self.donor else "Anonymous"
        return f"{donor_name} - {self.amount} {self.currency}"
