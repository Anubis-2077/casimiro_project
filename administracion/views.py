from typing import Any
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.views.generic import FormView, ListView, View, TemplateView
from administracion.forms import *
from django.urls import reverse_lazy
import string
import random
from datetime import datetime 
from django.shortcuts import get_object_or_404
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.db.models import Q
from django.db.models import Subquery, OuterRef
from django.urls import reverse
from django.http import Http404
from django.utils.dateparse import parse_datetime
from django.forms import inlineformset_factory
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory




@login_required
def index_admin(request):
    
    return render (request, 'index_admin.html')


#-------------------------------------Login Views-----------------------------------




class ProveedorView(FormView):
    template_name = 'administracion/proveedor_form.html'
    form_class = Proveedorform
    success_url= reverse_lazy('index_admin')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    
    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)
        
    
def proveedores_registrados(request):
    proveedores = Proveedor.objects.all()
    
    return render (request, 'administracion/proveedores_registrados.html', {'proveedores': proveedores})
   


class IngCosechaFormView(FormView):
    template_name = 'administracion/ingresar_cosecha.html'
    form_class = CargamentoForm
    success_url = reverse_lazy('index_admin')
    
    def generar_numero_lote(self):
        caracteres = string.ascii_letters + string.digits
        numero_lote = ''.join(random.choice(caracteres) for _ in range(4))
        ano_actual = str(datetime.now().year)[-2:]
        return numero_lote + ano_actual


    def form_valid(self, form):
        print("Form is valid. Saving data...")
        print(form.cleaned_data)
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['proveedores'] = Proveedor.objects.all()
        context['lote'] = self.generar_numero_lote()
        return context 
        
        
class CosechasRegistradasView(ListView):
    template_name = 'administracion/cosechas_registradas.html'
    model = Cargamento
    context_object_name = 'cosechas'
    

###### Fin administracion Cosechas #############


###### Administracion moliendas ###########    
    
    
class RegistrarMoliendaView(FormView):
    template_name = 'administracion/registrar_molienda.html'
    form_class = Moliendaform
    success_url = reverse_lazy ('index_admin')
    
    def form_valid(self, form):
        print ("el formulario es valido")
        print (form.cleaned_data)
        form.save()
        return super().form_valid(form)
    
    def form_invalid(self, form):
        print ("el formulario es invalido")
        print (form.errors)
        response = super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cargamentos = Cargamento.objects.exclude(molienda__isnull=False)
        context ["cargamentos"] = cargamentos
            
        print(context)
        return context
    
class MoliendasRegistradasView(ListView):
    template_name = 'administracion/moliendas_registradas.html'
    model = Molienda
    context_object_name = 'moliendas'
    
def obtener_cantidad_disponible(request, molienda_id):
    molienda = Molienda.objects.get(id=molienda_id)
    contenidos = Contenido.objects.filter(molienda=molienda)
    print('Este es el contenido de la molienda:')
    print( contenidos)
    cantidad_asignada = sum(contenido.cantidad for contenido in contenidos)
    print(cantidad_asignada)
    cantidad_disponible = molienda.rendimiento - cantidad_asignada
    print(cantidad_disponible)
    return HttpResponse(cantidad_disponible)
    
##### fin Moliendas   #############################################
    
    
##### Inicio Tanques/notas   #############################################
        
class ListaTanquesView(ListView):
    template_name = 'administracion/listado_tanques.html'
    model = Tanque
    context_object_name = 'tanques'
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for tanque in context['tanques']:
            # Obtén solo el último contenido de cada tanque
            tanque.ultimo_contenido = tanque.contenido_set.order_by('-fecha_ingreso').first()
        return context
        
