import re

from ckeditor.widgets import CKEditorWidget
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.forms import RadioSelect, TextInput, Textarea
from django.forms.models import ModelForm
from django.forms.widgets import HiddenInput
from django.utils import timezone
from django_ckeditor_5.widgets import CKEditor5Widget

from content.models import Article, Bulletin


class ArticleForm(ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'subtitle', 'description', 'content', 'status', 'visibility']
        widgets = {
            'status': RadioSelect,
            'visibility': RadioSelect,
            'title': TextInput(attrs={'class': 'form-control'}),
            'subtitle': TextInput(attrs={'class': 'form-control'}),
            'description': Textarea(attrs={'class': 'w-full', 'rows': 3}),
            'content': CKEditor5Widget(attrs={'class': 'django_ckeditor_5'}, config_name='default'),
        }
        error_messages = {
            'content': {
                'required': "Obsah článku je povinný.",
            }
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields["content"].required = True

        if user:
            try:
                self.fields['bulletin'].initial = user.profile.bulletin
                self.fields['bulletin'].disabled = True
            except AttributeError:
                # User profile or bulletin doesn't exist yet
                pass

        self.fields['status'].choices = [
            ('draft', 'Draft'),
            ('published', 'Published'),
        ]

    def clean_content(self):
        content = self.cleaned_data['content']

        if not content or content.strip() == '':
            raise ValidationError("Obsah článku je povinný.")

        text_only = re.sub(r'<[^>]*>', '', content)
        text_only = text_only.replace('&nbsp;', ' ').strip()

        if not text_only:
            raise ValidationError("Obsah článku je povinný.")

        return content


class ArticleEvaluationForm(ModelForm):
    class Meta:
        model = Article
        fields = ['evaluation']
        widgets = {'evaluation': RadioSelect}
        labels = {'evaluation': ''}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['evaluation'].choices = [
            ('approved', 'Schválené'),
            ('rejected', 'Zamietnuté'),
        ]


class BulletinForm(ModelForm):
    class Meta:
        model = Bulletin
        fields = ['title', 'description', 'slug']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            try:
                self.fields['owner'].initial = user.profile
                self.fields['owner'].disabled = True
            except AttributeError:
                # User profile doesn't exist yet
                pass