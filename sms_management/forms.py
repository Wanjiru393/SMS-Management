from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, CustomerInformation, MessageTemplate, TemplateSubmission

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'staff_number', 'department', 'station', 'password1', 'password2']

class CustomerInformationForm(forms.ModelForm):
    class Meta:
        model = CustomerInformation
        fields = ['full_name', 'contact', 'acc_number']

class MessageTemplateForm(forms.ModelForm):
    class Meta:
        model = MessageTemplate
        fields = ['name', 'content']

class TemplateSubmissionForm(forms.ModelForm):
    class Meta:
        model = TemplateSubmission
        fields = ['approved']

