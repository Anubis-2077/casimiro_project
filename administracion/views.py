from typing import Any
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.views.generic import FormView, ListView, View, TemplateView, DetailView
from administracion.forms import *
from contabilidad.views import Venta, Cliente
from django.urls import reverse_lazy
import string
import random
from datetime import datetime, timedelta
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
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.utils.decorators import method_decorator
from django.utils import timezone



def index(request):
    return render (request, 'index/index.html')





@login_required
def index_admin(request):
    
    resultado_sin_etiquetar = StockBodegaSinEtiquetar.objects.aggregate(total_botellas=Sum('cantidad_botellas'))
    if resultado_sin_etiquetar == None:
        total_botellas_sin_etiquetar = resultado_sin_etiquetar['total_botellas']
    else:
        total_botellas_sin_etiquetar = 0
    
    resultado_etiquetado = StockBodegaEtiquetado.objects.aggregate(total_botellas=Sum('cantidad_botellas'))
    if resultado_etiquetado == None:
        total_botellas_etiquetado = resultado_etiquetado['total_botellas']
    else:
        total_botellas_etiquetado = 0

    resultado_empaquetado = StockBodegaEmpaquetado.objects.aggregate(total_cajas=Sum('cantidad_cajas'))
    if resultado_empaquetado == None:
        total_botellas_empaquetado = resultado_empaquetado['total_cajas'] * 6
    else:
        total_botellas_empaquetado = 0
        
       

    
    
    total_bodega = total_botellas_sin_etiquetar + total_botellas_empaquetado + total_botellas_etiquetado
    
    # Obtener la fecha y hora actual
    ahora = timezone.now()

    # Calcular la fecha de hace 6 meses
    hace_6_meses = ahora - timedelta(days=6*30)

    # Convertir esa fecha a una cadena en formato ISO 8601
    fecha_en_cadena = hace_6_meses.isoformat()
    
    
    ventas_web = Venta.objects.filter(condicion='online', fecha_venta__gte=fecha_en_cadena).aggregate(total=Sum('precio_total'))['total']
        
    
    litros_en_tanque = Contenido.objects.aggregate(total_litros=Sum('cantidad'))
    total_litros_tanque = litros_en_tanque ['total_litros']
    
    insumos_escasos = Insumo.objects.filter(cantidad__lte = 50).count()
    
    tareas=Tarea.objects.all().order_by('-fecha')[:6]
    
    clientes=Cliente.objects.all()
    
    context = {
        'total_bodega': total_bodega,
        'ventas_web':ventas_web,
        'total_litros_en_tanque': total_litros_tanque,
        'insumos_escasos':insumos_escasos,
        'tareas':tareas,
        'clientes':clientes
    }
    

    return render (request, 'index_admin.html',context)

def not_found (request, exception):
    return render (request,'index/404.html', status=404)
#-------------------------------------Login Views-----------------------------------


#-------------------------------------- Cosecha Views


class ProveedorView(LoginRequiredMixin, FormView):
    """vista para registrar proveedor chequeada"""
    template_name = 'administracion/proveedor_form.html'
    form_class = Proveedorform
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    success_url= reverse_lazy('proveedores_registrados')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    
    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)
        
@login_required 
def proveedores_registrados(request):
    """vista proveedores registrados chequeadas"""
    proveedores = Proveedor.objects.all()
    
    return render (request, 'administracion/proveedores_registrados.html', {'proveedores': proveedores})
   
class IngCosechaFormView(LoginRequiredMixin, FormView):
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
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
        varietales = Varietal.objects.all()
        context ["varietales"] = varietales 
        return context 
        
class CosechasRegistradasView(LoginRequiredMixin, ListView):
    login_url = '/accounts/login'
    redirect_field_name = 'redirect_to'
    template_name = 'administracion/cosechas_registradas.html'
    model = Cargamento
    context_object_name = 'cosechas'
    

###### Fin administracion Cosechas #############






###### Administracion moliendas ###########    
    
    
class RegistrarMoliendaView(LoginRequiredMixin, FormView):
    login_url = '/accounts/login/'
    template_name = 'administracion/registrar_molienda.html'
    form_class = MoliendaForm
    success_url = reverse_lazy('moliendas_registradas')

    def get_context_data(self, **kwargs):
        context = super(RegistrarMoliendaView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['insumos_formset'] = ConsumoInsumoFormset(queryset=ConsumoInsumo.objects.none())
        else:
            context['insumos_formset'] = ConsumoInsumoFormset(queryset=ConsumoInsumo.objects.none())
        cargamentos = Cargamento.objects.exclude(molienda__isnull=False)
        context["cargamentos"] = cargamentos
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        insumos_formset = ConsumoInsumoFormset(request.POST)
        
        if form.is_valid() and insumos_formset.is_valid():
            return self.both_valid(form, insumos_formset)
        else:
            # Aquí corregimos pasando insumos_formset al método form_invalid.
            return self.form_invalid(form, insumos_formset)

    def both_valid(self, form, insumos_formset):
        molienda = form.save(commit=False)
        molienda.disponible = molienda.rendimiento
        molienda.save()

        # Asegura guardar el formset sin intentar asociarlo a molienda directamente
        insumos_instances = insumos_formset.save(commit=False)
        for instance in insumos_instances:
            insumo = instance.insumo
            insumo.cantidad -= instance.cantidad_consumida
            insumo.save()
            instance.save()

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, insumos_formset=None):
        # Se ajusta para manejar y potencialmente mostrar errores de insumos_formset
        print('Errores del formulario principal:', form.errors)
        if insumos_formset:
            print('Errores del formset:', insumos_formset.errors)
        return super().form_invalid(form)
    
