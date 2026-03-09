import uuid

from django.db import models

class CompanyInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_name = models.CharField(max_length=255)
    company_description = models.TextField()
    company_address = models.CharField(max_length=255)
    company_phone = models.CharField(max_length=255)
    company_email = models.CharField(max_length=255)
    company_website = models.CharField(max_length=255)
    company_logo = models.ImageField(upload_to='company_info/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    class Meta:
        verbose_name = "Company Info"
        verbose_name_plural = "Company Info"
        
    def __str__(self):
        return str(self.company_name)

class SocialMedia(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    url = models.URLField()
    icon = models.ImageField(upload_to='social_media/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Social Media"
        verbose_name_plural = "Social Media"
        
    def __str__(self):
        return str(self.name)

class WorkingDaysHours(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    day = models.CharField(max_length=255)
    start_hours = models.CharField(max_length=255)
    end_hours = models.CharField(max_length=255)
    close_days = models.BooleanField(default=['Saturday', 'Sunday'])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    class Meta:
        verbose_name = "Working Days Hours"
        verbose_name_plural = "Working Days Hours"
        
    def __str__(self):
        return str(self.day)
    