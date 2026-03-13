from django.apps import AppConfig


class WebsiteContentConfig(AppConfig):
    name = 'website_content'

    def ready(self):
        import website_content.signals
