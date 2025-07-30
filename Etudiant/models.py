from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from utilisateurs.models import Compte

class Classe(models.Model):
    """Modèle pour gérer les classes/niveaux scolaires"""
    nom = models.CharField(max_length=50, verbose_name="Nom de la classe")
    niveau = models.CharField(max_length=20, verbose_name="Niveau", help_text="Ex: 1ère année, 2ème année")
    annee_scolaire = models.CharField(max_length=9, verbose_name="Année scolaire", help_text="Ex: 2024-2025")
    date_creation = models.DateTimeField(auto_now_add=True)
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "Classe"
        verbose_name_plural = "Classes"
        ordering = ['niveau', 'nom']
    
    def __str__(self):
        return f"{self.nom} - {self.annee_scolaire}"

class Etudiant(models.Model):
    """Modèle pour gérer les informations des étudiants"""
    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]
    
    numero_etudiant = models.CharField(max_length=20, unique=True, verbose_name="Numéro étudiant")
    nom = models.CharField(max_length=100, verbose_name="Nom de famille")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    date_naissance = models.DateField(verbose_name="Date de naissance")
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES, verbose_name="Sexe")
    adresse = models.TextField(blank=True, verbose_name="Adresse")
    telephone = models.CharField(max_length=15, blank=True, verbose_name="Téléphone")
    email = models.EmailField(blank=True, verbose_name="Email")
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE, verbose_name="Classe")
    date_inscription = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")
    actif = models.BooleanField(default=True, verbose_name="Étudiant actif")
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    
    
    class Meta:
        verbose_name = "Étudiant"
        verbose_name_plural = "Étudiants"
        ordering = ['nom', 'prenom']
    
    def __str__(self):
        return f"{self.nom} {self.prenom} ({self.numero_etudiant})"
    
    @property
    def nom_complet(self):
        return f"{self.nom} {self.prenom}"

class Matiere(models.Model):
    """Modèle pour gérer les matières enseignées"""
    nom = models.CharField(max_length=100, verbose_name="Nom de la matière")
    code = models.CharField(max_length=10, unique=True, verbose_name="Code matière")
    coefficient = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        default=1.0,
        validators=[MinValueValidator(0.5), MaxValueValidator(10.0)],
        verbose_name="Coefficient"
    )
    description = models.TextField(blank=True, verbose_name="Description")
    enseignant = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="Enseignant",
        
    )
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    
    actif = models.BooleanField(default=True, verbose_name="Matière active")
    
    class Meta:
        verbose_name = "Matière"
        verbose_name_plural = "Matières"
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.nom} ({self.code})"

class Note(models.Model):
    """Modèle pour gérer les notes des étudiants"""
    TYPE_EVALUATION_CHOICES = [
        ('DS', 'Devoir Surveillé'),
        ('CC', 'Contrôle Continu'),
        ('EX', 'Examen'),
        ('TP', 'Travaux Pratiques'),
        ('OR', 'Oral'),
    ]
    
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, verbose_name="Étudiant")
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, verbose_name="Matière")
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    
    note = models.DecimalField(
        max_digits=4, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        verbose_name="Note"
    )
    note_sur = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=20.00,
        verbose_name="Note sur"
    )
    type_evaluation = models.CharField(
        max_length=2, 
        choices=TYPE_EVALUATION_CHOICES, 
        default='DS',
        verbose_name="Type d'évaluation"
    )
    date_evaluation = models.DateField(verbose_name="Date d'évaluation")
    semestre = models.CharField(max_length=2, verbose_name="Semestre", help_text="S1, S2")
    commentaire = models.TextField(blank=True, verbose_name="Commentaire")
    date_saisie = models.DateTimeField(auto_now_add=True, verbose_name="Date de saisie")
    modifie_par = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Modifié par"
    )
    
    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        ordering = ['-date_evaluation']
        unique_together = ['etudiant', 'matiere', 'type_evaluation', 'date_evaluation']
    
    def __str__(self):
        return f"{self.etudiant.nom_complet} - {self.matiere.nom} : {self.note}/{self.note_sur}"
    
    @property
    def note_sur_vingt(self):
        """Convertit la note sur 20"""
        return (self.note * 20) / self.note_sur if self.note_sur != 0 else 0

class Bulletin(models.Model):
    """Modèle pour gérer les bulletins de notes"""
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, verbose_name="Étudiant")
    semestre = models.CharField(max_length=2, verbose_name="Semestre")
    annee_scolaire = models.CharField(max_length=9, verbose_name="Année scolaire")
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    
    moyenne_generale = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name="Moyenne générale"
    )
    rang = models.PositiveIntegerField(null=True, blank=True, verbose_name="Rang")
    effectif_classe = models.PositiveIntegerField(null=True, blank=True, verbose_name="Effectif classe")
    appreciation = models.TextField(blank=True, verbose_name="Appréciation générale")
    date_generation = models.DateTimeField(auto_now_add=True, verbose_name="Date de génération")
    genere_par = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Généré par"
    )
    
    class Meta:
        verbose_name = "Bulletin"
        verbose_name_plural = "Bulletins"
        ordering = ['-date_generation']
        unique_together = ['etudiant', 'semestre', 'annee_scolaire']
    
    def __str__(self):
        return f"Bulletin {self.etudiant.nom_complet} - {self.semestre} {self.annee_scolaire}"
