from django.core.management.base import BaseCommand
from google_auth_oauthlib.flow import InstalledAppFlow

# Define el alcance necesario para tu aplicación
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class Command(BaseCommand):
    help = 'Obtiene un token de acceso de la API de Gmail'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando el flujo de autenticación de OAuth...')

        # Crea el flujo de autenticación
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)

        # Completa el flujo de OAuth para obtener un token
        creds = flow.run_local_server(port=8080)

        # Guarda el token para uso futuro
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

        self.stdout.write('Token guardado con éxito.')