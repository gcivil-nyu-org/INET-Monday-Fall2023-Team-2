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


class EditPostForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": """px-4 py-2 border focus:ring-gray-500 focus:border-gray-900
                w-full sm:text-sm border-gray-300 rounded-md focus:outline-none text-gray-600""",
                "name": "title",
            }
        )
    )
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": """px-4 py-2 border focus:ring-gray-500 focus:border-gray-900
                w-full sm:text-sm border-gray-300 rounded-md focus:outline-none text-gray-600""",
                "name": "description",
            }
        )
    )
    tags = forms.ModelMultipleChoiceField(
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

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # You can customize the form's appearance here if needed
    #
    # def clean_text(self):
    #     text = self.cleaned_data['text']
    #     # You can add additional validation for the text if needed
    #     return text
