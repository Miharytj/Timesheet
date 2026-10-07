import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _
import logging
from dotenv import load_dotenv
load_dotenv()  # Charger les variables d'environnement 

LANGUAGES = [
    ('fr', _('Français')),
    ('en', _('English')),
]

DEFAULT_LANGUAGE = 'fr'

# Cacher les logs liés à l'observation des fichiers
logging.getLogger('django.utils.autoreload').setLevel(logging.CRITICAL)

# Chemin de base
BASE_DIR = Path(__file__).resolve().parent.parent

# URL utilisée pour faire référence aux fichiers statiques
STATIC_URL = '/static/'

# Chemin absolu vers le répertoire où collectstatic rassemblera les fichiers
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Répertoires supplémentaires où Django cherchera des fichiers statiques
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Mode Debug - activé temporairement pour diagnostiquer l'erreur 500
DEBUG = True

# Configuration pour servir les fichiers statiques en développement
if DEBUG:
    import mimetypes
    mimetypes.add_type("text/css", ".css", True)

# Clé secrète (ne pas partager en production)
SECRET_KEY = 'django-insecure-4a+zwdpgfk$*5tjo54=!voi4(*xs8aexx8p&bot3(+5cv#$&k1'

# Hôtes autorisés
ALLOWED_HOSTS = ["*"]

# Ces paramètres forcent HTTPS - désactivés en développement
# SECURE_SSL_REDIRECT = True
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Configuration des niveaux de messages
MESSAGE_LEVEL = 100

# Paramètres de sécurité des cookies - en développement
SESSION_COOKIE_SECURE = False  # Ne pas utiliser HTTPS pour les cookies de session
CSRF_COOKIE_SECURE = False  # Ne pas utiliser HTTPS pour les cookies CSRF

# Applications installées
INSTALLED_APPS = [
    'jazzmin',
    'modeltranslation',
    'django_extensions',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',

    # Django Allauth (uniquement pour le login)
    'allauth',
    'allauth.account',
    'django.contrib.sites',
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'console': {
#             'class': 'logging.StreamHandler',
#         },
#         'file': {
#             'class': 'logging.FileHandler',
#             'filename': os.path.join(BASE_DIR, 'django_error.log'),
#         },
#     },
#     'root': {
#         'handlers': ['console', 'file'],
#         'level': 'DEBUG',
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['console', 'file'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#     },
# }

# ID du site pour le framework Sites
SITE_ID = 1

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Middleware de localisation à la bonne position
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

# URL de la configuration principale
ROOT_URLCONF = 'harel_mallac.urls'

# Configuration des templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # Requis par Allauth
                'django.template.context_processors.i18n',  # Ajouté pour l'internationalisation
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Application WSGI
WSGI_APPLICATION = 'harel_mallac.wsgi.application'

# Expiration du session
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Durée de la session (facultatif)
SESSION_COOKIE_AGE = 3600  # 1 heure

# Configuration WhiteNoise modifiée pour éviter l'erreur 500
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Configuration de la base de données
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'TS',
        'USER': 'postgres',
        'PASSWORD': '0123',  # Mot de passe simple
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Validateurs de mot de passe
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Chemins vers les fichiers de traduction
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),  
]

# Configuration linguistique et horaire
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = False

# Champ auto par défaut
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Redirections de connexion/déconnexion
LOGIN_REDIRECT_URL = '/app/dashboard/'
LOGOUT_REDIRECT_URL = ''
LOGIN_URL = '/accounts/login/'  # Assure-toi que c'est la bonne URL pour la connexion

# Backends d'authentification
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # Auth classique
]

# Configuration Django Allauth (uniquement pour le login)
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_SIGNUP_REDIRECT_URL = '/admin/login/'  # Redirection en cas de tentative d'accès à /signup/
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_SESSION_REMEMBER = True

# Design administration
JAZZMIN_SETTINGS = {
    # 🏠 TITRE & HEADER
    # "show_ui_builder": True,  # Activer l'UI Builder pour permettre le changement de thème
    "site_title": "Admin HMT",
    "site_header": "",  # Supprimé pour n'afficher que le logo
    "site_brand": "HMTM Admin",  # Supprimé pour n'afficher que le logo
    "site_logo": "img/logo 2.png",  # Chemin vers ton logo dans static/img/
    "welcome_sign": "Bienvenue sur l'interface d'administration HMT",
    "copyright": "© 2025 HMT",

    # 📌 NAVIGATION & SIDEBAR
    "navigation_expanded": True,  # Sidebar toujours ouvert
    "hide_apps": ['sites'],  # Ne masque aucune application
    "hide_models": ['groupes'],  # Ne masque aucun modèle
    "order_with_respect_to": [
        "app.Societe",
        "app.Service",
        "app.Employe",
        "app.Tache",
        "app.Pointage",
        "app.Conge",
        "app.Permission",
        "app.TypePermission",
    ],

    # 🎨 STYLE DU SIDEBAR & ADMIN
    "custom_css": "admin_custom.css",  # Fichier CSS perso
    "site_logo_classes": "img-fluid",  # Rendre le logo responsive
    "site_logo_text": "",  # Empêcher l'affichage du texte à côté du logo
     
    # 🏷️ ICÔNES DES MODÈLES
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.group": "fas fa-users",
        "app.Service": "fas fa-briefcase",
        "app.Societe": "fas fa-building",
        "app.Employe": "fas fa-id-badge",
        "app.Tache": "fas fa-tasks",
        "app.Pointage": "fas fa-clock",
        "app.Conge": "fas fa-calendar-alt",
        "app.Permission": "fas fa-user-shield",
        "app.TypePermission": "fas fa-shield-alt",
    },

    # 📅 DATE & TRI PAR DÉFAUT
    "default_sort": "id",  # Tri par ID par défaut
    "theme": "light",  # Choisis le thème par défaut, par exemple "light"
    "available_themes": [
        "light",  # Thème clair
        "dark",   # Thème sombre
        "blue",   # Thème bleu
        "green",  # Thème vert
    ],
}