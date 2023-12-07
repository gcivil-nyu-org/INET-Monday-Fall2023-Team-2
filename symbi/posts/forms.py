from django import forms

from .models import ActivityPost, Comment
from main.models import InterestTag


class NewPostForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": """px-4 py-2 border focus:ring-gray-500 focus:border-gray-900
                w-full sm:text-sm border-gray-300 rounded-md focus:outline-none text-gray-600"""
            }
        )
    )
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": """px-4 py-2 border focus:ring-gray-500 focus:border-gray-900
                w-full sm:text-sm border-gray-300 rounded-md focus:outline-none text-gray-600"""
            }
        )
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=InterestTag.objects.all(),
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "w-1/2 p-2 border border-gray-300 rounded max-h-52 overflow-y-auto"
            }
        ),
    )

    class Meta:
        model = ActivityPost
        fields = ["title", "description", "tags"]

    def clean_title(self):
        title = self.cleaned_data.get("title")
        if not title:
            raise forms.ValidationError("Title cannot be empty.")
        elif len(title.strip()) == 0:
            raise forms.ValidationError("Title cannot consist only of spaces.")
        elif len(title) < 10:
            raise forms.ValidationError("Title must be at least 10 characters long.")
        return title

    def clean_description(self):
        description = self.cleaned_data.get("description")
        if not description:
            raise forms.ValidationError("Description cannot be empty.")
        elif len(description.strip()) == 0:
            raise forms.ValidationError("Title cannot consist only of spaces.")
        elif len(description) < 10:
            raise forms.ValidationError(
                "Description must be at least 10 characters long."
            )
        return description


class EditPostForm(forms.ModelForm):
    title = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": """px-4 py-2 border focus:ring-gray-500 focus:border-gray-900
                w-full sm:text-sm border-gray-300 rounded-md focus:outline-none text-gray-600""",
                "name": "title",
            }
        ),
    )
    description = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={
                "class": """px-4 py-2 border focus:ring-gray-500 focus:border-gray-900
                w-full sm:text-sm border-gray-300 rounded-md focus:outline-none text-gray-600""",
                "name": "description",
            }
        ),
    )
    tags = forms.ModelMultipleChoiceField(
        required=True,
        queryset=InterestTag.objects.all(),
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "w-1/2 p-2 border border-gray-300 rounded max-h-52 overflow-y-auto",
                "name": "tags",
            }
        ),
    )

    class Meta:
        model = ActivityPost
        fields = ["title", "description", "tags"]

    def clean_title(self):
        title = self.cleaned_data.get("title")
        if not title:
            raise forms.ValidationError("Title cannot be empty.")
        elif len(title.strip()) == 0:
            raise forms.ValidationError("Title cannot consist only of spaces.")
        elif len(title) < 10:
            raise forms.ValidationError("Title must be at least 10 characters long.")
        return title

    def clean_description(self):
        description = self.cleaned_data.get("description")
        if not description:
            raise forms.ValidationError("Description cannot be empty.")
        elif len(description.strip()) == 0:
            raise forms.ValidationError("Title cannot consist only of spaces.")
        elif len(description) < 10:
            raise forms.ValidationError(
                "Description must be at least 10 characters long."
            )
        return description

class EditCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["edited_comment"]

    edited_comment = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": """px-4 py-2 border focus:ring-gray-500 focus:border-gray-900
                 w-full sm:text-sm border-gray-300 rounded-md focus:outline-none text-gray-600""",
                "name": "edited_comment",
            }
        )
    )
