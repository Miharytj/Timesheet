from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q, Field, Sum, Count, F
from .models import Tache, Conge, Employe, Pointage, Societe, Service, Permission, TypePermission
from datetime import datetime, timedelta, date
from django.contrib.auth.models import User
from django.http import Http404
from django.urls import reverse
from .forms import EmployeForm
import random, re
import pytz
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.utils import timezone
from django.utils.timezone import now
from django.db.models.functions import TruncWeek
from datetime import time
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import logout
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from django.db.models.functions import TruncMonth

def set_language(request):
    next_url = request.POST.get('next', '/')
    language = request.POST.get('language', 'fr')
    translation.activate(language)
    request.session[translation.LANGUAGE_SESSION_KEY] = language
    return HttpResponse(status=200)

@login_required(login_url='/login')  # Redirige l'utilisateur vers la page de connexion s'il n'est pas connecté
def admin_login_view(request):
    # Cette vue gère la page de connexion admin
    # Logique personnalisée pour l'admin
    return redirect('admin:index')

class CustomAdminLoginView(LoginView):
    template_name = 'registration/login.html'  # Modèle pour le login admin

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return redirect('/admin/')  # Redirige vers le panneau admin si l'utilisateur est déjà connecté
        return super().get(request, *args, **kwargs)

custom_login_view = CustomAdminLoginView.as_view()

def custom_admin_login(request): 
    if request.user.is_authenticated and request.user.is_staff: return redirect('/admin/') # Rediriger vers le tableau de bord admin si l'utilisateur est staff/admin 
    else: return redirect('/app/dashboard/')
 
@login_required   
def custom_logout(request):
    # Déconnexion universelle
    logout(request)
    return redirect('home')  # Rediriger vers la page d'accueil
    
@staff_member_required  # Assure que seuls les admins peuvent l'utiliser
def admin_logout(request):
    logout(request)  # Déconnecte l'utilisateur
    return redirect('/')  # Redirige vers la page d'accueil


@login_required
def aide(request):
    return render(request, 'aide.html')

@login_required
def dashboard(request):
    # Récupérer les paramètres de filtre depuis la requête avec nouvelles valeurs par défaut
    period = request.GET.get('period', 'month')  # Défaut: month au lieu de 'all'
    view_type = request.GET.get('view_type', 'personal')  # Défaut: personal au lieu de 'all'
    
    # Date et heure actuelles avec décalage horaire Madagascar (+3h UTC)
    current_datetime = now() + timedelta(hours=3, seconds=1)
    today = current_datetime.date()
    
    # Définir les dates de début et de fin selon la période sélectionnée
    start_date = None
    end_date = None
    
    if period == 'day':
        start_date = today
        end_date = today
        period_display = f"Journée du {today.strftime('%d/%m/%Y')}"
    elif period == 'week':
        start_date = today - timedelta(days=today.weekday())  # Lundi de cette semaine
        end_date = start_date + timedelta(days=6)  # Dimanche de cette semaine
        period_display = f"Semaine du {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}"
    elif period == 'month':
        start_date = today.replace(day=1)  # Premier jour du mois
        # Dernier jour du mois
        next_month = today.replace(day=28) + timedelta(days=4)
        end_date = next_month - timedelta(days=next_month.day)
        period_display = f"Mois de {start_date.strftime('%B %Y')}"
    elif period == 'year':
        start_date = today.replace(month=1, day=1)  # Premier jour de l'année
        end_date = today.replace(month=12, day=31)  # Dernier jour de l'année
        period_display = f"Année {today.year}"
    else:  # 'all'
        period_display = "Toutes les périodes"
    
    # Filtrer selon l'utilisateur connecté si view_type est 'personal'
    user_filter = {}
    if view_type == 'personal':
        try:
            current_employe = request.user.employe
            user_filter = {'matricule_Technicien': current_employe}
            user_display = f"Données personnelles de {current_employe.nom} {current_employe.prenom}"
        except Exception:
            # Si l'utilisateur n'a pas d'employé associé, on revient à 'all'
            view_type = 'all'
            user_display = "Toutes les données"
    else:
        user_display = "Toutes les données"
    
    # Générer les couleurs pour les employés
    employe_couleurs = get_employee_colors()
    
    # Récupérer les statistiques avec les filtres
    task_stats = get_task_statistics(start_date, end_date, user_filter if view_type == 'personal' else {})
    leave_stats = get_leave_statistics(start_date, end_date, user_filter if view_type == 'personal' else {})
    permission_stats = get_permission_statistics(start_date, end_date, user_filter if view_type == 'personal' else {})
    attendance_stats = get_attendance_statistics(start_date, end_date, user_filter.get('matricule_Technicien', None) if view_type == 'personal' else None)
    
    # Ajouter les couleurs aux statistiques de congés
    for conge in leave_stats['recents']:
        conge.matricule_Technicien.couleur = employe_couleurs.get(
            conge.matricule_Technicien.matricule, "#FFFFFF"
        )
    
    for stat in leave_stats['par_technicien']:
        stat['couleur'] = employe_couleurs.get(
            stat['matricule_Technicien__matricule'], "#FFFFFF"
        )
    
    # Récupérer les statistiques des permissions par technicien
    permissions_queryset = Permission.objects.all()
    
    # Appliquer les filtres de date
    if start_date and end_date:
        permissions_queryset = permissions_queryset.filter(
            DatePer__range=[start_date, end_date]
        )
    
    # Appliquer le filtre utilisateur
    if view_type == 'personal' and user_filter.get('matricule_Technicien'):
        permissions_queryset = permissions_queryset.filter(
            matricule_Technicien=user_filter['matricule_Technicien']
        )
    
    # Statistiques des permissions par technicien
    permissions_par_technicien = permissions_queryset.values(
        'matricule_Technicien__nom',
        'matricule_Technicien__prenom',
        'matricule_Technicien__matricule'
    ).annotate(
        total=Count('id_permission')
    ).order_by('-total')[:10]
    
    # Marquer les retards dans les pointages récents - PARTIE CORRIGÉE
    for pointage in attendance_stats['recents']:
        if pointage.heureArrivee is None:
            pointage.est_en_retard = False  # Si pas d'heure d'arrivée, pas de retard
        else:
            if isinstance(pointage.heureArrivee, str):
                heure_arrivee = datetime.strptime(
                    pointage.heureArrivee, "%H:%M:%S"
                ).time()
            else:
                heure_arrivee = pointage.heureArrivee
            pointage.est_en_retard = heure_arrivee > time(9, 30)
    
    # Statistiques supplémentaires
    service_stats = Service.objects.annotate(
        nombre_employes=Count('employe')
    ).order_by('-nombre_employes')
    
    # Préparer le contexte
    context = {
        'current_datetime': current_datetime,
        'period': period,
        'period_display': period_display,
        'view_type': view_type,
        'user_display': user_display,
        
        # Statistiques des tâches
        'total_taches': task_stats['total'],
        'taches_en_cours': task_stats['en_cours'],
        'taches_non_commencees': task_stats['non_commencees'],
        'taches_terminees': task_stats['terminees'],
        'taches_par_societe': task_stats['par_societe'],
        'recent_taches': task_stats['recentes'],
        
        # Statistiques des congés
        'total_conges': leave_stats['total'],
        'conges_ce_mois': leave_stats['ce_mois'],
        'conges_par_technicien': leave_stats['par_technicien'],
        'recent_conges': leave_stats['recents'],
        
        # Statistiques des permissions
        'total_permissions': permission_stats['total'],
        'permissions_aujourd_hui': permission_stats['aujourd_hui'],
        'permissions_par_type': permission_stats['par_type'],
        'permissions_par_technicien': permissions_par_technicien,
        'recent_permissions': permission_stats['recentes'],
        
        # Statistiques de pointage
        'total_pointages': attendance_stats['total'],
        'pointages_aujourd_hui': attendance_stats['aujourd_hui'],
        'retards_aujourd_hui': attendance_stats['retards_aujourd_hui'],
        'recent_pointages': attendance_stats['recents'],
        
        # Statistiques des services
        'service_stats': service_stats,
    }
    
    return render(request, 'dashboard.html', context)

