
from django.contrib import admin
from django.urls import path, include
from administracion.views import *
from contabilidad.views import *
from tareas.views import *
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name="index"),
    path('tienda/', TiendaView.as_view(), name='tienda'),
    path('index_admin/',index_admin, name='index_admin'),

    path('accounts/', include('allauth.urls')),
    
    # COSECHA URLS
    path('administracion/cosecha/registrar_proveedor/', ProveedorView.as_view(), name='registrar_proveedor'),
    path('administracion/cosecha/proveedores_registrados/',proveedores_registrados, name='proveedores_registrados'),
    path('administracion/cosecha/ingresar_cosecha/',IngCosechaFormView.as_view() ,name='ingresar_cosecha'),
    path('administracion/cosecha/cosecheas_registradas/',CosechasRegistradasView.as_view() ,name='cosechas_registradas'),
    
    
    # MOLIENDA URLS
    path('administracion/molienda/registrar_molienda/',RegistrarMoliendaView.as_view() ,name='registrar_molienda'),
    path('administracion/molienda/moliendas_registradas/',MoliendasRegistradasView.as_view() ,name='moliendas_registradas'),
    #path('obtener_cantidad_disponible/<int:int>/', obtener_cantidad_disponible, name='obtener_cantidad_disponible'),

    
    
    #TANQUE URLS
    path('tanques/lista_de_tanques/',ListaTanquesView.as_view() ,name='lista_tanques'),
    path('tanques/detalle_tanque/<int:numero>',DetalleTanqueView.as_view() ,name='detalle_tanque'),
    
    path('obtener_contenidos_tanques/<int:contenidoId>/', obtener_contenidos_tanques, name='obtener_contenidos_tanques'),
    
    
    #embotellamiento URls
    path('embotellamiento/', EmbotellamientoView.as_view(), name='embotellamiento'),
    
    #stock
    path('stock/seleccionar_stock/<int:pk>/', seleccionar_stock, name="seleccionar_stock"),

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
    path('deposito/mover_stock_etiquetado/<int:pk>/', MoverStockEtiquetadoView.as_view(), name='mover_stock_etiquetado'),
    path('deposito/mover_stock_empaquetado/<int:pk>/', MoverStockEmpaquetadoView.as_view(), name='mover_stock_empaquetado'),
    path('get_producto_info/<int:producto_id>/', get_producto_info, name='get_producto_info'),
    path('get_producto_info_empaquetado/<int:producto_id>/', get_producto_info_empaquetado, name='get_producto_info_empaquetado'),
    path('deposito/detalles/<int:pk>/', DetallesDepositoView.as_view(), name='detalles_deposito'),
    path('deposito/historial/', HistorialMovimientosView.as_view(), name='historial_movimientos_stock'),
    
    
    
    #--------------------------------------------contabilidad-------------------------------------------
    path('clientes/listado_clientes/', cliente_list, name='listado_clientes'),
    path('clientes/nuevo/', ClienteCreateView.as_view(), name='cliente_create'),
    path('clientes/editar/<int:pk>/', ClienteUpdateView.as_view(), name='cliente_update'),
    path('clientes/eliminar/<int:pk>/', eliminar_cliente, name='cliente_delete'),
    
    
    
    
    path('proveedores_insumos/listado_proveedores/', proveedor_list, name="listado_proveedores"),
    path('proveedores_insumos/nuevo/', ProveedorInsumosCreateView.as_view(), name='proveedor_create'),
    path('proveedores_insumos/editar/<int:pk>/', ProveedorInsumosUpdateView.as_view(), name='proveedor_update'),
    path('proveedores_insumos/delete/<int:pk>/', eliminar_proveedor, name='proveedor_delete'),
    
    
    path('contabilidad/actualizar__precios/', actualizar_precios, name='actualizar_precios'),
    path('contabilidad/actualizar_precios_empaquetado/', ActualizarPreciosEmpaquetadoView.as_view() ,name='actualizar_precios_empaquetado'),
    path('contabilidad/actualizar_precios_etiquetado/', ActualizarPreciosEtiquetadoView.as_view() ,name='actualizar_precios_etiquetado'),
    path('contabilidad/seleccion_deposito/', seleccion_deposito ,name='seleccion_deposito_venta'),
    path('contabilidad/obtener_detalles_venta/<int:producto_id>/<str:tipo>/', obtener_detalles_venta, name="obtener_detalles_venta"),
    path('contabilidad/obtener_detalles_venta_sucursal/<int:producto_id>/<str:tipo>/', obtener_detalles_venta_sucursal, name="obtener_detalles_venta_sucursal"),
    path('contabilidad/nueva_venta/1/', CrearVentaBodegaView.as_view() ,name='nueva_venta_bodega'),
    path('contabilidad/nueva_venta_sucursal/<int:pk>/', CrearVentaSucursalView.as_view() ,name='nueva_venta_sucursal'),
    path('registro_deudores/', registro_deudores ,name='registro_deudores'),
    path('registro_acreedores/', registro_acreedores ,name='registro_acreedores'),
    path('contabilidad/detalle_ventas/', DetallesVentasView.as_view(), name='detalle_ventas'),
    
    #--------------------------------VENTAS EN LINEA 
    path('create_preference/', CreatePreferenceView.as_view(), name='create_preference'),
    path('add-to-cart/', add_to_cart, name='add-to-cart'),
    path('carrito/detalle/', carrito_detalle, name='carrito-detalle'),
    path('incrementar-cantidad/<int:item_id>/', incrementar_cantidad, name='incrementar-cantidad'),
    path('decrementar-cantidad/<int:item_id>/', decrementar_cantidad, name='decrementar-cantidad'),
    path('eliminar-producto/<int:item_id>/', eliminar_producto, name='eliminar-producto'),
    path('limpiar-carrito/', limpiar_carrito, name='limpiar-carrito'),
    
    path('webhook/mercadopago/', mercadopago_webhook, name='mercadopago_webhook'),
     
    path('contabilidad/ventas_en_linea/', VentasEnLineaDashboardView.as_view(), name="ventas_en_linea"),
    path('success/', SuccessView.as_view(), name="success"),
    path('success_confirm/<int:pk>/', PaginaExitoView.as_view(), name='pagina_exito'),
    path('api/datos-ventas/', datos_ventas_json, name='datos-ventas-json'),
    
    path('contabilidad/envios_pendientes/', EnviosPendientesView.as_view(), name='envios_pendientes'),
    path('contabilidad/envios/actualizar_estado/<int:pk>/', ActualizarEnviosView.as_view(), name='actualizar_estado'),
    path('contabilidad/envios_realizados/', EnviosRealizadosView.as_view(), name='envios_realizados'),
    
    
    #---------------------------------------tareas---------------------------------------------
    path('administracion/nueva_tarea/', CrearTareaView.as_view() ,name='nueva_tarea'),
    path('administracion/tareas_realizadas/', ListadoTareasRealizadas.as_view() ,name='listado_tareas_realizadas'),
    path('administracion/tareas_pendientes', TareasPendientesView.as_view() ,name='listado_tareas_pendientes'),
    path('administracion/actualizar_tarea/<int:pk>', ActualizarEstadoTarea.as_view(), name='actualizar_tarea'),
    path('administracion/detalles_tarea/<int:pk>',DetallesTareaView.as_view(), name='detalles_tarea' ),
    
    #-----------------------------insumos----------------------------------
    path('administracion/agregar_insumo/',CrearInsumoView.as_view(), name='crear_inusmo'),
    path('administracion/lista_insumos/',ListadoInsumosView.as_view(), name='listado_insumos'),
    path('insumos/actualizar/<int:pk>/', ActualizarInsumoView.as_view(), name='actualizar_insumo'),
    
    
    
    
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


