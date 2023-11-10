from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import SocialUser, InterestTag

# from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    username = forms.CharField(max_length=30)
    email = forms.EmailField(required=True)

    class Meta:
        model = SocialUser
        fields = ["username", "full_name", "email", "password1", "password2"]

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if SocialUser.objects.filter(username=username).exists():
            raise forms.ValidationError(
                "This username is already taken. Please choose a different one."
            )
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        email_domain = email.split("@")[1]

        if email_domain != "nyu.edu":
            raise forms.ValidationError(
                "Invalid email domain. Please use an NYU email address to sign up."
            )
        elif SocialUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already associated with an account.")

        return email


class CreateProfileForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=InterestTag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Interest",
    )

    date_of_birth = forms.DateField(
        label="Date of Birth",
        required=True,
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"],
    )

    major = forms.CharField(
        initial="",
    )

    class Meta:
        model = SocialUser
        fields = ["date_of_birth", "age", "major", "pronouns", "tags"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"
        self.fields["tags"].widget.attrs["class"] = "tags-select"
        self.fields["age"].widget.attrs["class"] = "form-control age-field"
