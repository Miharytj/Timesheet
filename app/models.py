import datetime
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

class Service(models.Model):
    codeS = models.AutoField(primary_key=True, verbose_name=_("Code du service"))
    poste = models.CharField(max_length=150, verbose_name=_("Poste"))

    def __str__(self):
        return str(self.poste)

    class Meta:
        verbose_name = _("Service")
        verbose_name_plural = _("Services")

class Societe(models.Model):
    codeSoc = models.AutoField(primary_key=True, verbose_name=_("Code de la société"))
    NomSociete = models.CharField(max_length=250, verbose_name=_("Nom de la société"))

    def __str__(self):
        return self.NomSociete

    class Meta:
        verbose_name = _("Société")
        verbose_name_plural = _("Sociétés")
    
class TypePermission(models.Model):
    codetype = models.AutoField(primary_key=True, verbose_name=_("Code du type de permission"))
    Type = models.CharField(max_length=250, null=True, blank=True, verbose_name=_("Type de permission"))

    def __str__(self):
        return self.Type

    class Meta:
        verbose_name = _("Type de permission")
        verbose_name_plural = _("Types de permission")

class Employe(models.Model):
    matricule = models.CharField(max_length=100, primary_key=True, verbose_name=_("Matricule de l'employé"))
    nom = models.CharField(max_length=50, verbose_name=_("Nom"))
    prenom = models.CharField(max_length=250, verbose_name=_("Prénom"))
    adresse = models.CharField(max_length=250, verbose_name=_("Adresse"))
    mail = models.EmailField(max_length=250, verbose_name=_("E-mail"))
    codeS = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("Service"))
    departement = models.CharField(max_length=150, null=True, blank=True, verbose_name=_("Département"))
    numero = models.CharField(max_length=13, null=True, blank=True, verbose_name=_("Numéro téléphone"))
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employe', null=True, blank=True, verbose_name=_("Nom d'utilisateur"))

    def __str__(self):
        return f"{self.nom} {self.prenom}"

    class Meta:
        verbose_name = _("Employé")
        verbose_name_plural = _("Employés")

class Tache(models.Model):
    RefTache = models.CharField(max_length=100, primary_key=True, verbose_name=_("Référence tâche"))
    dateAjout = models.DateField(auto_now_add=True, verbose_name=_("Date d'ajout"))
    NomTache = models.CharField(max_length=250, null=True, verbose_name=_("Nom de la tâche"))
    description = models.CharField(max_length=255, verbose_name=_("Description"))
    DateDebut = models.DateTimeField(null=True, blank=True, verbose_name=_("Date et heure de début"))
    DateFin = models.DateTimeField(null=True, blank=True, verbose_name=_("Date et heure de fin"))
    codeSoc = models.ForeignKey(Societe, on_delete=models.CASCADE, verbose_name=_("Société"))
    matricule_Responsable = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='responsable_taches', verbose_name=_("Responsable"))
    matricule_Technicien = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='technicien_taches', null=True, blank=True, verbose_name=_("Employé"))

    def __str__(self):
        return str(self.RefTache)

    class Meta:
        verbose_name = _("Tâche")
        verbose_name_plural = _("Tâches")

class Conge(models.Model):
    numero = models.CharField(max_length=100, primary_key=True, verbose_name=_("Numéro de congé"))
    dateDemande = models.DateField(verbose_name=_("Date de demande"))
    DateDeb = models.DateTimeField(null=True, blank=True, verbose_name=_("Date et heure de début"))
    DateFin = models.DateTimeField(null=True, blank=True, verbose_name=_("Date et heure de fin"))
    MotifCo = models.CharField(max_length=250, null=True, verbose_name=_("Motif"))
    matricule_responsable = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='responsable_conges', verbose_name=_("Responsable"))
    matricule_Technicien = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='technicien_conges', verbose_name=_("Employé"))

    def __str__(self):
        return str(self.numero)

    class Meta:
        verbose_name = _("Congé")
        verbose_name_plural = _("Congés")

