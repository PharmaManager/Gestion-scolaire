# forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Classe, Etudiant, Matiere, Note, Bulletin
import datetime
from utilisateurs.models import ProfilUtilisateur,Compte
class ClasseForm(forms.ModelForm):
    """Formulaire pour la gestion des classes"""
    
    class Meta:
        model = Classe
        fields = ['nom', 'niveau', 'annee_scolaire']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Informatique A'
            }),
            'niveau': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 1ère année'
            }),
            'annee_scolaire': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '2024-2025'
            }),
        }
    
    def clean_annee_scolaire(self):
        annee = self.cleaned_data['annee_scolaire']
        # Validation du format année scolaire (YYYY-YYYY)
        if len(annee) != 9 or annee[4] != '-':
            raise ValidationError("Format incorrect. Utilisez le format YYYY-YYYY")
        
        try:
            annee_debut = int(annee[:4])
            annee_fin = int(annee[5:])
            if annee_fin != annee_debut + 1:
                raise ValidationError("L'année de fin doit être l'année suivant l'année de début")
        except ValueError:
            raise ValidationError("Années invalides")
        
        return annee

class EtudiantForm(forms.ModelForm):
    """Formulaire pour la gestion des étudiants"""
    
    class Meta:
        model = Etudiant
        fields = [
            'numero_etudiant', 'nom', 'prenom', 'date_naissance', 
            'sexe', 'adresse', 'telephone', 'email', 'classe', 'actif'
        ]
        widgets = {
            'numero_etudiant': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: ETU2024001'
            }),
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de famille'
            }),
            'prenom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prénom'
            }),
            'date_naissance': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'sexe': forms.Select(attrs={
                'class': 'form-control'
            }),
            'adresse': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Adresse complète'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: +212600000000'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com'
            }),
            'classe': forms.Select(attrs={
                'class': 'form-control'
            }),
            'actif': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # récupérer l'utilisateur connecté
        super().__init__(*args, **kwargs)
        
        if user:
            try:
                profil = ProfilUtilisateur.objects.get(user=user)
                compte = profil.compte
                self.fields['classe'].queryset = Classe.objects.filter(compte=compte)
            except ProfilUtilisateur.DoesNotExist:
                self.fields['classe'].queryset = Classe.objects.none()
                
    
    def clean_date_naissance(self):
        date_naissance = self.cleaned_data['date_naissance']
        aujourd_hui = datetime.date.today()
        age = aujourd_hui.year - date_naissance.year
        
        if date_naissance > aujourd_hui:
            raise ValidationError("La date de naissance ne peut pas être dans le futur")
        
        if age > 100:
            raise ValidationError("Âge invalide")
        
        return date_naissance
    
    def clean_numero_etudiant(self):
        numero = self.cleaned_data['numero_etudiant']
        # Vérifier l'unicité si c'est un nouvel étudiant
        if not self.instance.pk:
            if Etudiant.objects.filter(numero_etudiant=numero).exists():
                raise ValidationError("Ce numéro d'étudiant existe déjà")
        return numero

class MatiereForm(forms.ModelForm):
    """Formulaire pour la gestion des matières"""
    
    class Meta:
        model = Matiere
        fields = ['nom', 'code', 'coefficient', 'description', 'enseignant', 'actif']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Mathématiques'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: MATH101'
            }),
            'coefficient': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0.5',
                'max': '10'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description de la matière'
            }),
            'enseignant': forms.Select(attrs={
                'class': 'form-control'
            }),
            'actif': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
            utilisateur_connecte = kwargs.pop('user', None)  # on récupère l'utilisateur connecté
            print(f'l\'uti : {utilisateur_connecte}')
            super().__init__(*args, **kwargs)

            if utilisateur_connecte and not utilisateur_connecte.is_superuser:
                try:
                    # Vérifie que l'utilisateur a un profil avec un compte
                    profil = ProfilUtilisateur.objects.get(user=utilisateur_connecte)
                    compte = profil.compte

                    if compte:
                        print(f"Compte trouvé : {compte}")

                        # Tous les utilisateurs liés à ce compte
                        utilisateurs_du_compte = ProfilUtilisateur.objects.filter(compte=compte).values_list('user', flat=True)

                        # Limiter aux utilisateurs du compte uniquement
                        self.fields['enseignant'].queryset = User.objects.filter(id__in=utilisateurs_du_compte)
                        self.fields['enseignant'].empty_label = "Sélectionner un enseignant"
                    else:
                        print("Aucun compte associé.")
                        self.fields['enseignant'].queryset = User.objects.none()

                except ProfilUtilisateur.DoesNotExist:
                    print("L'utilisateur connecté n'a pas de profil.")
                    self.fields['enseignant'].queryset = User.objects.none()
            else:
                # Cas des superusers ou utilisateurs sans compte : tu peux autoriser tous les users actifs (optionnel)
                self.fields['enseignant'].queryset = User.objects.filter(is_active=True)
                self.fields['enseignant'].empty_label = "Sélectionner un enseignant"