# Modification des fonctions get_*_statistics pour supporter les filtres

def get_employee_colors():
    """Generate unique colors for employees."""
    employes = Employe.objects.all()
    return {emp.matricule: f'#{random.randint(0, 0xFFFFFF):06x}' for emp in employes}

def get_task_statistics(start_date=None, end_date=None, user_filter=None):
    """Get detailed task statistics with optional filters."""
    current_datetime = now()
    
    # Base queryset
    tasks_queryset = Tache.objects.all()
    
    # Appliquer les filtres de date si spécifiés
    if start_date and end_date:
        date_filter = Q(
            # Tâches qui chevauchent la période sélectionnée
            (Q(DateDebut__lte=end_date) & Q(DateFin__gte=start_date)) |
            # Tâches ajoutées pendant la période
            (Q(dateAjout__gte=start_date) & Q(dateAjout__lte=end_date))
        )
        tasks_queryset = tasks_queryset.filter(date_filter)
    
    # Appliquer les filtres utilisateur si spécifiés
    if user_filter:
        tasks_queryset = tasks_queryset.filter(**user_filter)
    
    # Statistiques filtrées
    return {
        'total': tasks_queryset.count(),
        'en_cours': tasks_queryset.filter(
            DateDebut__lte=current_datetime,
            DateFin__gte=current_datetime
        ).count(),
        'non_commencees': tasks_queryset.filter(
            DateDebut__gt=current_datetime
        ).count(),
        'terminees': tasks_queryset.filter(
            DateFin__lt=current_datetime
        ).count(),
        'par_societe': tasks_queryset.values('codeSoc__NomSociete')
            .annotate(total=Count('RefTache'))
            .order_by('-total'),
        'recentes': tasks_queryset.select_related(
            'codeSoc', 'matricule_Responsable', 'matricule_Technicien'
        ).order_by('-dateAjout')[:5]
    }

def get_leave_statistics(start_date=None, end_date=None, user_filter=None):
    """Get detailed leave statistics with optional filters."""
    current_month = now().month
    
    # Base queryset
    leave_queryset = Conge.objects.all()
    
    # Appliquer les filtres de date si spécifiés
    if start_date and end_date:
        date_filter = Q(
            # Congés qui chevauchent la période sélectionnée
            (Q(DateDeb__lte=end_date) & Q(DateFin__gte=start_date)) |
            # Congés demandés pendant la période
            (Q(dateDemande__gte=start_date) & Q(dateDemande__lte=end_date))
        )
        leave_queryset = leave_queryset.filter(date_filter)
    
    # Appliquer les filtres utilisateur si spécifiés
    if user_filter:
        leave_queryset = leave_queryset.filter(**user_filter)
    
    # Statistiques filtrées
    return {
        'total': leave_queryset.count(),
        'ce_mois': leave_queryset.filter(
            DateDeb__month=current_month
        ).count(),
        'par_technicien': leave_queryset.values(
            'matricule_Technicien__nom',
            'matricule_Technicien__matricule'
        ).annotate(total=Count('numero'))
        .order_by('-total'),
        'recents': leave_queryset.select_related(
            'matricule_responsable', 'matricule_Technicien'
        ).order_by('-dateDemande')[:5]
    }

