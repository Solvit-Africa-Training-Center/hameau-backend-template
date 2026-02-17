import pytest
from django.test import TestCase
from django.utils import timezone
from uuid import UUID
from public_modules.models.impact_models import ImpactStatistic, ContactMessage, ContactInfo
from public_modules.models.team_models import TeamMember


@pytest.mark.django_db
class TestImpactStatistic(TestCase):
    """Test cases for ImpactStatistic model"""
    
    def setUp(self):
        """Set up test data"""
        self.impact = ImpactStatistic.objects.create(
            title="Children Supported",
            value="500+",
            description="Total children supported by our programs",
            order=1,
            is_active=True
        )
    
    def test_impact_statistic_creation(self):
        """Test creating an impact statistic"""
        self.assertEqual(self.impact.title, "Children Supported")
        self.assertEqual(self.impact.value, "500+")
        self.assertIsInstance(self.impact.id, UUID)
        self.assertTrue(self.impact.is_active)
    
    def test_impact_statistic_str(self):
        """Test string representation"""
        expected_str = "Children Supported: 500+"
        self.assertEqual(str(self.impact), expected_str)
    
    def test_impact_statistic_ordering(self):
        """Test impact statistics are ordered by 'order' field"""
        impact2 = ImpactStatistic.objects.create(
            title="Communities Reached",
            value="25",
            order=2,
            is_active=True
        )
        impact3 = ImpactStatistic.objects.create(
            title="Staff Members",
            value="40",
            order=0,
            is_active=True
        )
        
        impacts = list(ImpactStatistic.objects.all())
        self.assertEqual(impacts[0].order, 0)
        self.assertEqual(impacts[1].order, 1)
        self.assertEqual(impacts[2].order, 2)
    
    def test_impact_statistic_inactive(self):
        """Test inactive impact statistics"""
        inactive = ImpactStatistic.objects.create(
            title="Inactive Stat",
            value="0",
            is_active=False
        )
        active_count = ImpactStatistic.objects.filter(is_active=True).count()
        self.assertEqual(active_count, 1)  # Only self.impact is active


@pytest.mark.django_db
class TestContactInfo(TestCase):
    """Test cases for ContactInfo model"""
    
    def setUp(self):
        """Set up test data"""
        self.contact_info = ContactInfo.objects.create(
            email="info@example.com",
            phone="+1 (555) 123-4567",
            address="123 Main St, City, State 12345",
            is_active=True
        )
    
    def test_contact_info_creation(self):
        """Test creating contact information"""
        self.assertEqual(self.contact_info.email, "info@example.com")
        self.assertEqual(self.contact_info.phone, "+1 (555) 123-4567")
        self.assertIn("Main St", self.contact_info.address)
        self.assertTrue(self.contact_info.is_active)
    
    def test_contact_info_str(self):
        """Test string representation"""
        expected_str = "Contact Info - info@example.com"
        self.assertEqual(str(self.contact_info), expected_str)
    
    def test_contact_info_timestamps(self):
        """Test created_on and updated_on timestamps"""
        self.assertIsNotNone(self.contact_info.created_on)
        self.assertIsNotNone(self.contact_info.updated_on)
        self.assertLessEqual(self.contact_info.created_on, self.contact_info.updated_on)
    
    def test_contact_info_single_active(self):
        """Test retrieving single active contact info"""
        inactive = ContactInfo.objects.create(
            email="old@example.com",
            phone="555",
            address="Old Address",
            office_hours="N/A",
            is_active=False
        )
        active = ContactInfo.objects.filter(is_active=True).first()
        self.assertEqual(active.email, "info@example.com")


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
            first_name="Alice",
            last_name="Johnson",
            role="Program Director",
            order=1,
            is_active=True
        )
    
    def test_team_member_creation(self):
        """Test creating a team member"""
        self.assertEqual(self.member.first_name, "Alice")
        self.assertEqual(self.member.last_name, "Johnson")
        self.assertEqual(self.member.role, "Program Director")
        self.assertTrue(self.member.is_active)
    
    def test_team_member_str(self):
        """Test string representation"""
        expected_str = "Alice Johnson"
        self.assertEqual(str(self.member), expected_str)
    
    def test_team_member_ordering(self):
        """Test team members ordered by 'order' field"""
        member2 = TeamMember.objects.create(
            first_name="Bob",
            last_name="Williams",
            role="Finance Manager",
            order=2
        )
        member3 = TeamMember.objects.create(
            first_name="Carol",
            last_name="Brown",
            role="Executive Director",
            order=0
        )
        
        members = list(TeamMember.objects.all())
        self.assertEqual(members[0].order, 0)
        self.assertEqual(members[1].order, 1)
        self.assertEqual(members[2].order, 2)
    
    def test_team_member_active_filter(self):
        """Test filtering active team members"""
        inactive_member = TeamMember.objects.create(
            first_name="David",
            last_name="Lee",
            role="Consultant",
            is_active=False
        )
        
        active_members = TeamMember.objects.filter(is_active=True)
        self.assertEqual(active_members.count(), 1)
        self.assertNotIn(inactive_member, active_members)
    
    def test_team_member_without_photo(self):
        """Test creating team member without optional photo"""
        member = TeamMember.objects.create(
            first_name="Eve",
            last_name="Davis",
            role="Intern"
        )
        # photo should be blank if not provided
        self.assertTrue(member.photo == "" or member.photo is None)


@pytest.mark.django_db
class TestDynamicDataIntegration(TestCase):
    """Integration tests for all dynamic data models"""
    
    def test_all_models_have_uuid_id(self):
        """Test all models use UUID primary key"""
        impact = ImpactStatistic.objects.create(title="Test", value="100")
        contact_info = ContactInfo.objects.create(
            email="test@test.com",
            phone="555",
            address="Test"
        )
        message = ContactMessage.objects.create(
            first_name="Test",
            last_name="User",
            email="test@test.com",
            subject="Test",
            message="Test message"
        )
        member = TeamMember.objects.create(
            first_name="Test",
            last_name="Member",
            role="Test Role"
        )
        
        self.assertIsInstance(impact.id, UUID)
        self.assertIsInstance(contact_info.id, UUID)
        self.assertIsInstance(message.id, UUID)
        self.assertIsInstance(member.id, UUID)
    
    def test_all_models_have_timestamps(self):
        """Test all models have created_on and updated_on"""
        impact = ImpactStatistic.objects.create(title="Test", value="100")
        contact_info = ContactInfo.objects.create(
            email="test@test.com", phone="555", address="Test"
        )
        message = ContactMessage.objects.create(
            first_name="Test", last_name="User", email="test@test.com",
            subject="Test", message="Test"
        )
        member = TeamMember.objects.create(
            first_name="Test", last_name="Member", role="Test"
        )
        
        for obj in [impact, contact_info, message, member]:
            self.assertIsNotNone(obj.created_on)
            self.assertIsNotNone(obj.updated_on)
