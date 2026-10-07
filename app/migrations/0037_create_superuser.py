import os
from django.db import migrations

def create_superuser_and_employe(apps, schema_editor):
    # Vérification des variables d'environnement
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'SuperAdmin.hmtm.tj')
    
    if not password:
        print("AVERTISSEMENT: Variable d'environnement DJANGO_SUPERUSER_PASSWORD non définie. Superuser non créé.")
        return
    
    User = apps.get_model("auth", "User")
    Employe = apps.get_model("app", "Employe")
    
    if not User.objects.filter(username=username).exists():
        superuser = User.objects.create_superuser(
            username=username,
            email=os.environ.get('DJANGO_SUPERUSER_EMAIL', ''),
            password=password
        )
        
        Employe.objects.create(
            matricule=os.environ.get('DJANGO_SUPERUSER_MATRICULE', 'ADMIN001'),
            nom=os.environ.get('DJANGO_SUPERUSER_NOM', 'Super'),
            prenom=os.environ.get('DJANGO_SUPERUSER_PRENOM', 'Admin'),
            adresse=os.environ.get('DJANGO_SUPERUSER_ADRESSE', 'None'),
            mail=os.environ.get('DJANGO_SUPERUSER_MAIL', 'admin@hmtm.tj'),
            numero=os.environ.get('DJANGO_SUPERUSER_NUMERO', '0000000000'),
            user=superuser
        )

class Migration(migrations.Migration):
    dependencies = [
        ('app', '0036_alter_permission_motifper'),  # Ajustez selon votre dernière migration
    ]
    operations = [
        migrations.RunPython(create_superuser_and_employe),
    ]