import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from programs.models.residentials_models import Child
from programs.models.ifashe_models import SponsoredChild, Family, Sponsorship
from programs.models.internships_models import InternshipProgram, InternshipApplication, Department
from public_modules.models.impact_models import ImpactStatistic
import uuid
from django.utils import timezone

@pytest.mark.django_db
class TestImpactStatistics:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse('impact-statistics-list') 

      
        self.stat_children = ImpactStatistic.objects.create(title="Children Supported", value="0", order=1)
        self.stat_families = ImpactStatistic.objects.create(title="Families Impacted", value="0", order=2)
        self.stat_internships = ImpactStatistic.objects.create(title="Internships Provided", value="0", order=3)

    def test_children_supported_calculation(self):
        
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        self.stat_children.refresh_from_db()
        assert self.stat_children.value == "0+"

        
        Child.objects.create(
            first_name="Res", last_name="Child", date_of_birth="2010-01-01",
            gender="MALE", start_date="2023-01-01", status=Child.ACTIVE
        )
        
       
        family = Family.objects.create(family_name="Test Family")
        sponsored_child = SponsoredChild.objects.create(
            family=family, first_name="Spon", last_name="Child",
            date_of_birth="2012-01-01", gender="FEMALE"
        )
        Sponsorship.objects.create(
            child=sponsored_child, start_date="2023-01-01", status=Sponsorship.ACTIVE
        )

        response = self.client.get(self.url)
        self.stat_children.refresh_from_db()
        assert self.stat_children.value == "2+"
        residential_child = Child.objects.first()
        residential_child.status = Child.LEFT
        residential_child.save()

        response = self.client.get(self.url)
        self.stat_children.refresh_from_db()
        assert self.stat_children.value == "1+"

    def test_families_impacted_calculation(self):
       
        family = Family.objects.create(family_name="Impacted Family")
        child = SponsoredChild.objects.create(
            family=family, first_name="Child", last_name="One",
            date_of_birth="2012-01-01", gender="MALE"
        )
        Sponsorship.objects.create(child=child, start_date="2023-01-01", status=Sponsorship.ACTIVE)

       
        Family.objects.create(family_name="Non-Impacted Family")

      
        self.client.get(self.url)
        self.stat_families.refresh_from_db()
        assert self.stat_families.value == "1+"

    def test_internships_calculation(self):
       
        dept = Department.objects.create(name="IT")
        app = InternshipApplication.objects.create(
            first_name="Intern", last_name="One", email="test@test.com", date_of_birth="2000-01-01"
        )
        
       
        InternshipProgram.objects.create(
            application=app, department=dept, start_date="2023-01-01", end_date="2023-06-01",
            status=InternshipProgram.ACTIVE
        )

       
        self.client.get(self.url)
        self.stat_internships.refresh_from_db()
        assert self.stat_internships.value == "1+"
