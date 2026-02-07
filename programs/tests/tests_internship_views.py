import datetime
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User
from programs.models.internships_models import InternshipApplication

class InternshipApplicationViewSetTest(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password="password123",
            first_name="Admin",
            last_name="User"
        )
        self.client.force_authenticate(user=self.admin)

        self.application_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone": "0788111222",
            "country": "Rwanda",
            "education_level": "Bachelor",
            "program": "Software Engineering",
            "availability_hours": "Full-time",
            "date_of_birth": "1995-10-10",
            "nationality": "Rwandan",
            "is_in_rwanda": True,
            "school_university": "University of Rwanda",
            "field_of_study": "IT"
        }

    def test_create_application(self):
        url = "/api/internship-applications/"
        response = self.client.post(url, self.application_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(InternshipApplication.objects.count(), 1)
        self.assertEqual(InternshipApplication.objects.get().status, InternshipApplication.SUBMITTED)

    def test_list_applications(self):
        InternshipApplication.objects.create(**self.application_data)
        url = "/api/internship-applications/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify pagination structure
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)

    def test_filter_applications(self):
        InternshipApplication.objects.create(**self.application_data)
        # Create another with different country
        data2 = self.application_data.copy()
        data2['email'] = "jane@example.com"
        data2['country'] = "Kenya"
        InternshipApplication.objects.create(**data2)

        url = "/api/internship-applications/?country=Rwanda"
        response = self.client.get(url)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['country'], "Rwanda")

    def test_update_status_and_email_trigger(self):
        app = InternshipApplication.objects.create(**self.application_data)
        url = f"/api/internship-applications/{app.id}/"
        
        # Update status to APPROVED
        response = self.client.patch(url, {"status": InternshipApplication.APPROVED}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        app.refresh_from_db()
        self.assertEqual(app.status, InternshipApplication.APPROVED)
        # Email triggered logic is in serializer, we verify the patch worked.
