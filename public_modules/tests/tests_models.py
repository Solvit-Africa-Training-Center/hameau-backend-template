from unittest.mock import patch
from django.test import override_settings
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from accounts.models import User
from public_modules.models.gallery_models import (
    GalleryCategory,
    GalleryMedia,
)


@override_settings(MEDIA_ROOT="/tmp/test_media/")
class GalleryAndDonationModelsTest(APITestCase):
    def setUp(self):
        # Prevent real Cloudinary uploads when running under dev/prod storage settings
        self.cloudinary_patcher = patch(
            "cloudinary_storage.storage.MediaCloudinaryStorage._save",
            return_value="media_gallery/test_image.jpg",
        )
        self.cloudinary_patcher.start()

        self.user = User.objects.create_user(
            email="testuser@example.com", password="password123", phone="+250731234567"
        )

        self.category = GalleryCategory.objects.create(
            name="Events", description="Event photos"
        )

        self.media_file = SimpleUploadedFile(
            name="test_image.jpg", content=b"file_content", content_type="image/jpeg"
        )

        self.gallery_media = GalleryMedia.objects.create(
            category=self.category,
            title="Community Event",
            description="Annual community gathering",
            media_url=self.media_file,
            is_public=True,
            uploaded_by=self.user,
        )

    def tearDown(self):
        self.cloudinary_patcher.stop()

    def test_gallery_category_creation(self):
        self.assertEqual(self.category.name, "Events")
        self.assertEqual(str(self.category), "Events")

    def test_gallery_media_creation(self):
        self.assertEqual(self.gallery_media.title, "Community Event")
        self.assertEqual(self.gallery_media.category, self.category)
        self.assertEqual(self.gallery_media.uploaded_by, self.user)
        self.assertTrue(self.gallery_media.is_public)
        self.assertEqual(str(self.gallery_media), "Community Event")
