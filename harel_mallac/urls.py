"""
URL configuration for harel_mallac project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from app import views
from django.views.generic import RedirectView
from django.contrib.auth.views import LogoutView
from django.conf.urls.i18n import set_language
from django.views.i18n import set_language as django_set_language
from django.contrib.admin.views.decorators import staff_member_required

urlpatterns = [
    path('', views.welcome, name='home'),
    
    # Connexion administrateur (rediriger automatiquement si non autorisé)
    path('admin/login/', views.custom_admin_login, name='admin-login'),
    # path('admin/logout/', views.admin_logout, name='admin-logout'),
    # path('admin/set-language/', django_set_language, name='set_language'),
    path('logout/', views.custom_logout, name='logout'),
    path('set-language/', django_set_language, name='set_language'),
    
    # Conserver la page de login d'Allauth
    path('accounts/', include('allauth.urls')),  # Page de login standard

    # Rediriger toutes les autres pages d'authentification vers la page de login
    re_path(r'^accounts/(?!login|logout).*$', RedirectView.as_view(url='/accounts/login/', permanent=True)),

    # Routes des fonctionnalités spécifiques
    path('admin/', admin.site.urls),
    path('app/', include('app.urls')),
    path('api/events/', views.events_list, name='events-list'),
    path('api/employes/', views.get_employes, name='get_employes'),    
]