class MoliendasRegistradasView(LoginRequiredMixin, ListView):
    login_url = '/accounts/login/'
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
        
class ListaTanquesView(LoginRequiredMixin,ListView):
    login_url = '/accounts/login/'
    template_name = 'administracion/listado_tanques.html'
    model = Tanque
    context_object_name = 'tanques'
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for tanque in context['tanques']:
            # Obtén solo el último contenido de cada tanque
            tanque.ultimo_contenido = tanque.contenido_set.order_by('-fecha_ingreso').first()
        return context
        
class DetalleTanqueView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    template_name = 'administracion/detalle_tanque.html'
    form1 = ContenidoForm
    form2 = MoverContenidoForm
    form3 = NotasDeCataForm
    
    

    def get(self, request, *args, **kwargs):
        numero_tanque = self.kwargs['numero']
        tanque_select = Tanque.objects.get(numero=numero_tanque)
        fecha_hora_actual = datetime.now()
        fecha_hora_formateada = fecha_hora_actual.strftime("%d/%m/%Y %H:%M:%S")
        form1_instance = self.form1()
        form2_instance = self.form2()
        form3_instance = self.form3()

        contenido = Contenido.objects.filter(tanque=tanque_select).last()
        
        tanque = Tanque.objects.get(numero = numero_tanque)
        tanques = Tanque.objects.all()
        notas_tanque= NotasDeCata.objects.filter(tanque=tanque).order_by('-fecha')
        
        
        moliendas_disponibles = Molienda.objects.filter(disponible__gt=0)
        print(f"moliendas disponibles {moliendas_disponibles}")
        
        contenidos_filtrados = []
        for tanque in tanques:
            ultimo_contenido = Contenido.objects.filter(tanque=tanque).select_related('molienda').order_by('-fecha_ingreso').first()
            if ultimo_contenido and ultimo_contenido.cantidad > 0 and not ultimo_contenido.embotellado:
                contenidos_filtrados.append(ultimo_contenido)
        

        context = {"tanque_detalle": tanque_select,
                   "molienda": moliendas_disponibles,
                   "molienda_contenido":contenidos_filtrados,
                   "fecha": fecha_hora_formateada,
                   "form1" : form1_instance,
                   "form2" : form2_instance,
                   "form3": form3_instance,
                   "contenido" : contenido,
                   "notas_tanque": notas_tanque
                   
                   
                   }

        return render(request, self.template_name, context)
    
    def post(self, request,  *args, **kwargs):
        form1_instance = self.form1(request.POST, request.FILES)
        form2_instance = self.form2(request.POST, request.FILES)
        form3_instance = self.form3(request.POST, request.FILES)
        
        form_type = request.POST.get('form_type')
        
        
        if form_type == 'form1':
            
                fecha_hora_actual = timezone.now()
                fecha_hora_formateada = fecha_hora_actual.strftime("%d/%m/%Y %H:%M:%S")

                if form1_instance.is_valid():
                    mover_contenido = request.POST.get('mover_contenido')
                    
                    
                    if mover_contenido == 'on':
                        
                        
                        
                        try:
                            molienda_id = request.POST.get('molienda')
                            molienda = Molienda.objects.get(id=molienda_id)
                            numero_tanque = self.kwargs['numero']
                            print(f"Tanque ID: {numero_tanque}")
                            tanque = Tanque.objects.get(id=numero_tanque)
                            cantidad_a_mover = form1_instance.cleaned_data['cantidad']
                            id_contenido_origen = request.POST.get('contenido_origen')
                            contenido_origen = Contenido.objects.get(id=id_contenido_origen)
                            
                            
                            
                                                        
                            if tanque.estado == 'vacio':
                                print("el tanque esta vacio")
                        
                                with transaction.atomic():
                                    if cantidad_a_mover == contenido_origen.cantidad:
                                        # Actualizar el tanque del contenido origen y marcar el tanque original como vacío
                                        tanque_origen = contenido_origen.tanque
                                        contenido_origen.tanque = tanque
                                        
                                        
                                        contenido_origen.save()

                                        tanque_origen.estado = 'vacio'
                                        tanque_origen.save()
                                        
                                        tanque.estado = 'en_uso'
                                        tanque.save()
                                        print("el codigo pasa por el if")
                                    
                                    elif cantidad_a_mover < contenido_origen.cantidad:
                                        # Restar cantidad a mover del contenido de origen
                                        contenido_origen.cantidad -= cantidad_a_mover
                                        contenido_origen.save()
                                        print('el codigo pasa por el elif')
                                        
                                        numero_tanque = self.kwargs['numero']
                                        print(f"Tanque ID: {numero_tanque}")
                                        tanque = Tanque.objects.get(id=numero_tanque)
                                        tanque.estado = 'en_uso'
                                        tanque.save()

                                        # Crear nueva instancia de Contenido para el tanque destino
                                        Contenido.objects.create(
                                            tanque=tanque,
                                            molienda=contenido_origen.molienda,
                                            cantidad=cantidad_a_mover,
                                            fecha_ingreso=fecha_hora_actual,
                                            fecha_salida=None,
                                            mover_contenido=False,
                                            contenido_trasladado=None,
                                            embotellado=False
                                            
                                        )
                                        
                                    else:
                                        #print('este es el contenido de origen:', contenido_origen)
                                        #print('este es el id:', contenido_origen.id)
                                        # Lanzar un error si la cantidad a mover es mayor que la permitida
                                        raise ValueError("La cantidad a mover no puede ser mayor que la cantidad disponible en el origen.")
                                    
                            elif tanque.estado == 'en_uso':
                                print("el tanque esta en uso")
                                
                                
                                try:
                                    contenido_existente = Contenido.objects.filter(tanque=tanque).order_by('-fecha_ingreso').first()
                                    id_contenido_origen = request.POST.get('contenido_origen')
                                    cantidad_a_mover = form1_instance.cleaned_data['cantidad']
                                    contenido_origen = Contenido.objects.get(id=id_contenido_origen)
                                    numero_tanque = contenido_origen.tanque.id
                                    tanque_origen = Tanque.objects.get(id=numero_tanque)
                                    
                                    
                                    print(f"este es el contenido de origen:{contenido_origen}")
                                    print(f"este es el contenido existente{contenido_existente}")
                                       
                                            
                                    if contenido_origen.molienda.cargamento.varietal.nombre == contenido_existente.molienda.cargamento.varietal.nombre:
                                                

                                                if cantidad_a_mover < contenido_origen.cantidad:
                                                    
                                                    contenido_existente.cantidad += cantidad_a_mover
                                                    contenido_origen.cantidad -= cantidad_a_mover
                                                            
                                                    contenido_origen.save()
                                                    contenido_existente.save()
                                                        
                                                        
                                                        
                                                elif cantidad_a_mover == contenido_origen.cantidad:
                                                    #print('la cantidad a mover es la misma que la de origen')
                                                    contenido_origen.cantidad = 0
                                                    #print('esta es la cantidad de origen:' ,contenido_origen.cantidad)
                                                    #print('esta es la cantidad a mover:', cantidad_a_mover)
                                                    #print(f"este es el contenido de origenactualizado: {contenido_origen}")
                                                    tanque_origen.estado = 'vacio'
                                                    #print('este es el id del tanque de origen:', tanque_origen.id)
                                                    #print(f"este es el estado del tanque de origen {tanque_origen.estado}")
                                                    contenido_existente.cantidad += cantidad_a_mover
                                                    contenido_existente.save()
                                                    #print(f"este es el contenido existente actualizado: {contenido_existente}")
                                                    tanque_origen.save()
                                                    contenido_origen.save()
                                                    
                                                    
                                                    
                                                elif contenido_existente.id == contenido_origen.id:
                                                    raise ValidationError("no se puede mover el mismo contenido al mismo tanque")
                                                else:
                                                    raise ValueError("no se puede mover mas contenido del disponible")
                                                
                                except (Tanque.DoesNotExist, Contenido.DoesNotExist, Molienda.DoesNotExist) as e:
                                            error_message = f"Error: {str(e)}"
                                            print('el error es por que no existe')
                                            print("este es el error:",error_message)
                                        

                            redirect ('lista_tanques')
                                

                        except Contenido.DoesNotExist:
                            print(f"El contenido con el id '{id_contenido_origen}' proporcionado no existe.")

                        except ObjectDoesNotExist:
                            print("El objeto buscado no existe.")  # Para el caso de tanque sin contenido
                        except Exception as e:
                            print(f"Error inesperado: {str(e)}")
                            
                        

                    else:
                        with transaction.atomic():
                            molienda_id = request.POST.get('molienda')
                            
                            cantidad_asignada = form1_instance.cleaned_data['cantidad']
                            print('esta es la cantidad asignada:', cantidad_asignada)

                            try:
                                molienda = Molienda.objects.get(id=molienda_id)
                                # Restar la cantidad asignada del disponible en la molienda
                                molienda.disponible -= cantidad_asignada
                                molienda.save()
                                numero_tanque = self.kwargs['numero']
                                tanque = Tanque.objects.get(id=numero_tanque)
                                tanque.estado = 'en_uso'
                                tanque.save()
                                print(f"este es el estado del tanque de origen:{tanque.estado}")

                                # Guardar la instancia del formulario si es necesario
                                form1_instance.save()
                            
                            except Molienda.DoesNotExist as e:
                                error_message = f"Error: {str(e)}"
                                print("este es el error:", error_message)
                                return render(request, self.template_name, {'error_message': error_message})

                                # Redirección con return
                        
                            print(form1_instance.errors)
                return redirect('lista_tanques')

        elif form_type == 'form2':
            # Procesar formulario 2
            if form2_instance.is_valid():
                form2_instance.save()
            else:
                print(form2_instance.errors)
        
        elif form_type == 'form3':
            if form3_instance.is_valid():
                # Asignamos el usuario a la instancia del modelo, no al formulario directamente
                modelo = form3_instance.save(commit=False)  # Guardamos la instancia del modelo sin enviar a la BD
                modelo.usuario = request.user  # Asignamos el usuario
                modelo.save()  # Ahora sí, guardamos en la BD
            else:
                print('hay errores en el form 3')
                print(form3_instance.errors)
                
                
  
        
        print('hay errores aca')
        return redirect(reverse_lazy('lista_tanques'))
              
    
