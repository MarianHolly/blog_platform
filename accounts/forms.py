from django.contrib.auth.forms import UserCreationForm
from django.db.transaction import atomic
from django.forms import CharField
from django.forms.fields import EmailField
from django.forms.widgets import PasswordInput

from accounts.models import Profile


class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        labels = {
            'username': 'Užívateľské meno',
            'first_name': 'Meno',
            'last_name': 'Priezvisko',
            'email': 'E-mail',
        }
        error_messages = {
            'username': {
                'unique': 'Toto užívateľské meno je už obsadené.',
                'required': 'Užívateľské meno je povinné.',
                'max_length': 'Užívateľské meno môže mať maximálne 150 znakov.',
            },
            'first_name': {
                'required': 'Meno je povinné.',
            },
            'last_name': {
                'required': 'Priezvisko je povinné.',
            },
        }

    password1 = CharField(
        widget=PasswordInput(attrs={'placeholder': 'Vyber si silné heslo'}),
        required=True,
        label="Heslo",
        error_messages={
            'required': 'Heslo je povinné.',
        })
    password2 = CharField(
        widget=PasswordInput(attrs={'placeholder': 'Zapamätáš si ho?'}),
        required=True,
        label="Potvrdiť heslo",
        error_messages={
            'required': 'Potvrdenie hesla je povinné.',
        })
    email = EmailField(
        max_length=254,
        help_text='Zadaj prosím platnú emailovu adresu.',
        error_messages={
            'required': 'E-mailová adresa je povinná.',
            'invalid': 'Zadajte platnú e-mailovú adresu.',
        })

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