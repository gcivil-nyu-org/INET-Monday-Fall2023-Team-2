from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import SocialUser

# from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    username = forms.CharField(max_length=30)
    email = forms.EmailField(required=True)
    date_of_birth = forms.DateField(
        widget=forms.SelectDateWidget(years=range(1970, 2030)), required=True
    )
    pronouns = forms.ChoiceField(choices=SocialUser.PRONOUN_CHOICES, required=True)

    class Meta:
        model = SocialUser
        fields = [
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
            "username",
            "date_of_birth",
            "pronouns",
        ]

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if SocialUser.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "This username is already taken. Please choose a different one."
            )
        return username
