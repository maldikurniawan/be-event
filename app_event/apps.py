from django.apps import AppConfig


class AppEventConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app_event"

    def ready(self):
        import app_event.signals
