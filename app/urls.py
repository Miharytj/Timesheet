from django.urls import path, re_path, include
from app import views
from django.views.generic import RedirectView
from django.contrib.auth.views import LogoutView
from django.conf.urls.i18n import set_language
from django.views.i18n import set_language as django_set_language
from django.contrib.admin.views.decorators import staff_member_required

urlpatterns = [
    path('timesheet/', views.timesheet_view, name='timesheet_view'),
    path('calendar/', views.calendar, name='calendar'),    
    path('pointage/', views.pointage_view, name='pointage'),
    path('aide/', views.aide, name='aide'),
    # path('notification/', views.notification, name='notifications'),    
    path('schedules/', views.schedules, name='schedules'),    
    path('details/', views.afficher_employe, name='afficher_employe'),
    path('employe/<str:matricule>/', views.afficher_employe, name='afficher_employe'),
    path('employe/<str:matricule>/modifier/', views.modifier_employe, name='modifier_employe'),
    # # path('welcome/', views.welcome, name='welcome'),
    
    path('dashboard/', views.dashboard, name='dashboard'),
    path('search/', views.search_view, name='search'),
    # path('reports/', views.reports, name='reports'),
    
    path('task/', views.task, name='task'),
    path('task/add/', views.add_task, name='add_task'),
    path('task/edit/<str:RefTache>/', views.edit_task, name='edit_task'),
    path('task/delete/<str:RefTache>/', views.delete_task, name='delete_task'),
    
    path('leave/', views.list_conges, name='list_conges'),
    path('leave/add/', views.add_conge, name='add_conge'),
    
    path('permission/', views.permission_list, name='permission_list'),
    path('permission/add/', views.add_permission, name='add_permission'),
    
    path('entreprise/', views.list_societes, name='list_societes'),  
    path('entreprise/add/', views.add_societe, name='add_societe'), 
    
    path('people/', views.liste_employes, name='liste_employes'),
    
]