def get_permission_statistics(start_date=None, end_date=None, user_filter=None):
    """Get detailed permission statistics with optional filters."""
    today = now().date()
    
    # Base queryset
    permission_queryset = Permission.objects.all()
    
    # Appliquer les filtres de date si spécifiés
    if start_date and end_date:
        permission_queryset = permission_queryset.filter(
            DatePer__gte=start_date,
            DatePer__lte=end_date
        )
    
    # Appliquer les filtres utilisateur si spécifiés
    if user_filter:
        permission_queryset = permission_queryset.filter(**user_filter)
    
    # Statistiques filtrées
    return {
        'total': permission_queryset.count(),
        'aujourd_hui': permission_queryset.filter(DatePer=today).count(),
        'par_type': permission_queryset.values(
            'codetype__Type'
        ).annotate(total=Count('id_permission'))
        .order_by('-total'),
        'recentes': permission_queryset.select_related(
            'codetype', 'matricule_responsable', 'matricule_Technicien'
        ).order_by('-DatePer')[:5]
    }

def get_attendance_statistics(start_date=None, end_date=None, employee=None):
    """Get detailed attendance statistics with optional filters."""
    today = now().date()
    
    # Base queryset
    attendance_queryset = Pointage.objects.all()
    
    # Appliquer les filtres de date si spécifiés
    if start_date and end_date:
        attendance_queryset = attendance_queryset.filter(
            datePoint__gte=start_date,
            datePoint__lte=end_date
        )
    
    # Appliquer les filtres d'employé si spécifiés
    if employee:
        attendance_queryset = attendance_queryset.filter(matricule=employee)
    
    # Statistiques filtrées
    return {
        'total': attendance_queryset.count(),
        'aujourd_hui': attendance_queryset.filter(datePoint=today).count(),
        'retards_aujourd_hui': attendance_queryset.filter(
            datePoint=today,
            heureArrivee__isnull=False,  # S'assurer que heureArrivee n'est pas None
            heureArrivee__gt=time(9, 30)
        ).count(),
        'recents': attendance_queryset.select_related('matricule')
            .order_by('-datePoint')[:5]
    }

@login_required
def task(request):
    return render(request, 'task/task.html')

def welcome(request):
    return render(request, 'welcome.html')

@login_required
def calendar(request):
    return render(request, 'calendar/calendar.html')

@login_required
def timesheet_view(request):
    # Obtenir la date de début à partir de la requête
    start_date_str = request.GET.get('start_date')
    
    if start_date_str:
        # Si une date est spécifiée dans la recherche, l'utiliser telle quelle
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    else:
        # Si aucune date n'est spécifiée, utiliser le lundi de la semaine courante
        today = datetime.now()
        start_date = today - timedelta(days=today.weekday())  # weekday() retourne 0 pour lundi, 1 pour mardi, etc.
    
    # Calculer la date de fin (7 jours après la date de début)
    end_date = start_date + timedelta(days=6)

    # Récupérer les services et filtrer par service sélectionné
    services = Service.objects.all()
    selected_service = request.GET.get('service', 'all')

    if selected_service != 'all':
        techniciens = Employe.objects.filter(codeS_id=selected_service)
    else:
        techniciens = Employe.objects.all()

    # Récupérer l'employé sélectionné (filtre par employé)
    selected_employee = request.GET.get('employee', 'all')
    if selected_employee != 'all':
        techniciens = techniciens.filter(matricule=selected_employee)

    # Construire les données pour chaque technicien
    technicien_data = []
    for technicien in techniciens:
        taches = Tache.objects.filter(matricule_Technicien=technicien)
        tache_data = []

        # Ajouter les tâches
        for tache in taches:
            tache_start_date = tache.DateDebut.date() if tache.DateDebut else None
            tache_end_date = tache.DateFin.date() if tache.DateFin else None
            if tache_start_date and tache_end_date:
                delta = tache_end_date - tache_start_date
                for i in range(delta.days + 1):
                    date = tache_start_date + timedelta(days=i)
                    if start_date.date() <= date <= end_date.date():
                        tache_data.append({
                            'id': tache.RefTache,
                            'type': 'tache',
                            'date': date,
                            'NomTache': tache.NomTache,
                            'description': tache.description,
                            'DateDebut': tache.DateDebut,
                            'DateFin': tache.DateFin,
                            'societe': tache.codeSoc.NomSociete if tache.codeSoc else 'N/A',
                        })

        # Ajouter les congés
        conges = Conge.objects.filter(matricule_Technicien=technicien)
        for conge in conges:
            conge_start_date = conge.DateDeb.date() if conge.DateDeb else None
            conge_end_date = conge.DateFin.date() if conge.DateFin else None
            if conge_start_date and conge_end_date:
                delta = conge_end_date - conge_start_date
                for i in range(delta.days + 1):
                    date = conge_start_date + timedelta(days=i)
                    if start_date.date() <= date <= end_date.date():
                        tache_data.append({
                            'id': conge.numero,
                            'type': 'conge',
                            'date': date,
                            'description': f"En congé",
                            'DateDeb': conge.DateDeb,
                            'DateFin': conge.DateFin,
                            'MotifCo': conge.MotifCo or 'Aucun motif',
                        })

        # Ajouter les permissions
        permissions = Permission.objects.filter(matricule_Technicien=technicien)
        for permission in permissions:
            perm_date = permission.DatePer
            if start_date.date() <= perm_date <= end_date.date():
                tache_data.append({
                    'id': permission.id_permission,
                    'type': 'permission',
                    'date': perm_date,
                    'description': f"Permission",
                    'DatePer': permission.DatePer,
                    'HeureDebPer': permission.HeureDebPer,
                    'HeureFinPer': permission.HeureFinPer,
                    'MotifPer': permission.MotifPer or 'Aucun motif',
                    'codetype': permission.codetype,
                })

        # Ajouter les données d'un technicien dans la liste principale
        technicien_data.append({
            'technicien': technicien,
            'taches': tache_data,
        })

    # Pour la navigation entre les semaines, on doit respecter la logique du lundi
    if not start_date_str:
        prev_week = (start_date - timedelta(days=7)).strftime('%Y-%m-%d')
        next_week = (start_date + timedelta(days=7)).strftime('%Y-%m-%d')
    else:
        # Si une date spécifique est recherchée, garder la même logique de navigation
        prev_week = (start_date - timedelta(days=7)).strftime('%Y-%m-%d')
        next_week = (start_date + timedelta(days=7)).strftime('%Y-%m-%d')

    # Préparer le contexte pour le template
    context = {
        'technicien_data': technicien_data,
        'days_of_week': [(start_date + timedelta(days=i)).date() for i in range(7)],
        'current_week': start_date.strftime('%d %B %Y'),
        'start_of_week': start_date,
        'end_of_week': end_date,
        'prev_week': prev_week,
        'next_week': next_week,
        'today': datetime.now().strftime('%Y-%m-%d'),
        'current_day': datetime.now().date(),
        'services': services,
        'selected_service': selected_service,
        'employees': Employe.objects.all(),
        'selected_employee': selected_employee,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
    }

    return render(request, 'timesheet/timesheet_view.html', context)

