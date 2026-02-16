from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from public_modules.models import GalleryCategory, GalleryMedia


class GalleryCategorySerializer(serializers.ModelSerializer):  
    media_count = serializers.SerializerMethodField()
    
    class Meta:
        model = GalleryCategory
        fields = [
            'id', 
            'name', 
            'description', 
            'created_on', 
            'updated_on',
            'media_count'
        ]
        read_only_fields = ['id', 'created_on', 'updated_on']
    
    @extend_schema_field(OpenApiTypes.INT)
    def get_media_count(self, obj):
        return obj.media_items.count()


class GalleryMediaSerializer(serializers.ModelSerializer):    
    category_name = serializers.CharField(source='category.name', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)
    media_url = serializers.FileField(required=True)
    
    class Meta:
        model = GalleryMedia
        fields = [
            'id',
            'category',
            'category_name',
            'title',
            'description',
            'media_url',
            'is_public',
            'uploaded_by',
            'uploaded_by_name',
            'created_on',
            'updated_on'
        ]
        read_only_fields = ['id', 'uploaded_by', 'created_on', 'updated_on']
    
    def create(self, validated_data):    
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)


class GalleryMediaListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = GalleryMedia
        fields = [
            'id',
            'category',
            'category_name',
            'title',
            'media_url',
            'is_public',
            'created_on'
        ]


class BulkGalleryMediaUploadSerializer(serializers.Serializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=GalleryCategory.objects.all(),
        required=True,
        help_text="UUID of the category to upload images to"
    )
    images = serializers.ListField(
        child=serializers.FileField(allow_empty_file=False),
        required=True,
        min_length=1,
        max_length=50,
        help_text="List of image files (max 50, 10MB each)"
    )
    is_public = serializers.BooleanField(
        default=True,
        help_text="Make all uploaded images public"
    )
    title_prefix = serializers.CharField(
        max_length=100, 
        required=False,
        help_text="Optional prefix for auto-generated titles (e.g., 'Event 2024')"
    )
    description = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text="Common description for all images"
    )
    
    def validate_images(self, value):
        """Validate that all files are valid images"""
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        valid_mime_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        
        for image in value:
            # Check file extension
            file_ext = image.name.lower().split('.')[-1]
            if f'.{file_ext}' not in valid_extensions:
                raise serializers.ValidationError(
                    f"File {image.name} has invalid extension. "
                    f"Allowed: {', '.join(valid_extensions)}"
                )
            
            # Check MIME type if available
            if hasattr(image, 'content_type') and image.content_type:
                if image.content_type not in valid_mime_types:
                    raise serializers.ValidationError(
                        f"File {image.name} has invalid MIME type: {image.content_type}"
                    )
            
            # Check file size (max 10MB per image)
            max_size = 10 * 1024 * 1024  # 10MB
            if image.size > max_size:
                raise serializers.ValidationError(
                    f"File {image.name} exceeds maximum size of 10MB"
                )
        
        return value
    
    def create(self, validated_data):    
        category = validated_data['category']
        images = validated_data['images']
        is_public = validated_data.get('is_public', True)
        title_prefix = validated_data.get('title_prefix', '')
        description = validated_data.get('description', '')
        user = self.context['request'].user
        
        created_media = []
        
        for index, image in enumerate(images, start=1):
            # Generate title from filename if no prefix provided
            if title_prefix:
                title = f"{title_prefix} {index}"
            else:
                # Use original filename without extension
                title = image.name.rsplit('.', 1)[0]
            
            media = GalleryMedia.objects.create(
                category=category,
                title=title,
                description=description,
                media_url=image,
                is_public=is_public,
                uploaded_by=user
            )
            created_media.append(media)
        
        return created_media


class BulkUploadResponseSerializer(serializers.Serializer):   
    message = serializers.CharField(help_text="Success message")
    count = serializers.IntegerField(help_text="Number of images uploaded")
    media_items = GalleryMediaListSerializer(many=True, help_text="List of uploaded media items")


class GalleryCategoryDetailSerializer(serializers.ModelSerializer):
    media_items = GalleryMediaListSerializer(many=True, read_only=True)
    media_count = serializers.SerializerMethodField()
    
    class Meta:
        model = GalleryCategory
        fields = [
            'id',
            'name',
            'description',
            'created_on',
            'updated_on',
            'media_count',
            'media_items'
        ]
        read_only_fields = ['id', 'created_on', 'updated_on']
    
    @extend_schema_field(OpenApiTypes.INT)
    def get_media_count(self, obj):
        return obj.media_items.count()


class CategoryStatsSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    media_count = serializers.IntegerField()
    public_media_count = serializers.IntegerField()


class CategoryStatsResponseSerializer(serializers.Serializer):
    total_categories = serializers.IntegerField()
    categories = CategoryStatsSerializer(many=True)