class DetalleTanqueView(View):
    template_name = 'administracion/detalle_tanque.html'
    form1 = ContenidoForm
    form2 = HistorialContenidoForm
    form3 = NotaTareasForm
    

    def get(self, request, *args, **kwargs):
        numero_tanque = self.kwargs['numero']
        tanque_select = Tanque.objects.get(numero=numero_tanque)
        fecha_hora_actual = datetime.now()
        fecha_hora_formateada = fecha_hora_actual.strftime("%d/%m/%Y %H:%M:%S")
        form1_instance = self.form1()
        form2_instance = self.form2()
        form3_instance = self.form3()
        contenido = Contenido.objects.filter(tanque=tanque_select).last()
        tareas = NotaTarea.objects.filter(tanque=tanque_select)
        tanque = Tanque.objects.get(numero = numero_tanque)
        moliendas = Molienda.objects.all()
        
        moliendas = [molienda for molienda in moliendas if not molienda.contenido_set.filter(embotellado=True).exists()]
        
        context = {"tanque_detalle": tanque_select,
                   "molienda": moliendas,
                   "fecha": fecha_hora_formateada,
                   "form1" : form1_instance,
                   "form2" : form2_instance,
                   "form3" : form3_instance,
                   "contenido" : contenido,
                   "tarea": tareas,
                   
                   }

        return render(request, self.template_name, context)
    
    def post(self, request,  *args, **kwargs):
        form1_instance = self.form1(request.POST, request.FILES)
        form2_instance = self.form2(request.POST, request.FILES)
        form3_instance = self.form3(request.POST, request.FILES)
        form_type = request.POST.get('form_type')
        
        
        if form_type == 'form1':
            fecha_hora_actual = datetime.now()
            fecha_hora_formateada = fecha_hora_actual.strftime("%d/%m/%Y %H:%M:%S")

            if form1_instance.is_valid():
                mover_contenido = request.POST.get('mover_contenido')

                if mover_contenido == 'on':
                    tanque_id = request.POST.get('tanque')
                    molienda_id = request.POST.get('molienda')
                    contenido_origen_id = request.POST.get('contenido_origen')
                    
                    try:
                        tanque = Tanque.objects.get(id=tanque_id)
                        contenido_origen = Contenido.objects.get(id=contenido_origen_id)
                        molienda = Molienda.objects.get(id=molienda_id)

                        # Actualizar fecha de salida en el contenido de origen
                        contenido_origen.fecha_salida = fecha_hora_actual
                        contenido_origen.save()
                        
                        #crear una nueva instancia del contenido en el tanque de origen en donde molienda sea
                        nuevo_contenido_origen = Contenido.objects.create(
                                tanque=contenido_origen.tanque,
                                molienda=Molienda.objects.get(pk=30),
                                fecha_ingreso=fecha_hora_actual,
                                fecha_salida=None,
                                cantidad=0,  # Siempre es 0 en este caso
                                mover_contenido=False,
                                contenido_trasladado=None
                                )
                                                        
                        nuevo_contenido_origen.save()
                        print(nuevo_contenido_origen)
                        # Ahora, puedes guardar la instancia de form1 si es necesario
                        form1_instance.save()
                        

                    except (Tanque.DoesNotExist, Contenido.DoesNotExist, Molienda.DoesNotExist) as e:
                        error_message = f"Error: {str(e)}"
                        return render(request, self.template_name, {'error_message': error_message})

                else:
                    form1_instance.save()

        elif form_type == 'form2':
            # Procesar formulario 2
            if form2_instance.is_valid():
                form2_instance.save()
            else:
                print(form2_instance.errors)
                
                
        elif form_type =='form3':
            #procesar formulario 3
            if form3_instance.is_valid():
                form3_instance.save()
            else:
                print(form3_instance.errors)

        return redirect(reverse_lazy('lista_tanques'))
              
    
def obtener_contenidos_tanques(request, id):
    contenidos_tanques = []
    tanques = Tanque.objects.all()
    molienda = Molienda.objects.get(id=id)  # Obtener la instancia de Molienda

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' and request.GET.get('mover_contenido') == 'true':
        for tanque in tanques:
            # Subquery para obtener el ID del último contenido para cada lote
            subquery = Contenido.objects.filter(
                molienda__cargamento__lote=OuterRef('molienda__cargamento__lote'),
                molienda__cargamento__varietal=OuterRef('molienda__cargamento__varietal')
            ).order_by('-fecha_ingreso').values('id')[:1]

            contenidos = Contenido.objects.filter(
                tanque=tanque,
                molienda=molienda,
                id=Subquery(subquery)
            )
            
            for contenido in contenidos:
                contenidos_tanques.append({
                    'contenido_id': contenido.id,
                    'contenido_lote': contenido.molienda.cargamento.lote,
                    'tanque_id': tanque.id,
                    'tanque': tanque.numero,
                    'contenido': contenido.molienda.cargamento.varietal,
                    'cantidad': contenido.cantidad
                })
    
    print(contenidos_tanques)
    return JsonResponse(contenidos_tanques, safe=False)
    
    # Añade una respuesta predeterminada aquí
    return HttpResponse("No se encontraron contenidos de tanques para la molienda seleccionada.")
  
    