class Permission(models.Model):
    id_permission = models.AutoField(primary_key=True, verbose_name=_("ID Permission"))
    DatePer = models.DateField(verbose_name=_("Date de demande"))
    HeureDebPer = models.DateTimeField(verbose_name=_("Date et heure de début"))
    HeureFinPer = models.DateTimeField(verbose_name=_("Date et heure de fin"))
    MotifPer = models.CharField(max_length=250, null=True, blank=True, verbose_name=_("Motifs"))
    codetype = models.ForeignKey('TypePermission', on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("Type de permission"))
    matricule_responsable = models.ForeignKey('Employe', on_delete=models.CASCADE, related_name='responsable_permissions', verbose_name=_("Responsable"))
    matricule_Technicien = models.ForeignKey('Employe', on_delete=models.CASCADE, related_name='technicien_permissions', verbose_name=_("Employé"))

    def __str__(self):
        return _("Permission %(id)s : %(nom)s %(prenom)s") % {
            'id': self.id_permission,
            'nom': self.matricule_Technicien.nom,
            'prenom': self.matricule_Technicien.prenom
        }

    class Meta:
        verbose_name = _("Permission")
        verbose_name_plural = _("Permissions")

class Pointage(models.Model):
    dateP = models.AutoField(primary_key=True, verbose_name=_("ID Pointage"))
    datePoint = models.DateField(null=True, blank=True, verbose_name=_("Date du pointage"))
    matricule = models.ForeignKey(Employe, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("Employé"))
    heureArrivee = models.TimeField(null=True, blank=True, verbose_name=_("Heure d'arrivée"))
    heureSortie = models.TimeField(null=True, blank=True, verbose_name=_("Heure de sortie"))
    remarque= models.CharField(max_length=250, null=True, blank=True, verbose_name=_("Remarque"))

    def __str__(self):
        return str(self.dateP)

    class Meta:
        verbose_name = _("Pointage")
        verbose_name_plural = _("Pointages")
    

@receiver(pre_save, sender=Tache)
def set_ref_tache(sender, instance, **kwargs):
    if not instance.RefTache or instance.RefTache == '':
        today_str = datetime.datetime.today().strftime('%d%m%Y')
        base_ref = f'HMTM-{today_str}T'
        compteur = 1

        # Boucle jusqu'à ce qu'une référence unique soit trouvée
        while True:
            nouvelle_ref = f'{base_ref}{str(compteur).zfill(4)}'
            if not Tache.objects.filter(RefTache=nouvelle_ref).exists():
                instance.RefTache = nouvelle_ref
                break
            compteur += 1

@receiver(pre_save, sender=Conge)
def set_numero_conge(sender, instance, **kwargs):
    # Ne générer un ID que s'il n'en existe pas déjà un
    if not instance.numero or instance.numero == '':
        today_str = datetime.datetime.today().strftime('%d%m%Y')
        
        # Trouver le dernier numéro utilisé pour aujourd'hui
        last_conge = Conge.objects.filter(
            numero__startswith=f'HMTM-{today_str}C'
        ).order_by('-numero').first()
        
        if last_conge:
            # Extraire le dernier numéro et l'incrémenter
            try:
                last_number = int(last_conge.numero.split('C')[1])
                new_number = last_number + 1
            except (IndexError, ValueError):
                new_number = 1
        else:
            new_number = 1
            
        instance.numero = f'HMTM-{today_str}C{str(new_number).zfill(2)}'

@receiver(pre_save, sender=Employe)
def set_matricule_employe(sender, instance, **kwargs):
    if not instance.matricule or instance.matricule == '':
        last_employe = Employe.objects.order_by('-matricule').first()
        if last_employe and last_employe.matricule.startswith('HMTM-') and \
            last_employe.matricule.endswith('E'):
            try:
                last_number = int(last_employe.matricule.split('-')[1].replace('E', ''))
                new_number = last_number + 1
            except (IndexError, ValueError):
                new_number = 1
        else:
            new_number = 1
        instance.matricule = f'HMTM-{str(new_number).zfill(4)}E'