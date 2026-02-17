import pytest
from unittest.mock import patch, MagicMock
from django.conf import settings
from donations.models import Donation, Donor
from donations.serializers import DonationSerializer
from decimal import Decimal

@pytest.mark.django_db
class TestIremboPayIntegration:
    
    def setup_method(self):
        self.donor = Donor.objects.create(
            fullname="Test Donor",
            email="donor@example.com",
            phone="0780000000"
        )
        
    @patch('utils.services.requests.post')
    def test_irembopay_invoice_creation_success(self, mock_post):
        # Mock successful response from IremboPay
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "invoiceNumber": "880419623157",
                "paymentLinkUrl": "https://irembo.gov/pay/880419623157"
            }
        }
        mock_post.return_value = mock_response
        
        data = {
            "donor": str(self.donor.id),
            "donation_type": Donation.GENERAL,
            "amount": "5000.00",
            "currency": "RWF",
            "payment_method": Donation.IREMBOPAY,
            "donation_purpose": "School Fees"
        }
        
        serializer = DonationSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        
        donation = serializer.save()
        
        # Verify mock was called
        mock_post.assert_called_once()
        
        # Verify results in notes
        assert "Irembo Invoice: 880419623157" in donation.notes
        assert "Payment Link: https://irembo.gov/pay/880419623157" in donation.notes
        
    @patch('utils.services.requests.post')
    def test_irembopay_invoice_creation_failure(self, mock_post):
        # Mock failed response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "success": False,
            "message": "Invalid request"
        }
        mock_post.return_value = mock_response
        
        data = {
            "donor": str(self.donor.id),
            "donation_type": Donation.GENERAL,
            "amount": "5000.00",
            "currency": "RWF",
            "payment_method": Donation.IREMBOPAY
        }
        
        serializer = DonationSerializer(data=data)
        assert serializer.is_valid()
        
        donation = serializer.save()
        
        # Verify failure warning in notes
        assert "WARNING: IremboPay Invoice Creation Failed" in donation.notes
