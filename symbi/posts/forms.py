from django import forms

from .models import ActivityPost
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
