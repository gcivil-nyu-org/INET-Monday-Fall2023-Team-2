from django import forms

from .models import InterestTag, SocialUser


class SocialUserForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=InterestTag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Interest",
    )

    class Meta:
        model = SocialUser
        fields = ["name", "age", "major", "pronouns", "tags"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"
        self.fields["tags"].widget.attrs["class"] = "tags-select"
        self.fields["age"].widget.attrs["class"] = "form-control age-field"
