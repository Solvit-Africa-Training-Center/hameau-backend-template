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