def obtener_contenidos_tanques(request, contenidoId):
    try:
        contenido = Contenido.objects.get(id=contenidoId)
        
        # Preparar el diccionario con la información del contenido seleccionado
        contenido_info = {
            'contenido_id': contenido.id,
            'contenido_lote': contenido.molienda.cargamento.lote,
            'tanque_id': contenido.tanque.id,
            'tanque': contenido.tanque.numero,
            'contenido': contenido.molienda.cargamento.varietal.nombre,
            'cantidad': contenido.cantidad
        }
        print('este es el contenido disponible:', contenido)
        # Retornar la información como JSON
        return JsonResponse(contenido_info)
        

    except Contenido.DoesNotExist:
        # Manejar el caso de que no se encuentre el contenido
        return HttpResponse("Contenido no encontrado.", status=404)
  
    

#################  Embotellamiento ##########################

class EmbotellamientoView(LoginRequiredMixin, FormView):
    login_url = '/accounts/login/'
    template_name = 'administracion/embotellamiento.html'
    form_class = EmbotellamientoForm
    success_url = reverse_lazy('sin_etiquetar')  # Asegúrate de que esta URL está definida en tus urls.py

    def get_context_data(self, **kwargs):
        context = super(EmbotellamientoView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['insumos_formset'] = ConsumoInsumoFormset(self.request.POST)
        else:
            context['insumos_formset'] = ConsumoInsumoFormset(queryset=ConsumoInsumo.objects.none())


        fecha_hora_actual = datetime.now()
        context["fecha_hoy"] = fecha_hora_actual.strftime("%Y-%m-%d %H:%M:%S")
        
        contenidos_filtrados = []
        tanques = Tanque.objects.all()
        for tanque in tanques:
            # Obtener el último contenido asociado a cada tanque
            ultimo_contenido = Contenido.objects.filter(tanque=tanque).order_by('-fecha_ingreso').first()
            
            # Si el contenido existe y su cantidad es mayor a 0, añadirlo a la lista
            if ultimo_contenido and ultimo_contenido.cantidad > 0 and ultimo_contenido.embotellado == False:
                contenidos_filtrados.append(ultimo_contenido)
        context["contenidos"] = context["contenidos"] = contenidos_filtrados
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        insumos_formset = ConsumoInsumoFormset(request.POST)
        
        if form.is_valid() and insumos_formset.is_valid():
            return self.both_valid(form, insumos_formset)
        else:
            # Ajuste aquí: pasar insumos_formset al contexto cuando sea inválido.
            return self.render_to_response(self.get_context_data(form=form, insumos_formset=insumos_formset))

    def both_valid(self, form, insumos_formset):
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
            print("este es el contenido pasando por el else:" ,contenido)
            contenido.save()
            print("el contenido se modifico:")
            print(contenido)
            print(contenido.embotellado)
        
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
        deposito=Deposito.objects.get(nombre="BODEGA")  
    )
        #print("este es el stock bodega:",stock_bodega)
        stock_bodega.save()

        # Guarda cada instancia del formset
        insumos_instances = insumos_formset.save(commit=False)
        for instance in insumos_instances:
            instance.save()  # Guarda el consumo de insumo
            insumo = instance.insumo
            insumo.cantidad -= instance.cantidad_consumida
            insumo.save()

        # Aquí continua tu lógica para manejar el objeto Embotellamiento y actualizar Contenido

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, insumos_formset = None):
        
        # Considera añadir manejo para el formset inválido si es necesario
        print("El formulario es inválido")
        print(form.errors)
        if insumos_formset:
            print('Errores del formset:', insumos_formset.errors)
        return super().form_invalid(form)
    
    
