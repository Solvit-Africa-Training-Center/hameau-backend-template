from rest_framework.test import APITestCase
from django.utils import timezone
from django.db import IntegrityError
from datetime import timedelta
import uuid

from accounts.models import (
    User,
    VerificationCode,
)


class UserManagerTests(APITestCase):
    def test_create_user_with_email_success(self):
        user = User.objects.create_user(
            email="test@example.com",
            password="password123",
            first_name="Test",
            last_name="User",
            phone="123456789",
            role=User.ADMIN,
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("password123"))

    def test_create_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email="",
                password="password123",
                role=User.ADMIN,
            )

    def test_create_superuser_sets_flags(self):
        admin = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpass",
            first_name="Admin",
            last_name="User",
            phone="999",
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertEqual(admin.role, User.ADMIN)


# User Model Tests
class UserModelTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="john@example.com",
            password="secret123",
            first_name="John",
            last_name="Doe",
            phone="123456",
            role=User.RESIDENTIAL_MANAGER,
        )

    def test_user_uuid_is_generated(self):
        self.assertIsInstance(self.user.id, uuid.UUID)

    def test_email_is_unique(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email="john@example.com",
                password="anotherpass",
                first_name="Jane",
                last_name="Doe",
                phone="555",
                role=User.ADMIN,
            )

    def test_user_is_active_by_default(self):
        self.assertTrue(self.user.is_active)

    def test_user_is_not_staff_by_default(self):
        self.assertFalse(self.user.is_staff)

    def test_user_str_representation(self):
        expected = "John Doe (john@example.com)"
        self.assertEqual(str(self.user), expected)

    def test_full_name_property(self):
        self.assertEqual(self.user.full_name, "John Doe")

    def test_full_name_handles_missing_names(self):
        user = User.objects.create_user(
            email="noname@example.com",
            password="pass",
            first_name="",
            last_name="",
            phone="000",
            role=User.ADMIN,
        )
        self.assertEqual(user.full_name, "")

    def test_created_on_is_set(self):
        self.assertIsNotNone(self.user.created_on)

    def test_updated_on_is_set(self):
        self.assertIsNotNone(self.user.updated_on)

    def test_updated_on_changes_on_save(self):
        old_updated_on = self.user.updated_on
        self.user.first_name = "Johnny"
        self.user.save()
        self.user.refresh_from_db()
        self.assertNotEqual(old_updated_on, self.user.updated_on)


# VerificationCode Model Tests
class VerificationCodeModelTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="verify@example.com",
            password="password",
            first_name="Verify",
            last_name="User",
            phone="111",
            role=User.ADMIN,
        )
        self.code = VerificationCode.objects.create(
            user=self.user,
            code="123456",
            purpose=VerificationCode.EMAIL_VERIFICATION,
            expires_on=timezone.now() + timedelta(minutes=10),
        )

    def test_verification_code_uuid_generated(self):
        self.assertIsInstance(self.code.id, uuid.UUID)

    def test_verification_code_default_is_used_false(self):
        self.assertFalse(self.code.is_used)

    def test_verification_code_has_user_relation(self):
        self.assertEqual(self.code.user, self.user)

    def test_verification_code_str_representation(self):
        expected = f"{self.user.email} - {self.code.purpose} - {self.code.code}"
        self.assertEqual(str(self.code), expected)

    def test_verification_code_expiry_in_future(self):
        self.assertGreater(self.code.expires_on, timezone.now())

    def test_user_can_have_multiple_verification_codes(self):
        VerificationCode.objects.create(
            user=self.user,
            code="654321",
            purpose=VerificationCode.PASSWORD_RESET,
            expires_on=timezone.now() + timedelta(minutes=5),
        )
        self.assertEqual(self.user.verification_codes.count(), 2)

    def test_verification_code_index_fields_exist(self):
        indexes = [index.fields for index in VerificationCode._meta.indexes]
        self.assertIn(["code", "purpose"], indexes)
