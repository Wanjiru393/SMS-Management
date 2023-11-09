from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    staff_number = models.CharField(max_length=20)
    department = models.CharField(max_length=100)
    station = models.CharField(max_length=100)

class CustomerInformation(models.Model):
    full_name = models.CharField(max_length=100)
    contact = models.CharField(max_length=15,unique=True)
    acc_number =models.CharField(max_length=15, null=True)


class MessageTemplate(models.Model):
    name = models.CharField(max_length=100)
    content = models.TextField()
    issue_type = models.CharField(max_length=100)

class TemplateSubmission(models.Model):
    template = models.ForeignKey(MessageTemplate, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    submission_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')

    class Meta:
        permissions = [
            ("can_approve_template", "Can Approve Template Submissions"),
            ("cannot_approve_template", "Cannot Approve Template Submissions"),
        ]

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(CustomerInformation, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    submission = models.ForeignKey(TemplateSubmission, on_delete=models.CASCADE)
    bulk_sms = models.ForeignKey(BulkSMS, on_delete=models.CASCADE)

class Role(models.Model):
    name = models.CharField(max_length=100)

class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

class BulkSMS(models.Model):
    sms_id = models.IntegerField(primary_key=True)
    messages = models.TextField()
    mobile = models.CharField(max_length=20)
    create_date = models.DateTimeField()
    date_sent = models.DateTimeField()
    user_id = models.CharField(max_length=50)
    description = models.CharField(max_length=200)

    class Meta:
        db_table = 'INCMS_INTER_ADMINIS.BULK_SMS'