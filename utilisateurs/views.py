from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Compte, ProfilUtilisateur
from .forms import *
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from django.utils import timezone
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.conf import settings
import random, string



def creer_compte(request):
    if request.method == 'POST':
        form = CompteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('connexion')
    else:
        form = CompteForm()
    return render(request, 'creer_compte.html', {'form': form})


@login_required
def ajouter_enseignant(request):
    try:
        profil_admin = ProfilUtilisateur.objects.get(user=request.user, role='admin')
    except ProfilUtilisateur.DoesNotExist:
        return HttpResponse("Vous n'avez pas le droit d'ajouter un enseignant.", status=403)

    if request.method == 'POST':
        form = AjouterEnseignantForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['mot_de_passe'],
                first_name=form.cleaned_data['nom']
            )
            ProfilUtilisateur.objects.create(
                user=user,
                compte=profil_admin.compte,
                role='enseignant'
            )
            return redirect('liste_enseignants')
    else:
        form = AjouterEnseignantForm()
    return render(request, 'ajouter_enseignant.html', {'form': form})




def connexion_view(request):
    if request.method == 'POST':
        form = ConnexionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = ConnexionForm()
    
    return render(request, 'connexion.html', {'form': form})


def deconnexion_view(request):
    logout(request)
    return redirect('connexion')



# pour stocker temporairement les codes dans une variable globale (pas production)
codes_temp = {}

def mot_de_passe_oublie(request):
    from .forms import DemandeResetForm
    if request.method == 'POST':
        form = DemandeResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                code = ''.join(random.choices(string.digits, k=6))
                expire = timezone.now() + timezone.timedelta(minutes=5)
                codes_temp[email] = {'code': code, 'expire': expire}

                send_mail(
                    "Code de réinitialisation",
                    f"Votre code est : {code}\nIl expire dans 5 minutes.",
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False
                )
                request.session['email_reset'] = email
                return redirect('verifier_code')
            except User.DoesNotExist:
                form.add_error('email', "Aucun utilisateur avec cet email.")
    else:
        form = DemandeResetForm()
    return render(request, 'mot_de_passe_oublie.html', {'form': form})


def verifier_code(request):
    from .forms import VerifCodeForm
    email = request.session.get('email_reset')
    if not email:
        return redirect('mot_de_passe_oublie')
    
    if request.method == 'POST':
        form = VerifCodeForm(request.POST)
        if form.is_valid():
            code_saisi = form.cleaned_data['code']
            data = codes_temp.get(email)
            if data and data['code'] == code_saisi and timezone.now() < data['expire']:
                request.session['code_valide'] = True
                return redirect('nouveau_mot_de_passe')
            else:
                form.add_error('code', "Code invalide ou expiré.")
    else:
        form = VerifCodeForm()
    return render(request, 'verifier_code.html', {'form': form})


def nouveau_mot_de_passe(request):
    from .forms import NouveauMotDePasseForm
    email = request.session.get('email_reset')
    if not email or not request.session.get('code_valide'):
        return redirect('mot_de_passe_oublie')
    
    if request.method == 'POST':
        form = NouveauMotDePasseForm(request.POST)
        if form.is_valid():
            nouveau = form.cleaned_data['nouveau_mot_de_passe']
            user = User.objects.get(email=email)
            user.set_password(nouveau)
            user.save()

            # Nettoyage
            codes_temp.pop(email, None)
            request.session.pop('email_reset', None)
            request.session.pop('code_valide', None)

            return redirect('connexion')
    else:
        form = NouveauMotDePasseForm()
    return render(request, 'nouveau_mot_de_passe.html', {'form': form})