class EditarNotaTareaView(View):
    form = NotaTareasForm
    
    def get(self, request, nota_tarea_id, *args, **kwargs):
        nota_tarea = get_object_or_404(NotaTarea, id=nota_tarea_id)
        form_instance = self.form(instance=nota_tarea)
        tarea = NotaTarea.objects.get(id=nota_tarea_id)
        fecha_hora_actual = datetime.now()
        fecha_hora_formateada = fecha_hora_actual.strftime("%d/%m/%Y %H:%M:%S")
        return render(request, 'editar_nota_tarea.html', {'form': form_instance, 'nota_tarea_id': nota_tarea_id, 'tarea': tarea, "fecha": fecha_hora_formateada,})
    
    def post(self, request, nota_tarea_id, *args, **kwargs):
        nota_tarea = get_object_or_404(NotaTarea, id=nota_tarea_id)
        form_instance = self.form(request.POST, instance=nota_tarea)
        
        if form_instance.is_valid():
            form_instance.save()
            tanque_id=nota_tarea.tanque.id
            print(tanque_id)
            return redirect('detalle_tanque', tanque_id)
        else:
            print(form_instance.errors)
        
        return render(request, 'administracion/editar_nota_tarea.html', {'form': form_instance, 'nota_tarea_id': nota_tarea_id})
    

#################  Embotellamiento ##########################

class EmbotellamientoView(FormView):
    template_name = 'administracion/embotellamiento.html'
    success_url = reverse_lazy('index_admin')
    form_class = EmbotellamientoForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fecha_hora_actual = datetime.now()
        fecha_hora_formateada = fecha_hora_actual.strftime("%Y-%m-%d %H:%M:%S")
        # Obtener la lista de tanques disponibles
        tanques = Tanque.objects.all()

        print("este es el valor/formato de fecha_hoy:")
        print(fecha_hora_formateada)
        contenidos_filtrados = []
        for tanque in tanques:
            # Obtener el último contenido asociado a cada tanque
            ultimo_contenido = Contenido.objects.filter(tanque=tanque).order_by('-fecha_ingreso').first()
            
            # Si el contenido existe y su cantidad es mayor a 0, añadirlo a la lista
            if ultimo_contenido and ultimo_contenido.cantidad > 0 and ultimo_contenido.embotellado == False:
                contenidos_filtrados.append(ultimo_contenido)


        context["contenidos"] = contenidos_filtrados
        context["fecha_hoy"] = fecha_hora_formateada
        context ["contenidos_id"] = Contenido.objects.all()
        return context

    

    def form_valid(self, form):
        # Recupera el ID del contenido seleccionado
        contenido_id = form.cleaned_data['contenido'].id 

        # Actualiza el campo 'embotellado' en el objeto Contenido
        contenido = Contenido.objects.get(pk=contenido_id)
        contenido.embotellado = True
        contenido.save()
        print("el contenido se modifico:")
        print(contenido)
        print(contenido.embotellado)
        

        # Crea una nueva instancia de Embotellamiento
        embotellamiento = form.save(commit=False)
        embotellamiento.contenido = contenido  # Asocia el contenido al embotellamiento
        embotellamiento.save()

        # Crea una nueva instancia de Contenido en el tanque de origen
        nuevo_contenido_origen = Contenido.objects.create(
            tanque=contenido.tanque,
            molienda=Molienda.objects.get(pk=30),
            fecha_ingreso=datetime.now(),
            fecha_salida=None,
            cantidad=0,  # Siempre es 0 en este caso
            mover_contenido=False,
            contenido_trasladado=None
        )
        nuevo_contenido_origen.save()

        # Crea una nueva instancia de StockBodega
        stock_bodega = StockBodegaSinEtiquetar(embotellamiento=embotellamiento)
        stock_bodega.save()

        return super().form_valid(form)
        
    
    def form_invalid(self, form):
        
        print ("el formulario es invalido")
        print (form.errors)
        print(form.cleaned_data)
        return super().form_invalid(form) 
    
    
