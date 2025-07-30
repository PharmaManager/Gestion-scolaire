# urls.py (dans votre app)
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # ================= CLASSES =================
    path('classes/', views.liste_classes, name='liste_classes'),
    path('classes/ajouter/', views.ajouter_classe, name='ajouter_classe'),
    path('classes/<int:pk>/modifier/', views.modifier_classe, name='modifier_classe'),
    path('classes/<int:pk>/supprimer/', views.supprimer_classe, name='supprimer_classe'),
    
    # ================= ÉTUDIANTS =================
    path('etudiants/', views.liste_etudiants, name='liste_etudiants'),
    path('etudiants/ajouter/', views.ajouter_etudiant, name='ajouter_etudiant'),
    path('etudiants/<int:pk>/', views.detail_etudiant, name='detail_etudiant'),
    path('etudiants/<int:pk>/modifier/', views.modifier_etudiant, name='modifier_etudiant'),
    path('etudiants/<int:pk>/supprimer/', views.supprimer_etudiant, name='supprimer_etudiant'),
    
    # ================= MATIÈRES =================
    path('matieres/', views.liste_matieres, name='liste_matieres'),
    path('matieres/ajouter/', views.ajouter_matiere, name='ajouter_matiere'),
    path('matieres/<int:pk>/modifier/', views.modifier_matiere, name='modifier_matiere'),
    path('matieres/<int:pk>/supprimer/', views.supprimer_matiere, name='supprimer_matiere'),
    
    # ================= NOTES =================
    path('notes/', views.liste_notes, name='liste_notes'),
    path('notes/ajouter/', views.ajouter_note, name='ajouter_note'),
    path('notes/<int:pk>/modifier/', views.modifier_note, name='modifier_note'),
    path('notes/<int:pk>/supprimer/', views.supprimer_note, name='supprimer_note'),
    path('notes/saisie-rapide/', views.saisie_rapide_notes, name='saisie_rapide_notes'),
    path('notes/<int:pk>/supprimer/', views.supprimer_note, name='supprimer_note'),
    
    # ================= IMPORT/EXPORT =================
    path('import/', views.importer_donnees, name='importer_donnees'),
    path('bulletins/', views.generation_bulletins, name='generation_bulletins'),
    
    # ================= AJAX =================
    path('ajax/etudiants-classe/', views.get_etudiants_classe, name='get_etudiants_classe'),
]