class StockSinEtiquetarView(LoginRequiredMixin, ListView):
    login_url = '/accounts/login/'
    """Vista que muestra la lista general del stock sin etiquetar."""
    template_name = 'administracion/stock_sin_etiquetar.html'
    model = StockBodegaSinEtiquetar

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        varietales = Varietal.objects.all()
        cantidades = {}
        total_botellas = 0

        for varietal in varietales:
            cantidad = StockBodegaSinEtiquetar.objects.filter(varietal=varietal, etiquetado=False).aggregate(Sum('cantidad_botellas'))['cantidad_botellas__sum'] or 0
            cantidades[varietal.id] = (varietal.nombre, cantidad)  # Guarda una tupla con el nombre y la cantidad
            total_botellas += cantidad

        context["total_botellas"] = total_botellas    
        context["cantidades"] = cantidades
        return context
 
class StockDetailView(LoginRequiredMixin, TemplateView):
    login_url = '/accounts/login/'
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
    
class RegistrarEtiquetadoView(LoginRequiredMixin, FormView):
    login_url = '/accounts/login/'
    """ vista con el formulario para registrar un etiquetado """
    template_name = 'administracion/stock_etiquetado_form.html'
    success_url = reverse_lazy('stock_etiquetado')
    form_class = EtiquetadoForm  

    def get(self, request, *args, **kwargs):
        #print("Cargando la vista RegistrarEtiquetadoView")
        return super().get(request, *args, **kwargs)

    
        

    def get_context_data(self, **kwargs):
        context = super(RegistrarEtiquetadoView, self).get_context_data(**kwargs)
        #print("Preparando el contexto para RegistrarEtiquetadoView")
        if self.request.POST:
            context['insumos_formset'] = ConsumoInsumoFormset(self.request.POST)
        else:
            context['insumos_formset'] = ConsumoInsumoFormset(queryset=ConsumoInsumo.objects.none())
        
        fecha_hora_formateada = datetime.today().strftime("%Y-%m-%d %H:%M")
        context["stock_embotellados"] = StockBodegaSinEtiquetar.objects.filter(etiquetado=False)
        context["fecha_hoy"] = fecha_hora_formateada
        return context
    
    
    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        insumos_formset = ConsumoInsumoFormset(request.POST)
        
        #print("POST data:", request.POST)  # Verificar los datos enviados por el usuario
        print("Formset is valid:", insumos_formset.is_valid())  # Verificar si el formset es válido
        
        if form.is_valid() and insumos_formset.is_valid():
            print("Ambos form y formset son válidos")
            return self.both_valid(form, insumos_formset)
        else:
            print("Form o formset inválido")
            if not insumos_formset.is_valid():
                print("Errores en el formset:", insumos_formset.errors)
                print('errores en el form: ', form.errors)
            # Ajuste aquí: pasar insumos_formset al contexto cuando sea inválido.
            return self.render_to_response(self.get_context_data(form=form, insumos_formset=insumos_formset))


    def both_valid(self, form, insumos_formset):
        print("En both_valid - procesando form y formset")
        cantidad_botellas = form.cleaned_data.get('cantidad_botellas')
        stock_id = form.cleaned_data.get('stock').id  # Obtiene el ID directamente del formulario
        with transaction.atomic():
            try:
                # Recupera directamente el stock sin etiquetar seleccionado usando el ID obtenido del formulario
                stock = StockBodegaSinEtiquetar.objects.get(pk=stock_id)

                if stock.cantidad_botellas >= cantidad_botellas:
                    # Restar la cantidad etiquetada a la cantidad embotellada
                    stock.cantidad_botellas -= cantidad_botellas
                    
                    # Marca el stock sin etiquetar como etiquetado si no quedan botellas
                    if stock.cantidad_botellas == 0:
                        stock.etiquetado = True
                        stock.cantidad_botellas = 0
                    
                    stock.save()  # Guarda los cambios en el stock

                    # Crea la nueva instancia de BotellaEtiquetada con los datos actualizados
                    botella_etiquetada = StockBodegaEtiquetado.objects.create(
                        stock=stock,
                        fecha_etiquetado=timezone.now(),
                        cantidad_botellas=cantidad_botellas,
                        varietal=stock.varietal,  
                        lote=stock.lote,         
                        empaquetado=False,       
                        observaciones="",        
                        deposito=Deposito.objects.get(nombre="BODEGA")  
                    )
                    botella_etiquetada.save()

                else:
                    # Si la cantidad de botellas a etiquetar excede la cantidad disponible, agrega un error al formulario
                    form.add_error('cantidad_botellas', 'No se puede etiquetar más de lo disponible')
                    return self.form_invalid(form)
                
            except StockBodegaSinEtiquetar.DoesNotExist:
                raise Http404("El stock sin etiquetar no existe")
            
            
            insumos_instances = insumos_formset.save(commit=False)
            print("Instancias de InsumoFormset a ser guardadas:", insumos_instances)

            # Bandera para rastrear si hay errores relacionados con la cantidad de insumos
            hay_error_en_cantidad = False

            for instance in insumos_instances:
                print(f"Procesando instancia de insumo: {instance.insumo.nombre}, cantidad consumida: {instance.cantidad_consumida}")
                
                # Aquí se corrige la comparación para usar la cantidad disponible del insumo
                if instance.insumo.cantidad >= instance.cantidad_consumida:
                    insumo = instance.insumo
                    insumo.cantidad -= instance.cantidad_consumida
                    print(f"Nueva cantidad de {insumo.nombre}: {insumo.cantidad}")
                    insumo.save()
                else:
                    # Si no hay suficiente insumo, se marca que hay un error
                    hay_error_en_cantidad = True
                    # Aquí terminamos el loop porque ya encontramos un error
                    break

            # Si hubo un error en las cantidades de insumo, se maneja aquí
            if hay_error_en_cantidad:
                # Aquí no podemos usar form.add_error para el formset directamente.
                # Necesitas manejar este error de forma que se muestre adecuadamente al usuario.
                # Por ejemplo, puedes usar el sistema de mensajes de Django para mostrar un error general,
                # o agregar un error no específico de campo con form.add_error(None, 'Mensaje de error')
                form.add_error(None, 'No hay suficiente cantidad de insumos disponibles para realizar esta operación. Consulte el stock.')
                return self.form_invalid(form)

            # Si llegamos aquí, significa que no hubo problemas con las cantidades de insumo y podemos proceder.
            # Guardamos las instancias del formset después de hacer todas las verificaciones.
            for instance in insumos_instances:
                instance.save()

            return super().form_valid(form)

            # Aquí continua tu lógica para manejar el objeto Embotellamiento y actualizar Contenido

            return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, insumos_formset = None):
        
        # Considera añadir manejo para el formset inválido si es necesario
        print("El formulario es inválido")
        print(form.errors)
        if insumos_formset:
            print('Errores del formset:', insumos_formset.errors)
        return super().form_invalid(form)
  
