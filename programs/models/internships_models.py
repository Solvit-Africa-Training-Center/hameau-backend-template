import uuid

from django.db import models

from accounts.models import User
from accounts.models import TimeStampedModel, SoftDeleteModel


class InternshipApplication(TimeStampedModel):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
        (REJECTED, "Rejected"),
        (COMPLETED, "Completed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=50)
    phone = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    nationality = models.CharField(max_length=30)
    is_in_rwanda = models.BooleanField(default=False)
    school_university = models.CharField(max_length=200)
    field_of_study = models.CharField(max_length=200)
    cv_url = models.FileField(upload_to="applications_cvs/", null=True, blank=True)
    motivation_letter = models.FileField(upload_to="applications_letters/", blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    admin_notes = models.TextField(blank=True)
    applied_on = models.DateTimeField(auto_now_add=True)
    reviewed_on = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_applications",
    )

    class Meta:
        db_table = "internship_applications"
        ordering = ["applied_on"]
        verbose_name = "Internship Application"
        verbose_name_plural = "Internship Applications"

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.status}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Department(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "departments"
        ordering = ["name"]
        verbose_name = "Department"
        verbose_name_plural = "Departments"

    def __str__(self):
        return self.name


class Supervisor(TimeStampedModel, SoftDeleteModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=20, blank=True)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="supervisors"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "supervisors"
        ordering = ["first_name"]
        verbose_name = "Supervisor"
        verbose_name_plural = "Supervisors"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class InternshipProgram(TimeStampedModel):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    TERMINATED = "TERMINATED"

    STATUS_CHOICES = [
        (ACTIVE, "Active"),
        (COMPLETED, "Completed"),
        (TERMINATED, "Terminated"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.OneToOneField(
        InternshipApplication,
        on_delete=models.CASCADE,
        related_name="internship_program",
    )
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="internship_programs"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, blank=True)

    class Meta:
        db_table = "internship_program"
        verbose_name = "Internship Program"
        verbose_name_plural = "Internship Programs"

    def __str__(self):
        return f"{self.application.full_name} - {self.department.name}"


class InternshipFeedback(models.Model):
    INTERN = "INTERN"
    SUPERVISOR = "SUPERVISOR"
    FINAL = "FINAL"

    FEEDBACK_TYPE_CHOICES = [
        (INTERN, "Intern"),
        (SUPERVISOR, "Supervisor"),
        (FINAL, "Final"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    internship = models.ForeignKey(
        InternshipProgram, on_delete=models.CASCADE, related_name="feedbacks"
    )
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE_CHOICES)
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submitted_feedbacks",
    )
    rating = models.IntegerField(null=True, blank=True, help_text="1-5 scale")
    comments = models.TextField(blank=True)
    submitted_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "internship_feedback"
        ordering = ["submitted_on"]
        verbose_name = "Internship Feedback"
        verbose_name_plural = "Internship Feedbacks"

    def __str__(self):
        return f"{self.internship} - {self.feedback_type}"
