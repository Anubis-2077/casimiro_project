from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.views.generic import CreateView,UpdateView,View
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.forms import inlineformset_factory
from django.db.models.functions import TruncMonth
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Create your views here.


def registro_deudores (request):
    return render (request, 'contabilidad/registro_deudores.html')

def registro_acreedores (request):
    return render (request, 'contabilidad/registro_acreedores.html')






# ------------------------------------  CONTABILIDAD   ---------------------------------------------
# ------------------------------------  CLIENTES -------------------------------------

def cliente_list(request):
    listado_clientes = Cliente.objects.all()
    return render (request, 'contabilidad/listado_clientes.html', {'listado_clientes': listado_clientes})

class ClienteCreateView(CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'contabilidad/create_cliente.html'
    success_url = reverse_lazy('listado_clientes')  

class ClienteUpdateView(UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'contabilidad/create_cliente.html'
    success_url = reverse_lazy('listado_clientes')
    

@csrf_exempt
@require_POST
def eliminar_cliente(request, pk):
    cliente_id = request.POST.get('id')
    cliente = get_object_or_404(Cliente, id=cliente_id)
    cliente.delete()
    return JsonResponse({'success': True})
    
    
# ------------------------------------  PROVEEDORES -------------------------------------
    
    
def proveedor_list (request):
    listado_proveedores = ProveedorInsumos.objects.all()
    return render (request, 'contabilidad/listado_proveedores.html', {'listado_proveedores': listado_proveedores})

class ProveedorInsumosCreateView(CreateView):
    model = ProveedorInsumos
    form_class = ProveedorInsumosForm
    template_name = 'contabilidad/create_proveedor.html'
    success_url = reverse_lazy('listado_proveedores')  

class ProveedorInsumosUpdateView(UpdateView):
    model = ProveedorInsumos
    form_class = ProveedorInsumosForm
    template_name = 'contabilidad/create_proveedor.html'
    success_url = reverse_lazy('listado_proveedores')
    
@csrf_exempt
@require_POST
def eliminar_proveedor(request, pk):
    proveedor_id = request.POST.get('id')
    proveedor = get_object_or_404(ProveedorInsumos, id=proveedor_id)
    proveedor.delete()
    print("el proveedor se elimino exitosamente")
    return JsonResponse({'success': True})




#ACTUALIZAR PRECIOS----------------------------------------------------


def actualizar_precios(request):
    return render (request,'contabilidad/actualizar_precios.html')


class ActualizarPreciosEmpaquetadoView(View):
    template_name = 'contabilidad/actualizar_precios_empaquetado.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        empaquetado_formset = StockBodegaEmpaquetadoPrecioFormSet(request.POST, queryset=StockBodegaEmpaquetado.objects.all())
        
        if empaquetado_formset.is_valid() :
            empaquetado_formset.save()
            
            #print("este es el empaquetado formset: ", empaquetado_formset.cleaned_data)
            return redirect('index_admin')

        else:
            print("Errores del formset empaquetado:", empaquetado_formset.errors)
        return render(request, self.template_name, {
            'empaquetado_formset': empaquetado_formset,
            
        })

    def get_context_data(self, **kwargs):
        context = {}
        context["empaquetado_formset"] = StockBodegaEmpaquetadoPrecioFormSet(queryset=StockBodegaEmpaquetado.objects.all())
        return context
    
    

class ActualizarPreciosEtiquetadoView(View):
    template_name = 'contabilidad/actualizar_precios_etiquetado.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        etiquetado_formset = StockBodegaEtiquetadoPrecioFormSet(request.POST, queryset=StockBodegaEtiquetado.objects.all())

        if etiquetado_formset.is_valid():
            
            etiquetado_formset.save()
            #print("este es el formset etiquetado: ", etiquetado_formset.cleaned_data)
            
            # Redirigir a alguna URL de éxito
            return redirect('index_admin')

        else:
            
            print("Errores del formset etiquetado:", etiquetado_formset.errors)
            
            
        return render(request, self.template_name, {
            
            'etiquetado_formset': etiquetado_formset,
            
        })

    def get_context_data(self, **kwargs):
        context = {}
        context["etiquetado_formset"] = StockBodegaEtiquetadoPrecioFormSet(queryset=StockBodegaEtiquetado.objects.all())
        return context
    
#FIN ACTUALIZAR PRECIOS ------------------------------------------    




#VENTAS---------------------------------------(detalles de ventas)

def seleccion_deposito(request):
    depositos = Deposito.objects.all()
    context ={
        'depositos':depositos
    }
    return render (request, 'contabilidad/seleccion_deposito.html', context)

def obtener_detalles_venta(request, producto_id, tipo):
    if tipo == 'etiquetado':
        producto = get_object_or_404(StockBodegaEtiquetado, id=producto_id)
        data = {
            'tipo': 'etiquetado',
            'precio_unitario': producto.precio,
            'cantidad_disponible': producto.cantidad_botellas
        }
    elif tipo == 'empaquetado':
        producto = get_object_or_404(StockBodegaEmpaquetado, id=producto_id)
        data = {
            'tipo': 'empaquetado',
            'precio_unitario': producto.precio,
            'cantidad_disponible': producto.cantidad_cajas
        }
    else:
        data = {'error': 'Tipo de producto no especificado'}
        
    return JsonResponse(data)


def obtener_detalles_venta_sucursal(request, producto_id, tipo):
    if tipo == 'etiquetado':
        producto = get_object_or_404(MoverStockEtiquetado, id=producto_id)
        data = {
            'tipo': 'etiquetado',
            'precio_unitario': producto.stock.precio,
            'cantidad_disponible': producto.cantidad
        }
    elif tipo == 'empaquetado':
        producto = get_object_or_404(MoverStockEmpaquetado, id=producto_id)
        data = {
            'tipo': 'empaquetado',
            'precio_unitario': producto.stock.precio,
            'cantidad_disponible': producto.cantidad
        }
    else:
        data = {'error': 'Tipo de producto no especificado'}
        
    return JsonResponse(data)


#VENTAS-----------------------------------------------(BODEGA)

class CrearVentaBodegaView(CreateView):
    model = Venta
    form_class = VentaForm
    template_name = 'contabilidad/nueva_venta_bodega.html'
    success_url = reverse_lazy('index_admin')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['empaquetados'] = StockBodegaEmpaquetado.objects.filter(cantidad_cajas__gt=0)
        context['etiquetados'] = StockBodegaEtiquetado.objects.filter(cantidad_botellas__gt=0)
        context['clientes'] = Cliente.objects.all()
        context['depositos']= Deposito.objects.all()
        context['condiciones']= Venta.condicion.field.choices
        context['fecha']= datetime.today().strftime('%d/%m/%Y %H:%M')
        if self.request.POST:
            context['detalle_formset'] = DetalleVentaFormset(self.request.POST)
        else:
            context['detalle_formset'] = DetalleVentaFormset()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        detalle_formset = context['detalle_formset']

        self.object = form.save()

        if detalle_formset.is_valid():
            #print("este es el formulario Ventas: ", form.cleaned_data)  # Imprime los datos limpios del formulario de Venta

            detalle_formset.instance = self.object

            # Antes de guardar los detalles, actualiza el stock
            for detalle_form in detalle_formset.cleaned_data:
                if not detalle_form.get('DELETE', False):  # Ignora los formularios marcados para borrar
                    producto_id = detalle_form.get('prod_empaquetado') or detalle_form.get('prod_etiquetado')
                    cantidad = detalle_form.get('cantidad')

                    if 'prod_empaquetado' in detalle_form and detalle_form['prod_empaquetado']:
                        # Actualiza StockBodegaEmpaquetado
                        producto = StockBodegaEmpaquetado.objects.get(id=producto_id.id)
                        
                        producto.cantidad_cajas -= cantidad
                        #print("este es el prodcto empaquetado : ", producto)
                        producto.save()
                    elif 'prod_etiquetado' in detalle_form and detalle_form['prod_etiquetado']:
                        # Actualiza StockBodegaEtiquetado
                        producto = StockBodegaEtiquetado.objects.get(id=producto_id.id)
                        producto.cantidad_botellas -= cantidad
                        #print("este es el prodcto etiquetado : ", producto)
                        producto.save()

            detalle_formset.save()
            #print("este es un detalle de ventas: ", detalle_formset.cleaned_data)
            return super().form_valid(form)
    
        else:
            for detalle_form in detalle_formset:
                
                print("este es un detalle de ventas: ",detalle_form.errors)
            return self.render_to_response(self.get_context_data(form=form))

DetalleVentaFormset = inlineformset_factory(Venta, DetalleVenta, form=DetalleVentaForm, extra=20)

#VENTAS--------------------------------------------------(SUCURSALES)

class CrearVentaSucursalView(CreateView):
    model = Venta
    form_class = VentaForm
    template_name = 'contabilidad/nueva_venta_sucursal.html'
    success_url = reverse_lazy('index_admin')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        deposito_id = self.kwargs.get('pk')
        
        context['clientes'] = Cliente.objects.all()
        context['deposito'] = Deposito.objects.get(id=deposito_id)
        context['condiciones'] = Venta.condicion.field.choices
        context['fecha'] = datetime.today().strftime('%d/%m/%Y %H:%M')

        # Preparar el formset con deposito_id
        formset_kwargs = {'queryset': DetalleVentaSucursal.objects.none()}  # Asumiendo que quieres evitar cargar objetos existentes por defecto
        if self.request.POST:
            context['detalle_sucursal_formset'] = DetalleVentaSucursalFormset(self.request.POST, form_kwargs={'deposito_id': deposito_id})
        else:
            context['detalle_sucursal_formset'] = DetalleVentaSucursalFormset(form_kwargs={'deposito_id': deposito_id}, **formset_kwargs)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        detalle_sucursal_formset = context['detalle_sucursal_formset']

        self.object = form.save()

        if detalle_sucursal_formset.is_valid():
            #print("este es el formulario Ventas: ", form.cleaned_data)  # Imprime los datos limpios del formulario de Venta

            detalle_sucursal_formset.instance = self.object

            # Antes de guardar los detalles, actualiza el stock
            for detalle_sucursal_form in detalle_sucursal_formset.cleaned_data:
                if not detalle_sucursal_form.get('DELETE', False):  
                    producto_id = detalle_sucursal_form.get('prod_empaquetado') or detalle_sucursal_form.get('prod_etiquetado')
                    cantidad = detalle_sucursal_form.get('cantidad')

                    if 'prod_empaquetado' in detalle_sucursal_form and detalle_sucursal_form['prod_empaquetado']:
                        
                        producto = MoverStockEmpaquetado.objects.get(id=producto_id.id)
                        
                        producto.cantidad -= cantidad
                        #print("este es el prodcto empaquetado : ", producto)
                        producto.save()
                    elif 'prod_etiquetado' in detalle_sucursal_form and detalle_sucursal_form['prod_etiquetado']:
                        
                        producto = MoverStockEtiquetado.objects.get(id=producto_id.id)
                        producto.cantidad -= cantidad
                        #print("este es el prodcto etiquetado : ", producto)
                        producto.save()

            detalle_sucursal_formset.save()
            #print("este es un detalle de ventas: ", detalle_sucursal_formset.cleaned_data)
            return super().form_valid(form)
    
        else:
            for detalle_sucursal_form in detalle_sucursal_formset:
                print("este es un detalle de ventas: ",detalle_sucursal_form.errors)
            return self.render_to_response(self.get_context_data(form=form))

DetalleVentaSucursalFormset = inlineformset_factory(Venta, DetalleVentaSucursal, form=DetalleVentaSucursalForm, extra=20)


#VENTAS-------------------------------------------------(DETALLES)


class DetallesVentasView(View):
    def get(self, request, *args, **kwargs):
        ventas_por_mes = Venta.objects.annotate(mes=TruncMonth('fecha_venta')).values('mes').annotate(total=Sum('precio_total')).order_by('mes')
        
        meses = [venta['mes'] for venta in ventas_por_mes]
        totales = [venta['total'] for venta in ventas_por_mes]
        ultimo_año_mes = [datetime.now() - relativedelta(months=i) for i in range(12)]
        meses_formato = [fecha.strftime("%Y-%m") for fecha in ultimo_año_mes]
        ventas_por_mes = Venta.objects.annotate(mes=TruncMonth('fecha_venta')).values('mes').annotate(total=Sum('precio_total')).order_by('mes')

# Convertir a diccionario para acceso rápido
        ventas_dict = {venta['mes'].strftime("%Y-%m"): venta['total'] for venta in ventas_por_mes}

        # Asegurar todos los meses en el rango están representados
        totales = [ventas_dict.get(mes, 0) for mes in meses_formato]
        totales_float = [float(total) for total in totales]
        
        context = {
            'meses': meses_formato,
            'totales': totales_float,
        }
        return render(request, 'contabilidad/detalle_ventas.html', context)
    
    
    


# --------------------VENTAS EN LINEA ------------------------------
import mercadopago
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from administracion.models import StockBodegaEmpaquetado, StockBodegaEtiquetado
from .serializers import StockBodegaEtiquetadoSerializer

class TiendaView(View):
    template_name = 'index/tienda2.0.html'
    
    def get(self, request):
        deposito = Deposito.objects.get(nombre="BODEGA")
        stock_etiquetado = StockBodegaEtiquetado.objects.filter(deposito__id=deposito.id)
        stock_empaquetado = StockBodegaEmpaquetado.objects.filter(deposito__id=deposito.id)
        
        carrito_id = request.session.get('carrito_id')
        
        # Intenta obtener el carrito si carrito_id existe, de lo contrario, será None
        carrito = Carrito.objects.filter(id=carrito_id).first() if carrito_id else None
        
        if carrito:
            items_del_carrito = CartItem.objects.filter(carrito=carrito)
            carrito_vacio = not items_del_carrito.exists()
            cantidades_productos = {item.producto.id: item.cantidad for item in items_del_carrito}
            precio_total = calcular_precio_total(carrito) if not carrito_vacio else 0
        else:
            carrito_vacio = True
            items_del_carrito = []
            cantidades_productos = {}
            precio_total = 0
        
        return render(request, self.template_name, {
            'stock_etiquetado': stock_etiquetado,
            'stock_empaquetado': stock_empaquetado,
            'items_del_carrito': items_del_carrito,
            'cantidades_productos': cantidades_productos,
            'precio_total': precio_total,
            'carrito_vacio': carrito_vacio
        })



class CreatePreferenceView(APIView):
    def post(self, request, *args, **kwargs):
        carrito_id = request.session.get('carrito_id', None)
        if not carrito_id:
            return Response({"error": "Carrito no encontrado"}, status=404)
        
        carrito = Carrito.objects.filter(id=carrito_id).first()
        if not carrito:
            return Response({"error": "Carrito no encontrado"}, status=404)
        
        items = []
        for item in carrito.items.all():
            producto = item.producto  # Asegúrate de tener una forma de acceder a la instancia de producto aquí
            items.append({
                "title": producto.varietal.nombre,
                "quantity": item.cantidad,
                "unit_price": producto.precio,
            })
        
        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
        preference_data = {"items": items}
        preference_response = sdk.preference().create(preference_data)
        preference_id = preference_response["response"]["id"]
        
        return Response({"preference_id": preference_id})

    
    
@csrf_exempt
def add_to_cart(request):
    producto_tipo = request.POST.get('producto_tipo')
    producto_id = request.POST.get('producto_id')

    # Asignar el modelo basado en el tipo de producto
    modelo_producto = {
        'etiquetado': StockBodegaEtiquetado,
        'empaquetado': StockBodegaEmpaquetado,
    }.get(producto_tipo)

    if not modelo_producto:
        return JsonResponse({'error': 'Tipo de producto no válido'}, status=400)

    producto = get_object_or_404(modelo_producto, id=producto_id)

    carrito_id = request.session.get('carrito_id', None)
    
    if carrito_id:
        carrito, created = Carrito.objects.get_or_create(id=carrito_id)
        if created:
            print("Nuevo carrito creado con éxito.")
        else:
            print("Carrito recuperado con éxito.")
    else:
        carrito = Carrito.objects.create()  # Crear un nuevo carrito si no existe uno
        request.session['carrito_id'] = carrito.id
        print("Nuevo carrito creado y asignado a la sesión con éxito.")
    
    carrito, created = Carrito.objects.get_or_create(id=carrito_id)

    # Verificar si el producto ya está en el carrito
    content_type = ContentType.objects.get_for_model(producto)
    cart_item, created = CartItem.objects.get_or_create(
        carrito=carrito,
        content_type=content_type,
        object_id=producto.id,
        defaults={'cantidad': 1}
    )

    producto_url_imagen = request.build_absolute_uri(producto.varietal.imagen.url)
    

    if not created:
        cart_item.cantidad += 1
        cart_item.save()
        ya_en_carrito = True
    else:
        ya_en_carrito = False

    # Actualizar el ID del carrito en la sesión si es necesario
    if not carrito_id:
        request.session['carrito_id'] = carrito.id
        
    cantidad_actual = cart_item.cantidad
    
    es_empaquetado = producto_tipo == 'empaquetado'
    precio = producto.precio
    item_id = cart_item.id
    
    precio_total= calcular_precio_total(carrito)
    print("este es el precio total:",precio_total )

    return JsonResponse({
        'ya_en_carrito': ya_en_carrito,
        'mensaje': 'Producto ya agregado al carrito' if ya_en_carrito else 'Producto añadido al carrito',
        'producto_id': producto.id,
        'producto_nombre': producto.varietal.nombre,
        'producto_url_imagen': producto_url_imagen,
        'producto_precio': producto.precio,
        'cantidad_actual': cantidad_actual,
        'es_empaquetado': es_empaquetado,
        'precio': producto.precio,
        'cart_item_id': item_id,
        'precio_total_carrito': precio_total,
    })
    
    
def carrito_detalle(request):
    carrito_id = request.session.get('carrito_id')
    if not carrito_id:
        return JsonResponse({'error': 'Carrito no encontrado'}, status=404)

    carrito = Carrito.objects.get(id=carrito_id)
    items = list(carrito.items.values('producto__nombre', 'cantidad', 'producto__precio'))
    
    return JsonResponse({'items': items})


@require_POST 
@csrf_exempt
def incrementar_cantidad(request, item_id):
    
    item = get_object_or_404(CartItem, id=item_id)
    cart_item_id = item.id
    item.cantidad += 1
    item.save()
    carrito = item.carrito
    precio_total_carrito = calcular_precio_total(carrito)
    return JsonResponse({'nueva_cantidad': item.cantidad, 'precio_total_carrito': precio_total_carrito, 'cart-item-id': cart_item_id})

@require_POST 
@csrf_exempt
def decrementar_cantidad(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    
    item.cantidad = max(item.cantidad - 1, 1)  # Evita cantidades negativas
    item.save()
    carrito = item.carrito
    precio_total_carrito = calcular_precio_total(carrito)
    return JsonResponse({'nueva_cantidad': item.cantidad, 'precio_total_carrito': precio_total_carrito})


def calcular_precio_total(carrito):
    items = CartItem.objects.filter(carrito=carrito)
    precio_total = sum(item.producto.precio * item.cantidad for item in items)
    #for item in items:
        #print (item.producto)
    return precio_total


@csrf_exempt
@require_POST
def limpiar_carrito(request):
    carrito_id = request.session.get('carrito_id')
    if carrito_id:
        # Eliminar el carrito existente
        Carrito.objects.filter(id=carrito_id).delete()
        # Crear un nuevo carrito vacío
        nuevo_carrito = Carrito.objects.create()
        # Actualizar el ID del carrito en la sesión
        request.session['carrito_id'] = nuevo_carrito.id
        mensaje = 'Carrito limpiado correctamente, nuevo carrito creado con éxito.'
    else:
        mensaje = 'No hay carrito para limpiar.'
        nuevo_carrito = Carrito.objects.create()  # Crear un nuevo carrito si no existía uno
        request.session['carrito_id'] = nuevo_carrito.id

    return JsonResponse({'mensaje': mensaje, 'carrito_id': nuevo_carrito.id})



@require_POST 
@csrf_exempt
def eliminar_producto(request, item_id):
    item = CartItem.objects.get(id=item_id)
    item.delete()
    return JsonResponse({'mensaje': 'Producto eliminado del carrito'})