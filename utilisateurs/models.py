from django.db import models
from django.contrib.auth.models import User

class Compte(models.Model):
    nom = models.CharField(max_length=100)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comptes_admin")

    def __str__(self):
        return self.nom

class ProfilUtilisateur(models.Model):
    ROLES = (
        ('admin', 'Administrateur'),
        ('enseignant', 'Enseignant'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"
