from django.forms import ModelForm, Textarea

from engagement.models import Comment


class CommentModelForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': 'Zapoj sa do diskusie:'
        }
        widgets = {
            'content': Textarea(attrs={'placeholder': 'Vyjadri svoj názor...'}),
        }