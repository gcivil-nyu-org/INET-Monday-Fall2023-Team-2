from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import SocialUser, InterestTag

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


class ProfileCreationForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={"placeholder": "First Name"}),
    )
    last_name = forms.CharField(
        max_length=30, widget=forms.TextInput(attrs={"placeholder": ":Last Name"})
    )
    email = forms.EmailField(
        required=True, widget=forms.TextInput(attrs={"placeholder": "Email"})
    )
    date_of_birth = forms.DateField(
        input_formats=["%m/%d/%m/%"],
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "placeholder": "mm-dd-yyyy (DOB)",
            }
        ),
    )
    pronouns = forms.ChoiceField(
        choices=SocialUser.PRONOUN_CHOICES,
    )
    major = forms.CharField(
        max_length=100, widget=forms.TextInput(attrs={"placeholder": "Major"})
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=InterestTag.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "multiselect"}),
    )

    class Meta:
        model = SocialUser
        fields = [
            "first_name",
            "last_name",
            "pronouns",
            "date_of_birth",
            "major",
            "pronouns",
            "tags",
        ]
