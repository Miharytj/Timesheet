import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Employe

# Configuration du logger
logger = logging.getLogger(__name__)

# Signal pour créer un employé lorsqu'un utilisateur est créé
@receiver(post_save, sender=User)
def create_employe(sender, instance, created, **kwargs):
    if created:  # Si un nouvel utilisateur est créé
        # Pour la création d'un employé, on doit s'assurer que le matricule est généré automatiquement
        # comme défini dans le pré-save signal du modèle Employe
        # Le matricule sera généré automatiquement par le signal pre_save dans models.py
        Employe.objects.create(
            user=instance,
            nom=instance.last_name or instance.username,
            prenom=instance.first_name or "",
            mail=instance.email or "",
            adresse=""  # Champ obligatoire selon le modèle
        )
        logger.info(f"Employe created for user: {instance.username}")

# Signal pour mettre à jour l'utilisateur lorsqu'un employé est modifié
@receiver(post_save, sender=Employe)
def update_user_profile(sender, instance, created=False, **kwargs):
    # Ne mettre à jour que si l'employé est modifié, pas créé
    # pour éviter les boucles infinies
    if not created and instance.user:
        user = instance.user
        logger.info(f"Updating user profile for {user.username}")
        
        # Mise à jour des champs utilisateur à partir de l'employé
        user.first_name = instance.prenom
        user.last_name = instance.nom
        user.email = instance.mail
        
        # Sauvegarder sans déclencher de signaux supplémentaires pour éviter des boucles
        User.objects.filter(pk=user.pk).update(
            first_name=instance.prenom,
            last_name=instance.nom,
            email=instance.mail
        )
        logger.info(f"User profile updated: {user.first_name} {user.last_name}, {user.email}")

