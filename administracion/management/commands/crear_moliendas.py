from django.core.management.base import BaseCommand
from administracion.models import Molienda, Cargamento
import random
from datetime import date

class Command(BaseCommand):
    help = "Asignación de Cargamentos a Molienda"

    def handle(self, *args, **kwargs):
        cargamentos = Cargamento.objects.all()
        responsables = ['Responsable1', 'Responsable2', 'Responsable3', 'Responsable4']
        agregados =['ventonita', 'cloro', 'aguarras']

        for cargamento in cargamentos:
            fecha_molienda = date.today()  # Puedes ajustar la fecha según tus necesidades
            agregados = random.choice(agregados)
            
            responsables = random.choice(responsables)
            cantidad_operarios = random.randint(1, 10)
            rendimiento = random.randint(100, 35000)

            Molienda.objects.create(
                cargamento=cargamento,
                fecha_molienda=fecha_molienda,
                agregados=agregados,
                
                responsables=responsables,
                cantidad_operarios=cantidad_operarios,
                rendimiento=rendimiento,
            )

        self.stdout.write(self.style.SUCCESS('Cargamentos asignados a Molienda correctamente'))
