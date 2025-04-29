from django.forms import RadioSelect, TextInput, Textarea
from django.forms.models import ModelForm

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
            'content': Textarea(attrs={'class': 'w-full'})
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.bulletin = self.user.profile.bulletin
        if commit:
            instance.save()
        return instance

    def clean(self):
        pass


class BulletinForm(ModelForm):
    class Meta:
        model = Bulletin
        fields = ['title', 'description']