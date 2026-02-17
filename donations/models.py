import uuid
from django.db import models
from django.utils import timezone
from accounts.models import TimeStampedModel, SoftDeleteModel

class Donor(TimeStampedModel, SoftDeleteModel):
    """
    Represents an individual or organization that provides financial support.
    Track donor contact information and classification.
    """
    INDIVIDUAL = "INDIVIDUAL"
    ORGANIZATION = "ORGANIZATION"
    ANONYMOUS = "ANONYMOUS"

    DONOR_TYPE_CHOICES = [
        (INDIVIDUAL, "Individual"),
        (ORGANIZATION, "Organization"),
        (ANONYMOUS, "Anonymous"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fullname = models.CharField(max_length=200, help_text="Full name of the donor or organization.")
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True, help_text="Contact email for report delivery.")
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    donor_type = models.CharField(
        max_length=50, choices=DONOR_TYPE_CHOICES, default=INDIVIDUAL
    )

    class Meta:
        db_table = "donors"
        ordering = ["fullname"]
        verbose_name = "Donor"
        verbose_name_plural = "Donors"

    def __str__(self):
        return self.fullname


class Donation(TimeStampedModel):
    """
    Stores record of financial contributions. Supports three types: General, 
    Residential Child, and Ifashe Family. Handles both one-time and periodic payments.
    """
    GENERAL = "GENERAL"
    RESIDENTIAL_CHILD = "RESIDENTIAL_CHILD"
    IFASHE_FAMILY = "IFASHE_FAMILY"

    DONATION_TYPE_CHOICES = [
        (GENERAL, "General Donation"),
        (RESIDENTIAL_CHILD, "Donation to Residential Child"),
        (IFASHE_FAMILY, "Donation to Ifashe-Tugufashe Family"),
    ]

    CASH = "CASH"
    MOBILE_MONEY = "MOBILE_MONEY"
    BANK_TRANSFER = "BANK_TRANSFER"
    CREDIT_CARD = "CREDIT_CARD"
    IREMBOPAY = "IREMBOPAY"

    PAYMENT_METHOD_CHOICES = [
        (CASH, "Cash"),
        (MOBILE_MONEY, "Mobile Money"),
        (BANK_TRANSFER, "Bank Transfer"),
        (CREDIT_CARD, "Credit Card"),
        (IREMBOPAY, "IremboPay"),
    ]

    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"
    RECURRING_INTERVAL_CHOICES = [
        (MONTHLY, "Monthly"),
        (YEARLY, "Yearly"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donor = models.ForeignKey(
        Donor, on_delete=models.SET_NULL, null=True, blank=True, related_name="donations"
    )
    donation_type = models.CharField(
        max_length=50, choices=DONATION_TYPE_CHOICES, default=GENERAL,
        help_text="Determines if the donation is general or restricted to a child/family."
    )
    
    # Links for specific donation types
    child = models.ForeignKey(
        "programs.Child",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="donations",
        help_text="Required if donation_type is RESIDENTIAL_CHILD."
    )
    family = models.ForeignKey(
        "programs.Family",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="donations",
        help_text="Required if donation_type is IFASHE_FAMILY."
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="RWF")
    donation_purpose = models.CharField(max_length=200, blank=True, help_text="e.g., School supplies, Medical assist.")
    payment_method = models.CharField(
        max_length=50, choices=PAYMENT_METHOD_CHOICES, default=CASH
    )
    
    # Periodic payments
    is_recurring = models.BooleanField(default=False, help_text="Set for automatic secured deduction.")
    recurring_interval = models.CharField(
        max_length=20, choices=RECURRING_INTERVAL_CHOICES, null=True, blank=True,
        help_text="Frequency of the recurring donation."
    )
    next_deduction_date = models.DateField(null=True, blank=True, help_text="System-calculated date for the next payment.")
    
    donation_date = models.DateTimeField(default=timezone.now)
    receipt_image = models.ImageField(upload_to="donations_receipts/", blank=True, null=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "donations"
        ordering = ["-donation_date"]
        verbose_name = "Donation"
        verbose_name_plural = "Donations"

    def __str__(self):
        donor_name = self.donor.fullname if self.donor else "Anonymous"
        return f"{donor_name} - {self.amount} {self.currency} ({self.donation_type})"


class SponsorEmailLog(TimeStampedModel):
    """
    Log of monthly progress reports sent to donors.
    Prevents duplicate emails and tracks delivery status.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donor = models.ForeignKey(
        Donor, on_delete=models.CASCADE, related_name="email_logs"
    )
    child = models.ForeignKey(
        "programs.Child", on_delete=models.CASCADE, related_name="donor_email_logs"
    )
    sent_at = models.DateTimeField(default=timezone.now)
    month = models.IntegerField(help_text="Report month (1-12).")
    year = models.IntegerField(help_text="Report year.")
    status = models.CharField(max_length=20, default="SUCCESS")
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "donor_email_logs"
        ordering = ["-sent_at"]
        verbose_name = "Donor Email Log"
        verbose_name_plural = "Donor Email Logs"

    def __str__(self):
        return f"{self.donor.fullname} - {self.child.full_name} - {self.month}/{self.year}"

class ChildMonthlySummary(TimeStampedModel):
    """
    AI-generated text summary of a child's progress for a specific month.
    Used to cache OpenAI API results for inclusion in sponsor emails.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(
        "programs.Child", on_delete=models.CASCADE, related_name="monthly_summaries"
    )
    month = models.IntegerField()
    year = models.IntegerField()
    summary_text = models.TextField()

    class Meta:
        db_table = "child_monthly_summaries"
        unique_together = ("child", "month", "year")
        verbose_name = "Child Monthly Summary"
        verbose_name_plural = "Child Monthly Summaries"

    def __str__(self):
        return f"{self.child.full_name} - {self.month}/{self.year}"
