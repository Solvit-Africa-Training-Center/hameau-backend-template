import pytest
from django.test import TestCase
from django.utils import timezone
from uuid import UUID

from public_modules.models.content_models import ContactMessage, TeamMember, PublicContent



@pytest.mark.django_db
class TestContactMessage(TestCase):
    """Test cases for ContactMessage model"""
    
    def setUp(self):
        """Set up test data"""
        self.message = ContactMessage.objects.create(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="+1 (555) 987-6543",
            subject="General Inquiry",
            message="I would like to learn more about your programs.",
            status=ContactMessage.PENDING
        )
    
    def test_contact_message_creation(self):
        """Test creating a contact message"""
        self.assertEqual(self.message.first_name, "John")
        self.assertEqual(self.message.last_name, "Doe")
        self.assertEqual(self.message.email, "john@example.com")
        self.assertEqual(self.message.status, ContactMessage.PENDING)
    
    def test_contact_message_fullname_property(self):
        """Test fullname property"""
        self.assertEqual(self.message.fullname, "John Doe")
    
    def test_contact_message_str(self):
        """Test string representation"""
        expected_str = "John Doe - General Inquiry"
        self.assertEqual(str(self.message), expected_str)
    
    def test_contact_message_status_choices(self):
        """Test status field choices"""
        self.assertEqual(self.message.status, ContactMessage.PENDING)
        
        self.message.status = ContactMessage.VIEWED
        self.message.save()
        self.assertEqual(self.message.status, ContactMessage.VIEWED)
        
        self.message.status = ContactMessage.RESPONDED
        self.message.save()
        self.assertEqual(self.message.status, ContactMessage.RESPONDED)
    
    def test_contact_message_admin_notes(self):
        """Test adding admin notes"""
        self.assertIsNone(self.message.admin_notes)
        
        self.message.admin_notes = "Follow up requested"
        self.message.save()
        self.assertEqual(self.message.admin_notes, "Follow up requested")
    
    def test_contact_message_ordering(self):
        """Test messages ordered by created_on (newest first)"""
        msg2 = ContactMessage.objects.create(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            subject="Another Inquiry",
            message="More info please."
        )
        
        messages = list(ContactMessage.objects.all())
        # Should be ordered by -created_on (newest first)
        self.assertEqual(messages[0].id, msg2.id)
        self.assertEqual(messages[1].id, self.message.id)


@pytest.mark.django_db
class TestTeamMember(TestCase):
    """Test cases for TeamMember model"""
    
    def setUp(self):
        """Set up test data"""
        self.member = TeamMember.objects.create(
            name="Alice Johnson",
            title="Program Director",
            order=1,
            is_active=True
        )
    
    def test_team_member_creation(self):
        """Test creating a team member"""
        self.assertEqual(self.member.name, "Alice Johnson")
        self.assertEqual(self.member.title, "Program Director")
        self.assertTrue(self.member.is_active)
    
    def test_team_member_str(self):
        """Test string representation"""
        expected_str = "Alice Johnson - Program Director"
        self.assertEqual(str(self.member), expected_str)
    
    def test_team_member_ordering(self):
        """Test team members ordered by 'order' field"""
        member2 = TeamMember.objects.create(
            name="Bob Williams",
            title="Finance Manager",
            order=2
        )
        member3 = TeamMember.objects.create(
            name="Carol Brown",
            title="Executive Director",
            order=0
        )
        
        members = list(TeamMember.objects.all())
        self.assertEqual(members[0].order, 0)
        self.assertEqual(members[1].order, 1)
        self.assertEqual(members[2].order, 2)
    
    def test_team_member_active_filter(self):
        """Test filtering active team members"""
        inactive_member = TeamMember.objects.create(
            name="David Lee",
            title="Consultant",
            is_active=False
        )
        
        active_members = TeamMember.objects.filter(is_active=True)
        self.assertEqual(active_members.count(), 1)
        self.assertNotIn(inactive_member, active_members)
    
    def test_team_member_without_photo(self):
        """Test creating team member without optional photo"""
        member = TeamMember.objects.create(
            name="Eve Davis",
            title="Intern"
        )
        # image should be blank if not provided
        self.assertTrue(member.image == "" or member.image is None)


@pytest.mark.django_db
class TestDynamicDataIntegration(TestCase):
    """Integration tests for remaining public modules models"""
    
    def test_all_models_have_uuid_id(self):
        """Test all models use UUID primary key"""
        content = PublicContent.objects.create(category=PublicContent.CATEGORY_TEAM, title="Test", is_active=True)
        message = ContactMessage.objects.create(
            first_name="Test",
            last_name="User",
            email="test@test.com",
            subject="Test",
            message="Test message"
        )
        member = TeamMember.objects.create(
            name="Test Member",
            title="Test Role"
        )
        
        self.assertIsInstance(content.id, UUID)
        self.assertIsInstance(message.id, UUID)
        self.assertIsInstance(member.id, UUID)
    
    def test_all_models_have_timestamps(self):
        """Test all models have created_on and updated_on"""
        content = PublicContent.objects.create(category=PublicContent.CATEGORY_TEAM, title="Test", is_active=True)
        message = ContactMessage.objects.create(
            first_name="Test", last_name="User", email="test@test.com",
            subject="Test", message="Test"
        )
        member = TeamMember.objects.create(
            name="Test Member", title="Test Role"
        )
        
        for obj in [content, message, member]:
            self.assertIsNotNone(obj.created_on)
            self.assertIsNotNone(obj.updated_on)
