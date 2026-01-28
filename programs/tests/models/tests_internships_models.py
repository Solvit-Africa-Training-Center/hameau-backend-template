import datetime
from django.test import TestCase

from rest_framework.test import APITestCase

from accounts.models import User
from programs.models import (
    InternshipApplication,
    Department,
    Supervisor,
    InternshipProgram,
    InternshipFeedback,
)


class InternshipApplicationModelTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="admin@gmail.com",
            password="password123",
            first_name="admin",
            last_name="admin",
            phone="+243771234568",
            role=User.ADMIN,
        )

        self.application = InternshipApplication.objects.create(
            first_name="applicant",
            last_name="name",
            email="applicant@gmail.com",
            phone="+250788000000",
            date_of_birth=datetime.date(2000, 1, 1),
            nationality="Rwandan",
            is_in_rwanda=True,
            school_university="University of Rwanda",
            field_of_study="Computer Science",
            status=InternshipApplication.PENDING,
            reviewed_by=self.user,
        )

    def test_application_created(self):
        self.assertEqual(InternshipApplication.objects.count(), 1)

    def test_application_str(self):
        self.assertEqual(
            str(self.application),
            "applicant name - PENDING"
        )

    def test_full_name_property(self):
        self.assertEqual(self.application.full_name, "applicant name")

    def test_default_status(self):
        app = InternshipApplication.objects.create(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
            phone="0788000000",
            date_of_birth=datetime.date(1999, 5, 5),
            nationality="Kenyan",
            is_in_rwanda=False,
            school_university="UoN",
            field_of_study="IT",
        )
        self.assertEqual(app.status, InternshipApplication.PENDING)


class DepartmentModelTest(APITestCase):

    def setUp(self):
        self.department = Department.objects.create(
            name="IT Department",
            description="Handles all IT operations"
        )

    def test_department_created(self):
        self.assertEqual(Department.objects.count(), 1)

    def test_department_str(self):
        self.assertEqual(str(self.department), "IT Department")


class SupervisorModelTest(APITestCase):

    def setUp(self):
        self.department = Department.objects.create(
            name="HR Department"
        )

        self.supervisor = Supervisor.objects.create(
            first_name="Alice",
            last_name="Mukamana",
            email="alice@example.com",
            phone="+250700000000",
            department=self.department,
            is_active=True,
        )

    def test_supervisor_created(self):
        self.assertEqual(Supervisor.objects.count(), 1)

    def test_supervisor_str(self):
        self.assertEqual(str(self.supervisor), "Alice Mukamana")

    def test_supervisor_full_name(self):
        self.assertEqual(self.supervisor.full_name, "Alice Mukamana")

    def test_supervisor_department_relation(self):
        self.assertEqual(self.supervisor.department.name, "HR Department")


class InternshipProgramModelTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="reviewer@example.com",
            password="password123"
        )

        self.department = Department.objects.create(
            name="Engineering"
        )

        self.application = InternshipApplication.objects.create(
            first_name="Eric",
            last_name="Niyonzima",
            email="eric@example.com",
            phone="0788123456",
            date_of_birth=datetime.date(1998, 3, 3),
            nationality="Rwandan",
            is_in_rwanda=True,
            school_university="UR",
            field_of_study="Engineering",
            status=InternshipApplication.ACCEPTED,
            reviewed_by=self.user,
        )

        self.program = InternshipProgram.objects.create(
            application=self.application,
            department=self.department,
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 6, 1),
            status=InternshipProgram.ACTIVE,
        )

    def test_program_created(self):
        self.assertEqual(InternshipProgram.objects.count(), 1)

    def test_program_str(self):
        self.assertEqual(
            str(self.program),
            "Eric Niyonzima - Engineering"
        )

    def test_program_relationships(self):
        self.assertEqual(self.program.application, self.application)
        self.assertEqual(self.program.department, self.department)


class InternshipFeedbackModelTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="intern@example.com",
            password="password123"
        )

        self.department = Department.objects.create(
            name="Finance"
        )

        self.application = InternshipApplication.objects.create(
            first_name="Paul",
            last_name="Kagabo",
            email="paul@example.com",
            phone="0788999999",
            date_of_birth=datetime.date(2001, 7, 7),
            nationality="Rwandan",
            is_in_rwanda=True,
            school_university="AUCA",
            field_of_study="Accounting",
        )

        self.program = InternshipProgram.objects.create(
            application=self.application,
            department=self.department,
            start_date=datetime.date(2024, 2, 1),
            end_date=datetime.date(2024, 8, 1),
            status=InternshipProgram.ACTIVE,
        )

        self.feedback = InternshipFeedback.objects.create(
            internship=self.program,
            feedback_type=InternshipFeedback.INTERN,
            submitted_by=self.user,
            rating=5,
            comments="Great learning experience",
        )

    def test_feedback_created(self):
        self.assertEqual(InternshipFeedback.objects.count(), 1)

    def test_feedback_str(self):
        self.assertEqual(
            str(self.feedback),
            f"{self.program} - INTERN"
        )

    def test_feedback_relationships(self):
        self.assertEqual(self.feedback.internship, self.program)
        self.assertEqual(self.feedback.submitted_by, self.user)

    def test_feedback_rating(self):
        self.assertEqual(self.feedback.rating, 5)
