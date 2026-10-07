from django.apps import AppConfig
from django.db.models.signals import post_migrate

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'  # Assurez-vous que c'est le nom correct de votre app

    def ready(self):
        # Import signals
        import app.signals  # Assurez-vous que c'est le bon chemin d'importation
        
        # Connecter le signal post_migrate
        from django.dispatch import receiver
        
        @receiver(post_migrate)
        def create_default_superuser(sender, **kwargs):
            # Ne créer le superutilisateur que si l'application concernée est 'app'
            if sender.name == self.name:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                if not User.objects.filter(username="admin").exists():
                    admin_user = User.objects.create_superuser(
                        username="admin",
                        email="admin@example.com",
                        password="admin123"
                    )
                    print("Superuser 'admin' created successfully!")
                    
                    # Le signal create_employe s'occupera automatiquement de créer
                    # un employé associé à ce superutilisateur