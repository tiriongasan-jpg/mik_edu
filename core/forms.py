from django import forms
from .models import Lecture


class LectureUploadForm(forms.ModelForm):
    class Meta:
        model = Lecture
        fields = ['title', 'module', 'file', 'assigned_groups']
