import pytest
import datetime
from django.core.management import call_command
from django.core import mail
from django.utils import timezone
from unittest.mock import patch
from donations.models import Donor, Donation, SponsorEmailLog
from donations.tasks import send_monthly_donor_emails_task
from programs.models.residentials_models import Child, ChildProgress

@pytest.mark.django_db
class TestDonorEmails:
    @pytest.fixture
    def setup_data(self):
        # 1. Create a child
        self.child = Child.objects.create(
            first_name="Alice",
            last_name="Wonderland",
            date_of_birth=datetime.date(2015, 1, 1),
            gender="FEMALE",
            start_date=datetime.date(2023, 1, 1)
        )
        
        # 2. Create a donor
        self.donor = Donor.objects.create(
            fullname="Sandrine Kwizera",
            email="sandra@gmail.com"
        )
        
        # 3. Create a donation linked to the child
        self.donation = Donation.objects.create(
            donor=self.donor,
            child=self.child,
            amount=20000.00,
            currency="RWF",
            donation_purpose="Monthly Support"
        )
        
        # 4. Create child progress records for the previous month
        today = timezone.now().date()
        first_day_current = today.replace(day=1)
        prev_month_date = first_day_current - datetime.timedelta(days=15)
        
        progress = ChildProgress.objects.create(
            child=self.child,
            notes="Alice is showing great enthusiasm in art class.",
        )
        # Update created_on to bypass auto_now_add
        ChildProgress.objects.filter(id=progress.id).update(
            created_on=timezone.make_aware(datetime.datetime.combine(prev_month_date, datetime.time()))
        )

    def test_donor_child_donation_link(self, setup_data):
        assert self.donation.child == self.child
        assert self.donation.donor == self.donor
        assert self.child.donations.count() == 1

    @patch("donations.tasks.get_ai_summary")
    def test_send_monthly_donor_emails_command(self, mock_get_summary, setup_data):
        mock_get_summary.return_value = "Summary for Alice: She is doing well."
        
        # Run task
        send_monthly_donor_emails_task()
        
        # Check if email was sent
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [self.donor.email]
        assert "Monthly Progress Update" in mail.outbox[0].subject
        assert "Summary for Alice" in mail.outbox[0].body
        
        # Check if log was created
        assert SponsorEmailLog.objects.filter(
            donor=self.donor,
            child=self.child,
            status="SUCCESS"
        ).exists()

    @patch("donations.tasks.get_ai_summary")
    def test_duplicate_prevention(self, mock_get_summary, setup_data):
        mock_get_summary.return_value = "Summary content."
        
        # Run task twice
        send_monthly_donor_emails_task()
        assert len(mail.outbox) == 1
        
        # Second run should not send again
        send_monthly_donor_emails_task()
        assert len(mail.outbox) == 1 

    @patch("donations.tasks.get_ai_summary")
    def test_force_flag(self, mock_get_summary, setup_data):
        mock_get_summary.return_value = "Summary content."
        
        send_monthly_donor_emails_task()
        assert len(mail.outbox) == 1
        
        # Should send again with force
        send_monthly_donor_emails_task(force=True)
        assert len(mail.outbox) == 2
