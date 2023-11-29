from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import PermissionDenied
from django.conf import settings

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    full_name = models.CharField(max_length=100)
    staff_number = models.CharField(max_length=20)
    department = models.CharField(max_length=100)
    station = models.CharField(max_length=100)

    @receiver(post_save, sender=User)
    def create_or_update_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)
        else:
            instance.userprofile.save()

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        print("Saving user profile for:", instance)
        instance.userprofile.save()

class CustomerInformation(models.Model):
    full_name = models.CharField(max_length=100)
    contact = models.CharField(max_length=15,unique=True)
    acc_number =models.CharField(max_length=15, null=True)

class MessageTemplate(models.Model):
    name = models.CharField(max_length=100)
    content = models.TextField()
    issue_type = models.CharField(max_length=100)

class MessageSubmission(models.Model):   #message created from a template and awaiting approval.
    template = models.ForeignKey(MessageTemplate, on_delete=models.CASCADE)
    edited_template = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(CustomerInformation, on_delete=models.CASCADE)
    issue = models.CharField(max_length=200, null=True, blank=True)
    submission_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')

    class Meta:
        permissions = [
            ("can_approve_message", "Can Approve message Submissions"),
            ("cannot_approve_message", "Cannot Approve message Submissions"),
        ]

class BulkSMS(models.Model):   #approved message that is ready to be sent
    sms_id = models.AutoField(primary_key=True)
    messages = models.TextField()
    mobile = models.CharField(max_length=20)
    create_date = models.DateTimeField()
    date_sent = models.DateTimeField(null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    submission = models.ForeignKey(MessageSubmission, on_delete=models.CASCADE)

    class Meta:
        db_table = 'INCMS_INTER_ADMINIS.BULK_SMS'

class Approval(models.Model):   #approval of a MessageSubmission.
    submission = models.ForeignKey(MessageSubmission, on_delete=models.CASCADE)
    approver = models.ForeignKey(User, on_delete=models.CASCADE)
    approval_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Approvals"


# Signal to send a message after approval
@receiver(post_save, sender=Approval)
def send_message_after_approval(sender, instance, **kwargs):
    if instance.submission.status == 'approved':
        recipient = instance.submission.customer.contact
        message = f"Your message has been approved. {instance.submission.bulksms.description}"
        send_sms(recipient, message)

# Function to send an SMS
def send_sms(recipient, message):
    africastalking_username = settings.AF_API_USERNAME
    africastalking_api_key = settings.AF_API_KEY
    Africastalking.initialize(africastalking_username, africastalking_api_key)

    sms = SMS
    try:
        response = sms.send(message, [recipient])
        print(response)
        return True
    except Exception as e:
        print(f"SMS sending failed: {e}")
        return False

class SentMessage(models.Model):   #a message that has been sent.
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(CustomerInformation, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    submission = models.ForeignKey(MessageSubmission, on_delete=models.CASCADE)
    issue_type = models.CharField(max_length=100)

