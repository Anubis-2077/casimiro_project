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