from celery import shared_task
from .models import SMSRequest, SMSLog
from .safaricom_sms_gateway import send_sms_to_safaricom

@shared_task
def process_sms_request(sms_request_id):
    try:
        # Retrieve SMS request from the database
        sms_request = SMSRequest.objects.get(pk=sms_request_id)

        # Send SMS to Safaricom SMS gateway
        success = send_sms_to_safaricom(sms_request.recipient, sms_request.message)

        # Log the result
        SMSLog.objects.create(request=sms_request, success=success)

    except SMSRequest.DoesNotExist:
        # Handle case where SMS request does not exist
        pass
