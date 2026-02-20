
from django.db import models
import uuid
from accounts.models import TimeStampedModel


class PublicContent(TimeStampedModel):
    CATEGORY_IMPACT = "IMPACT"
    CATEGORY_TEAM = "TEAM"
    CATEGORY_SUCCESS_STORY = "SUCCESS_STORY"
    CATEGORY_CONTACT_INFO = "CONTACT_INFO"
    CATEGORY_CONTACT_MESSAGE = "CONTACT_MESSAGE"

    CATEGORY_CHOICES = [
        (CATEGORY_IMPACT, "Impact Statistic"),
        (CATEGORY_TEAM, "Team Member"),
        (CATEGORY_SUCCESS_STORY, "Success Story"),
        (CATEGORY_CONTACT_INFO, "Contact Info"),
        (CATEGORY_CONTACT_MESSAGE, "Contact Message"),
    ]

    IMPACT_CHILDREN = "CHILDREN"
    IMPACT_FAMILIES = "FAMILIES"
    IMPACT_YOUTH = "YOUTH"
    IMPACT_YEARS = "YEARS"

    IMPACT_TYPE_CHOICES = [
        (IMPACT_CHILDREN, "Children Supported"),
        (IMPACT_FAMILIES, "Families Empowered"),
        (IMPACT_YOUTH, "Youth Trained"),
        (IMPACT_YEARS, "Years of Service"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, db_index=True)
    title = models.CharField(max_length=200, help_text=" ")
    subtitle = models.CharField(max_length=200, blank=True, help_text="Team Role")
    value = models.CharField(
        max_length=100,
        blank=True,
        help_text="For Impact Stats: Base integer value (e.g. '500')",
    )
    impact_type = models.CharField(
        max_length=50,
        choices=IMPACT_TYPE_CHOICES,
        blank=True,
        null=True,
        help_text="For Impact Stats: Type of statistic to calculate",
    )
    text_content = models.TextField(
        blank=True,
        help_text="For Success Stories or Message Body/Address",
    )
    image = models.ImageField(
        upload_to="public_content/", blank=True, null=True, help_text="For Team / Success Stories"
    )
    order = models.IntegerField(default=0, help_text="Display order")
    is_active = models.BooleanField(default=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "public_content"
        ordering = ["category", "order", "-created_on"]
        verbose_name = "Public Content"
        verbose_name_plural = "Public Contents"

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"

    @property
    def fullname(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.title


class ContactMessage(TimeStampedModel):


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100, help_text="First name of the sender")
    last_name = models.CharField(max_length=100, help_text="Last name of the sender")
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    REASON_QUESTION = "QUESTION"
    REASON_PARTNERSHIP = "PARTNERSHIP"
    REASON_SUPPORT = "SUPPORT"
    REASON_CHOICES = [
        (REASON_QUESTION, "General Question"),
        (REASON_PARTNERSHIP, "Partnership"),
        (REASON_SUPPORT, "Need Support"),
    ]

    reason = models.CharField(max_length=50, choices=REASON_CHOICES, default=REASON_QUESTION, help_text="Reason to contact")
    message = models.TextField(default="")
    
    admin_notes = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "contact_messages"
        ordering = ["-created_on"]
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.reason}"

    @property
    def fullname(self):
        return f"{self.first_name} {self.last_name}".strip()


class TeamMember(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, help_text="Team member name")
    title = models.CharField(max_length=100, help_text="Job Title")
    image = models.ImageField(upload_to="team_images/", blank=True, null=True)
    order = models.IntegerField(default=0, help_text="Display order")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "team_members"
        ordering = ["order", "name"]
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"

    def __str__(self):
        return f"{self.name} - {self.title}"


class SuccessStory(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, help_text="Story Title")
    subtitle = models.CharField(max_length=200, blank=True, null=True, help_text="Story Subtitle")
    story = models.TextField(help_text="The success story content")
    image = models.ImageField(upload_to="success_stories/", blank=True, null=True)
    order = models.IntegerField(default=0, help_text="Display order")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "success_stories"
        ordering = ["order", "-created_on"]
        verbose_name = "Success Story"
        verbose_name_plural = "Success Stories"

    def __str__(self):
        return self.title
