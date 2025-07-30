from django.urls import path
from .views import *

urlpatterns = [
    path('creer-compte/', creer_compte, name='creer_compte'),
     path('connexion/', connexion_view, name='connexion'),
    path('deconnexion/', deconnexion_view, name='deconnexion'),
    path('ajouter-enseignant/', ajouter_enseignant, name='ajouter_enseignant'),
    path('mot-de-passe-oublie/', mot_de_passe_oublie, name='mot_de_passe_oublie'),
    path('verifier-code/', verifier_code, name='verifier_code'),
    path('nouveau-mot-de-passe/', nouveau_mot_de_passe, name='nouveau_mot_de_passe'),
]
