from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CreateUser(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d\'utilisateur', 'name': 'username'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe', 'name': 'password'}),
        }