@login_required
def afficher_employe(request, matricule):
    try:
        # Récupère l'employé basé sur le matricule
        employe = get_object_or_404(Employe, matricule=matricule)
        
        # Vérifie que l'employé est bien lié à l'utilisateur connecté
        if employe.user != request.user:
            raise Http404("Cet employé ne vous appartient pas.")

    except Employe.DoesNotExist:
        raise Http404("Employé non trouvé")
    
    # Renvoie la page avec les informations de l'employé
    return render(request, 'employe/afficher_employe.html', {'employe': employe})

@login_required
def modifier_employe(request, matricule):
    employe = get_object_or_404(Employe, matricule=matricule)
    
    if request.method == "POST":
        form = EmployeForm(request.POST, instance=employe)
        
        # Validation personnalisée
        errors = {}
        
        # Validation du numéro de téléphone (format: 038 05 266 67)
        telephone = request.POST.get('telephone', '').strip()
        if telephone:
            if not re.match(r'^\d{3}\s\d{2}\s\d{3}\s\d{2}$', telephone):
                errors['telephone'] = "Le format du numéro doit être: 038 05 266 67 (10 chiffres avec espaces)"
        
        # Si des erreurs personnalisées existent, les ajouter au formulaire
        if errors:
            for field, error in errors.items():
                form.add_error(field, error)
        
        if form.is_valid() and not errors:
            form.save()
            messages.success(request, "Vos informations ont été mises à jour avec succès.")
            return redirect(reverse('afficher_employe', args=[employe.matricule]))
    else:
        form = EmployeForm(instance=employe)
    
    return render(request, 'employe/modifier_employe.html', {
        'form': form, 
        'employe': employe
    })


@login_required
def events_list(request):
    # Récupérer le paramètre de filtrage avec "moi" comme valeur par défaut
    filtre = request.GET.get("filtre", "moi")
    
    user = request.user  # Utilisateur connecté
    
    # Filtrage des tâches, congés et permissions selon l'option choisie
    if filtre == "moi":
        taches = Tache.objects.filter(matricule_Technicien__user=user).select_related('matricule_Technicien')
        conges = Conge.objects.filter(matricule_Technicien__user=user).select_related('matricule_Technicien')
        permissions = Permission.objects.filter(matricule_Technicien__user=user).select_related('matricule_Technicien', 'codetype')
    else:
        taches = Tache.objects.select_related('matricule_Technicien')
        conges = Conge.objects.select_related('matricule_Technicien')
        permissions = Permission.objects.select_related('matricule_Technicien', 'codetype')
    
    # Liste de couleurs
    couleurs = ["#00B0B8", "#B8B200", "#B86900", "#B83E00", "#B80009",
              "#6C00B8", "#76B800", "#0045B8", "#B8007E", "#00B853"]

    events = []

    # Ajout des tâches avec des couleurs aléatoires
    for tache in taches:
        technicien = f"{tache.matricule_Technicien.nom} {tache.matricule_Technicien.prenom}" if tache.matricule_Technicien else "Non assigné"
        couleur = random.choice(couleurs)  # Choisir une couleur aléatoire
        
        events.append({
            "title": f"Tâche: {tache.description}. Technicien: {technicien}",
            "start": tache.DateDebut.isoformat() if tache.DateDebut else None,
            "end": tache.DateFin.isoformat() if tache.DateFin else None,
            "backgroundColor": couleur,
            "borderColor": couleur,
        })

    # Ajout des congés (en rouge fixe)
    for conge in conges:
        technicien = f"{conge.matricule_Technicien.nom} {conge.matricule_Technicien.prenom}"
        events.append({
            "title": f"Congé de: {technicien}. Dates: du {conge.DateDeb} au {conge.DateFin}",
            "start": conge.DateDeb.isoformat(),
            "end": (conge.DateFin + timedelta(days=1)).isoformat(),  # Inclure le dernier jour
            "backgroundColor": "#FF0000",  # Rouge pour les congés
            "borderColor": "#FF0000",
            "allDay": True,
        })
    
    # Ajout des permissions (en violet)
    for permission in permissions:
        technicien = f"{permission.matricule_Technicien.nom} {permission.matricule_Technicien.prenom}"
        type_permission = permission.codetype.Type if permission.codetype else "Non spécifié"
        motif = permission.MotifPer if permission.MotifPer else "Non spécifié"
        
        events.append({
            "title": f"Permission: {technicien}. Type: {type_permission}. Motif: {motif}",
            "start": permission.HeureDebPer.isoformat(),
            "end": permission.HeureFinPer.isoformat(),
            "backgroundColor": "#9900CC",  # Violet pour les permissions
            "borderColor": "#9900CC",
        })

    return JsonResponse(events, safe=False)