class StockSinEtiquetarView(ListView):
    """ vista que muestra la lista general del stock sin etiquetar """
    template_name = 'administracion/stock_sin_etiquetar.html'
    model = StockBodegaSinEtiquetar

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Define los varietales
        varietales = ['Rose', 'Cabernet Franc', 'Cabernet Sauvignon', 'Extra Brut', 'Reserva Malbec', 'Malbec OAK', 'Malbec', 'Syrah', 'Moscatel', 'Alejandria']

        # Crea un diccionario para almacenar las cantidades de cada varietal
        cantidades = {}
        
        # Inicializar la suma total de botellas
        total_botellas = 0

        # Obtiene las cantidades de cada varietal para botellas sin etiquetar
        for varietal in varietales:
            cantidad = StockBodegaSinEtiquetar.objects.filter(varietal=varietal, etiquetado=False).aggregate(Sum('cantidad_botellas'))['cantidad_botellas__sum'] or 0
            cantidades[varietal] = cantidad
            total_botellas += cantidad  # Suma la cantidad de botellas de este varietal al total

        context["total_botellas"] = total_botellas    
        context["cantidades"] = cantidades
        return context
 
class StockDetailView(TemplateView):
    """ vista que muestra el detalle del stock de cada uno de los varietales sin etiquetar """
    template_name = 'administracion/detalle_sotck_sin_etiquetar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Reemplaza los guiones bajos por espacios en blanco para obtener el nombre original del varietal
        varietal = self.kwargs['varietal'].replace('_', ' ')

        # Filtra los objetos StockBodega por varietal y etiquetado
        stocks = StockBodegaSinEtiquetar.objects.filter(varietal=varietal, etiquetado=False)

        # Calcula la cantidad total de botellas
        total_botellas = stocks.aggregate(Sum('cantidad_botellas'))['cantidad_botellas__sum'] or 0

        # Añade los stocks y el total de botellas al contexto
        context['stocks'] = stocks
        context['total_botellas'] = total_botellas

        return context  
    
    
    
    
class RegistrarEtiquetadoView(FormView):
    """ vista con el formulario para registrar un etiquetado """
    template_name = 'administracion/stock_etiquetado_form.html'
    success_url = reverse_lazy('stock_bodega')
    form_class = EtiquetadoForm  

    def get(self, request, *args, **kwargs):
        print("Cargando la vista RegistrarEtiquetadoView")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        print("Formulario enviado en RegistrarEtiquetadoView")
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        print("Preparando el contexto para RegistrarEtiquetadoView")
        context = super().get_context_data(**kwargs)
        fecha_hora_formateada = datetime.today().strftime("%Y-%m-%d %H:%M")
        context["stock_embotellados"] = StockBodegaSinEtiquetar.objects.filter(etiquetado=False)
        context["fecha_hoy"] = fecha_hora_formateada
        return context

    def form_valid(self, form):
        print("Formulario válido en RegistrarEtiquetadoView")
        cantidad_botellas = form.cleaned_data.get('cantidad_botellas')
        stock_id = form.cleaned_data.get('stock').id
        try:
                # Recupera el ID del stock sin etiquetar seleccionado
                stock_id = form.cleaned_data['stock'].id
                stock = StockBodegaSinEtiquetar.objects.get(pk=stock_id)

                #Restar la cantidad etiquetada a la cantidad embotellada
                stock.cantidad_botellas = stock.cantidad_botellas - cantidad_botellas
                
                # Marca el stock sin etiquetar como etiquetado
                if stock.cantidad_botellas == 0:
                    print("el codigo pasa por aca")
                    stock.etiquetado = True
                print("el codigo esta pasando por el try")
                print(stock.etiquetado)
                print(stock)
                stock.save()  # Guardar el objeto modificado en la base de datos

                # Crea una nueva instancia de BotellaEtiquetada
                botella_etiquetada = StockBodegaEtiquetado(stock=stock, cantidad_botellas=cantidad_botellas)
                botella_etiquetada.save()  # Guardar el objeto en la base de datos

                return super().form_valid(form)
        except StockBodegaSinEtiquetar.DoesNotExist:
            print("StockBodegaSinEtiquetar no encontrado")
            raise Http404("El stock sin etiquetar no existe")

        else:
            raise ValidationError("No puede etiquetar más de lo disponible")

        return super().form_valid(form)

    def form_invalid(self, form):
        print("Formulario inválido en RegistrarEtiquetadoView")
        print("Errores del formulario:", form.errors)
        return super().form_invalid(form)
  
