from django import forms
from django.contrib.auth.models import User
from .models import Compte

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Compte

class CompteForm(forms.ModelForm):
    nom_utilisateur = forms.CharField(label="Nom complet", max_length=150)
    email = forms.EmailField()
    mot_de_passe = forms.CharField(widget=forms.PasswordInput)
    confirmation_mot_de_passe = forms.CharField(widget=forms.PasswordInput, label="Confirmer le mot de passe")

    class Meta:
        model = Compte
        fields = []  # On ne remplit pas le champ 'nom' directement car on le fixe automatiquement

    def clean(self):
        cleaned_data = super().clean()
        mdp = cleaned_data.get("mot_de_passe")
        mdp_conf = cleaned_data.get("confirmation_mot_de_passe")

        if mdp and mdp_conf and mdp != mdp_conf:
            raise ValidationError("Les mots de passe ne correspondent pas.")

        # Optionnel : vérifier que l'email n'est pas déjà utilisé
        email = cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Un utilisateur avec cet email existe déjà.")

        return cleaned_data

    def save(self, commit=True):
        # Le nom du compte = le nom utilisateur saisi
        nom_utilisateur = self.cleaned_data['nom_utilisateur']
        email = self.cleaned_data['email']
        mot_de_passe = self.cleaned_data['mot_de_passe']

        compte = Compte(nom=nom_utilisateur)

        if commit:
            # Créer l'utilisateur admin
            user = User.objects.create_user(
                username=nom_utilisateur,
                email=email,
                password=mot_de_passe,
                first_name=nom_utilisateur,
            )
            compte.admin = user
            compte.save()

            from .models import ProfilUtilisateur
            ProfilUtilisateur.objects.create(
                user=user,
                compte=compte,
                role='admin'
            )

        return compte



class AjouterEnseignantForm(forms.Form):
    nom = forms.CharField(max_length=150)
    email = forms.EmailField()
    mot_de_passe = forms.CharField(widget=forms.PasswordInput)
    
    
class DemandeResetForm(forms.Form):
    email = forms.EmailField(label="Votre email")
    
class VerifCodeForm(forms.Form):
    code = forms.CharField(max_length=6, label="Code reçu")

class NouveauMotDePasseForm(forms.Form):
    nouveau_mot_de_passe = forms.CharField(widget=forms.PasswordInput, label="Nouveau mot de passe")
    confirmer = forms.CharField(widget=forms.PasswordInput, label="Confirmer le mot de passe")

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('nouveau_mot_de_passe') != cleaned_data.get('confirmer'):
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data

# forms.py

from django import forms


class ConnexionForm(forms.Form):
    username = forms.CharField(
        label="Nom d'utilisateur",
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Nom d’utilisateur', 'class': 'form-control', 'id': 'username'})
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe', 'class': 'form-control', 'id': 'password'})
    )

