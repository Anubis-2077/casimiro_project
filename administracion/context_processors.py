from administracion.views import *
from administracion.models import *

from contabilidad.views import *
from contabilidad.views import *





def notificaciones(request):
    
    tareas = Tarea.objects.filter(realizada =False)
    numero_de_tareas = tareas.count() 
    
    nuevos_envios = Envio.objects.filter(enviado=False)
    numero_de_envios = nuevos_envios.count()
    
    nuevas_notificaciones = numero_de_envios + numero_de_tareas
    
    


    return {
        'tareas': tareas,
        'numero_tareas': numero_de_tareas,
        'envios': nuevos_envios,
        'numero_envios': numero_de_envios,
        'nuevas_notificaciones': nuevas_notificaciones}