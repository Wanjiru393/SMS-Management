from django.apps import AppConfig


class SmsManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sms_management'

    def ready(self):
        import sms_management.models 