class StockEtiquetadoLista(ListView):
    """ vista que muestra el stock etiquetado en general """  
    template_name = 'administracion/stock_etiquetado_lista.html'
    model = StockBodegaEtiquetado
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Define los varietales
        varietales = ['Rose', 'Cabernet Franc', 'Cabernet Sauvignon', 'Extra Brut', 'Reserva Malbec', 'Malbec OAK', 'Malbec', 'Syrah', 'Moscatel', 'Alejandria','Torrontes']
        deposito = Deposito.objects.get(nombre='Bodega')
        # Crea un diccionario para almacenar las cantidades de cada varietal
        cantidades = {}
        
        # Inicializar la suma total de botellas
        total_botellas = 0

        # Obtiene las cantidades de cada varietal para botellas etiquetadas y no empaquetadas
        for varietal in varietales:
            cantidad = StockBodegaEtiquetado.objects.filter(varietal=varietal, empaquetado=False, deposito=deposito).aggregate(Sum('cantidad_botellas'))['cantidad_botellas__sum'] or 0
            cantidades[varietal] = cantidad
            total_botellas += cantidad  # Suma la cantidad de botellas de este varietal al total

        context["total_botellas"] = total_botellas    
        context["cantidades"] = cantidades
        return context

class StockBodegaEtiquetadoDetalle(TemplateView):
    """ muestra el detalle del stock etiquetado de cada uno de los varietales """
    template_name = 'administracion/detalle_stock_etiquetado.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Reemplaza los guiones bajos por espacios en blanco para obtener el nombre original del varietal
        varietal = self.kwargs['varietal'].replace('_', ' ')
        deposito = Deposito.objects.get(nombre='Bodega')
        # Filtra los objetos StockBodegaEtiquetado por varietal y etiquetado
        stocks = StockBodegaEtiquetado.objects.filter(varietal=varietal, deposito=deposito)
        print(stocks)
        # Calcula la cantidad total de botellas
        total_botellas = stocks.aggregate(Sum('cantidad_botellas'))['cantidad_botellas__sum'] or 0

        # Añade los stocks y el total de botellas al contexto
        context['stocks'] = stocks
        context['total_botellas'] = total_botellas

        return context





class RegistrarEmpaquetadoView(FormView):
    template_name = 'administracion/stock_empaquetado_form.html'
    success_url = reverse_lazy('stock_bodega')
    form_class = EmpaquetadoForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fecha_hora_formateada = datetime.today().strftime("%Y-%m-%d %H:%M")
        context["stock_etiquetados"] = StockBodegaEtiquetado.objects.filter(empaquetado=False)
        context["fecha_hoy"] = fecha_hora_formateada
        return context

    def form_valid(self, form):
        cantidad_cajas = form.cleaned_data.get('cantidad_cajas')
        stock_id = form.cleaned_data['stock'].id
        stock = StockBodegaEtiquetado.objects.get(pk=stock_id)
        cantidad_disponible = stock.cantidad_botellas

        

        
            
        if cantidad_disponible >= cantidad_cajas * 6:
            stock.cantidad_botellas -= cantidad_cajas * 6
            if stock.cantidad_botellas == 0:
                stock.empaquetado = True
            print("este es el stock")
            print(stock)
            stock.save()
            
            deposito_defecto = Deposito.objects.get(nombre='Bodega')
            fecha_empaquetado_actual = datetime.now()
            stock_empaquetado = StockBodegaEmpaquetado(stock=stock, cantidad_cajas=cantidad_cajas)
            stock_empaquetado.fecha_empaquetado = fecha_empaquetado_actual
            stock_empaquetado.varietal = stock.varietal  # Aquí accedes a varietal desde el objeto stock
            stock_empaquetado.lote = stock.lote
            stock_empaquetado.deposito = deposito_defecto
            print("este es el stock empaquetado")
            print(stock_empaquetado)
            
            stock_empaquetado.save()

            return super().form_valid(form)
        
        else:
            raise ValidationError("No puede empaquetar más de lo disponible")
        
    def form_invalid(self, form):
        print ("el formulario es invalido")
        print (form.errors)
        return super().form_invalid(form)

