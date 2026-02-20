
import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from public_modules.models.content_models import PublicContent
from accounts.models import User
from programs.models.residentials_models import Child
from programs.models.ifashe_models import Family, SponsoredChild, Sponsorship
from programs.models.internships_models import InternshipProgram, InternshipApplication, Department

@pytest.mark.django_db
class TestPublicContent:
    def setup_method(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(username='admin', password='password', is_staff=True)
        self.regular_user = User.objects.create_user(username='user', password='password')
        
        # Create sample content
        self.impact_children = PublicContent.objects.create(
            category=PublicContent.CATEGORY_IMPACT,
            title="Children Supported",
            value="100", # Base value
            impact_type=PublicContent.IMPACT_CHILDREN,
            order=1
        )
        self.team = PublicContent.objects.create(
            category=PublicContent.CATEGORY_TEAM,
            title="John Mugabo",
            subtitle="Director",
            order=1
        )
        self.message = PublicContent.objects.create(
            category=PublicContent.CATEGORY_CONTACT_MESSAGE,
            title="Inquiry",
            text_content="Hello",
            email="john@example.com",
            first_name="John",
            last_name="Mugabo"
        )

    def test_dynamic_impact_calculation(self):
        # Create Dummy Data for Counts
        # 1. Active Child
        Child.objects.create(
            first_name="C1", last_name="L1", date_of_birth="2010-01-01", 
            gender=Child.MALE, start_date="2020-01-01", status=Child.ACTIVE
        )
        # 2. Left Child (Should not count)
        Child.objects.create(
            first_name="C2", last_name="L2", date_of_birth="2010-01-01", 
            gender=Child.FEMALE, start_date="2020-01-01", status=Child.LEFT
        )
        
        url = reverse('public-content-by-category', kwargs={'category': 'IMPACT'})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        
        item = next(item for item in response.data if item['title'] == "Children Supported")
        # 100 (base) + 1 (Active Child) = 101
        assert item['calculated_value'] == "101"

    def test_submit_message_public(self):
        url = reverse('contact-create')
        data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane@example.com",
            "phone": "555-5678",
            "title": "New Inquiry", # Subject
            "text_content": "I am interested" # Message
        }
        response = self.client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify it was created
        msg = PublicContent.objects.filter(email="jane@example.com").first()
        assert msg is not None
        assert msg.category == PublicContent.CATEGORY_CONTACT_MESSAGE
        assert msg.title == "New Inquiry"

    def test_messages_hidden_from_public_list(self):
        url = reverse('public-content-by-category', kwargs={'category': 'CONTACT_MESSAGE'})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK 
        assert len(response.data) == 0 
