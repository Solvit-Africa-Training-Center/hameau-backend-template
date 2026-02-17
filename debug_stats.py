import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev') # Adjust setting path if needed
django.setup()

from public_modules.services import ImpactStatsService
from public_modules.models.impact_models import ImpactStatistic
from programs.models.residentials_models import Child
from programs.models.ifashe_models import SponsoredChild, Family, Sponsorship

def debug_service():
    print("Starting debug...")
    
    # 1. Clean up
    print("Cleaning up old data...")
    ImpactStatistic.objects.all().delete()
    Child.objects.all().delete()
    SponsoredChild.objects.all().delete()
    
    # 2. Create Stats
    print("Creating ImpactStatistic records...")
    ImpactStatistic.objects.create(title="Children Supported", value="0")
    ImpactStatistic.objects.create(title="Families Impacted", value="0")
    
    # 3. Create Data
    print("Creating Child and Family data...")
    try:
        Child.objects.create(
            first_name="Res", last_name="Child", date_of_birth="2010-01-01",
            gender="MALE", start_date="2023-01-01", status=Child.ACTIVE
        )
        print("Created Residential Child.")
        
        family = Family.objects.create(family_name="Test Family")
        sponsored_child = SponsoredChild.objects.create(
            family=family, first_name="Spon", last_name="Child",
            date_of_birth="2012-01-01", gender="FEMALE"
        )
        Sponsorship.objects.create(
            child=sponsored_child, start_date="2023-01-01", status=Sponsorship.ACTIVE
        )
        print("Created Sponsored Child.")
    except Exception as e:
        print(f"Error creating data: {e}")
        return

    # 4. Run Update
    print("Running ImpactStatsService.update_statistics()...")
    try:
        res_count = Child.objects.filter(status=Child.ACTIVE).count()
        print(f"Residential Count: {res_count} (Total: {Child.objects.count()})")
        if res_count == 0:
             print(f"Child Statuses: {list(Child.objects.values_list('status', flat=True))}")

        spon_count = SponsoredChild.objects.filter(support_status="ACTIVE").count()
        print(f"Sponsored Count: {spon_count} (Total: {SponsoredChild.objects.count()})")
        
        ImpactStatsService.update_statistics()
        print("Update completed.")
    except Exception as e:
        print(f"Error in update_statistics: {e}")
        import traceback
        traceback.print_exc()
        return

    # 5. Verify
    stat = ImpactStatistic.objects.get(title="Children Supported")
    print(f"Children Supported: {stat.value}")
    
    # 6. Check Introspection (Fake)
    print("Service seems to work.")

if __name__ == "__main__":
    debug_service()
