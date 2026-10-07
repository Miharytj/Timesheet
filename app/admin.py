from django.contrib import admin
from .models import Service, Societe, Pointage, Employe, Tache, Conge, Permission, TypePermission
from django.utils.translation import gettext_lazy as _
from django.utils.translation import activate
from django.http import HttpResponseRedirect
from django import forms
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError

class LanguageSwitcherForm(forms.Form):
    language = forms.ChoiceField(
        choices=[('fr', _('Français')), ('en', _('Anglais'))],
        widget=forms.Select(attrs={'onchange': 'this.form.submit();'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['language'].initial = 'fr'

def set_language(request):
    if request.method == "POST" and "language" in request.POST:
        lang = request.POST["language"]
        activate(lang)
        request.session["django_language"] = lang
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/"))

class DateFilter(admin.SimpleListFilter):
    title = _('Date')
    parameter_name = 'date'

    def lookups(self, request, model_admin):
        return (
            ('today', _('Aujourd\'hui')),
            ('yesterday', _('Hier')),
            ('this_week', _('Cette semaine')),
            ('last_week', _('Semaine dernière')),
            ('this_month', _('Ce mois')),
            ('last_month', _('Mois dernier')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'today':
            return queryset.filter(dateP__date=timezone.now().date())
        if self.value() == 'yesterday':
            yesterday = timezone.now() - timedelta(days=1)
            return queryset.filter(dateP__date=yesterday.date())
        if self.value() == 'this_week':
            start = timezone.now() - timedelta(days=timezone.now().weekday())
            return queryset.filter(dateP__gte=start)
        if self.value() == 'last_week':
            start = timezone.now() - timedelta(days=timezone.now().weekday() + 7)
            end = timezone.now() - timedelta(days=timezone.now().weekday())
            return queryset.filter(dateP__gte=start, dateP__lt=end)
        if self.value() == 'this_month':
            return queryset.filter(dateP__month=timezone.now().month)
        if self.value() == 'last_month':
            last_month = timezone.now().month - 1 if timezone.now().month > 1 else 12
            return queryset.filter(dateP__month=last_month)

# Fonction utilitaire pour valider l'année
def validate_current_year(date_value, field_name):
    """
    Valide qu'une date n'est pas inférieure à l'année actuelle
    """
    if date_value and date_value.year < timezone.now().year:
        raise ValidationError(
            _('%(field_name)s ne peut pas être antérieure à l\'année actuelle (%(current_year)s).') % {
                'field_name': field_name,
                'current_year': timezone.now().year
            }
        )

# Formulaires personnalisés avec validation
class TacheAdminForm(forms.ModelForm):
    class Meta:
        model = Tache
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('DateDebut')
        date_fin = cleaned_data.get('DateFin')
        
        # Validation des dates par rapport à l'année actuelle
        validate_current_year(date_debut, 'Date de début')
        validate_current_year(date_fin, 'Date de fin')
        
        # Validation de la cohérence des dates
        if date_debut and date_fin and date_debut > date_fin:
            raise ValidationError(
                _('La date de début ne peut pas être supérieure à la date de fin.')
            )
        
        return cleaned_data

class CongeAdminForm(forms.ModelForm):
    class Meta:
        model = Conge
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('DateDeb')
        date_fin = cleaned_data.get('DateFin')
        
        # Validation des dates par rapport à l'année actuelle
        validate_current_year(date_debut, 'Date de début')
        validate_current_year(date_fin, 'Date de fin')
        
        # Validation de la cohérence des dates
        if date_debut and date_fin and date_debut > date_fin:
            raise ValidationError(
                _('La date de début ne peut pas être supérieure à la date de fin.')
            )
        
        return cleaned_data

class PermissionAdminForm(forms.ModelForm):
    class Meta:
        model = Permission
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        date_permission = cleaned_data.get('DatePer')
        heure_debut = cleaned_data.get('HeureDebPer')
        heure_fin = cleaned_data.get('HeureFinPer')
        
        # Validation de la date par rapport à l'année actuelle
        validate_current_year(date_permission, 'Date de permission')
        
        # Validation des heures
        if heure_debut and heure_fin and heure_debut >= heure_fin:
            raise ValidationError(
                _('L\'heure de début ne peut pas être supérieure ou égale à l\'heure de fin.')
            )
        
        return cleaned_data

class PointageAdminForm(forms.ModelForm):
    class Meta:
        model = Pointage
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        date_pointage = cleaned_data.get('datePoint')  # Assuming datePoint is the date field
        heure_arrivee = cleaned_data.get('heureArrivee')
        heure_sortie = cleaned_data.get('heureSortie')
        
        # Validation de la date par rapport à l'année actuelle
        if date_pointage:
            validate_current_year(date_pointage, 'Date de pointage')
        
        # Validation des heures
        if heure_arrivee and heure_sortie and heure_arrivee >= heure_sortie:
            raise ValidationError(
                _('L\'heure d\'arrivée ne peut pas être supérieure ou égale à l\'heure de sortie.')
            )
        
        return cleaned_data

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('codeS', 'poste')
    search_fields = ('codeS', 'poste')
    list_per_page = 20

class SocieteAdmin(admin.ModelAdmin):
    list_display = ('codeSoc', 'NomSociete')
    search_fields = ('codeSoc', 'NomSociete')
    list_per_page = 20

class TypePermissionAdmin(admin.ModelAdmin):
    list_display = ('codetype', 'Type')
    search_fields = ('codetype', 'Type')
    list_per_page = 20

class EmployeAdmin(admin.ModelAdmin):
    readonly_fields = ('matricule',)
    list_display = ('matricule', 'nom', 'prenom', 'adresse', 'mail', 'numero', 'departement', 'get_service')
    search_fields = ('matricule', 'nom', 'prenom', 'mail', 'numero', 'departement')
    list_filter = ('codeS', 'departement')
    list_per_page = 20
    
    def get_service(self, obj):
        return obj.codeS.poste if obj.codeS else "-"
    get_service.short_description = "Service"
    
    @transaction.atomic
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

class TacheAdmin(admin.ModelAdmin):
    form = TacheAdminForm
    readonly_fields = ('RefTache',)
    list_display = ('RefTache', 'dateAjout', 'NomTache', 'description', 'DateDebut', 'DateFin', 'get_societe', 'matricule_Responsable', 'matricule_Technicien')
    search_fields = ('RefTache', 'NomTache', 'description', 'matricule_Responsable__nom', 'matricule_Responsable__prenom', 'matricule_Technicien__nom', 'matricule_Technicien__prenom')
    list_filter = ('codeSoc', 'matricule_Responsable', 'matricule_Technicien', DateFilter)
    date_hierarchy = 'DateDebut'
    ordering = ('-DateDebut',)
    list_per_page = 20
    
    def get_societe(self, obj):
        return obj.codeSoc.NomSociete
    get_societe.short_description = "Société"
    
    @transaction.atomic
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

class CongeAdmin(admin.ModelAdmin):
    form = CongeAdminForm
    readonly_fields = ('numero',)
    list_display = ('numero', 'dateDemande', 'DateDeb', 'DateFin', 'matricule_responsable', 'matricule_Technicien')
    search_fields = ('numero', 'matricule_responsable__nom', 'matricule_responsable__prenom', 'matricule_Technicien__nom', 'matricule_Technicien__prenom')
    list_filter = ('matricule_responsable', 'matricule_Technicien', DateFilter)
    date_hierarchy = 'DateDeb'
    ordering = ('-DateDeb',)
    list_per_page = 20
    
    @transaction.atomic
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

class PointageAdmin(admin.ModelAdmin):
    form = PointageAdminForm
    list_display = ('dateP', 'datePoint', 'matricule', 'heureArrivee', 'heureSortie', 'remarque')
    search_fields = ('matricule__nom', 'matricule__prenom', 'matricule__matricule', 'remarque')
    list_filter = ('matricule', DateFilter)
    ordering = ('-dateP',)
    list_per_page = 20

class PermissionAdmin(admin.ModelAdmin):
    form = PermissionAdminForm
    list_display = ('id_permission', 'DatePer', 'HeureDebPer', 'HeureFinPer', 'MotifPer', 'matricule_responsable', 'matricule_Technicien', 'codetype')
    search_fields = ('id_permission', 'MotifPer', 'matricule_responsable__nom', 'matricule_responsable__prenom', 'matricule_Technicien__nom', 'matricule_Technicien__prenom', 'codetype__Type')
    list_filter = ('matricule_responsable', 'matricule_Technicien', 'codetype', DateFilter)
    date_hierarchy = 'DatePer'
    ordering = ('-DatePer', 'HeureDebPer')
    list_per_page = 20
    
    fieldsets = (
        (None, {
            'fields': ('DatePer', 'HeureDebPer', 'HeureFinPer', 'MotifPer', 'codetype')
        }),
        ('Associations', {
            'fields': ('matricule_responsable', 'matricule_Technicien')
        }),
    )

admin.site.register(Service, ServiceAdmin)
admin.site.register(Societe, SocieteAdmin)
admin.site.register(TypePermission, TypePermissionAdmin)
admin.site.register(Pointage, PointageAdmin)
admin.site.register(Employe, EmployeAdmin)
admin.site.register(Tache, TacheAdmin)
admin.site.register(Conge, CongeAdmin)
admin.site.register(Permission, PermissionAdmin)