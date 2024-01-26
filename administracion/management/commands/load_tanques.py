from typing import Any
from django.core.management.base import BaseCommand
from administracion.models import Tanque
import random

class Command(BaseCommand):
    help="carga de 48 tanques"
    
    def handle(self, *args,**kwargs):
        materiales = ['PVC', 'Hormigon', 'Acero Inoxidable']
        
        for numero in range (1,49):
            volumen = random.randint(10000, 100000)
            material = random.choice(materiales)
            Tanque.objects.create(numero=numero, volumen=volumen, material=material, qr="")
        
        self.stdout.write(self.style.SUCCESS('Datos cargados correctamente'))
        