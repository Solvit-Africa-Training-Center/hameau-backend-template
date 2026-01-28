from datetime import date
from rest_framework.test import APITestCase

from accounts.models import User
from programs.models import (
    Family,
    Parent,
    SponsoredChild,
    Sponsorship,
    School,
    SchoolSupport,
    DressingDistribution,
    ParentWorkContract,
    ParentAttendance,
    ParentPerformance,
)


class BaseModelTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone="+250791234567",
            email="tester@example.com",
            password="password123",
        )

        self.family = Family.objects.create(
            family_name="Elie Family",
            address="Kigali",
            province="Kigali City",
            district="Gasabo",
            family_members=5,
        )

        self.parent = Parent.objects.create(
            family=self.family,
            first_name="Arnold",
            last_name="Mataba",
            relationship=Parent.FATHER,
            phone="0780000000",
            national_id="1234567890123456",
        )

        self.child = SponsoredChild.objects.create(
            family=self.family,
            first_name="Armand",
            last_name="Mataba",
            date_of_birth=date(2015, 1, 1),
            gender=SponsoredChild.FEMALE,
            school_level="Primary",
        )


class FamilyModelTest(BaseModelTestCase):

    def test_family_creation(self):
        self.assertEqual(self.family.family_name, "Elie Family")
        self.assertEqual(str(self.family), "Elie Family")


class ParentModelTest(BaseModelTestCase):

    def test_parent_creation(self):
        self.assertEqual(self.parent.family, self.family)
        self.assertEqual(self.parent.relationship, Parent.FATHER)

    def test_parent_full_name_property(self):
        self.assertEqual(self.parent.full_name, "Arnold Mataba")

    def test_parent_str(self):
        self.assertEqual(str(self.parent), "Arnold Mataba")



class SponsoredChildModelTest(BaseModelTestCase):

    def test_child_creation(self):
        self.assertEqual(self.child.family, self.family)
        self.assertEqual(self.child.gender, SponsoredChild.FEMALE)

    def test_child_full_name_property(self):
        self.assertEqual(self.child.full_name, "Armand Mataba")

    def test_child_str(self):
        self.assertEqual(str(self.child), "Armand Mataba")



class SponsorshipModelTest(BaseModelTestCase):

    def setUp(self):
        super().setUp()
        self.sponsorship = Sponsorship.objects.create(
            child=self.child,
            sponsorship_type=Sponsorship.FULL,
            start_date=date.today(),
            status=Sponsorship.ACTIVE,
        )

    def test_sponsorship_creation(self):
        self.assertEqual(self.sponsorship.child, self.child)
        self.assertEqual(self.sponsorship.status, Sponsorship.ACTIVE)

    def test_sponsorship_str(self):
        self.assertIn("Armand Mataba", str(self.sponsorship))



class SchoolSupportModelTest(BaseModelTestCase):

    def setUp(self):
        super().setUp()
        self.school = School.objects.create(
            name="Green Hills Academy",
            address="Kigali",
        )

        self.school_support = SchoolSupport.objects.create(
            child=self.child,
            school=self.school,
            academic_year="2024-2025",
            school_fees=50000,
            materials_cost=10000,
            payment_status=SchoolSupport.PAID,
        )

    def test_school_support_total_cost(self):
        self.assertEqual(self.school_support.total_cost, 60000)

    def test_school_support_str(self):
        self.assertIn("2024-2025", str(self.school_support))


class DressingDistributionModelTest(BaseModelTestCase):

    def setUp(self):
        super().setUp()
        self.distribution = DressingDistribution.objects.create(
            child=self.child,
            distribution_date=date.today(),
            item_type="Shoes",
            size="34",
            quantity=2,
        )

    def test_dressing_distribution_creation(self):
        self.assertEqual(self.distribution.quantity, 2)

    def test_dressing_distribution_str(self):
        self.assertIn("Shoes", str(self.distribution))


class ParentWorkContractModelTest(BaseModelTestCase):

    def setUp(self):
        super().setUp()
        self.contract = ParentWorkContract.objects.create(
            parent=self.parent,
            job_role="Cleaner",
            contract_start_date=date.today(),
            status=ParentWorkContract.ACTIVE,
        )

    def test_work_contract_creation(self):
        self.assertEqual(self.contract.parent, self.parent)
        self.assertEqual(self.contract.status, ParentWorkContract.ACTIVE)

    def test_work_contract_str(self):
        self.assertIn("Cleaner", str(self.contract))


class ParentAttendanceModelTest(BaseModelTestCase):

    def setUp(self):
        super().setUp()
        self.contract = ParentWorkContract.objects.create(
            parent=self.parent,
            job_role="Gardener",
            contract_start_date=date.today(),
        )

        self.attendance = ParentAttendance.objects.create(
            work_record=self.contract,
            attendance_date=date.today(),
            status=ParentAttendance.PRESENT,
        )

    def test_attendance_creation(self):
        self.assertEqual(self.attendance.status, ParentAttendance.PRESENT)

    def test_attendance_str(self):
        self.assertIn(str(self.parent), str(self.attendance))


class ParentPerformanceModelTest(BaseModelTestCase):

    def setUp(self):
        super().setUp()
        self.contract = ParentWorkContract.objects.create(
            parent=self.parent,
            job_role="Cook",
            contract_start_date=date.today(),
        )

        self.performance = ParentPerformance.objects.create(
            work_record=self.contract,
            evaluation_date=date.today(),
            rating=4,
            comments="Good performance",
            evaluated_by=self.user,
        )

    def test_performance_creation(self):
        self.assertEqual(self.performance.rating, 4)
        self.assertEqual(self.performance.evaluated_by, self.user)

    def test_performance_str(self):
        self.assertIn(str(self.parent), str(self.performance))