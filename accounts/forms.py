from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, RegexValidator
from django.db.transaction import atomic
from django.forms import Form, CharField, ModelForm, ImageField, FileField
from django.forms.fields import EmailField, FileInput
from django.forms.widgets import PasswordInput, Textarea, ClearableFileInput
from PIL import Image

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

    username = CharField(
        validators=[
            RegexValidator(r'^[a-zA-Z0-9_]+$', 'Username contains invalid characters')
        ]
    )
    password1 = CharField(
        widget=PasswordInput(attrs={'autocomplete': 'new-password', 'placeholder': 'Vyber si silné heslo'}),
        required=True,
        label="Heslo",
        error_messages={
            'required': 'Heslo je povinné.',
        })
    password2 = CharField(
        widget=PasswordInput(attrs={'autocomplete': 'new-password', 'placeholder': 'Zapamätáš si ho?'}),
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

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already registered")
        return email

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


def validate_image_size(value):
    if value.size > 5 * 1024 * 1024:  # 5MB limit
        raise ValidationError("Image too large (max 5MB)")


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['biography', 'avatar']

    avatar = ImageField(
        required=False,
        help_text='',
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif']), validate_image_size],
        widget=FileInput(
            attrs={
                "class": "block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-gray-50 file:text-gray-700 hover:file:bg-gray-200 hover:cursor-pointer border border-gray-300 rounded-3xl"
            }
        )
    )