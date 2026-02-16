import uuid
from django.db import models
from django.utils import timezone
from accounts.models import TimeStampedModel, SoftDeleteModel
from programs.models.residentials_models import Child

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
    email = models.EmailField(max_length=255, unique=True, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    donor_type = models.CharField(max_length=50, choices=DONOR_TYPE_CHOICES, default=INDIVIDUAL)

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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donor = models.ForeignKey(
        Donor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="donations",
    )
    child = models.ForeignKey(
        Child,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="donations",
        help_text="The child this donation is specifically for (if any)."
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="RWF")
    donation_purpose = models.CharField(max_length=200, blank=True)
    payment_method = models.CharField(
        max_length=50, choices=PAYMENT_METHOD_CHOICES, default=CASH
    )
    donation_date = models.DateTimeField(default=timezone.now)
    receipt_image = models.ImageField(
        upload_to="donations_receipts/", null=True, blank=True
    )
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "donations"
        ordering = ["-donation_date"]
        verbose_name = "Donation"
        verbose_name_plural = "Donations"

    def __str__(self):
        donor_name = self.donor.fullname if self.donor else "Anonymous"
        return f"{donor_name} - {self.amount} {self.currency}"


class SponsorEmailLog(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donor = models.ForeignKey(
        Donor, on_delete=models.CASCADE, related_name="email_logs"
    )
    child = models.ForeignKey(
        Child, on_delete=models.CASCADE, related_name="donor_email_logs"
    )
    sent_at = models.DateTimeField(default=timezone.now)
    month = models.IntegerField()
    year = models.IntegerField()
    status = models.CharField(max_length=20, default="SUCCESS")
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "donor_email_logs"
        ordering = ["-sent_at"]
        verbose_name = "Donor Email Log"
        verbose_name_plural = "Donor Email Logs"

    def __str__(self):
        return f"Email to {self.donor} for {self.child} - {self.month}/{self.year}"


class ChildMonthlySummary(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(
        Child, on_delete=models.CASCADE, related_name="monthly_summaries"
    )
    month = models.IntegerField()
    year = models.IntegerField()
    summary_text = models.TextField()

    class Meta:
        db_table = "child_monthly_summaries"
        unique_together = ["child", "month", "year"]
        verbose_name = "Child Monthly Summary"
        verbose_name_plural = "Child Monthly Summaries"

    def __str__(self):
        return f"Summary for {self.child} - {self.month}/{self.year}"
