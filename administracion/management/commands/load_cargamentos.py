from typing import Any
from django.core.management.base import BaseCommand
from datetime import date
from administracion.models import Cargamento, Proveedor
import random
import string

class Command(BaseCommand):
    help = "Carga de 20 cargamentos"

    def handle(self, *args, **kwargs):
        proveedores = Proveedor.objects.all()
        varietal_choices = ['Malbec', 'Malbeck OAK', 'Torrontes', 'Cabernet Franc', 'Bonarda', 'Cabernet Sauvignon']
        origen_choices = ['Origen1', 'Origen2', 'Origen3', 'Origen4']
        parral_choices = ['Parral1', 'Parral2', 'Parral3', 'Parral4']

        for _ in range(20):
            fecha = date.today()  # Puedes ajustar la fecha según tus necesidades
            lote = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(4)) + "23"
            peso_bruto = random.randint(1000, 10000)
            peso_neto = peso_bruto - random.randint(100, 1000)
            tara = peso_bruto - peso_neto
            camion = f"Camion-{random.randint(1, 10)}"
            dominio = f"AAA{random.randint(100, 999)}"
            camionero = f"Camionero-{random.randint(1, 5)}"
            camionero_razon_social = f"RazonSocial-{random.randint(1, 5)}"
            camionero_cuit = str(random.randint(10000000000, 99999999999))
            proveedor = random.choice(proveedores)
            varietal = random.choice(varietal_choices)
            origen = random.choice(origen_choices)
            parral = random.choice(parral_choices)
            cuartel = f"Cuartel-{random.randint(1, 10)}"
            declarado = random.choice([True, False])
            azucar = round(random.uniform(0, 10), 2)

            Cargamento.objects.create(
                fecha=fecha,
                lote=lote,
                peso_bruto=peso_bruto,
                peso_neto=peso_neto,
                tara=tara,
                camion=camion,
                dominio=dominio,
                camionero=camionero,
                camionero_razon_social=camionero_razon_social,
                camionero_cuit=camionero_cuit,
                proveedor=proveedor,
                varietal=varietal,
                origen=origen,
                parral=parral,
                cuartel=cuartel,
                declarado=declarado,
                azucar=azucar,
            )

        self.stdout.write(self.style.SUCCESS('Datos cargados correctamente'))