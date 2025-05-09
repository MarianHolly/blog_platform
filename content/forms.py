from ckeditor.widgets import CKEditorWidget
from django.forms import RadioSelect, TextInput, Textarea
from django.forms.models import ModelForm
from django.forms.widgets import HiddenInput
from django.utils import timezone

from content.models import Article, Bulletin


class ArticleForm(ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'subtite', 'description', 'content', 'status', 'visibility']
        widgets = {
            'status': RadioSelect,
            'visibility': RadioSelect,
            'title': TextInput(attrs={'class': 'form-control'}),
            'subtite': TextInput(attrs={'class': 'form-control'}),
            'description': Textarea(attrs={'class': 'w-full', 'rows': 3}),
            'content': CKEditorWidget(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            try:
                self.fields['bulletin'].initial = user.profile.bulletin
                self.fields['bulletin'].disabled = True
            except:
                pass

    def save(self, commit=True):
        article = super().save(commit=False)

        if article.status == 'published' and article.published is None:
            article.published = timezone.now()

        if commit:
            article.save()

        return article


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
            except:
                pass