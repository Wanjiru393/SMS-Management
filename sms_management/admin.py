from django.contrib import admin
from .models import UserProfile,CustomerInformation, MessageTemplate, TemplateSubmission, Message, BulkSMS, Approval


admin.site.register(UserProfile)
admin.site.register(CustomerInformation)
admin.site.register(MessageTemplate)
admin.site.register(TemplateSubmission)
admin.site.register(Message)
admin.site.register(BulkSMS)
admin.site.register(Approval)



