from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from ..models.content_models import PublicContent, ContactMessage, TeamMember

class PublicModuleTests(TestCase):
    def setUp(self):
        self.client = APIClient()
       
        self.team_member = TeamMember.objects.create(
            name="Jean-Claude Niyonzima",
            title="Education Coordinator",
            order=1
        )
        
        self.impact_stat = PublicContent.objects.create(
            category=PublicContent.CATEGORY_IMPACT,
            title="Children Supported",
            value="100",
            order=1
        )

    def test_list_teams(self):
        url = reverse('team-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
       
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], "Jean-Claude Niyonzima")
        self.assertEqual(response.data['results'][0]['title'], "Education Coordinator")

    def test_pagination_team(self):
        # Create many team members to trigger pagination (1 + 15 = 16 total)
        for i in range(15):
            TeamMember.objects.create(
                name=f"Member {i}",
                title="Staff",
                order=i
            )
        url = reverse('team-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should be paginated
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 9) # Page size is 9
        self.assertIsNotNone(response.data['next'])

    def test_impact_no_pagination(self):
        # Create impact stats
        for i in range(15):
            PublicContent.objects.create(
                category=PublicContent.CATEGORY_IMPACT,
                title=f"Stat {i}",
                value="10",
                order=i
            )
        url = reverse('impact-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should NOT be paginated (so direct list, no 'results' key)
        self.assertIsInstance(response.data, list)
        self.assertNotIn('results', response.data)
        self.assertGreaterEqual(len(response.data), 15)

    def test_create_contact_message(self):
        url = reverse('contact-message-list')
        data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "phone": "1234567890",
            "subject": "Hello",
            "message": "This is a test message"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ContactMessage.objects.count(), 1)
        msg = ContactMessage.objects.first()
        self.assertEqual(msg.subject, "Hello")
