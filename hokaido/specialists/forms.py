from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'comment-textarea',
                'rows': 5,
                'placeholder': 'Ваш комментарий, отзыв или предложение...'
            })
        }
        labels = {
            'text': ''
        }