def get_employes(request):
    employes = Employe.objects.all()
    events = []
    hour = 9  # Commence à 9 heures du matin

    for employe in employes:
        start_time = f"2023-01-01T{hour:02d}:00:00"
        end_time = f"2023-01-01T{hour:02d}:59:59"
        events.append({
            'title': f'{employe.nom} {employe.prenom}',
            'start': start_time,
            'end': end_time,
            'display': 'background'  # Afficher l'événement en arrière-plan
        })
        hour += 1  # Incrémente l'heure pour le prochain employé

    return JsonResponse(events, safe=False)

# # --------------------------------- ajout, modification, suppresion tache ---------------------------------
@login_required
def task(request):
    """ Vue pour afficher toutes les tâches de l'utilisateur connecté ou filtrer selon le choix. """
    if not hasattr(request.user, 'employe'):
        messages.error(request, "Vous devez être un employé pour accéder à cette page.")
        return redirect('login')

    # Récupérer les paramètres de filtrage
    filter_option = request.GET.get('filter', 'mine')
    selected_employe = request.GET.get('employe', '')

    # Appliquer les filtres de base
    if filter_option == 'all':
        taches = Tache.objects.all()
    else:
        taches = Tache.objects.filter(matricule_Technicien=request.user.employe)

    # Appliquer le filtre par employé si sélectionné
    if selected_employe:
        taches = taches.filter(matricule_Technicien=selected_employe)

    # Ordonner les tâches par date d'ajout décroissante
    taches = taches.order_by('-dateAjout')

    # Configuration de la pagination
    paginator = Paginator(taches, 10)  # 10 tâches par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Préparer le contexte
    context = {
        'taches': page_obj,  # Remplacer taches par page_obj
        'filter_option': filter_option,
        'employes': Employe.objects.all(),
        'selected_employe': selected_employe,
    }

    return render(request, 'task/task.html', context)

@login_required
def add_task(request):
    """ Vue pour ajouter une nouvelle tâche. """
    if not hasattr(request.user, 'employe'):
        messages.error(request, "Vous devez être un employé pour ajouter une tâche.")
        return redirect('task')

    employes = Employe.objects.all()
    societes = Societe.objects.all()

    if request.method == 'POST':
        NomTache = request.POST.get('NomTache')
        description = request.POST.get('description')
        DateDebut = request.POST.get('DateDebut')
        DateFin = request.POST.get('DateFin')
        codeSoc_id = request.POST.get('codeSoc')
        responsable_id = request.POST.get('matricule_responsable')

        if not NomTache or not description or not codeSoc_id or not responsable_id:
            messages.error(request, "Tous les champs requis doivent être remplis.")
            return render(request, 'task/form.html', {'societes': societes, 'employes': employes})

        if DateDebut >= DateFin:
            messages.error(request, "La date de début doit être antérieure à la date de fin.")
            return render(request, 'task/form.html', {'societes': societes, 'employes': employes})

        responsable = Employe.objects.get(matricule=responsable_id)
        technicien = request.user.employe

        Tache.objects.create(
            NomTache=NomTache,
            description=description,
            DateDebut=DateDebut,
            DateFin=DateFin,
            codeSoc_id=codeSoc_id,
            matricule_Responsable=responsable,
            matricule_Technicien=technicien
        )

        messages.success(request, "Tâche ajoutée avec succès.")
        return redirect('task')

    return render(request, 'task/form.html', {'societes': societes, 'employes': employes})

@login_required
def edit_task(request, RefTache):
    """ Vue pour modifier une tâche existante. """
    tache = get_object_or_404(Tache, pk=RefTache)

    if tache.matricule_Technicien != request.user.employe:
        messages.error(request, "Vous ne pouvez pas modifier cette tâche.")
        return redirect('task')

    employes = Employe.objects.all()
    societes = Societe.objects.all()

    if request.method == 'POST':
        tache.NomTache = request.POST.get('NomTache')
        tache.description = request.POST.get('description')
        DateDebut = request.POST.get('DateDebut')
        DateFin = request.POST.get('DateFin')
        tache.codeSoc_id = request.POST.get('codeSoc')
        responsable_id = request.POST.get('matricule_responsable')

        if not responsable_id:
            messages.error(request, "Vous devez sélectionner un responsable.")
            return render(request, 'task/form.html', {'tache': tache, 'societes': societes, 'employes': employes})

        if DateDebut >= DateFin:
            messages.error(request, "La date de début doit être antérieure à la date de fin.")
            return render(request, 'task/form.html', {'tache': tache, 'societes': societes, 'employes': employes})

        tache.matricule_Responsable = Employe.objects.get(matricule=responsable_id)
        tache.DateDebut = DateDebut
        tache.DateFin = DateFin
        tache.save()

        messages.success(request, "Tâche modifiée avec succès.")
        return redirect('task')

    return render(request, 'task/form.html', {'tache': tache, 'societes': societes, 'employes': employes})

