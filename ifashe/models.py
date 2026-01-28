from django.db import models
from accounts.models import User
import uuid
from accounts.models import TimeStampedModel, SoftDeleteModel


class Family(TimeStampedModel, SoftDeleteModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family_name = models.CharField(max_length=100)
    address = models.TextField()
    province = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    sector = models.CharField(max_length=100, blank=True)
    cell = models.CharField(max_length=100, blank=True)
    village = models.CharField(max_length=100, blank=True)
    family_members = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "families"
        verbose_name = "Family"
        verbose_name_plural = "Families"

    def __str__(self):
        return self.family_name


class Parent(TimeStampedModel, SoftDeleteModel):
    FATHER = "Father"
    MOTHER = "Mother"
    GUARDIAN = "Guardian"

    RELATIONSHIP_CHOICES = [
        (FATHER, "Father"),
        (MOTHER, "Mother"),
        (GUARDIAN, "Guardian"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey(Family, on_delete=models.CASCADE, related_name="parents")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50, choices=RELATIONSHIP_CHOICES)
    phone = models.CharField(max_length=20, blank=True)
    national_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "parents"
        verbose_name = "Parent"
        verbose_name_plural = "Parents"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class SponsoredChild(TimeStampedModel, SoftDeleteModel):
    MALE = "Male"
    FEMALE = "Female"
    GENDER_CHOICES = [
        (MALE, "Male"),
        (FEMALE, "Female"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey(
        Family, on_delete=models.CASCADE, related_name="children"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    school_level = models.CharField(
        max_length=100, blank=True, help_text="Primary, Secondary, etc."
    )
    profile_image = models.ImageField(
        upload_to="sponsored_children_profiles/", blank=True
    )

    class Meta:
        db_table = "sponsored_children"
        verbose_name = "Sponsored Child"
        verbose_name_plural = "Sponsored Children"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Sponsorship(TimeStampedModel):
    ACTIVE = "Active"
    PAUSED = "Paused"
    COMPLETED = "Completed"

    STATUS_CHOICES = [
        (ACTIVE, "Active"),
        (PAUSED, "Paused"),
        (COMPLETED, "Completed"),
    ]

    FULL = "full"
    EDUCATION_ONLY = "education_only"
    RENTING_ONLY = "renting_only"
    DRESSING_ONLY = "dressing_only"

    SPONSORSHIP_TYPE = [
        (FULL, "Full"),
        (EDUCATION_ONLY, "Education only"),
        (RENTING_ONLY, "Renting only"),
        (DRESSING_ONLY, "Dressing only"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(
        SponsoredChild, on_delete=models.CASCADE, related_name="sponsorships"
    )
    sponsorship_type = models.CharField(
        max_length=100, choices=SPONSORSHIP_TYPE, default=FULL
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE)
    pause_reason = models.TextField(blank=True)

    class Meta:
        db_table = "sponsorships"
        verbose_name = "Sponsorship"
        verbose_name_plural = "Sponsorships"

    def __str__(self):
        return f"{self.child} - {self.sponsorship_type}"


class School(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(max_length=255, blank=True)

    class Meta:
        db_table = "schools"
        verbose_name = "School"
        verbose_name_plural = "Schools"

    def __str__(self):
        return self.name


class SchoolSupport(TimeStampedModel):
    PAID = "Paid"
    PENDING = "Pending"
    PARTIAL = "Partial"

    PAYMENT_STATUS_CHOICES = [
        (PAID, "Paid"),
        (PENDING, "Pending"),
        (PARTIAL, "Partial"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(
        SponsoredChild, on_delete=models.CASCADE, related_name="school_support"
    )
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name="supported_children"
    )
    academic_year = models.CharField(max_length=12)
    school_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    materials_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, blank=True
    )
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "school_support"
        verbose_name = "School Support"
        verbose_name_plural = "School Support Records"

    def __str__(self):
        return f"{self.child} - {self.academic_year}"

    @property
    def total_cost(self):
        return self.school_fees + self.materials_cost


class DressingDistribution(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(
        SponsoredChild, on_delete=models.CASCADE, related_name="dressing_distributions"
    )
    distribution_date = models.DateField()
    item_type = models.CharField(
        max_length=100, blank=True, help_text="Shirt, Pants, Shoes, etc."
    )
    size = models.CharField(max_length=20, blank=True)
    quantity = models.IntegerField(default=1)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "dressing_distribution"
        verbose_name = "Dressing Distribution"
        verbose_name_plural = "Dressing Distributions"

    def __str__(self):
        return f"{self.child} - {self.item_type}"


class ParentWorkContract(TimeStampedModel):
    ACTIVE = "Active"
    PAUSED = "Paused"
    TERMINATED = "Terminated"

    STATUS_CHOICES = [
        (ACTIVE, "Active"),
        (PAUSED, "Paused"),
        (TERMINATED, "Terminated"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey(
        Parent, on_delete=models.CASCADE, related_name="work_contracts"
    )
    job_role = models.CharField(max_length=100)
    contract_start_date = models.DateField()
    contract_end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Active")

    class Meta:
        db_table = "parent_work_contracts"
        verbose_name = "Parent Work Contract"
        verbose_name_plural = "Parent Work Contracts"

    def __str__(self):
        return f"{self.parent} - {self.job_role}"


class ParentAttendance(TimeStampedModel):
    PRESENT = "Present"
    ABSENT = "Absent"
    LATE = "Late"
    SICK_LEAVE = "Sick_Leave"

    STATUS_CHOICES = [
        (PRESENT, "Present"),
        (ABSENT, "Absent"),
        (LATE, "Late"),
        (SICK_LEAVE, "Sick Leave"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    work_record = models.ForeignKey(
        ParentWorkContract, on_delete=models.CASCADE, related_name="attendances"
    )
    attendance_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "parent_attendance"
        verbose_name = "Parent Attendance"
        verbose_name_plural = "Parent Attendance Records"

    def __str__(self):
        return f"{self.work_record.parent} - {self.attendance_date}"


class ParentPerformance(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    work_record = models.ForeignKey(
        ParentWorkContract, on_delete=models.CASCADE, related_name="performances"
    )
    evaluation_date = models.DateField()
    rating = models.IntegerField(null=True, blank=True, help_text="1-5 scale")
    comments = models.TextField(blank=True)
    evaluated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evaluated_performances",
    )

    class Meta:
        db_table = "parent_performance"
        verbose_name = "Parent Performance"
        verbose_name_plural = "Parent Performance Records"

    def __str__(self):
        return f"{self.work_record.parent} - {self.evaluation_date}"