class StockEtiquetadoLista(LoginRequiredMixin, ListView):
    login_url = '/accounts/login/'
    """ vista que muestra el stock etiquetado en general """  
    template_name = 'administracion/stock_etiquetado_lista.html'
    model = StockBodegaEtiquetado
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Define los varietales
        varietales = Varietal.objects.all()
        deposito = Deposito.objects.get(nombre="BODEGA") #poner el id del deposito Bodega
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
        print(total_botellas)
        print (cantidades)
        return context

class StockBodegaEtiquetadoDetalle(LoginRequiredMixin, TemplateView):
    login_url = '/accounts/login/'
    """ muestra el detalle del stock etiquetado de cada uno de los varietales """
    template_name = 'administracion/detalle_stock_etiquetado.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Reemplaza los guiones bajos por espacios en blanco para obtener el nombre original del varietal
        varietal = self.kwargs['varietal'].replace('_', ' ')
        deposito = Deposito.objects.get(nombre='BODEGA')
        # Filtra los objetos StockBodegaEtiquetado por varietal y etiquetado
        stocks = StockBodegaEtiquetado.objects.filter(varietal=varietal, deposito=deposito)
        
        # Calcula la cantidad total de botellas
        total_botellas = stocks.aggregate(Sum('cantidad_botellas'))['cantidad_botellas__sum'] or 0

        # Añade los stocks y el total de botellas al contexto
        context['stocks'] = stocks
        context['total_botellas'] = total_botellas

        return context


