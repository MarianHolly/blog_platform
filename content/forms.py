from django.forms import RadioSelect, TextInput, Textarea
from django.forms.models import ModelForm

from content.models import Article, Bulletin


class ArticleForm(ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'subtite', 'description', 'content', 'bulletin', 'status', 'visibility']
        widgets = {
            'status': RadioSelect,
            'visibility': RadioSelect,
            'title': TextInput(attrs={'class': 'form-control'}),
            'subtite': TextInput(attrs={'class': 'form-control'}),
            'description': Textarea(attrs={'class': 'w-full', 'rows': 3}),
            'content': Textarea(attrs={'class': 'w-full'})
        }

    #This form will be accessible only for user with role 'writer'
    #TODO: User is provided, take bulletin from user.profile.bulletin


class BulletinForm(ModelForm):
    class Meta:
        model = Bulletin
        fields = ['title', 'description']