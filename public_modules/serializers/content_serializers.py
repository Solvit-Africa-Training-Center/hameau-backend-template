from rest_framework import serializers
from ..models.content_models import PublicContent, TeamMember, ContactMessage
from programs.models.residentials_models import Child
from programs.models.ifashe_models import SponsoredChild
class PublicContentSerializer(serializers.ModelSerializer):
    calculated_value = serializers.SerializerMethodField()
    
    class Meta:
        model = PublicContent
        fields = [
            "id",
            "category",
            "title",
            "subtitle",
            "value",
            "calculated_value",
            "impact_type",
            "text_content",
            "image",
            "order",
            "is_active",
            "first_name",
            "last_name",
            "email",
            "phone",
            "admin_notes",
            "created_on",
            "fullname"
        ]
        read_only_fields = ["id", "created_on", "fullname", "calculated_value"]

    def get_calculated_value(self, obj):
       
        if obj.category != PublicContent.CATEGORY_IMPACT or not obj.impact_type:
            return obj.value

        base_val = 0
        if obj.value and obj.value.isdigit():
            base_val = int(obj.value)
        
        dynamic_count = 0
        
        try:
            if obj.impact_type == PublicContent.IMPACT_CHILDREN:
                
                
                res_count = Child.objects.filter(status=Child.ACTIVE).count()
                spon_count = SponsoredChild.objects.filter(support_status="ACTIVE").count()
                dynamic_count = res_count + spon_count
                
            elif obj.impact_type == PublicContent.IMPACT_FAMILIES:
                from programs.models.ifashe_models import Family, Sponsorship
                
                dynamic_count = Family.objects.filter(children__sponsorships__status=Sponsorship.ACTIVE).distinct().count()
                
            elif obj.impact_type == PublicContent.IMPACT_YOUTH:
                from programs.models.internships_models import InternshipProgram
               
                dynamic_count = InternshipProgram.objects.filter(status__in=[InternshipProgram.ACTIVE, InternshipProgram.COMPLETED]).count()
                
            elif obj.impact_type == PublicContent.IMPACT_YEARS:
                from django.utils import timezone
                if obj.value and obj.value.isdigit():
                    start_year = int(obj.value)
                    current_year = timezone.now().year
                
                    dynamic_count = max(0, current_year - start_year)
                
        except Exception as e:
            
            print(f"Error calculating dynamic stats: {e}")
            pass


        if obj.impact_type == PublicContent.IMPACT_YEARS:
             return str(dynamic_count)

        total = base_val + dynamic_count
        return str(total)

class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = [
            "id",
            "name",
            "title",
            "image",
            "order",
            "is_active",
        ]
        read_only_fields = ["id"]

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "reason",
            "message",
            "created_on",
        ]
        read_only_fields = ["id", "created_on"]

    def create(self, validated_data):
        instance = super().create(validated_data)
        try:
            from utils.emails import send_contact_message_email
            send_contact_message_email(instance)
        except Exception as e:
            print(f"Failed to send email: {e}")
        return instance

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
