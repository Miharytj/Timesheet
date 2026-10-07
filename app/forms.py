from django import forms
from .models import Employe, Service

class EmployeForm(forms.ModelForm):
    class Meta:
        model = Employe
        fields = ['nom', 'prenom', 'adresse', 'mail', 'numero', 'codeS', 'departement']
    
    # Personnaliser le widget pour chaque champ
    nom = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control custom-input', 'placeholder': 'Nom'}))
    prenom = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control custom-input', 'placeholder': 'Prénom'}))
    adresse = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control custom-input', 'placeholder': 'Adresse'}))
    mail = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control custom-input', 'placeholder': 'Email'}))
    numero = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control custom-input', 'placeholder': 'Number'}))
    # codeS = forms.ModelChoiceField(queryset=Service.objects.all(), widget=forms.Select(attrs={'class': 'form-control custom-input'}))
    codeS = forms.ModelChoiceField(
        queryset=Service.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control custom-input'}),
        empty_label="Choisissez un poste"
    )
    departement = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control custom-input', 'placeholder': 'Département'}),
        required=False
    )