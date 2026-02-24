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
        InternshipApplication.objects.all().delete()
        # Create an application that should be found by the filter
        application_to_find = InternshipApplication.objects.create(
            first_name="Test",
            last_name="One",
            email="test1@example.com",
            phone="0788111001",
            date_of_birth="1990-01-01",
            nationality="Rwandan",
            is_in_rwanda=True,
            school_university="University X",
            field_of_study="Math"
        )

        # Create another application that should NOT be found by the filter
        InternshipApplication.objects.create(
            first_name="Test",
            last_name="Two",
            email="test2@example.com",
            phone="0788111002",
            date_of_birth="1991-02-02",
            nationality="Rwandan",
            is_in_rwanda=True,
            school_university="University Y",
            field_of_study="Physics"
        )

        url = "/api/internship-applications/?search=test1@example.com"
        response = self.client.get(url)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['email'], "test1@example.com")

    def test_update_status_and_email_trigger(self):
        app = InternshipApplication.objects.create(**self.application_data)
        url = f"/api/internship-applications/{app.id}/"
        
        # Update status to APPROVED
        response = self.client.patch(url, {"status": InternshipApplication.APPROVED}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        app.refresh_from_db()
        self.assertEqual(app.status, InternshipApplication.APPROVED)
        