@login_required
def delete_task(request, RefTache):
    """ Vue pour supprimer une tâche existante. """
    tache = get_object_or_404(Tache, pk=RefTache)
    if tache.matricule_Technicien != request.user.employe:
        messages.error(request, "Vous ne pouvez pas supprimer cette tâche.")
        return redirect('task')

    tache.delete()
    messages.success(request, "Tâche supprimée avec succès.")
    return redirect('task')

#-------------------------------------------------Fêtes------------------------------------------------
def get_easter_date(year):
    """Calcul de la date de Pâques"""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)

def get_variable_holidays(year):
    easter_date = get_easter_date(year)
    pentecost_date = easter_date + timedelta(days=49)
    holidays = [
        {"date": date(year, 1, 1), "name": _("Jour de l'An")},
        {"date": date(year, 3, 8), "name": _("Journée internationale des femmes")},
        {"date": date(year, 3, 29), "name": _("Jour des martyrs")},
        {"date": easter_date, "name": _("Pâques")},
        {"date": easter_date + timedelta(days=1), "name": _("Lundi de Pâques")},
        {"date": date(year, 5, 1), "name": _("Fête du Travail")},
        {"date": date(year, 5, 29), "name": _("Ascension")},
        {"date": pentecost_date, "name": _("Pentecôte")},
        {"date": pentecost_date + timedelta(days=1), "name": _("Lundi de Pentecôte")},
        {"date": date(year, 6, 26), "name": _("Jour de l'Indépendance")},
        {"date": date(year, 8, 15), "name": _("Assomption de Marie")},
        {"date": date(year, 11, 1), "name": _("Toussaint")},
        {"date": date(year, 12, 25), "name": _("Noël")},
        {"date": date(year, 12, 31), "name": _("Saint-Sylvestre")},
    ]
    return holidays

@login_required 
def schedules(request, year=None):
    if year is None:
        year = timezone.now().year
    events = get_variable_holidays(year)
    return render(request, 'calendar/schedule.html', {'events': events, 'current_year': year})

#----------------------------------------------------conge------------------------------------------------------
@login_required
def list_conges(request):
    """ Vue pour afficher tous les congés. """
    if not hasattr(request.user, 'employe'):
        messages.error(request, "Vous devez être un employé pour accéder à cette page.")
        return redirect('login')
    
    # Filtre les congés pour l'utilisateur connecté (responsable ou technicien)
    employe = request.user.employe
    conges = Conge.objects.filter(
        matricule_responsable=employe
    ) | Conge.objects.filter(matricule_Technicien=employe)
    
    # Ordonner les congés par DateDeb décroissante
    conges = conges.order_by('-DateDeb')

    # Configuration de la pagination
    paginator = Paginator(conges, 10)  # 10 congés par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Préparer le contexte
    context = {
        'conges': page_obj,
    }
    
    return render(request, 'leave/leave.html', context)

@login_required
def add_conge(request):
    """ Vue pour ajouter un nouveau congé. """
    employes = Employe.objects.all()  # Charger tous les employés
    
    # L'employé connecté est le technicien
    try:
        employe_connecte = Employe.objects.get(user=request.user)
    except Employe.DoesNotExist:
        messages.error(request, "Profil employé non trouvé pour cet utilisateur.")
        return redirect('home')  # Rediriger vers une page appropriée
    
    if request.method == 'POST':
        dateDemande = request.POST.get('dateDemande')
        DateDeb = request.POST.get('DateDeb') or None
        DateFin = request.POST.get('DateFin') or None
        MotifCo = request.POST.get('MotifCo')
        matricule_responsable = request.POST.get('matricule_responsable')

        # Validation des champs requis
        if not dateDemande or not MotifCo or not matricule_responsable:
            messages.error(request, "Les champs Date de Demande, Motif et Responsable sont requis.")
            return render(request, 'leave/form.html', {'employes': employes, 'employe_connecte': employe_connecte})

        # Validation des dates si elles sont fournies
        if DateDeb and DateFin and DateDeb >= DateFin:
            messages.error(request, "La date de début doit être antérieure à la date de fin.")
            return render(request, 'leave/form.html', {'employes': employes, 'employe_connecte': employe_connecte})
        
        if DateDeb and dateDemande > DateDeb:
            messages.error(request, "La date de demande doit être antérieure ou égale à la date de début.")
            return render(request, 'leave/form.html', {'employes': employes, 'employe_connecte': employe_connecte})

        if DateFin and dateDemande > DateFin:
            messages.error(request, "La date de demande doit être antérieure ou égale à la date de fin.")
            return render(request, 'leave/form.html', {'employes': employes, 'employe_connecte': employe_connecte})

        # Générer un numéro de congé unique
        from datetime import date
        aujourd_hui = date.today()
        prefix = f"C-{aujourd_hui.strftime('%Y%m%d')}"
        dernier_conge = Conge.objects.filter(numero__startswith=prefix).order_by('numero').last()
        
        if dernier_conge:
            numero_existant = dernier_conge.numero
            numero_sequence = int(numero_existant.split('-')[-1]) + 1
        else:
            numero_sequence = 1
            
        numero_conge = f"{prefix}-{numero_sequence:03d}"

        # Créer et sauvegarder le congé
        nouveau_conge = Conge(
            numero=numero_conge,
            dateDemande=dateDemande,
            MotifCo=MotifCo,
            matricule_responsable_id=matricule_responsable,
            matricule_Technicien=employe_connecte  # Utiliser l'employé connecté
        )
        
        # Ajouter les dates si fournies
        if DateDeb:
            nouveau_conge.DateDeb = DateDeb
        if DateFin:
            nouveau_conge.DateFin = DateFin
            
        nouveau_conge.save()
        
        messages.success(request, "Congé ajouté avec succès.")
        return redirect('list_conges')

    context = {
        'employes': employes,
        'employe_connecte': employe_connecte,
    }
    return render(request, 'leave/form.html', context)

