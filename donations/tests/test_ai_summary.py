
import pytest
import datetime
from django.utils import timezone
from ..models import Child, ChildProgress, Caretaker, House, FoodSupplier, ChildCaretakerAssignment
from ..services import get_ai_summary

@pytest.mark.django_db
def test_ai_summary_generation():
    # Setup
    child = Child.objects.create(
        first_name="Test",
        last_name="Child",
        date_of_birth=datetime.date(2015, 1, 1),
        gender="MALE",
        start_date=datetime.date(2023, 1, 1)
    )
    
    # Create Progress
    ChildProgress.objects.create(
        child=child,
        notes="He learned to ride a bike today.",
        created_on=timezone.now()
    )
    
    ChildProgress.objects.create(
        child=child,
        notes="He made a new friend named Sam.",
        created_on=timezone.now()
    )
    
    # Check if OPENAI_API_KEY is available
    from django.conf import settings
    if not settings.OPENAI_API_KEY:
        pytest.skip("Skipping AI summary test because OPENAI_API_KEY is not set.")

    # Execute
    year = timezone.now().year
    month = timezone.now().month
    summary = get_ai_summary(child, year, month)
    
    # Verify
    assert summary is not None
    assert isinstance(summary, str)
    assert len(summary) > 0
    print(f"\nGenerated Summary:\n{summary}")
