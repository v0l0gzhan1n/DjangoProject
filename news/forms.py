from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Article, Category, Comment
from django.contrib.auth.models import User

class SearchForm(forms.Form):
    query = forms.CharField(label='Поиск', required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите искомое'}))
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label='Категория',
        required=False,
        empty_label='Все категории'
    )
    date_from = forms.DateField(
        label='От',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    date_to = forms.DateField(
        label='До',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ваш email'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'placeholder': 'Придумайте пароль'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Повторите пароль'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Придумайте логин'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Придумайте пароль'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Повторите пароль'
            }),
        }


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Логин",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш логин'
        })
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш пароль'
        })
    )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Напишите ваш комментарий...'
            }),
        }