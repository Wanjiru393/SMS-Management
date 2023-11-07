from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    staff_number = models.CharField(max_length=20)
    department = models.CharField(max_length=100)
    station = models.CharField(max_length=100)

class UserRegistration(models.Model):
    full_name = models.CharField(max_length=100)
    staff_number = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    station = models.CharField(max_length=100)
    password = models.CharField(max_length=128) 
    confirm_password = models.CharField(max_length=128)

class CustomerInformation(models.Model):
    full_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    meter_number = models.CharField(max_length=20)
    service_type = models.CharField(max_length=50)

class MessageTemplate(models.Model):
    name = models.CharField(max_length=100)
    content = models.TextField()


class TemplateSubmission(models.Model):
    template = models.ForeignKey(MessageTemplate, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    submission_date = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    class Meta:
        permissions = [
            ("can_approve_template", "Can Approve Template Submissions"),
            ("cannot_approve_template", "Cannot Approve Template Submissions"),
        ]
class Approval(models.Model):
    submission = models.ForeignKey(TemplateSubmission, on_delete=models.CASCADE)
    approver = models.ForeignKey(User, on_delete=models.CASCADE)
    approval_date = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(CustomerInformation, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)