import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "casimiro.settings") # Cambia 'casimiro.settings' por tu configuración de Django
import django
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "codexweb.sj@gmail.com", "123")
else:
    print("Superuser already exists.")
