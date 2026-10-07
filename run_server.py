from waitress import serve
from harel_mallac.wsgi import application  # Remplacez par le nom correct de votre projet

# Configuration de l'adresse IP et du port
ip_address = "192.168.0.104"  # Votre adresse IP
port = 8000

if __name__ == "__main__":
    print(f"Serveur démarré à https://{ip_address}:{port}")
    serve(application, host=ip_address, port=port)