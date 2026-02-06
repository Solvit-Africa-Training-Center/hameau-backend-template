import uuid

from django.db import models

from accounts.models import User
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
        ordering = ["family_name"]
        verbose_name = "Family"
        verbose_name_plural = "Families"

    def __str__(self):
        return self.family_name


class Parent(TimeStampedModel, SoftDeleteModel):
    FATHER = "FATHER"
    MOTHER = "MOTHER"
    GUARDIAN = "GUARDIAN"

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
        ordering = ["first_name", "last_name"]
        verbose_name = "Parent"
        verbose_name_plural = "Parents"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class SponsoredChild(TimeStampedModel, SoftDeleteModel):
    MALE = "MALE"
    FEMALE = "MALE"
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
        ordering = ["first_name", "last_name"]
        verbose_name = "Sponsored Child"
        verbose_name_plural = "Sponsored Children"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Sponsorship(TimeStampedModel):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"

    STATUS_CHOICES = [
        (ACTIVE, "Active"),
        (PAUSED, "Paused"),
        (COMPLETED, "Completed"),
    ]

    FULL = "FULL"
    EDUCATION_ONLY = "EDUCATION_ONLY"
    RENTING_ONLY = "RENTING_ONLY"
    DRESSING_ONLY = "DRESSING_ONLY"

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
        ordering = ["start_date"]
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
        ordering = ["name"]
        verbose_name = "School"
        verbose_name_plural = "Schools"

    def __str__(self):
        return self.name


class SchoolSupport(TimeStampedModel):
    PAID = "PAID"
    PENDING = "PENDING"
    PARTIAL = "PARTIAL"

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
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    TERMINATED = "TERMINATED"

    STATUS_CHOICES = [
        (ACTIVE, "Active"),
        (PAUSED, "Paused"),
        (TERMINATED, "Terminated"),
    ]

    KITCHEN = "KITCHEN"
    CLEANING = "CLEANING"
    FARMING = "FARMING"
    OTHER = "OTHER"

    DEPARTMENT_CHOICES = [
        (KITCHEN, "Kitchen"),
        (CLEANING, "Cleaning"),
        (FARMING, "Farming"),
        (OTHER, "Other"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey(
        Parent, on_delete=models.CASCADE, related_name="work_contracts"
    )
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES, default=OTHER)
    supervisor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supervised_contracts",
        help_text="Supervisor responsible for this parent"
    )
    contract_start_date = models.DateField()
    contract_end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE)

    class Meta:
        db_table = "parent_work_contracts"
        ordering = ["department"]
        verbose_name = "Parent Work Contract"
        verbose_name_plural = "Parent Work Contracts"

    def __str__(self):
        return f"{self.parent} - {self.department}"


class ParentAttendance(TimeStampedModel):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"
    SICK_LEAVE = "SICK_LEAVE"

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
        ordering = ["attendance_date"]
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
        ordering = ["evaluation_date"]
        verbose_name = "Parent Performance"
        verbose_name_plural = "Parent Performance Records"

    def __str__(self):
        return f"{self.work_record.parent} - {self.evaluation_date}"