#-------------------------------------------permission-----------------------------------------
@login_required
def permission_list(request):
    """Afficher la liste des permissions."""
    permissions = Permission.objects.all()
    return render(request, 'permission/permission.html', {'permissions': permissions})

@login_required
def add_permission(request):
    """Ajouter une nouvelle permission."""
    responsables = Employe.objects.all()
    types_permission = TypePermission.objects.all()
    
    if request.method == 'POST':
        date_per = request.POST.get('DatePer')
        heure_deb_per = request.POST.get('HeureDebPer')
        heure_fin_per = request.POST.get('HeureFinPer')
        motif_per = request.POST.get('MotifPer')
        responsable_id = request.POST.get('responsable')
        codetype_id = request.POST.get('codetype')
        
        # Débogage - afficher les valeurs reçues
        print(f"Date: {date_per}")
        print(f"Heure début: {heure_deb_per}")
        print(f"Heure fin: {heure_fin_per}")
        print(f"Motif: {motif_per}")
        print(f"Responsable ID: {responsable_id}")
        print(f"Type permission ID: {codetype_id}")
        
        # Validation des champs requis
        if not date_per or not heure_deb_per or not heure_fin_per or not motif_per or not responsable_id or not codetype_id:
            messages.error(request, "Tous les champs sont requis.")
            return render(request, 'permission/form.html', {
                'responsables': responsables,
                'types_permission': types_permission,
            })
        
        try:
            # Convertir les chaînes en objets datetime
            heure_debut = datetime.fromisoformat(heure_deb_per)
            heure_fin = datetime.fromisoformat(heure_fin_per)
        except ValueError as e:
            print(f"Erreur de conversion de date: {e}")
            messages.error(request, f"Le format de la date/heure est invalide: {e}")
            return render(request, 'permission/form.html', {
                'responsables': responsables,
                'types_permission': types_permission,
            })
        
        if heure_debut >= heure_fin:
            messages.error(request, "L'heure de début doit être antérieure à l'heure de fin.")
            return render(request, 'permission/form.html', {
                'responsables': responsables,
                'types_permission': types_permission,
            })
        
        if (heure_fin - heure_debut) > timedelta(hours=3):
            messages.error(request, "La durée de la permission ne peut pas dépasser 3 heures.")
            return render(request, 'permission/form.html', {
                'responsables': responsables,
                'types_permission': types_permission,
            })
        
        # Récupérer l'employé connecté
        try:
            technicien = Employe.objects.get(user=request.user)
        except Employe.DoesNotExist:
            messages.error(request, "L'utilisateur connecté n'est pas lié à un employé.")
            return redirect('permission_list')
        
        try:
            # Création de la permission
            permission = Permission(
                DatePer=date_per,
                HeureDebPer=heure_debut,
                HeureFinPer=heure_fin,
                MotifPer=motif_per,
                matricule_responsable_id=responsable_id,
                matricule_Technicien=technicien,
                codetype_id=codetype_id
            )
            permission.save()
            messages.success(request, "Permission ajoutée avec succès.")
            return redirect('permission_list')
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            messages.error(request, f"Erreur lors de la création de la permission: {e}")
    
    return render(request, 'permission/form.html', {
        'responsables': responsables,
        'types_permission': types_permission,
    })

#-------------------------------------------------societe------------------------------------------------
@login_required
def list_societes(request):
    societes = Societe.objects.all()  # Récupérer toutes les sociétés
    return render(request, 'societe/societe.html', {'societes': societes})

@login_required
def add_societe(request):
    if request.method == 'POST':
        nom_societe = request.POST.get('NomSociete')  # Récupérer le nom soumis
        if nom_societe:
            Societe.objects.create(NomSociete=nom_societe)  # Créer une nouvelle société
            return redirect(reverse('list_societes'))  # Rediriger vers la liste des sociétés
    return render(request, 'societe/form.html')

#-----------------------------------------people--------------------------------------------
@login_required
def liste_employes(request):
    """Vue pour afficher la liste des employés."""
    employes = Employe.objects.select_related('codeS').all()
    return render(request, 'people/people.html', {'employes': employes})

