from django.contrib.auth.forms import UserCreationForm
from django.db.transaction import atomic
from django.forms import CharField
from django.forms.fields import EmailField
from django.forms.widgets import PasswordInput

from accounts.models import Profile


class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    password1 = CharField(widget=PasswordInput(attrs={'placeholder': 'Vyber si silné heslo'}), required=True, label="Heslo")
    password2 = CharField(widget=PasswordInput(attrs={'placeholder': 'Zapamätáš si ho?'}), required=True, label="Potvrdiť heslo")
    email = EmailField(max_length=254, help_text='Zadaj prosím platnú emailovu adresu.')

    @atomic
    def save(self, commit=True):
        self.instance.is_active = True
        user = super().save(commit)

        profile = Profile(
            user=user
        )

        if commit:
            profile.save()
        return user