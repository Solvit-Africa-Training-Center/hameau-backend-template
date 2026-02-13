import os
import django
import random
from faker import Faker
from datetime import timedelta

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from accounts.models import User
from programs.models.ifashe_models import (
    Family, Parent, SponsoredChild, Sponsorship, School, SchoolSupport, SchoolPayment,
    DressingDistribution, ParentWorkContract, ParentAttendance, ParentPerformance
)

def populate():
    print('Populating database...')
    fake = Faker()
    
    # Create Evaluator User
    evaluator, created = User.objects.get_or_create(
        email='evaluator@example.com',
        defaults={
            'first_name': 'Ifashe',
            'last_name': 'Manager',
            'role': 'ifashe_manager',
            'password': 'password123',
            'is_active': True
        }
    )
    if created:
        evaluator.set_password('password123')
        evaluator.save()
        print("Created evaluator user.")

    # Create Schools
    schools = []
    for _ in range(5):
        school = School.objects.create(
            name=fake.company() + " School",
            address=fake.address(),
            phone=fake.phone_number()[:20],
            email=fake.email()
        )
        schools.append(school)
    print(f'Created {len(schools)} schools')

    # Create Families
    for _ in range(100):
        try:
            family = Family.objects.create(
                family_name=fake.last_name() + " Family",
                address=fake.address(),
                province=fake.state(),
                district=fake.city(),
                sector=fake.city_suffix(),
                cell=fake.street_name(),
                village=fake.street_suffix(),
                family_members=random.randint(2, 8)
            )

            # Create Parents (1 or 2 per family)
            for _ in range(random.randint(1, 2)):
                parent = Parent.objects.create(
                    family=family,
                    first_name=fake.first_name(),
                    last_name=family.family_name.split()[0],
                    relationship=random.choice(['Father', 'Mother', 'Guardian']),
                    phone=fake.phone_number()[:20],
                    national_id=fake.unique.random_number(digits=16),
                    date_of_birth=fake.date_of_birth(minimum_age=25, maximum_age=60)
                )

                # Parent Work Contract (Randomly assigned)
                if random.choice([True, False]):
                    contract = ParentWorkContract.objects.create(
                        parent=parent,
                        job_role=random.choice(['Kitchen Staff', 'Cleaner', 'Gardener', 'Repair']),
                        contract_start_date=fake.date_between(start_date='-1y', end_date='today'),
                        status='Active'
                    )
                    
                    # Parent Attendance
                    for _ in range(5):
                        ParentAttendance.objects.create(
                            work_record=contract,
                            attendance_date=fake.date_between(start_date=contract.contract_start_date, end_date='today'),
                            status=random.choice(['Present', 'Absent', 'Late']),
                            notes=fake.sentence()
                        )
                    
                    # Parent Performance
                    if random.choice([True, False]):
                        ParentPerformance.objects.create(
                            work_record=contract,
                            evaluation_date=fake.date_between(start_date=contract.contract_start_date, end_date='today'),
                            rating=random.randint(1, 5),
                            comments=fake.paragraph(),
                            evaluated_by=evaluator
                        )

            # Create Sponsored Children (1 to 3 per family)
            for _ in range(random.randint(1, 3)):
                child = SponsoredChild.objects.create(
                    family=family,
                    first_name=fake.first_name(),
                    last_name=family.family_name.split()[0],
                    date_of_birth=fake.date_of_birth(minimum_age=5, maximum_age=18),
                    gender=random.choice(['Male', 'Female']),
                    school_level=random.choice(['Primary', 'Secondary']),
                    photo_url=fake.image_url()
                )

                # Sponsorship
                Sponsorship.objects.create(
                    child=child,
                    sponsorship_type=random.choice(['Full', 'Partial']),
                    start_date=fake.date_between(start_date='-2y', end_date='-1y'),
                    status='Active'
                )

                # School Support
                support = SchoolSupport.objects.create(
                    child=child,
                    school=random.choice(schools),
                    academic_year='2025-2026',
                    school_fees=random.uniform(50000, 200000),
                    materials_cost=random.uniform(10000, 50000),
                    payment_status=random.choice(['Paid', 'Pending', 'Partial']),
                    notes=fake.sentence()
                )
                
                # School Payments (Randomly add payments for support)
                if support.payment_status in ['Paid', 'Partial']:
                    num_payments = random.randint(1, 3)
                    for _ in range(num_payments):
                        SchoolPayment.objects.create(
                            school_support=support,
                            amount=random.uniform(10000, 50000),
                            payment_date=fake.date_between(start_date='-6m', end_date='today'),
                            receipt_number=fake.bothify(text='REC-####-????'),
                            status='Paid',
                            notes=fake.sentence()
                        )

                # Dressing Distribution
                if random.choice([True, False]):
                    DressingDistribution.objects.create(
                        child=child,
                        distribution_date=fake.date_this_year(),
                        item_type=random.choice(['Uniform', 'Shoes', 'Sportswear']),
                        size=random.choice(['S', 'M', 'L', '32', '34']),
                        quantity=random.randint(1, 2)
                    )
        except Exception as e:
            print(f"Error creating family or related data: {e}")

    print('Successfully populated database with 100 families and related data')

if __name__ == '__main__':
    populate()