#-------------------------------------------Pointage----------------------------------------
@login_required
def pointage_view(request):
    # Obtenir la date de début à partir de la requête
    start_date_str = request.GET.get('start_date')
    
    if start_date_str:
        # Si une date est spécifiée dans la recherche, l'utiliser telle quelle
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    else:
        # Si aucune date n'est spécifiée, utiliser le lundi de la semaine courante
        today = datetime.now()
        start_date = today - timedelta(days=today.weekday())  # weekday() retourne 0 pour lundi, 1 pour mardi, etc.
   
    # Calculer la date de fin (7 jours après la date de début)
    end_date = start_date + timedelta(days=6)

    # Récupérer les services et filtrer par service sélectionné
    selected_service = request.GET.get('service', 'all')
    services = Service.objects.all()
   
    if selected_service != 'all':
        employes = Employe.objects.filter(codeS_id=selected_service)
    else:
        employes = Employe.objects.all()
   
    # Récupérer l'employé sélectionné (filtre par employé)
    selected_employee = request.GET.get('employee', 'all')
    if selected_employee != 'all':
        employes = employes.filter(matricule=selected_employee)
   
    # Récupérer les pointages en fonction des employés filtrés
    pointages = Pointage.objects.select_related('matricule').filter(matricule__in=employes)
   
    # Convertir employe_data en une forme plus simple
    employe_data_simple = []
    for employe in employes:
        data = {'employe': employe, 'pointages': []}
        
        for day in [(start_date + timedelta(days=i)).date() for i in range(7)]:
            pointage_for_day = pointages.filter(matricule=employe, datePoint=day).first()
            
            if pointage_for_day:
                data['pointages'].append({
                    'jour': day,
                    'arrivee': pointage_for_day.heureArrivee or '-',
                    'arrivee_style': 'red' if pointage_for_day.heureArrivee and pointage_for_day.heureArrivee >= time(9, 30) else 'black',
                    'sortie': pointage_for_day.heureSortie or '-',
                    'remarque': pointage_for_day.remarque or '',
                    'id': pointage_for_day.dateP  # Utiliser dateP qui est la clé primaire du modèle
                })
            else:
                data['pointages'].append({
                    'jour': day,
                    'arrivee': '-',
                    'arrivee_style': 'black',
                    'sortie': '-',
                    'remarque': '',
                    'id': ''
                })
                
        employe_data_simple.append(data)
   
    # Pour la navigation entre les semaines
    prev_week = (start_date - timedelta(days=7)).strftime('%Y-%m-%d')
    next_week = (start_date + timedelta(days=7)).strftime('%Y-%m-%d')
   
    context = {
        'services': services,
        'selected_service': selected_service,
        'days_of_week': [(start_date + timedelta(days=i)).date() for i in range(7)],
        'today': datetime.now().date(),
        'employe_data': employe_data_simple,
        'current_week': start_date.strftime('%d %B %Y'),
        'prev_week': prev_week,
        'next_week': next_week,
        'today_str': datetime.now().strftime('%Y-%m-%d'),
        'employees': Employe.objects.all(),
        'selected_employee': selected_employee,
        'start_of_week': start_date,
        'end_of_week': end_date,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
    }
   
    return render(request, 'pointage/pointage.html', context)

def get_model_fields(instance):
    fields = []
    for field in instance._meta.get_fields():
        if isinstance(field, Field) and not field.many_to_many and not field.one_to_many:
            try:
                value = getattr(instance, field.name)
                fields.append((field.verbose_name, value))
            except AttributeError:
                continue
    return fields

@login_required
def search_view(request):
    query = request.GET.get('q', '')
    results = []
    
    if query:
        # Recherche dans les modèles
        employes = Employe.objects.filter(
            Q(nom__icontains=query) | Q(prenom__icontains=query) | Q(mail__icontains=query) | Q(adresse__icontains=query)
        )
        taches = Tache.objects.filter(
            Q(RefTache__icontains=query) | Q(NomTache__icontains=query) | Q(description__icontains=query)
        )
        conges = Conge.objects.filter(
            Q(numero__icontains=query) | Q(MotifCo__icontains=query)
        )
        permissions = Permission.objects.filter(
            Q(MotifPer__icontains=query)
        )
        
        # Les listes pour chaque type de résultat
        employe_results = []
        other_results = []
        
        # Traiter les employés
        for result in employes:
            fields = get_model_fields(result)
            result_data = {'instance': result, 'fields': fields}
            
            # Tâches assignées à l'employé - limitées aux 10 plus récentes
            taches_assignées = Tache.objects.filter(
                matricule_Responsable=result
            ).order_by('-DateDebut')[:10]  # Limite à 10 et ordre décroissant par date
            
            taches_formatted = [(tache.NomTache, tache.DateDebut.strftime('%d %B %Y %H:%M'), 
                                tache.DateFin.strftime('%d %B %Y %H:%M')) for tache in taches_assignées]
            
            # Congés à venir et en cours - limités aux 10 plus récents
            today = datetime.now().date()
            conges_avenir_et_en_cours = Conge.objects.filter(
                matricule_Technicien=result,
                DateFin__gte=today
            ).order_by('-DateDeb')[:10]  # Limite à 10 et ordre décroissant par date
            
            conges_formatted = [(conge.MotifCo, conge.DateDeb.strftime('%d %B %Y'), 
                                conge.DateFin.strftime('%d %B %Y')) for conge in conges_avenir_et_en_cours]
            
            # Pointage des 7 derniers jours - limités aux 10 plus récents
            pointages_recent = Pointage.objects.filter(
                matricule=result,
                datePoint__gte=today - timedelta(days=7)
            ).order_by('-datePoint')[:10]  # Limite à 10 et ordre décroissant par date
            
            pointages_formatted = [(pointage.datePoint.strftime('%d %B %Y'), 
                                   pointage.heureArrivee.strftime('%H:%M'), 
                                   pointage.heureSortie.strftime('%H:%M')) for pointage in pointages_recent]
            
            # Ajouter ces informations au résultat
            result_data['taches'] = taches_formatted
            result_data['conges'] = conges_formatted
            result_data['pointages'] = pointages_formatted
            result_data['type'] = 'employe'
            
            employe_results.append(result_data)
        
        # Traiter les autres types de résultats
        for result in list(taches) + list(conges) + list(permissions):
            fields = get_model_fields(result)
            result_data = {
                'instance': result, 
                'fields': fields,
                'type': result.__class__.__name__.lower()
            }
            other_results.append(result_data)
        
        # Combiner les résultats sans duplication
        results = employe_results + other_results
    
    return render(request, 'search.html', {
        'results': results,
        'query': query,
    })
    