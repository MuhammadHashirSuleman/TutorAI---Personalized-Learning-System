from django.apps import AppConfig


class ProgressConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.progress'
    verbose_name = 'Progress Tracking'
    
    def ready(self):
        """Initialize app-specific configurations"""
        # Import any signals here if needed
        pass
