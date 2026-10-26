
from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title',
            'slug',
            'content',
            'cover_image',
            'category',
            'tags',
            'status',
        ]
        widgets = {
            'title': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'slug': forms.TextInput(
                attrs={'class': 'form-control'}
            ),
            'content': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 8}
            ),
            'cover_image': forms.ClearableFileInput(
                attrs={'class': 'form-control'}
            ),
            'category': forms.Select(
                attrs={'class': 'form-select'}
            ),
            'tags': forms.SelectMultiple(
                attrs={'class': 'form-select'}
            ),
            'status': forms.Select(
                attrs={'class': 'form-select'}
            ),
        }
