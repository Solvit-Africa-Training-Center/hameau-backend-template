from datetime import date
from decimal import Decimal

from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APITestCase

from programs.models import (
    Child,
    Caretaker,
    House,
    ChildCaretakerAssignment,
    EducationInstitution,
    EducationProgram,
    ChildEducation,
    ChildInsurance,
    FoodSupplier,
    FoodItem,
    HealthRecord,
    ResidentialFinancialPlan,
)


@override_settings(MEDIA_ROOT="/tmp/test_media/")
class ChildrenModelsTest(APITestCase):
    def setUp(self):
        today = timezone.now().date()

        self.child = Child.objects.create(
            first_name="Arnold",
            last_name="Cikuru",
            date_of_birth=date(today.year - 10, today.month, today.day),
            gender=Child.FEMALE,
            start_date=today,
            end_date=today,
            status=Child.ACTIVE,
        )

       
        self.caretaker = Caretaker.objects.create(
            first_name="Armand",
            last_name="Cito",
            gender=Caretaker.MALE,
            phone="+250700000000",
            hire_date=today,
            is_active=True,
        )

        self.house = House.objects.create(
            caretaker=self.caretaker
        )

        self.assignment = ChildCaretakerAssignment.objects.create(
            child=self.child,
            house=self.house,
            assigned_date=today,
            is_active=True,
        )

        self.institution = EducationInstitution.objects.create(
            name="Saint Kizito School",
            type=EducationInstitution.SCHOOL,
        )

        self.program = EducationProgram.objects.create(
            institution=self.institution,
            program_name="Primary Education",
            program_level="Primary",
            cost=Decimal("0.00"),
        )

        self.child_education = ChildEducation.objects.create(
            child=self.child,
            program=self.program,
            start_date=today,
            status=ChildEducation.ACTIVE,
            cost=Decimal("0.00"),
        )

        self.insurance = ChildInsurance.objects.create(
            child=self.child,
            provider_name="Mutuelle de Santé",
            insurance_type="Health",
            insurance_number="INS-12345",
            start_date=today,
            end_date=today.replace(year=today.year + 1),
            payment_status=ChildInsurance.PAID,
            cost=Decimal("3000.00"),
        )

        self.supplier = FoodSupplier.objects.create(
            name="Local Market",
            phone="+250788888888",
        )

        self.food_item = FoodItem.objects.create(
            supplier=self.supplier,
            purchase_date=today,
            item_description="Rice and Beans",
            quantity=Decimal("10"),
            unit_cost=Decimal("500"),
        )

        self.health_record = HealthRecord.objects.create(
            child=self.child,
            record_type=HealthRecord.MEDICAL_VISIT,
            visit_date=today,
            diagnosis="Flu",
        )

        self.financial_plan = ResidentialFinancialPlan.objects.create(
            child=self.child,
            month=today,
            year=today,
            education_cost=Decimal("20000"),
            food_cost=Decimal("15000"),
            insurance_cost=Decimal("3000"),
            other_costs=Decimal("2000"),
        )

    def test_child_creation_and_properties(self):
        self.assertEqual(str(self.child), "Arnold Cikuru")
        self.assertEqual(self.child.full_name, "Arnold Cikuru")
        self.assertIsInstance(self.child.age, int)

    def test_caretaker_creation(self):
        self.assertEqual(str(self.caretaker), "Armand Cito")
        self.assertEqual(self.caretaker.full_name, "Armand Cito")

    def test_house_creation(self):
        self.assertEqual(self.house.caretaker, self.caretaker)

    def test_child_caretaker_assignment(self):
        self.assertEqual(self.assignment.child, self.child)
        self.assertEqual(self.assignment.house, self.house)
        self.assertIn("Arnold Cikuru", str(self.assignment))

    def test_education_institution_and_program(self):
        self.assertEqual(str(self.institution), "Saint Kizito School")
        self.assertEqual(
            str(self.program),
            "Primary Education - Saint Kizito School"
        )

    def test_child_education(self):
        self.assertEqual(self.child_education.child, self.child)
        self.assertEqual(
            str(self.child_education),
            "Arnold Cikuru - Primary Education"
        )

    def test_child_insurance(self):
        self.assertEqual(
            str(self.insurance),
            "Arnold Cikuru - Mutuelle de Santé"
        )

    def test_food_item_total_cost(self):
        self.assertEqual(self.food_item.total_cost, Decimal("5000"))
        self.assertIn("Local Market", str(self.food_item))

    def test_health_record(self):
        self.assertIn("medical_visit", str(self.health_record))

    def test_residential_financial_plan_total_cost(self):
        self.assertEqual(
            self.financial_plan.total_cost,
            Decimal("40000")
        )
