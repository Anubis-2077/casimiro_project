
from django.contrib import admin
from django.urls import path, include
from administracion.views import *
from contabilidad.views import *
from tareas.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index_admin/',index_admin, name='index_admin'),

    path('accounts/', include('allauth.urls')),
    
    # COSECHA URLS
    path('administracion/cosecha/registrar_proveedor/',ProveedorView.as_view(), name='registrar_proveedor'),
    path('administracion/cosecha/proveedores_registrados/',proveedores_registrados, name='proveedores_registrados'),
    path('administracion/cosecha/ingresar_cosecha/',IngCosechaFormView.as_view() ,name='ingresar_cosecha'),
    path('administracion/cosecha/cosecheas_registradas/',CosechasRegistradasView.as_view() ,name='cosechas_registradas'),
    
    
    # MOLIENDA URLS
    path('administracion/molienda/registrar_molienda/',RegistrarMoliendaView.as_view() ,name='registrar_molienda'),
    path('administracion/molienda/moliendas_registradas/',MoliendasRegistradasView.as_view() ,name='moliendas_registradas'),
    path('obtener_cantidad_disponible/<int:molienda_id>/', obtener_cantidad_disponible, name='obtener_cantidad_disponible'),

    
    
    #TANQUE URLS
    path('tanques/lista_de_tanques/',ListaTanquesView.as_view() ,name='lista_tanques'),
    path('tanques/detalle_tanque/<int:numero>',DetalleTanqueView.as_view() ,name='detalle_tanque'),
    path('nota_tarea/<int:nota_tarea_id>/editar/', EditarNotaTareaView.as_view(), name='editar_nota_tarea'),
    path('obtener_contenidos_tanques/<int:id>/', obtener_contenidos_tanques, name='obtener_contenidos_tanques'),
    
    
    #embotellamiento URls
    path('embotellamiento/', EmbotellamientoView.as_view(), name='embotellamiento'),
    
    #stock
    path('stock/sin_etiquetar/', StockSinEtiquetarView.as_view(), name='sin_etiquetar'),
    path('stock/sin_etiquetar/<str:varietal>/', StockDetailView.as_view(), name='stock_detail'),
    path('stock/registrar_etiquetado/', RegistrarEtiquetadoView.as_view(), name='registrar_etiquetado'),
    path('stock/etiquetado/', StockEtiquetadoLista.as_view(), name='stock_etiquetado'),
    path('stock/etiquetado/<str:varietal>/', StockBodegaEtiquetadoDetalle.as_view(), name='stock_detail_etiquetado'),
    path('stock/registrar_empaquetado/', RegistrarEmpaquetadoView.as_view(), name='registrar_empaquetado'),
    path('stock/empaquetado/', StockEmpaquetadoLista.as_view(), name='stock_empaquetado'),
    path('stock/empaquetado/<str:varietal>/', StockEmpaquetadoDetalle.as_view(), name='stock_detail_empaquetado'),
    
    
    path('stock/', stock ,name='stock'),
    path('stock-bodega/', stock_bodega, name="stock_bodega"),
    
    #depositos
    path('stock/crear_deposito', crear_deposito, name="crear_deposito"),
    path('stock/lista_depositos', lista_depositos, name="lista_depositos"),
    path('deposito/editar/<int:pk>/', editar_deposito, name='editar_deposito'),
    path('deposito/eliminar/<int:pk>/', eliminar_deposito, name='eliminar_deposito'),
    path('deposito/detalles_deposito/<int:pk>/', detalles_deposito, name='detalles_deposito'),
    path('deposito/mover_stock/<int:pk>/', mover_stock, name='mover_stock'),
    #informacion del producto para la tabla
    path('get_producto_info/<int:producto_id>/', get_producto_info, name='get_producto_info'),
    
    
    
    #--------------------------------------------contabilidad-------------------------------------------
    path('clientes/listado_clientes/', cliente_list, name='listado_clientes'),
    path('clientes/nuevo/', ClienteCreateView.as_view(), name='cliente_create'),
    path('clientes/editar/<int:pk>/', ClienteUpdateView.as_view(), name='cliente_update'),
    path('clientes/eliminar/<int:pk>/', eliminar_cliente, name='cliente_delete'),
    path('proveedores_insumos/listado_proveedores/', proveedor_list, name="listado_proveedores"),
    path('proveedores_insumos/nuevo/', ProveedorInsumosCreateView.as_view(), name='proveedor_create'),
    path('proveedores_insumos/editar/<int:pk>/', ProveedorInsumosUpdateView.as_view(), name='proveedor_update'),
    path('proveedores_insumos/delete/<int:pk>/', eliminar_proveedor, name='proveedor_delete'),
    
    path('ventas/', registrar_ventas ,name='ventas'),
    path('registro_deudores/', registro_deudores ,name='registro_deudores'),
    path('registro_acreedores/', registro_acreedores ,name='registro_acreedores'),
    
    
    
    
    
    
    path('nueva_tarea/', nueva_tarea ,name='nueva_tarea'),
    path('tareas_realizadas/', tareas_realizadas ,name='tareas_realizadas'),
    path('listado_tareas/', listado_tareas ,name='listado_tareas'),
]