##################### Empaquetado ####################



class RegistrarEmpaquetadoView(LoginRequiredMixin, FormView):
    login_url = '/accounts/login/'
    template_name = 'administracion/stock_empaquetado_form.html'
    success_url = reverse_lazy('stock_empaquetado')
    form_class = EmpaquetadoForm

    def get_context_data(self, **kwargs):
        context = super(RegistrarEmpaquetadoView, self).get_context_data(**kwargs)
        #print("Preparando el contexto para RegistrarEtiquetadoView")
        if self.request.POST:
            context['insumos_formset'] = ConsumoInsumoFormset(self.request.POST)
        else:
            context['insumos_formset'] = ConsumoInsumoFormset(queryset=ConsumoInsumo.objects.none())
        
        fecha_hora_formateada = timezone.now().strftime("%Y-%m-%d %H:%M")
        context["stock_etiquetados"] = StockBodegaEtiquetado.objects.filter(empaquetado=False)
        context["fecha_hoy"] = fecha_hora_formateada
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        insumos_formset = ConsumoInsumoFormset(request.POST)
        
        #print("POST data:", request.POST)  # Verificar los datos enviados por el usuario
        print("Formset is valid:", insumos_formset.is_valid())  # Verificar si el formset es válido
        
        if form.is_valid() and insumos_formset.is_valid():
            print("Ambos form y formset son válidos")
            return self.both_valid(form, insumos_formset)
        else:
            print("Form o formset inválido")
            if not insumos_formset.is_valid():
                print("Errores en el formset:", insumos_formset.errors)
            # Ajuste aquí: pasar insumos_formset al contexto cuando sea inválido.
            return self.render_to_response(self.get_context_data(form=form, insumos_formset=insumos_formset))
        
        
        
        
    def both_valid(self, form, insumos_formset):
        print("En both_valid - procesando form y formset")
        cantidad_cajas = form.cleaned_data.get('cantidad_cajas')
        stock_id = form.cleaned_data['stock'].id
        stock = StockBodegaEtiquetado.objects.get(pk=stock_id)
        cantidad_disponible = stock.cantidad_botellas
        
        with transaction.atomic():
            try:
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
                    
                    deposito_defecto = Deposito.objects.get(nombre="BODEGA")
                    
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
                    print('form procesado con exito')
                    
                
                else:
                    raise ValidationError("No puede empaquetar más de lo disponible")
                    return self.form_invalid(form)
                
            except StockBodegaSinEtiquetar.DoesNotExist:
                raise Http404("El stock sin etiquetar no existe")
            
            
            insumos_instances = insumos_formset.save(commit=False)
            print("Instancias de InsumoFormset a ser guardadas:", insumos_instances)

            # Bandera para rastrear si hay errores relacionados con la cantidad de insumos
            hay_error_en_cantidad = False

            for instance in insumos_instances:
                print(f"Procesando instancia de insumo: {instance.insumo.nombre}, cantidad consumida: {instance.cantidad_consumida}")
                
                # Aquí se corrige la comparación para usar la cantidad disponible del insumo
                if instance.insumo.cantidad >= instance.cantidad_consumida:
                    insumo = instance.insumo
                    insumo.cantidad -= instance.cantidad_consumida
                    print(f"Nueva cantidad de {insumo.nombre}: {insumo.cantidad}")
                    insumo.save()
                else:
                    # Si no hay suficiente insumo, se marca que hay un error
                    hay_error_en_cantidad = True
                    # Aquí terminamos el loop porque ya encontramos un error
                    break

            # Si hubo un error en las cantidades de insumo, se maneja aquí
            if hay_error_en_cantidad:
                # Aquí no podemos usar form.add_error para el formset directamente.
                # Necesitas manejar este error de forma que se muestre adecuadamente al usuario.
                # Por ejemplo, puedes usar el sistema de mensajes de Django para mostrar un error general,
                # o agregar un error no específico de campo con form.add_error(None, 'Mensaje de error')
                form.add_error(None, 'No hay suficiente cantidad de insumos disponibles para realizar esta operación. Consulte el stock.')
                return self.form_invalid(form)

            # Si llegamos aquí, significa que no hubo problemas con las cantidades de insumo y podemos proceder.
            # Guardamos las instancias del formset después de hacer todas las verificaciones.
            for instance in insumos_instances:
                instance.save()

            return super().form_valid(form)

            # Aquí continua tu lógica para manejar el objeto Embotellamiento y actualizar Contenido

            return HttpResponseRedirect(self.get_success_url())
        
    
        
    def form_invalid(self, form):
        print ("el formulario es invalido")
        print (form.errors)
        return super().form_invalid(form)

