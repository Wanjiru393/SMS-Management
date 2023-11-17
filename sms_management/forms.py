from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import MessageTemplate, MessageSubmission
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

from django.contrib.auth import get_user_model
User = get_user_model()

class MessageSubmissionForm(forms.ModelForm):
    edited_template = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(MessageSubmissionForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(MessageSubmissionForm, self).save(commit=False)
        instance.user = self.user
        instance.status = 'pending'
        instance.edited_template = self.cleaned_data.get('edited_template') 
        if commit:
            instance.save()
        return instance

    class Meta:
        model = MessageSubmission
        fields = ['template', 'edited_template']

