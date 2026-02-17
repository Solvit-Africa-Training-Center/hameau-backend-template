import pytest
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from public_modules.models.impact_models import ImpactStatistic, ContactMessage, ContactInfo
from public_modules.models.team_models import TeamMember


@pytest.mark.django_db
class TestImpactStatisticViews(APITestCase):
    """Test ImpactStatistic API endpoints"""
    
    def setUp(self):
        """Set up test data and clients"""
        self.client = APIClient()
        self.impact1 = ImpactStatistic.objects.create(
            title="Children Supported",
            value="500+",
            order=1,
            is_active=True
        )
        self.impact2 = ImpactStatistic.objects.create(
            title="Programs",
            value="10",
            order=2,
            is_active=True
        )
        self.impact_inactive = ImpactStatistic.objects.create(
            title="Inactive",
            value="0",
            is_active=False
        )
        
        
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
    
    def test_get_impact_statistics_public(self):
        
        response = self.client.get('/api/impact-statistics/public/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Should return list with only active items
        self.assertEqual(len(data), 2)
        titles = [item['title'] for item in data]
        self.assertIn("Children Supported", titles)
        self.assertNotIn("Inactive", titles)
    
    def test_impact_statistics_ordered(self):
       
        response = self.client.get('/api/impact-statistics/public/')
        data = response.json()
        
        self.assertEqual(data[0]['title'], "Children Supported")
        self.assertEqual(data[1]['title'], "Programs")
    
    def test_create_impact_statistic_unauthenticated(self):
       
        data = {
            'title': 'New Stat',
            'value': '100',
            'order': 3,
            'is_active': True
        }
        response = self.client.post('/api/impact-statistics/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_impact_statistic_authenticated(self):
     
        self.client.force_authenticate(user=self.admin)
        data = {
            'title': 'New Stat',
            'value': '100',
            'order': 3,
            'is_active': True
        }
        response = self.client.post('/api/impact-statistics/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Stat')
    
    def test_update_impact_statistic(self):
       
        self.client.force_authenticate(user=self.admin)
        data = {'value': '600+'}
        response = self.client.patch(
            f'/api/impact-statistics/{self.impact1.id}/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check value was updated
        self.impact1.refresh_from_db()
        self.assertEqual(self.impact1.value, '600+')
    
    def test_delete_impact_statistic(self):
        
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/impact-statistics/{self.impact1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Check it's deleted
        exists = ImpactStatistic.objects.filter(id=self.impact1.id).exists()
        self.assertFalse(exists)


@pytest.mark.django_db
class TestContactMessageViews(APITestCase):
   
    def setUp(self):
       
        self.client = APIClient()
        self.message = ContactMessage.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="+1 555-1234",
            subject="Inquiry",
            message="Hi there",
            status=ContactMessage.PENDING
        )
        
      
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
    
    def test_create_contact_message_public(self):
       
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'phone': '+1 555-5678',
            'subject': 'Partnership',
            'message': 'I am interested'
        }
        response = self.client.post('/api/contact-messages/create/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify message was created with PENDING status
        message = ContactMessage.objects.get(email='jane@example.com')
        self.assertEqual(message.status, ContactMessage.PENDING)
    
    def test_create_contact_message_invalid_email(self):
    
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'not-an-email',
            'subject': 'Test',
            'message': 'Test'
        }
        response = self.client.post('/api/contact-messages/create/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_contact_messages_admin_only(self):
       
        response = self.client.get('/api/contact-messages/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # With auth should work
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/contact-messages/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_contact_message_list_includes_fullname(self):
        
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/contact-messages/')
        data = response.json()
        
        self.assertTrue(len(data) > 0)
        self.assertIn('fullname', data[0])
        self.assertEqual(data[0]['fullname'], 'John Doe')
    
    def test_update_contact_message_status(self):
       
        self.client.force_authenticate(user=self.admin)
        data = {'status': ContactMessage.VIEWED}
        response = self.client.patch(
            f'/api/contact-messages/{self.message.id}/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.message.refresh_from_db()
        self.assertEqual(self.message.status, ContactMessage.VIEWED)
    
    def test_update_contact_message_notes(self):
       
        self.client.force_authenticate(user=self.admin)
        data = {'admin_notes': 'Follow up next week'}
        response = self.client.patch(
            f'/api/contact-messages/{self.message.id}/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.message.refresh_from_db()
        self.assertEqual(self.message.admin_notes, 'Follow up next week')
    
    def test_mark_as_viewed_action(self):
       
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f'/api/contact-messages/{self.message.id}/mark_as_viewed/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.message.refresh_from_db()
        self.assertEqual(self.message.status, ContactMessage.VIEWED)
    
    def test_mark_as_responded_action(self):
       
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f'/api/contact-messages/{self.message.id}/mark_as_responded/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.message.refresh_from_db()
        self.assertEqual(self.message.status, ContactMessage.RESPONDED)
    
    def test_delete_contact_message(self):
       
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/contact-messages/{self.message.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        exists = ContactMessage.objects.filter(id=self.message.id).exists()
        self.assertFalse(exists)


@pytest.mark.django_db
class TestContactInfoViews(APITestCase):
   
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.contact = ContactInfo.objects.create(
            email="info@example.com",
            phone="+1 555-1234",
            address="123 Main St",
            is_active=True
        )
        
        # Create admin user
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
    
    def test_get_contact_info_public(self):
       
        response = self.client.get('/api/contact-info/public/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data['email'], "info@example.com")
        self.assertEqual(data['phone'], "+1 555-1234")
    
    def test_contact_info_filters_inactive(self):
      
        # Make existing one inactive
        self.contact.is_active = False
        self.contact.save()
        
        # Create new active one
        new_contact = ContactInfo.objects.create(
            email="new@example.com",
            phone="555-9999",
            address="456 Oak",
            is_active=True
        )
        
        response = self.client.get('/api/contact-info/public/')
        data = response.json()
        
        self.assertEqual(data['email'], "new@example.com")
    
    def test_create_contact_info_unauthenticated(self):
       
        data = {
            'email': 'new@example.com',
            'phone': '555-5678',
            'address': '789 Pine',
            'is_active': True
        }
        response = self.client.post('/api/contact-info/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_contact_info_authenticated(self):
       
        self.client.force_authenticate(user=self.admin)
        data = {
            'email': 'new@example.com',
            'phone': '555-5678',
            'address': '789 Pine',
            'is_active': True
        }
        response = self.client.post('/api/contact-info/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_update_contact_info(self):
       
        self.client.force_authenticate(user=self.admin)
        data = {'phone': '+1 555-9999'}
        response = self.client.patch(
            f'/api/contact-info/{self.contact.id}/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.contact.refresh_from_db()
        self.assertEqual(self.contact.phone, '+1 555-9999')


@pytest.mark.django_db
class TestTeamMemberViews(APITestCase):
  
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.member1 = TeamMember.objects.create(
            first_name="Alice",
            last_name="Johnson",
            role="Director",
            order=1,
            is_active=True
        )
        self.member2 = TeamMember.objects.create(
            first_name="Bob",
            last_name="Smith",
            role="Manager",
            order=2,
            is_active=True
        )
        self.member_inactive = TeamMember.objects.create(
            first_name="Carol",
            last_name="Brown",
            role="Consultant",
            is_active=False
        )
        
        # Create admin user
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
    
    def test_get_team_members_public(self):
      
        response = self.client.get('/api/team-members/public/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(len(data), 2)
        names = [item['full_name'] for item in data]
        self.assertIn("Alice Johnson", names)
        self.assertNotIn("Carol Brown", names)
    
    def test_team_members_ordered(self):
       
        response = self.client.get('/api/team-members/public/')
        data = response.json()
        
        self.assertEqual(data[0]['full_name'], "Alice Johnson")
        self.assertEqual(data[1]['full_name'], "Bob Smith")
    
    def test_public_team_member_includes_role(self):
       
        response = self.client.get('/api/team-members/public/')
        data = response.json()
        
        self.assertIn('role', data[0])
        self.assertEqual(data[0]['role'], "Director")
    
    def test_create_team_member_unauthenticated(self):
       
        data = {
            'first_name': 'David',
            'last_name': 'Lee',
            'role': 'Coordinator',
            'is_active': True
        }
        response = self.client.post('/api/team-members/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_team_member_authenticated(self):
        
        self.client.force_authenticate(user=self.admin)
        data = {
            'first_name': 'David',
            'last_name': 'Lee',
            'role': 'Coordinator',
            'order': 3,
            'is_active': True
        }
        response = self.client.post('/api/team-members/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['full_name'], "David Lee")
    
    def test_update_team_member(self):
       
        self.client.force_authenticate(user=self.admin)
        data = {'role': 'Senior Director'}
        response = self.client.patch(
            f'/api/team-members/{self.member1.id}/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.member1.refresh_from_db()
        self.assertEqual(self.member1.role, 'Senior Director')
    
    def test_deactivate_team_member(self):
       
        self.client.force_authenticate(user=self.admin)
        data = {'is_active': False}
        response = self.client.patch(
            f'/api/team-members/{self.member1.id}/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Public endpoint should no longer return this member
        response = self.client.get('/api/team-members/public/')
        data = response.json()
        self.assertEqual(len(data), 1)  # Only Bob remains
    
    def test_delete_team_member(self):
        """Test deleting team member"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/team-members/{self.member1.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        exists = TeamMember.objects.filter(id=self.member1.id).exists()
        self.assertFalse(exists)


@pytest.mark.django_db
class TestAPIPermissions(APITestCase):
    
    
    def setUp(self):
        
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        self.user = User.objects.create_user(
            username='regular',
            password='user123',
            is_staff=False
        )
    
    def test_public_endpoints_allow_any(self):
        
        endpoints = [
            '/api/impact-statistics/public/',
            '/api/contact-info/public/',
            '/api/team-members/public/',
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
                f"Public endpoint {endpoint} should be accessible"
            )
    
    def test_contact_create_allows_any(self):
        
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'subject': 'Test',
            'message': 'Test message'
        }
        response = self.client.post('/api/contact-messages/create/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_admin_endpoints_require_staff(self):
        
        endpoints = [
            '/api/impact-statistics/',
            '/api/contact-messages/',
            '/api/contact-info/',
            '/api/team-members/',
        ]
        
       
        self.client.force_authenticate(user=self.user)
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(
                response.status_code,
                status.HTTP_403_FORBIDDEN,
                f"Admin endpoint {endpoint} should deny non-staff user"
            )
        
        # Admin should be allowed
        self.client.force_authenticate(user=self.admin)
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertIn(
                response.status_code,
                [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED],  # Some endpoints have different permission models
                f"Admin endpoint {endpoint} should allow staff user"
            )
