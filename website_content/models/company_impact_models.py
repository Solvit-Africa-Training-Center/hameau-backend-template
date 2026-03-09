import uuid

from django.db import models

class CompanyImpact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    children_supported = models.CharField(max_length=255)
    years_of_service = models.CharField(max_length=255)
    families_strengthened = models.CharField(max_length=255)
    communities_impacted = models.CharField(max_length=255)
    schools_supported = models.CharField(max_length=255)
    youth_trained = models.CharField(max_length=255)
    success_rate = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    class Meta:
        verbose_name = "Company Impact"
        verbose_name_plural = "Company Impact"
        
    def __str__(self):
        return str(self.children_supported)