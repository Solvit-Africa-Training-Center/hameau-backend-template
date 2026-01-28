from django.db import models
from django.utils import timezone
from dateutil.relativedelta import relativedelta
import uuid
from accounts.models import TimeStampedModel, SoftDeleteModel


class Child(TimeStampedModel, SoftDeleteModel):
    MALE = "Male"
    FEMALE = "Female"

    GENDER_CHOICES = [
        (MALE, "Male"),
        (FEMALE, "Female"),
    ]

    ACTIVE = "Active"
    COMPLETED = "Completed"
    LEFT = "Left"
    STATUS_CHOICES = [
        (ACTIVE, "Active"),
        (COMPLETED, "Completed"),
        (LEFT, "Left"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    profile_image = models.ImageField(upload_to="profile_images_children/", blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Active")
    special_needs = models.TextField(blank=True)
    vigilant_contact_name = models.CharField(max_length=100, blank=True)
    vigilant_contact_phone = models.CharField(max_length=20, blank=True)

    class Meta:
        db_table = "children"
        verbose_name = "Child"
        verbose_name_plural = "Children"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if self.start_date and not self.end_date:
            self.end_date = self.start_date + relativedelta(years=2)
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        if self.date_of_birth:
            today = timezone.now().date()
            return (
                today.year
                - self.date_of_birth.year
                - (
                    (today.month, today.day)
                    < (self.date_of_birth.month, self.date_of_birth.day)
                )
            )
        return None


class Caretaker(TimeStampedModel, SoftDeleteModel):
    MALE = "Male"
    FEMALE = "Female"

    GENDER_CHOICES = [
        (MALE, "Male"),
        (FEMALE, "Female"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    role = models.CharField(max_length=50, blank=True)
    hire_date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "caretakers"
        verbose_name = "Caretaker"
        verbose_name_plural = "Caretakers"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class House(TimeStampedModel, SoftDeleteModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    caretaker = models.ForeignKey(
        Caretaker, on_delete=models.CASCADE, related_name="house_caretaker"
    )


class ChildCaretakerAssignment(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(
        Child, on_delete=models.CASCADE, related_name="caretaker_assignments"
    )
    house = models.ForeignKey(
        House, on_delete=models.CASCADE, related_name="house_assignments"
    )
    assigned_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "child_caretaker_assignments"
        verbose_name = "Child Caretaker Assignment"
        verbose_name_plural = "Child Caretaker Assignments"

    def __str__(self):
        return f"{self.child} - {self.house}"


class EducationInstitution(TimeStampedModel):
    SCHOOL = "School"
    TVET = "TVET"
    ONLINE = "Online"
    OTHER = "Other"

    TYPE_CHOICES = [
        (SCHOOL, "School"),
        (TVET, "TVET"),
        (ONLINE, "Online"),
        (OTHER, "Other"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(max_length=255, blank=True)

    class Meta:
        db_table = "education_institutions"
        verbose_name = "Education Institution"
        verbose_name_plural = "Education Institutions"

    def __str__(self):
        return self.name


class EducationProgram(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(
        EducationInstitution, on_delete=models.CASCADE, related_name="programs"
    )
    program_name = models.CharField(max_length=200)
    program_level = models.CharField(
        max_length=100, blank=True, help_text="Primary, Secondary, Vocational, etc."
    )
    cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, help_text="Free for Saint Kizito"
    )

    class Meta:
        db_table = "education_programs"
        verbose_name = "Education Program"
        verbose_name_plural = "Education Programs"

    def __str__(self):
        return f"{self.program_name} - {self.institution.name}"


class ChildEducation(TimeStampedModel):
    ACTIVE = "Active"
    COMPLETED = "Completed"
    DISCONTINUED = "Discontinued"

    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Completed", "Completed"),
        ("Discontinued", "Discontinued"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(
        Child, on_delete=models.CASCADE, related_name="education_records"
    )
    program = models.ForeignKey(
        EducationProgram, on_delete=models.CASCADE, related_name="enrolled_children"
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "child_education"
        verbose_name = "Child Education"
        verbose_name_plural = "Child Education Records"

    def __str__(self):
        return f"{self.child} - {self.program.program_name}"


class ChildInsurance(TimeStampedModel):
    PAID = "Paid"
    PENDING = "Pending"
    OVERDUE = "Overdue"

    PAYMENT_STATUS_CHOICES = [
        ("Paid", "Paid"),
        ("Pending", "Pending"),
        ("Overdue", "Overdue"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(
        Child, on_delete=models.CASCADE, related_name="insurance_records"
    )
    provider_name = models.CharField(max_length=200)
    insurance_type = models.CharField(
        max_length=100, blank=True, help_text="Mutuelle de Santé, etc."
    )
    insurance_number = models.CharField(max_length=100, unique=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = "child_insurance"
        verbose_name = "Child Insurance"
        verbose_name_plural = "Child Insurance Records"

    def __str__(self):
        return f"{self.child} - {self.provider_name}"


class FoodSupplier(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(max_length=255, blank=True)
    address = models.TextField(blank=True)

    class Meta:
        db_table = "food_suppliers"
        verbose_name = "Food Supplier"
        verbose_name_plural = "Food Suppliers"

    def __str__(self):
        return self.name


class FoodItem(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier = models.ForeignKey(
        FoodSupplier, on_delete=models.CASCADE, related_name="food_items"
    )
    purchase_date = models.DateField()
    item_description = models.TextField(blank=True)
    quantity = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    unit_cost = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    class Meta:
        db_table = "food_items"
        verbose_name = "Food Item"
        verbose_name_plural = "Food Items"

    def __str__(self):
        return f"{self.item_description[:50]} - {self.supplier.name}"

    @property
    def total_cost(self):
        if self.quantity and self.unit_cost:
            return self.quantity * self.unit_cost
        return 0


class HealthRecord(TimeStampedModel):
    MEDICAL_VISIT = "medical_visit"
    VACCINATION = "Vaccination"
    ILLNESS = "Illness"

    RECORD_TYPE_CHOICES = [
        (MEDICAL_VISIT, "Medical Visit"),
        (VACCINATION, "Vaccination"),
        (ILLNESS, "Illness"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(
        Child, on_delete=models.CASCADE, related_name="health_records"
    )
    record_type = models.CharField(max_length=50, choices=RECORD_TYPE_CHOICES)
    visit_date = models.DateField()
    diagnosis = models.TextField(blank=True)
    treatment = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "health_records"
        verbose_name = "Health Record"
        verbose_name_plural = "Health Records"

    def __str__(self):
        return f"{self.child} - {self.record_type} on {self.visit_date}"


class ResidentialFinancialPlan(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(
        Child, on_delete=models.CASCADE, related_name="financial_plans"
    )
    month = models.DateField()
    year = models.DateField()
    education_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    food_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    insurance_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_costs = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "residential_financial_plans"
        verbose_name = "Residential Financial Plan"
        verbose_name_plural = "Residential Financial Plans"

    def __str__(self):
        return f"{self.child} - {self.month}/{self.year}"

    @property
    def total_cost(self):
        return (
            self.education_cost
            + self.food_cost
            + self.insurance_cost
            + self.other_costs
        )
