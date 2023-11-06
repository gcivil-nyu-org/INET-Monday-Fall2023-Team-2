from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from datetime import date
from django.core.exceptions import ValidationError


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    date_of_birth = forms.DateField(widget=forms.SelectDateWidget(years=range(1970, 2030)), required=True)
    
    class Meta:
        model = User
        fields = ["username", "email", "date_of_birth", "password1", "password2"]
        
    
    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data['date_of_birth']
        today = date.today()

        if date_of_birth > today:
            raise ValidationError('Date of birth must be in the past.')

        if today.year - date_of_birth.year < 18:
            raise ValidationError('Must be 18 years of age or older to sign up.')

        return date_of_birth
    
    
    def clean_email(self):
        email = self.cleaned_data['email']
        email_domain = email.split('@')[1]

        if email_domain != 'nyu.edu':
            raise ValidationError('Invalid email domain. Please use an NYU email address to sign up.')
        elif User.objects.filter(email=email).exists():
            raise ValidationError('Email is already associated with an account.')

        return email
    
    
    def validate_password(password1, password2):
        if len(password1) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        elif password1.isnumeric():
            raise ValidationError('Password cannot be all numeric.')
        elif password1 != password2:
            raise ValidationError('Passwords must match.')
