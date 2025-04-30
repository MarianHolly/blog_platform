from django.forms import RadioSelect, TextInput, Textarea
from django.forms.models import ModelForm
from django.forms.widgets import HiddenInput

from content.models import Article, Bulletin


class ArticleForm(ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'subtite', 'description', 'bulletin','content', 'status', 'visibility']
        widgets = {
            'status': RadioSelect,
            'visibility': RadioSelect,
            'title': TextInput(attrs={'class': 'form-control'}),
            'subtite': TextInput(attrs={'class': 'form-control'}),
            'description': Textarea(attrs={'class': 'w-full', 'rows': 3}),
            'content': Textarea(attrs={'class': 'w-full'}),
            'bulletin': HiddenInput(),
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