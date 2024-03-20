from django.contrib import admin
from administracion.models import *

# Register your models here.
admin.site.register(Proveedor)
admin.site.register(Cargamento)
admin.site.register(Molienda)
admin.site.register(Tanque)
admin.site.register(Contenido)

admin.site.register(StockBodegaEtiquetado)
admin.site.register(StockBodegaSinEtiquetar)
admin.site.register(StockBodegaEmpaquetado)
admin.site.register(Deposito)
admin.site.register(Embotellamiento)
admin.site.register(MoverStockEtiquetado)
admin.site.register(MoverStockEmpaquetado)
admin.site.register(Varietal)
admin.site.register(Tarea)
admin.site.register(ConsumoInsumo)
admin.site.register(NotasDeCata)