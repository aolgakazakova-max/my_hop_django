from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User

from .models import Profile


class RegisterForm(forms.Form):
    username = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )

    email = forms.EmailField(
        label='Почта',
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Почта',
            }
        ),
    )

    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Пароль',
            }
        ),
    )

    password_confirm = forms.CharField(
        label='Подтвердите пароль',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Подтвердите пароль',
            }
        ),
    )

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()

        if User.objects.filter(
            email__iexact=email,
        ).exists():
            raise forms.ValidationError(
                'Эта почта уже зарегистрирована.'
            )

        return email

    def clean(self):
        cleaned_data = super().clean()

        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get(
            'password_confirm',
        )

        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError(
                    'Пароли не совпадают.'
                )

        if email:
            username = email.split('@')[0]

            if User.objects.filter(
                username=username,
            ).exists():
                self.add_error(
                    'username',
                    'Этот username уже зарегистрирован.',
                )
            else:
                cleaned_data['username'] = username

        return cleaned_data

    def save(self):
        email = self.cleaned_data['email']
        username = self.cleaned_data['username']

        return User.objects.create_user(
            username=username,
            email=email,
            password=self.cleaned_data['password'],
        )


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = [
            'full_name',
            'phone',
            'city',
            'address',
        ]

        widgets = {
            'full_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'ФИО',
                }
            ),
            'phone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Телефон',
                }
            ),
            'city': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Город',
                }
            ),
            'address': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Адрес',
                }
            ),
        }


class UserPasswordChangeForm(PasswordChangeForm):
    """
    Форма смены пароля пользователя.
    Использует стандартную проверку Django.
    """

    old_password = forms.CharField(
        label='Текущий пароль',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Текущий пароль',
            }
        ),
    )

    new_password1 = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Новый пароль',
            }
        ),
        help_text='',
    )

    new_password2 = forms.CharField(
        label='Подтвердите новый пароль',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Подтвердите новый пароль',
            }
        ),
    )

