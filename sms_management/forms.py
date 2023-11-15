from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, CustomerInformation, MessageTemplate, TemplateSubmission
from django.contrib.auth.models import User

class UserRegistrationForm(UserCreationForm):
    full_name = forms.CharField(max_length=100)
    staff_number = forms.CharField(max_length=20)
    department = forms.CharField(max_length=100)
    station = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['staff_number', 'full_name', 'department', 'station', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['staff_number']
        if commit:
            user.save()
        return user
    
class CustomerInformationForm(forms.Form):
    csv_file = forms.FileField()

class MessageTemplateForm(forms.ModelForm):
    class Meta:
        model = MessageTemplate
        fields = ['name', 'content', 'issue_type']

class TemplateSubmissionForm(forms.ModelForm):
    class Meta:
        model = TemplateSubmission
        fields = ['template', 'user', 'status'] 

