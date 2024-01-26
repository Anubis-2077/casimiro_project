from django.shortcuts import render

# Create your views here.

def registrar_ventas (request):
    return render (request, 'contabilidad/registrar_ventas.html')

def registro_deudores (request):
    return render (request, 'contabilidad/registro_deudores.html')

def registro_acreedores (request):
    return render (request, 'contabilidad/registro_acreedores.html')

def clientes (request):
    return render (request, 'contabilidad/clientes.html')

def proveedores (request):
    return render (request, 'contabilidad/proveedores.html')