class StockEmpaquetadoLista(ListView):
    template_name = 'administracion/stock_empaquetado_lista.html'
    model = StockBodegaEmpaquetado
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Define los varietales
        varietales = ['Rose', 'Cabernet Franc', 'Cabernet Sauvignon', 'Extra Brut', 'Reserva Malbec', 'Malbec OAK', 'Malbec', 'Syrah', 'Moscatel', 'Alejandria','Torrontes']

        # Crea un diccionario para almacenar las cantidades de cada varietal
        cantidades = {}
        
        # Crea un diccionario para almacenar los lotes de cada varietal
        lotes = {}

        # Inicializar la suma total de cajas
        total_cajas = 0

        #deposito
        deposito = Deposito.objects.get(nombre='Bodega')
        
        # Obtiene las cantidades y los lotes de cada varietal
        for varietal in varietales:
            stocks = StockBodegaEmpaquetado.objects.filter(varietal=varietal, deposito=deposito)
            cantidad = stocks.aggregate(Sum('cantidad_cajas'))['cantidad_cajas__sum'] or 0
            cantidades[varietal] = cantidad
            total_cajas += cantidad  # Suma la cantidad de cajas de este varietal al total

            # Obtiene los lotes para este varietal
            lotes[varietal] = [stock.lote for stock in stocks]

        
        context['deposito'] = deposito
        context["total_cajas"] = total_cajas    
        context["cantidades"] = cantidades
        context["lotes"] = lotes
        return context

class StockEmpaquetadoDetalle(TemplateView):
    template_name = 'administracion/detalle_stock_empaquetado.html'
    model = StockBodegaEmpaquetado

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Reemplaza los guiones bajos por espacios en blanco para obtener el nombre original del varietal
        varietal = self.kwargs['varietal'].replace('_', ' ')
        deposito = Deposito.objects.get(nombre='Bodega')
        # Filtra los objetos StockBodegaEmpaquetado por varietal
        stocks = StockBodegaEmpaquetado.objects.filter(varietal=varietal, deposito=deposito)

        # Calcula la cantidad total de cajas
        total_cajas = stocks.aggregate(Sum('cantidad_cajas'))['cantidad_cajas__sum'] or 0

        # Añade los stocks y el total de cajas al contexto
        context['stocks'] = stocks
        context['total_cajas'] = total_cajas

        return context
    
    
    
    
# ------------------------------- Depositos ------------------------------    
    
def stock(request):
    return render (request, 'administracion/stock.html')

def stock_bodega(request):
    # Sumar la cantidad total de todos los contenidos
    total_contenido = Contenido.objects.aggregate(total=Sum('cantidad'))
    total_litros = total_contenido['total']  # Esto es el total de litros en todos los contenidos

    # En caso de que desees sumar solo los contenidos que cumplen ciertas condiciones
    # Por ejemplo, sumar solo los contenidos que aún están en los tanques (fecha_salida es None)
    total_contenido_en_tanques = Contenido.objects.filter(fecha_salida__isnull=True).aggregate(total=Sum('cantidad'))
    BOTELLAS_POR_CAJA = 6
    
    total_botellas_sin_etiquetar = StockBodegaSinEtiquetar.objects.filter(etiquetado=False).aggregate(total=Sum('cantidad_botellas'))
    total_botellas_etiquetadas = StockBodegaEtiquetado.objects.filter(empaquetado=False).aggregate(total=Sum('cantidad_botellas'))
    resultado = StockBodegaEmpaquetado.objects.filter(fecha_empaquetado__isnull=False).aggregate(total=Sum('cantidad_cajas'))
    total_cajas = resultado['total'] if resultado['total'] is not None else 0
    total_botellas_en_caja = total_cajas * BOTELLAS_POR_CAJA
    
    print("total de botellas en caja")
    print(total_cajas)
    
    
    context ={
        'total_litros_en_tanques' : total_contenido_en_tanques['total'],
        'total_botellas_sin_etiquetar' : total_botellas_sin_etiquetar['total'] if total_botellas_sin_etiquetar['total'] is not None else 0,
        'total_botellas_etiquetadas': total_botellas_etiquetadas['total'] if total_botellas_etiquetadas['total'] is not None else 0,
        'total_cajas' : total_cajas,
        'total_botellas_en_caja' : total_botellas_en_caja
    }
    
    
    return render (request, 'administracion/stock_bodega.html', context)


