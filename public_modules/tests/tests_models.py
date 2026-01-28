from django.test import override_settings
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal

from accounts.models import User
from ..models import (
    GalleryCategory,
    GalleryMedia,
    Donor,
    Donation,
)


@override_settings(MEDIA_ROOT="/tmp/test_media/")
class GalleryAndDonationModelsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password123",
            phone="+250731234567"
        )

        self.category = GalleryCategory.objects.create(
            name="Events",
            description="Event photos"
        )

        self.media_file = SimpleUploadedFile(
            name="test_image.jpg",
            content=b"file_content",
            content_type="image/jpeg"
        )

        self.gallery_media = GalleryMedia.objects.create(
            category=self.category,
            title="Community Event",
            description="Annual community gathering",
            media_url=self.media_file,
            is_public=True,
            uploaded_by=self.user,
        )

       

        self.donor = Donor.objects.create(
            fullname="Arnold Ciku",
            email="arnold@gmail.com",
            phone="+250700000000",
            address="Kigali, Rwanda",
            donor_type=Donor.INDIVIDUAL,
        )

        self.donation = Donation.objects.create(
            donor=self.donor,
            amount=Decimal("150.00"),
            currency="RWF",
            donation_purpose="Community support",
            payment_method=Donation.CASH,
            notes="Test donation",
        )

    def test_gallery_category_creation(self):
        self.assertEqual(self.category.name, "Events")
        self.assertEqual(str(self.category), "Events")

    def test_gallery_media_creation(self):
        self.assertEqual(self.gallery_media.title, "Community Event")
        self.assertEqual(self.gallery_media.category, self.category)
        self.assertEqual(self.gallery_media.uploaded_by, self.user)
        self.assertTrue(self.gallery_media.is_public)
        self.assertEqual(str(self.gallery_media), "Community Event")

    def test_donor_creation(self):
        self.assertEqual(self.donor.fullname, "Arnold Ciku")
        self.assertEqual(self.donor.donor_type, Donor.INDIVIDUAL)
        self.assertEqual(str(self.donor), "Arnold Ciku")

    def test_donation_creation(self):
        self.assertEqual(self.donation.amount, Decimal("150.00"))
        self.assertEqual(self.donation.currency, "RWF")
        self.assertEqual(self.donation.donor, self.donor)
        self.assertEqual(
            str(self.donation),
            "Arnold Ciku - 150.00 RWF"
        )

    def test_anonymous_donation_str(self):
        anonymous_donation = Donation.objects.create(
            donor=None,
            amount=Decimal("50.00"),
            currency="RWF",
        )
        self.assertEqual(
            str(anonymous_donation),
            "Anonymous - 50.00 RWF"
        )
