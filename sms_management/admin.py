from django.contrib import admin
from .models import UserProfile, UserRegistration, CustomerInformation, MessageTemplate, TemplateSubmission, Approval, Message

# Register your models here
admin.site.register(UserProfile)
admin.site.register(UserRegistration)
admin.site.register(CustomerInformation)
admin.site.register(MessageTemplate)
admin.site.register(TemplateSubmission)
admin.site.register(Approval)
admin.site.register(Message)