def crear_deposito(request):
    if request.method == 'POST':
        form = DepositoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_depositos')  # Redirige a donde necesites después de crear el depósito
    else:
        form = DepositoForm()

    return render(request, 'depositos/nuevo_deposito.html', {'form': form})

def lista_depositos(request):
    depositos = Deposito.objects.all()
    return render (request, 'depositos/lista_depositos.html', {'depositos':depositos})

def editar_deposito(request, pk):
    deposito = get_object_or_404(Deposito, pk=pk)
    if request.method == 'POST':
        form = DepositoForm(request.POST, instance=deposito)
        if form.is_valid():
            form.save()
            return redirect('lista_depositos')
    else:
        form = DepositoForm(instance=deposito)

    return render(request, 'depositos/editar_deposito.html', {'form': form, 'deposito':deposito})

def eliminar_deposito(request, pk):
    deposito = get_object_or_404(Deposito, pk=pk)
    if request.method == 'POST':
        deposito.delete()
        return redirect('lista_depositos')

    return render(request, 'depositos/confirmar_eliminar.html', {'deposito': deposito})

def detalles_deposito(request,pk):
    deposito = get_object_or_404(Deposito, pk=pk)

    return render (request, 'depositos/detalles_deposito.html', {'deposito':deposito})

def get_producto_info(request, producto_id):
    try:
        producto = StockBodegaEtiquetado.objects.get(id=producto_id)
        # Accediendo a fecha_envasado a través de la relación con StockBodegaSinEtiquetar y Embotellamiento
        fecha_envasado = producto.stock.embotellamiento.fecha_envasado
        tipo = "Stock etiquetado"
    except StockBodegaEtiquetado.DoesNotExist:
        producto = get_object_or_404(StockBodegaEmpaquetado, id=producto_id)
        # Si es un StockBodegaEmpaquetado, debes acceder a través de dos niveles de relaciones
        fecha_envasado = producto.stock.stock.embotellamiento.fecha_envasado
        tipo = "Stock empaquetado"

    data = {
        'lote': producto.lote,
        'tipo': tipo,
        'fecha_envasado': fecha_envasado.strftime('%Y-%m-%d') if fecha_envasado else ''
    }
    return JsonResponse(data)



class MoverStockView(FormView):
    template_name='depositos/mover_stock.html'
    form_class = formset_factory(MoverStockForm, extra=2)
    success_url='index_admin'
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super(MoverStockView, self).get_context_data(**kwargs)
        
    # Agrega tus variables personalizadas al contexto
        BODEGA_ID = 3
        deposito = get_object_or_404(Deposito, pk=self.kwargs['pk'])  # Asume que 'pk' se pasa como parámetro a la URL
        stock_etiquetado = StockBodegaEtiquetado.objects.filter(deposito_id=BODEGA_ID)

        # Agregar deposito y stock_etiquetado al contexto
        context['deposito'] = deposito
        context['stock_etiquetado'] = stock_etiquetado

        return context
    
    def form_valid(self, form):
       
       
        print("formulario valido")
        for f in form:
            print (f.cleaned_data)
        return super(MoverStockView, self).form_valid(form)

    def form_invalid(self, formset):
        
        print("formulario invalido")
        for form in formset:
            print(form.errors)
        return self.render_to_response(self.get_context_data(form=formset))
    
    


   

    
    
    


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