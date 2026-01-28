from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone
import uuid


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_on = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_on = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_on"])

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.ADMIN)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    ADMIN = "system_admin"
    RESIDENTIAL_MANAGER = "residential_manager"
    INTERNSHIP_MANAGER = "internship_manager"
    IFASHE_MANAGER = "ifashe_manager"

    ROLE_CHOICES = [
        (ADMIN, "System Admin"),
        (RESIDENTIAL_MANAGER, "Residential Manager"),
        (INTERNSHIP_MANAGER, "Internship Manager"),
        (IFASHE_MANAGER, "Ifashe Manager"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "phone"]

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class VerificationCode(models.Model):
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
    PASSWORD_CHANGE = "password_change"

    PURPOSE_CHOICES = [
        (EMAIL_VERIFICATION, "Email Verification"),
        (PASSWORD_RESET, "Password Reset"),
        (PASSWORD_CHANGE, "Change Password"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="verification_codes"
    )
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES)
    is_used = models.BooleanField(default=False)
    expires_on = models.DateTimeField()
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["code", "purpose"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.purpose} - {self.code}"
