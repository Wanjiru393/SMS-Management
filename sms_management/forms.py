from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, CustomerInformation, MessageTemplate, TemplateSubmission
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

class UserRegistrationForm(UserCreationForm):
    full_name = forms.CharField(max_length=100)
    staff_number = forms.CharField(max_length=20)
    department = forms.CharField(max_length=100)
    station = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['username', 'full_name', 'staff_number', 'department', 'station', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user_profile = UserProfile(user=user, full_name=self.cleaned_data['full_name'], staff_number=self.cleaned_data['staff_number'], department=self.cleaned_data['department'], station=self.cleaned_data['station'])
        if commit:
            user.save()
            user_profile.save()
        return user

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
        fields = ['template', 'user', 'status'] 

