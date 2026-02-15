from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GalleryCategoryViewSet, GalleryMediaViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'gallery-categories', GalleryCategoryViewSet, basename='gallery-category')
router.register(r'gallery-media', GalleryMediaViewSet, basename='gallery-media')

urlpatterns = [
    path('', include(router.urls)),
]

"""
Available Endpoints:

GALLERY CATEGORIES:
- GET    /api/gallery-categories/                 - List all categories
- POST   /api/gallery-categories/                 - Create new category
- GET    /api/gallery-categories/{id}/            - Get specific category with media
- PUT    /api/gallery-categories/{id}/            - Full update category
- PATCH  /api/gallery-categories/{id}/            - Partial update category
- DELETE /api/gallery-categories/{id}/            - Delete category
- GET    /api/gallery-categories/{id}/media/      - Get all media in category
- GET    /api/gallery-categories/stats/           - Get category statistics

GALLERY MEDIA:
- GET    /api/gallery-media/                      - List all media items
- POST   /api/gallery-media/                      - Upload single media
- GET    /api/gallery-media/{id}/                 - Get specific media item
- PUT    /api/gallery-media/{id}/                 - Full update media
- PATCH  /api/gallery-media/{id}/                 - Partial update media
- DELETE /api/gallery-media/{id}/                 - Delete media
- POST   /api/gallery-media/bulk_upload/          - Upload multiple images
- GET    /api/gallery-media/my_uploads/           - Get current user's uploads
- GET    /api/gallery-media/public/               - Get all public media
- POST   /api/gallery-media/{id}/toggle_visibility/ - Toggle public/private

Query Parameters:
- search: Search in title/description/name
- ordering: Sort by fields (e.g., -created_on, title)
- category: Filter by category UUID
- is_public: Filter by public status (true/false)
- uploaded_by: Filter by user ID
"""