"""
WSGI config for harel_mallac project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'harel_mallac.settings')

application = get_wsgi_application()

# Créer le superuser au démarrage
try:
    call_command('create_superuser')
except:
    # Gestion silencieuse des erreurs pour ne pas bloquer le démarrage
    pass