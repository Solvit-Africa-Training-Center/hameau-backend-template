import logging
from django.db.models import Count
from .models.impact_models import ImpactStatistic

logger = logging.getLogger(__name__)

class ImpactStatsService:
    """
    Service to calculate and update dynamic impact statistics.
    """

    @staticmethod
    def get_total_children_supported():
        from programs.models.residentials_models import Child
        from programs.models.ifashe_models import SponsoredChild
        
        residential_count = Child.objects.filter(status=Child.ACTIVE).count()
        sponsored_count = SponsoredChild.objects.filter(support_status="ACTIVE").count()
        return residential_count + sponsored_count

    @staticmethod
    def get_total_families_supported():
        from programs.models.ifashe_models import Family, Sponsorship
        
        # Assuming families with at least one active sponsored child are considered supported
        # Or simply count all families registered in Ifashe if that's the program definition
        # Let's count families with active sponsorships contentiously
        return Family.objects.filter(children__sponsorships__status=Sponsorship.ACTIVE).distinct().count()

    @staticmethod
    def get_total_internships():
        from programs.models.internships_models import InternshipProgram
        
        return InternshipProgram.objects.filter(status__in=[InternshipProgram.ACTIVE, InternshipProgram.COMPLETED]).count()

    @classmethod
    def update_statistics(cls):
        """
        Updates the values of existing ImpactStatistic records based on calculations.
        Only updates records with specific titles to avoid overwriting custom stats.
        """
        stats_map = {
            "Children Supported": cls.get_total_children_supported(),
            "Families Impacted": cls.get_total_families_supported(),
            "Internships Provided": cls.get_total_internships(),
             # Add more mappings as needed
        }

        for title, value in stats_map.items():
            try:
                stat = ImpactStatistic.objects.get(title__iexact=title)
                stat.value = f"{value}+" # Adding '+' for visual effect, can be adjusted
                stat.save()
            except ImpactStatistic.DoesNotExist:
                pass # Stat doesn't exist, skip update
            except ImpactStatistic.MultipleObjectsReturned:
                # Update the first one found if duplicates exist
                stat = ImpactStatistic.objects.filter(title__iexact=title).first()
                if stat:
                    stat.value = f"{value}+"
                    stat.save()