class StockEmpaquetadoLista(LoginRequiredMixin, ListView):
    login_url = '/accounts/login/'
    template_name = 'administracion/stock_empaquetado_lista.html'
    model = StockBodegaEmpaquetado
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Define los varietales
        varietales = Varietal.objects.all()

        # Crea un diccionario para almacenar las cantidades de cada varietal
        cantidades = {}
        
        # Crea un diccionario para almacenar los lotes de cada varietal
        lotes = {}

        # Inicializar la suma total de cajas
        total_cajas = 0

        #deposito
        deposito = Deposito.objects.get(nombre="BODEGA")
        
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




class StockEmpaquetadoDetalle(LoginRequiredMixin, TemplateView):
    login_url = '/accounts/login/'
    template_name = 'administracion/detalle_stock_empaquetado.html'
    model = StockBodegaEmpaquetado

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Reemplaza los guiones bajos por espacios en blanco para obtener el nombre original del varietal
        varietal = self.kwargs['varietal'].replace('_', ' ')
        
        deposito = Deposito.objects.get(nombre='BODEGA')
        # Filtra los objetos StockBodegaEmpaquetado por varietal
        stocks = StockBodegaEmpaquetado.objects.filter(varietal=varietal, deposito=deposito)

        # Calcula la cantidad total de cajas
        total_cajas = stocks.aggregate(Sum('cantidad_cajas'))['cantidad_cajas__sum'] or 0

        # Añade los stocks y el total de cajas al contexto
        context['stocks'] = stocks
        context['total_cajas'] = total_cajas

        return context
    
    
    
# ------------------------------- Depositos--- Bodega!!!!!!! ------------------------------    

@login_required    
def stock(request):
    return render (request, 'administracion/stock.html')
@login_required
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
@login_required
def crear_deposito(request):
    if request.method == 'POST':
        form = DepositoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_depositos')  # Redirige a donde necesites después de crear el depósito
    else:
        form = DepositoForm()

    return render(request, 'depositos/nuevo_deposito.html', {'form': form})
@login_required
def lista_depositos(request):
    depositos = Deposito.objects.all()
    return render (request, 'depositos/lista_depositos.html', {'depositos':depositos})
@login_required
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
@login_required
def eliminar_deposito(request, pk):
    deposito = get_object_or_404(Deposito, pk=pk)
    if request.method == 'POST':
        deposito.delete()
        return redirect('lista_depositos')

    return render(request, 'depositos/confirmar_eliminar.html', {'deposito': deposito})
@login_required
def detalles_deposito(request,pk):
    deposito = get_object_or_404(Deposito, pk=pk)

    return render (request, 'depositos/detalles_deposito.html', {'deposito':deposito})
@login_required
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
@login_required
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

@login_required
def seleccionar_stock(request, pk):
    # Recuperar el depósito utilizando el pk
    deposito = get_object_or_404(Deposito, pk=pk)

    # Pasar el depósito a la plantilla
    return render(request, 'depositos/redireccionar.html', {'deposito': deposito})

class DetallesDepositoView(LoginRequiredMixin, DetailView):
    login_url = 'accounts/login/'
    model = Deposito
    template_name = 'depositos/detalles_deposito.html'
    context_object_name = 'deposito'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        deposito = self.object  # El objeto Deposito ya recuperado por DetailView
        
        
        context['etiquetados'] = MoverStockEtiquetado.objects.filter(deposito=deposito)
        context['empaquetados'] = MoverStockEmpaquetado.objects.filter(deposito=deposito)
        
        return context
        