class NoteForm(forms.ModelForm):
    """Formulaire pour la saisie des notes"""
    
    class Meta:
        model = Note
        fields = [
            'etudiant', 'matiere', 'note', 'note_sur', 'type_evaluation',
            'date_evaluation', 'semestre', 'commentaire'
        ]
        widgets = {
            'etudiant': forms.Select(attrs={
                'class': 'form-control'
            }),
            'matiere': forms.Select(attrs={
                'class': 'form-control'
            }),
            'note': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'note_sur': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'value': '20'
            }),
            'type_evaluation': forms.Select(attrs={
                'class': 'form-control'
            }),
            'date_evaluation': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'semestre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: S1'
            }),
            'commentaire': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Commentaire sur la note (optionnel)'
            }),
        }
    
    
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # accepter l'argument user mais ne rien en faire
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        note = cleaned_data.get('note')
        note_sur = cleaned_data.get('note_sur')
        
        if note and note_sur:
            if note > note_sur:
                raise ValidationError("La note ne peut pas être supérieure à la note maximale")
        
        return cleaned_data
    
    def clean_date_evaluation(self):
        date_eval = self.cleaned_data['date_evaluation']
        if date_eval > datetime.date.today():
            raise ValidationError("La date d'évaluation ne peut pas être dans le futur")
        return date_eval

class NoteRapideForm(forms.Form):
    """Formulaire pour la saisie rapide de notes pour une classe entière"""
    
    matiere = forms.ModelChoiceField(
        queryset=Matiere.objects.filter(actif=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Matière"
    )
    type_evaluation = forms.ChoiceField(
        choices=Note.TYPE_EVALUATION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Type d'évaluation"
    )
    date_evaluation = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Date d'évaluation"
    )
    semestre = forms.CharField(
        max_length=2,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'S1'}),
        label="Semestre"
    )
    note_sur = forms.DecimalField(
        initial=20,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label="Note sur"
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # accepte user mais ne fait rien
        super().__init__(*args, **kwargs)



class ImportDonneesForm(forms.Form):
    """Formulaire pour l'import de données via fichiers Excel/CSV"""
    
    TYPE_IMPORT_CHOICES = [
        ('etudiants', 'Étudiants'),
        ('classe', 'Classes'),
        ('matieres', 'Matières'),
    ]
    
    type_import = forms.ChoiceField(
        choices=TYPE_IMPORT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Type de données à importer"
    )
    fichier = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls,.csv'
        }),
        label="Fichier à importer",
        help_text="Formats acceptés: Excel (.xlsx, .xls) ou CSV (.csv)"
    )
    

    def clean_fichier(self):
        fichier = self.cleaned_data['fichier']
        
        nom_fichier = fichier.name.lower()
        extensions_valides = ['.xlsx', '.xls', '.csv']

        if not any(nom_fichier.endswith(ext) for ext in extensions_valides):
            raise ValidationError("Format de fichier non supporté. Utilisez Excel ou CSV.")

        # Vérifier MIME (facultatif mais recommandé)
        import mimetypes
        mime_type, _ = mimetypes.guess_type(nom_fichier)
        if mime_type not in ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/csv']:
            raise ValidationError("Le contenu du fichier ne correspond pas à un format Excel ou CSV valide.")

        if fichier.size > 5 * 1024 * 1024:
            raise ValidationError("Le fichier est trop volumineux (max 5MB)")

        return fichier

class RechercheEtudiantForm(forms.Form):
    """Formulaire de recherche d'étudiants"""
    
    recherche = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher par nom, prénom ou numéro...'
        }),
        label="Recherche"
    )
    classe = forms.ModelChoiceField(
        queryset=Classe.objects.none(),
        required=False,
        empty_label="Toutes les classes",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Classe"
    )
    actif = forms.ChoiceField(
        choices=[('', 'Tous'), ('True', 'Actifs seulement'), ('False', 'Inactifs seulement')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Statut"
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Récupère l'utilisateur connecté
        super().__init__(*args, **kwargs)
        
         
        if user:
            try:
                # On récupère le profil utilisateur lié à ce user
                profil = ProfilUtilisateur.objects.get(user=user)

                # Puis on récupère le compte lié au profil
                compte = profil.compte

                # Enfin on filtre les classes liées à ce compte
                self.fields['classe'].queryset = Classe.objects.filter(compte=compte)
            except ProfilUtilisateur.DoesNotExist:
                # Pas de profil : pas de classes visibles
                self.fields['classe'].queryset = Classe.objects.none()

class GenerationBulletinForm(forms.Form):
    """Formulaire pour la génération de bulletins"""
    
    classe = forms.ModelChoiceField(
        queryset=Classe.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Classe"
    )
    semestre = forms.CharField(
        max_length=2,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'S1'}),
        label="Semestre"
    )
    annee_scolaire = forms.CharField(
        max_length=9,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '2024-2025'}),
        label="Année scolaire"
    )
    format_export = forms.ChoiceField(
        choices=[
            ('pdf', 'PDF individuel'),
            ('pdf_groupe', 'PDF groupé'),
            ('excel', 'Excel')
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Format d'export"
    )