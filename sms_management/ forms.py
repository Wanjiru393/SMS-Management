from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'staff_number', 'department', 'station', 'password1', 'password2']