class MoverStockEtiquetadoView(LoginRequiredMixin, View):
    login_url = 'accounts/login/'
    template_name= 'depositos/mover_stock_etiquetado.html'
    
    def get(self, request, *args, **kwargs):
        Formset = modelformset_factory(MoverStockEtiquetado, form=MoverStockEtiquetadoForm, extra=10)
        formset = Formset(queryset=MoverStockEtiquetado.objects.none())

        deposito = Deposito.objects.get(nombre="BODEGA")
        BODEGA_ID = deposito.id
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

class MoverStockEmpaquetadoView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    template_name= 'depositos/mover_stock_empaquetado.html'
    
    def get(self, request, *args, **kwargs):
        Formset = modelformset_factory(MoverStockEmpaquetado, form=MoverStockEmpaquetadoForm, extra=10)
        formset = Formset(queryset=MoverStockEmpaquetado.objects.none())
       
        bodega = Deposito.objects.get(nombre="BODEGA")
        
        deposito = get_object_or_404(Deposito, pk=self.kwargs['pk'])  
        stock_empaquetado = StockBodegaEmpaquetado.objects.filter(deposito_id=bodega.id)

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
            

class HistorialMovimientosView(LoginRequiredMixin, ListView):
    login_url = '/accounts/login/'
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
        


class CrearTareaView(LoginRequiredMixin, FormView):
    login_url ='/accounts/login'
    template_name = 'administracion/crear_tarea.html'
    model = Tarea
    form_class = TareaForm
    success_url = reverse_lazy('listado_tareas_pendientes')
    
    def form_valid(self, form):
        tarea = form.save(commit=False)
        # Establece el campo `creado_por` con el usuario actual
        # Nota: Cambiado a usar el usuario completo en lugar de email, basado en la definición del modelo
        tarea.creado_por = self.request.user
        tarea.save()
        # Asegúrate de llamar a `save_m2m` si tu formulario tiene campos many-to-many que necesiten guardarse.
        form.save()
        print('el formulario se guardo de forma exitosa')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        if form.errors:
            for e in form.errors:
                print(' estos son los errores en el codigo: ', e)
        return super().form_invalid(form)
    
class TareasPendientesView(LoginRequiredMixin, ListView):
    login_url = 'accounts/login'
    model = Tarea
    template_name = 'administracion/tareas_pendientes.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tareas_pendientes"] = Tarea.objects.filter(realizada=False)
        tareas_sin_realizar = Tarea.objects.filter(realizada=False)
        print(tareas_sin_realizar)
        return context
    
class ActualizarEstadoTarea(LoginRequiredMixin, UpdateView):
    login_url = '/accounts/login/'      
    model = Tarea
    form_class = TareaForm
    template_name = 'administracion/actualizar_tarea.html'
    success_url = reverse_lazy('listado_tareas_pendientes')  # Asegúrate de definir esto

    def form_valid(self, form):
        # Recuperar el ID de la tarea desde self.kwargs y obtener la instancia de Tarea
        tarea_id = self.kwargs.get('pk')
        instancia_tarea = get_object_or_404(Tarea, id=tarea_id)
        
        tarea = form.save(commit=False)
        
        if form.instance.realizada:
            tarea.completado_por = self.request.user
            print('tarea realizada por: ', self.request.user)
            tarea.fecha_realizada = timezone.now()

        # Usar el valor de 'creado_por' de la instancia recuperada manualmente
        tarea.creado_por = instancia_tarea.creado_por
        tarea.save()

        return super().form_valid(form)
    
class ListadoTareasRealizadas(LoginRequiredMixin, ListView):
    login_url = 'accounts/login'
    template_name= 'administracion/tareas_realizadas.html'
    model = Tarea
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tareas_realizadas"] = Tarea.objects.filter(realizada=True)
        return context
    
    
class DetallesTareaView(LoginRequiredMixin, TemplateView):
    login_url ='accounts/login'
    template_name = 'administracion/tareas_detalles.html'
    model = Tarea
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tarea_pk = self.kwargs.get('pk')
        print('este es el pk: ', tarea_pk)
        context["tarea"] = Tarea.objects.get(pk=tarea_pk)
        return context
    

class CrearInsumoView(FormView):
    template_name = 'administracion/crear_insumo.html'  # Asegúrate de crear este template
    form_class = InsumoForm
    success_url = reverse_lazy('listado_insumos')  # Asume que tienes esta URL definida para el listado de insumos

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    
class ListadoInsumosView(ListView):
    model = Insumo
    template_name = 'administracion/listado_insumos.html'  # Asegúrate de crear este template
    context_object_name = 'insumos'
    
class ActualizarInsumoView(UpdateView):
    model = Insumo
    form_class = InsumoForm
    template_name = 'administracion/actualizar_insumo.html'  # Crea este template
    success_url = reverse_lazy('listado_insumos')  # Redirige aquí después de actualizar un insumo

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['accion'] = 'Actualizar'  # Opcional: Agregar contexto adicional si es necesario
        return context
    


    