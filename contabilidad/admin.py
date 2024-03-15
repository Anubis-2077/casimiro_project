from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Venta)
admin.site.register(DetalleVenta)
admin.site.register(Carrito)
admin.site.register(CartItem)
admin.site.register(Cliente)
admin.site.register(Envio)
