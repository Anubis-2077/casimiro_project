from typing import Any
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.views.generic import FormView, ListView, View, TemplateView, DetailView
from administracion.forms import *
from django.urls import reverse_lazy
import string
import random
from datetime import datetime 
from django.shortcuts import get_object_or_404
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.db.models import Q
from django.db.models import Subquery, OuterRef, Exists
from django.urls import reverse
from django.http import Http404
from django.utils.dateparse import parse_datetime
from django.forms import modelformset_factory
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.forms import formset_factory
from itertools import chain

from django.utils.decorators import method_decorator



@login_required
def index_admin(request):
    
    return render (request, 'index_admin.html')


#-------------------------------------Login Views-----------------------------------


#-------------------------------------- Cosecha Views

class ProveedorView(FormView):
    template_name = 'administracion/proveedor_form.html'
    form_class = Proveedorform
    success_url= reverse_lazy('proveedores_registrados')

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
    success_url = reverse_lazy('cosechas_registradas')
    
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
    success_url = reverse_lazy ('moliendas_registradas')
    
    def form_valid(self, form):
        
        
        form.save()
        return super().form_valid(form)
    
    def form_invalid(self, form):
        
        print (form.errors)
        response = super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cargamentos = Cargamento.objects.exclude(molienda__isnull=False)
        context ["cargamentos"] = cargamentos
            
        
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
        tanques = Tanque.objects.all()
        #moliendas = Molienda.objects.all()
        
        #moliendas = [molienda for molienda in moliendas if not molienda.contenido_set.filter(embotellado=True).exists()]
        
        moliendas_no_en_contenido = Molienda.objects.annotate(
        esta_en_contenido=Exists(
            Contenido.objects.filter(molienda_id=OuterRef('pk'))
        )
        ).filter(esta_en_contenido=False)
        
        """moliendas_no_embotelladas = Molienda.objects.annotate(
        esta_embotellada=Exists(
            Contenido.objects.filter(molienda_id=OuterRef('pk'), embotellado=False)
        )
        ).filter(esta_embotellada=True)"""
        
        contenidos_filtrados = []
        for tanque in tanques:
            ultimo_contenido = Contenido.objects.filter(tanque=tanque).select_related('molienda').order_by('-fecha_ingreso').first()
            if ultimo_contenido and ultimo_contenido.cantidad > 0 and not ultimo_contenido.embotellado:
                contenidos_filtrados.append(ultimo_contenido)
        
        
        
        
        
        
        
        context = {"tanque_detalle": tanque_select,
                   "molienda": moliendas_no_en_contenido,
                   "molienda_contenido":contenidos_filtrados,
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
                        
                        #print(contenido_origen)

                        # Actualizar fecha de salida en el contenido de origen
                        contenido_origen.fecha_salida = fecha_hora_actual
                        contenido_origen.save()
                        
                        #print("este es el contenido de origen:",contenido_origen)
                        
                        
                        #crear una nueva instancia del contenido en el tanque de origen en donde molienda sea
                        nuevo_contenido_origen = Contenido.objects.create(
                                tanque=contenido_origen.tanque,
                                molienda=molienda,
                                fecha_ingreso=fecha_hora_actual,
                                fecha_salida=None,
                                cantidad=0,  # Siempre es 0 en este caso
                                mover_contenido=False,
                                contenido_trasladado=None,
                                embotellado=False
                                )
                        
                                                        
                        nuevo_contenido_origen.save()
                        
                        #print("este es el nuevo contenido de origen:",nuevo_contenido_origen)
                        
                        #print("esta es la instancia del formulario1:",form1_instance)
                        # Ahora, puedes guardar la instancia de form1 si es necesario
                        form1_instance.save()
                        redirect ('lista_tanques')
                        

                    except (Tanque.DoesNotExist, Contenido.DoesNotExist, Molienda.DoesNotExist) as e:
                        error_message = f"Error: {str(e)}"
                        print("este es el error:",error_message)
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
    success_url = reverse_lazy('sin_etiquetar')
    form_class = EmbotellamientoForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fecha_hora_actual = datetime.now()
        fecha_hora_formateada = fecha_hora_actual.strftime("%Y-%m-%d %H:%M:%S")
        # Obtener la lista de tanques disponibles
        tanques = Tanque.objects.all()

        #print("este es el valor/formato de fecha_hoy:")
        #print(fecha_hora_formateada)
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
        # Cantidad máxima de botellas basada en los litros disponibles
        max_botellas = contenido.cantidad / 0.75  # Asumiendo que cada botella es de 750ml

        numero_botellas_emb = form.cleaned_data['cantidad_botellas']  # Asumiendo que este campo existe en tu formulario

        if numero_botellas_emb > max_botellas:
            form.add_error('cantidad_botellas', 'No puedes embotellar más botellas de las disponibles.')
            return self.form_invalid(form)

        # Actualizar la cantidad restante en el tanque
        litros_restantes = contenido.cantidad - (numero_botellas_emb * 0.75)
        if litros_restantes > 0.74:
        # Si queda más de 0.74 litros, actualizar la cantidad
            contenido.cantidad = litros_restantes
            #print("este es el contenido:", contenido)
            contenido.save()
        else:
            # Si no quedan litros, marcar el contenido como embotellado
            
            contenido.embotellado = True
            contenido.cantidad = 0
           #print("este es el contenido pasando por el else:" ,contenido)
            contenido.save()
            #print("el contenido se modifico:")
            #print(contenido)
            #print(contenido.embotellado)
        
        # Crea una nueva instancia de Embotellamiento
        embotellamiento = form.save(commit=False)
        embotellamiento.contenido = contenido  # Asocia el contenido al embotellamiento
        embotellamiento.save()

        # Crea una nueva instancia de StockBodega
        stock_bodega = StockBodegaSinEtiquetar.objects.create(
        embotellamiento=embotellamiento,
        cantidad_botellas=form.cleaned_data['cantidad_botellas'],  
        varietal=contenido.molienda.cargamento.varietal,  
        lote=contenido.molienda.cargamento.lote, 
        etiquetado=False,
        deposito=Deposito.objects.get(id=3)  
    )
        #print("este es el stock bodega:",stock_bodega)
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
        varietales = ['Rose', 'Cabernet Franc', 'tempranillo', 'Semillon', 'Cabernet Sauvignon', 'Extra Brut', 'Reserva Malbec', 'Malbec OAK', 'Malbec', 'Syrah', 'Moscatel', 'Alejandria','Torrontes']

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
    
    
####################  Etiquetado ########################    
    
class RegistrarEtiquetadoView(FormView):
    """ vista con el formulario para registrar un etiquetado """
    template_name = 'administracion/stock_etiquetado_form.html'
    success_url = reverse_lazy('stock_etiquetado')
    form_class = EtiquetadoForm  

    def get(self, request, *args, **kwargs):
        #print("Cargando la vista RegistrarEtiquetadoView")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        #print("Formulario enviado en RegistrarEtiquetadoView")
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        #print("Preparando el contexto para RegistrarEtiquetadoView")
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
                    stock.cantidad_botellas = 0
                print("el codigo esta pasando por el try")
                print("este es el stock etiquetado:",stock.etiquetado)
                print("este es el stock sin etiquetar:",stock)
                stock.save()  # Guardar el objeto modificado en la base de datos

                # Crea una nueva instancia de BotellaEtiquetada
                
                botella_etiquetada = StockBodegaEtiquetado.objects.create(
                    stock=stock,
                    fecha_etiquetado=datetime.now(),  # O la fecha que corresponda
                    cantidad_botellas=cantidad_botellas,
                    varietal=stock.varietal,  #
                    lote=stock.lote,         
                    empaquetado=False,       
                    observaciones="",        
                    deposito=Deposito.objects.get(pk=3)  
                )
                print("este es el nuevos tock etiquetado:",botella_etiquetada)
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
        varietales = ['Rose', 'Cabernet Franc', 'Cabernet Sauvignon', 'Semillon', 'Extra Brut', 'Reserva Malbec', 'Malbec OAK', 'Malbec', 'Syrah', 'Moscatel', 'Alejandria','Torrontes', 'tempranillo']
        deposito = Deposito.objects.get(id=3) #poner el id del deposito Bodega
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


##################### Empaquetado ####################



class RegistrarEmpaquetadoView(FormView):
    template_name = 'administracion/stock_empaquetado_form.html'
    success_url = reverse_lazy('stock_empaquetado')
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

        

        
        if stock.cantidad_botellas >= cantidad_cajas * 6:
            stock.cantidad_botellas -= cantidad_cajas * 6
            stock.empaquetado = stock.cantidad_botellas <= 0
            stock.save()
            #print("este es el stock: ",stock)
            """ if cantidad_disponible >= cantidad_cajas * 6:
                stock.cantidad_botellas -= cantidad_cajas * 6
                if stock.cantidad_botellas <= 0:
                    stock.empaquetado = True """
            
            #stock.save()
            
            deposito_defecto = Deposito.objects.get(id=3)
            fecha_empaquetado_actual = timezone.now()
            stock_empaquetado = StockBodegaEmpaquetado.objects.create(
            stock=stock,
            cantidad_cajas=cantidad_cajas,
            empaquetado=stock.empaquetado,
            varietal=stock.varietal,
            lote=stock.lote,
            fecha_empaquetado=fecha_empaquetado_actual,
            deposito=deposito_defecto
        )
            #print("este es el stock empaquetado: ",stock_empaquetado)
            
            stock_empaquetado.save()

            return super().form_valid(form)
        
        else:
            raise ValidationError("No puede empaquetar más de lo disponible")
            return self.form_invalid(form)
        
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
        varietales = ['Semillon', 'tempranillo', 'Rose', 'Cabernet Franc', 'Cabernet Sauvignon', 'Extra Brut', 'Reserva Malbec', 'Malbec OAK', 'Malbec', 'Syrah', 'Moscatel', 'Alejandria','Torrontes']

        # Crea un diccionario para almacenar las cantidades de cada varietal
        cantidades = {}
        
        # Crea un diccionario para almacenar los lotes de cada varietal
        lotes = {}

        # Inicializar la suma total de cajas
        total_cajas = 0

        #deposito
        deposito = Deposito.objects.get(id=3)
        
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
    
    
    
# ------------------------------- Depositos--- Bodega!!!!!!! ------------------------------    

    
def stock(request):
    return render (request, 'administracion/stock.html')

def stock_bodega(request):
    # Sumar la cantidad total de todos los contenidos
    total_contenido = Contenido.objects.aggregate(total=Sum('cantidad'))
    
    
    
    total_litros = total_contenido['total']  # Esto es el total de litros en todos los contenidos

    # En caso de que desees sumar solo los contenidos que cumplen ciertas condiciones
    # Por ejemplo, sumar solo los contenidos que aún están en los tanques (fecha_salida es None)
    total_contenido_en_tanques = Contenido.objects.filter(fecha_salida__isnull=True).aggregate(total=Sum('cantidad'))
    
    """ contenidos_en_tanques = Contenido.objects.filter(fecha_salida__isnull=True)

    # Imprimir cada contenido y su cantidad
    for contenido in contenidos_en_tanques:
        print(f"Contenido ID: {contenido.id}, Cantidad: {contenido.cantidad}")

    # Sumar y mostrar el total
    total_contenido_en_tanques = contenidos_en_tanques.aggregate(total=Sum('cantidad'))
    print(f"Total calculado: {total_contenido_en_tanques['total']}") """
    
    
    
    
    
    
    
    
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


#--------------------------Depositos --- Secundarios

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
    producto = StockBodegaEtiquetado.objects.get(id=producto_id)
        # Accediendo a fecha_envasado a través de la relación con StockBodegaSinEtiquetar y Embotellamiento
    fecha_envasado = producto.stock.embotellamiento.fecha_envasado
    tipo = "Stock etiquetado"
    cantidad_botellas= producto.cantidad_botellas

    data = {
            'lote': producto.lote,
            'tipo': tipo,
            'fecha_envasado': fecha_envasado.strftime('%Y-%m-%d') if fecha_envasado else '',
            'cantidad_botellas': cantidad_botellas
        }
    
    return JsonResponse(data)

def get_producto_info_empaquetado(request, producto_id):
    producto = StockBodegaEmpaquetado.objects.get(id=producto_id)
        # Accediendo a fecha_envasado a través de la relación con StockBodegaSinEtiquetar y Embotellamiento
    fecha_empaquetado = producto.stock.stock.embotellamiento.fecha_envasado
    tipo = "Stock empaquetado"
    cantidad_cajas= producto.cantidad_cajas
    cantidad_botellas = cantidad_cajas * 6

    data = {
            'lote': producto.lote,
            'tipo': tipo,
            'fecha_envasado': fecha_empaquetado.strftime('%Y-%m-%d') if fecha_empaquetado else '',
            'cantidad_cajas': cantidad_cajas,
            'cantidad_botellas': cantidad_botellas
        }
    
    return JsonResponse(data)


#---------------------------Movimiento de stock-------------------------------------------


def seleccionar_stock(request, pk):
    # Recuperar el depósito utilizando el pk
    deposito = get_object_or_404(Deposito, pk=pk)

    # Pasar el depósito a la plantilla
    return render(request, 'depositos/redireccionar.html', {'deposito': deposito})

class DetallesDepositoView(DetailView):
    model = Deposito
    template_name = 'depositos/detalles_deposito.html'
    context_object_name = 'deposito'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        deposito = self.object  # El objeto Deposito ya recuperado por DetailView
        
        
        context['etiquetados'] = MoverStockEtiquetado.objects.filter(deposito=deposito)
        context['empaquetados'] = MoverStockEmpaquetado.objects.filter(deposito=deposito)
        
        return context
        
class MoverStockEtiquetadoView(View):
    template_name= 'depositos/mover_stock_etiquetado.html'
    
    def get(self, request, *args, **kwargs):
        Formset = modelformset_factory(MoverStockEtiquetado, form=MoverStockEtiquetadoForm, extra=10)
        formset = Formset(queryset=MoverStockEtiquetado.objects.none())

        BODEGA_ID = 3
        deposito = get_object_or_404(Deposito, pk=self.kwargs['pk'])  # Asume que 'pk' se pasa como parámetro a la URL
        stock_etiquetado = StockBodegaEtiquetado.objects.filter(deposito_id=BODEGA_ID)

        context = {
            'formset': formset,
            'deposito': deposito,
            'stock_etiquetado': stock_etiquetado
        }

        return render(request, self.template_name, context)
            
    def post(self, request, *args, **kwargs):
        Formset = modelformset_factory(MoverStockEtiquetado, form=MoverStockEtiquetadoForm, extra=10)
        formset = Formset(request.POST)
        deposito = get_object_or_404(Deposito, pk=self.kwargs['pk']) 

        if formset.is_valid():
            for form in formset.forms:  # Iterar sobre formset.forms
                # Ahora puedes acceder a form.cleaned_data porque formset.is_valid() fue llamado
                if form.cleaned_data:  # Asegúrate de que el formulario no esté vacío
                    stock_id = form.cleaned_data.get('stock').id
                    cantidad_a_mover = form.cleaned_data.get('cantidad')
                    
                    stock_etiquetado = StockBodegaEtiquetado.objects.get(id=stock_id)
                    stock_etiquetado.cantidad_botellas -= cantidad_a_mover
                    if stock_etiquetado.cantidad_botellas < 0:
                        stock_etiquetado.cantidad_botellas = 0
                    
                    stock_etiquetado.save()
                    form.save()
                    #print("este es el stock empaquetado: " ,stock_etiquetado)
                    #print("este es el form: ", form.cleaned_data)

            return redirect(reverse('detalles_deposito', kwargs={'pk': deposito.pk}))
        else:
            print("estos son los errores: ", formset.errors)
            
        return render(request, 'depositos/mover_stock_etiquetado.html', {'formset': formset})
    
    
    
    
    
#--------------------------stock empaquetado----------------------------

class MoverStockEmpaquetadoView(View):
    template_name= 'depositos/mover_stock_empaquetado.html'
    
    def get(self, request, *args, **kwargs):
        Formset = modelformset_factory(MoverStockEmpaquetado, form=MoverStockEmpaquetadoForm, extra=10)
        formset = Formset(queryset=MoverStockEmpaquetado.objects.none())

        BODEGA_ID = 3
        deposito = get_object_or_404(Deposito, pk=self.kwargs['pk'])  
        stock_empaquetado = StockBodegaEmpaquetado.objects.filter(deposito_id=BODEGA_ID)

        context = {
            'formset': formset,
            'deposito': deposito,
            'stock_empaquetado': stock_empaquetado
        }

        return render(request, self.template_name, context)

    
    def post(self, request, *args, **kwargs):
        Formset = modelformset_factory(MoverStockEmpaquetado, form=MoverStockEmpaquetadoForm, extra=10)
        formset = Formset(request.POST)
        deposito = get_object_or_404(Deposito, pk=self.kwargs['pk']) 

        if formset.is_valid():
            for form in formset.forms:  # Iterar sobre formset.forms
                # Ahora puedes acceder a form.cleaned_data porque formset.is_valid() fue llamado
                if form.cleaned_data:  # Asegúrate de que el formulario no esté vacío
                    stock_id = form.cleaned_data.get('stock').id
                    cantidad_a_mover = form.cleaned_data.get('cantidad')
                    
                    stock_empaquetado = StockBodegaEmpaquetado.objects.get(id=stock_id)
                    stock_empaquetado.cantidad_cajas -= cantidad_a_mover
                    if stock_empaquetado.cantidad_cajas < 0:
                        stock_empaquetado.cantidad_cajas = 0
                    
                    stock_empaquetado.save()
                    form.save()
                    #print("este es el stock empaquetado: " ,stock_empaquetado)
                    #print("este es el form: ", form.cleaned_data)

            return redirect(reverse('detalles_deposito', kwargs={'pk': deposito.pk}))
        else:
            # Manejo de formset no válido
            return render(request, 'depositos/mover_stock_empaquetado.html', {'formset': formset})
            

class HistorialMovimientosView(ListView):
    model = MoverStockEmpaquetado
    template_name = 'depositos/historial_movimientos.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        movimientos_empaquetado = MoverStockEmpaquetado.objects.all()
        for movimiento in movimientos_empaquetado:
            movimiento.tipo_movimiento = 'Empaquetado'
        
        movimientos_etiquetados = MoverStockEtiquetado.objects.all()
        for movimiento in movimientos_etiquetados:
            movimiento.tipo_movimiento = 'Etiquetado'
        
        # Combina y opcionalmente ordena los movimientos
        movimientos_combinados = sorted(
            chain(movimientos_empaquetado, movimientos_etiquetados),
            key=lambda movimiento: movimiento.fecha_movimiento, reverse=True)
        
        context['movimientos'] = movimientos_combinados
        
        return context
        


   

    
    
    


    