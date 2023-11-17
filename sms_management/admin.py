from django.contrib import admin
from .models import UserProfile,CustomerInformation, MessageTemplate, MessageSubmission, SentMessage, BulkSMS, Approval

admin.site.register(UserProfile)
admin.site.register(CustomerInformation)
admin.site.register(MessageTemplate)
admin.site.register(MessageSubmission)
admin.site.register(SentMessage)
admin.site.register(BulkSMS)
admin.site.register(Approval)