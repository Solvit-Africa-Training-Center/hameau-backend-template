from django.urls import path, include

from website_content.views.company_impact_views import CompanyImpactCreateView
from website_content.views.company_info_views import CompanyInfoCreateView, SocialMediaCreateView, WorkingDaysHoursCreateView
from website_content.views.contact_us_views import ContactMessageCreateView, ReplyToContactMessageCreateView
from website_content.views.team_views import TeamCreateView
from website_content.views.testimonial_views import TestimonialCreateView
from website_content.views.work_views import WorkCreateView
from website_content.views.we_are_views import WeAreCreateView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"company-impact", CompanyImpactCreateView, basename="company-impact")
router.register(r"company-info", CompanyInfoCreateView, basename="company-info")
router.register(r"contact-us", ContactMessageCreateView, basename="contact-us")
router.register(r"team", TeamCreateView, basename="team")
router.register(r"testimonial", TestimonialCreateView, basename="testimonial")
router.register(r"work", WorkCreateView, basename="work")
router.register(r"we-are", WeAreCreateView, basename="we-are")
router.register(r"social-media", SocialMediaCreateView, basename="social-media")
router.register(r"working-days-hours", WorkingDaysHoursCreateView, basename="working-days-hours")
router.register(r"reply-contact-message", ReplyToContactMessageCreateView, basename="reply-contact-message")
urlpatterns = [
    path('', include(router.urls)),
]
