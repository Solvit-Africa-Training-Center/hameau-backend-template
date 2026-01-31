import os
from rest_framework import serializers
from django.utils import timezone
from decimal import Decimal
from ..models import (
    Child,
    ChildProgress,
    ProgressMedia,
    ChildEducation,
    EducationInstitution,
    EducationProgram,
)


class ChildReadSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    end_date = serializers.DateField(read_only=True)

    class Meta:
        model = Child
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "gender",
            "date_of_birth",
            "age",
            "profile_image",
            "start_date",
            "end_date",
            "status",
            "special_needs",
            "vigilant_contact_name",
            "vigilant_contact_phone",
            "story",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "created_on", "updated_on"]


class ChildWriteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Child
        fields = [
            "first_name",
            "last_name",
            "date_of_birth",
            "gender",
            "profile_image",
            "start_date",
            "special_needs",
            "vigilant_contact_name",
            "vigilant_contact_phone",
            "story",
        ]

    def validate_date_of_birth(self, value):
        if value > timezone.now().date():
            raise serializers.ValidationError(
                "Date of birth can not be in the future."
            )
        return value

    def validate_start_date(self, value):
        if value < timezone.now().date().replace(year=timezone.now().year - 10):
            raise serializers.ValidationError(
                "The date seems to be incorrect."
            )
        return value

    def validate(self, attrs):
        date_of_birth = attrs.get('date_of_birth')
        start_date = attrs.get('start_date')        
        if date_of_birth and start_date:
            if start_date < date_of_birth:
                raise serializers.ValidationError({
                    'start_date': "The starting date cannot be older that the date of birth"
                })        
        return attrs


class ProgressMediaWriteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProgressMedia
        fields = [
            "progress_image",
            "progress_video",
        ]
    
    def validate_progress_video(self, video):
        allowed_extensions = [".mp4", ".mov", ".avi", ".mkv"]
        ext = os.path.splitext(video.name)[1].lower()
        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                "Not supported video format. Formats accepted : mp4, mov, avi, mkv."
            )
        return video

    def validate(self, attrs):
        if not attrs.get('progress_image') and not attrs.get('progress_video'):
            raise serializers.ValidationError(
                "Submit at least a video or an image"
            )
        return attrs


class ProgressMediaReadSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ProgressMedia
        fields = [
            "id",
            "progress_image",
            "progress_video",
            "created_on",
        ]
        read_only_fields = ["id", "created_on"]


class ChildProgressWriteSerializer(serializers.ModelSerializer):
    media = ProgressMediaWriteSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = ChildProgress
        fields = [
            "notes",
            "media",
        ]

    def create(self, validated_data):
        media_data = validated_data.pop("media", [])
        
        child = self.context.get('child')
        if not child:
            raise serializers.ValidationError(
                "Child must be specified in context"
            )
        progress = ChildProgress.objects.create(child=child, **validated_data)
        for media in media_data:
            ProgressMedia.objects.create(progress=progress, **media)

        return progress


class ChildProgressReadSerializer(serializers.ModelSerializer):
    progress_media = ProgressMediaReadSerializer(many=True, read_only=True)

    class Meta:
        model = ChildProgress
        fields = [
            "id",
            "notes",
            "progress_media",
            "created_on",
        ]
        read_only_fields = ["id", "created_on"]


class EducationInstitutionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = EducationInstitution
        fields = "__all__"
        read_only_fields = ["id", "created_on", "updated_on"]


class EducationProgramReadSerializer(serializers.ModelSerializer):
    institution = EducationInstitutionSerializer(read_only=True)

    class Meta:
        model = EducationProgram
        fields = "__all__"
        read_only_fields = ["id", "created_on", "updated_on"]


class EducationProgramWriteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = EducationProgram
        fields = [
            "institution",
            "program_name",
            "program_level",
            "cost",
        ]

    def validate_cost(self, value):
        if value is not None and value < Decimal('0'):
            raise serializers.ValidationError(
                "Cost must be positive."
            )
        return value


class ChildEducationWriteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ChildEducation
        fields = [
            "child",
            "program",
            "start_date",
            "end_date",
            "status",
            "cost",
            "notes",
        ]

    def validate_cost(self, value):
        if value is not None and value < Decimal('0'):
            raise serializers.ValidationError(
                "Cost must be positive"
            )
        return value

    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        
        if start_date and end_date:
            if end_date < start_date:
                raise serializers.ValidationError({
                    'end_date': "End-date cannot come before start date"
                })
        
        return attrs


class ChildEducationReadSerializer(serializers.ModelSerializer):
    program = EducationProgramReadSerializer(read_only=True)
    child = ChildReadSerializer(read_only=True)

    class Meta:
        model = ChildEducation
        fields = [
            "id",
            "child",
            "program",
            "start_date",
            "end_date",
            "status",
            "cost",
            "notes",
            "created_on",
            "updated_on",
        ]
        read_only_fields = ["id", "created_on", "updated_on"]