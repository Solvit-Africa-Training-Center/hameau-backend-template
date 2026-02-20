from rest_framework import serializers
from ..models.content_models import PublicContent, ContactMessage, TeamMember, SuccessStory
from programs.models.residentials_models import Child
from programs.models.ifashe_models import SponsoredChild, Family
from programs.models.internships_models import InternshipApplication

class PublicContentSerializer(serializers.ModelSerializer):
    value = serializers.SerializerMethodField()

    class Meta:
        model = PublicContent
        fields = [
            'id', 'category', 'title', 'subtitle', 'value', 'impact_type',
            'text_content', 'image', 'order', 'is_active', 'email', 'phone',
            'full_name', 'created_on', 'updated_on'
        ]

    def get_value(self, obj):
      
        if obj.category != PublicContent.CATEGORY_IMPACT:
            return obj.value

        base_value = 0
        if obj.value and obj.value.isdigit():
            base_value = int(obj.value)
        if obj.impact_type == PublicContent.IMPACT_CHILDREN:     # Calculate dynamic counts based on impact_type    # Count from both programs: Child + SponsoredChild
         
            child_count = Child.objects.filter(is_deleted=False).count()
            sponsored_child_count = SponsoredChild.objects.filter(is_deleted=False).count()
            return str(base_value + child_count + sponsored_child_count) + "+"

        elif obj.impact_type == PublicContent.IMPACT_FAMILIES:
            family_count = Family.objects.filter(is_deleted=False).count()
            return str(base_value + family_count) + "+"

        elif obj.impact_type == PublicContent.IMPACT_YOUTH:
            
            youth_trained_count = InternshipApplication.objects.filter(status=InternshipApplication.APPROVED).count()
            return str(base_value + youth_trained_count) + "+"

        elif obj.impact_type == PublicContent.IMPACT_YEARS:

            return str(base_value) + "+"

        return obj.value

class ContactMessageSerializer(serializers.ModelSerializer):
    fullname = serializers.CharField(read_only=True)

    class Meta:
        model = ContactMessage
        fields = [
            'id', 'first_name', 'last_name', 'email', 'phone', 'reason',
            'message', 'fullname', 'created_on'
        ]

class TeamMemberSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='name', read_only=True)
    member_jobtitle = serializers.CharField(source='title', read_only=True)
    member_image = serializers.ImageField(source='image', read_only=True)

    class Meta:
        model = TeamMember
        fields = [
            'id', 'member_name', 'member_jobtitle', 'member_image', 'order', 'is_active', 'created_on'
        ]

class SuccessStorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SuccessStory
        fields = [
            'id', 'title', 'subtitle', 'story', 'image', 'order', 'is_active', 'created_on'
        ]
