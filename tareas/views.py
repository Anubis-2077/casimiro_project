from django.shortcuts import render

# Create your views here.

def nueva_tarea (request):
    return render (request, 'tareas/nueva_tarea.html')

def tareas_realizadas (request):
    return render (request, 'tareas/tareas_realizadas.html')

def listado_tareas (request):
    return render (request, 'tareas/listado_tareas.html')

