# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    user_type = forms.ChoiceField(choices=CustomUser.user_type_choices, required=True)
    gender = forms.CharField(max_length=10, required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'user_type', 'gender', 'password1', 'password2']
