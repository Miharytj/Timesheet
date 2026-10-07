from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Employe
import os

class Command(BaseCommand):
    help = 'Create a superuser and associated employee'

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        
        if not username or not password:
            self.stdout.write(self.style.ERROR('Environment variables not set'))
            return
            
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
            
            self.stdout.write(self.style.SUCCESS('Superuser created successfully'))
        else:
            self.stdout.write(self.style.WARNING('Superuser already exists'))