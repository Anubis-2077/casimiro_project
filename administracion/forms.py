from django import forms
from administracion.models import *
from allauth.account.forms import LoginForm
from django.forms.models import modelformset_factory
from django.core.exceptions import ValidationError, ObjectDoesNotExist

class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.fields['login'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})
        print("Formulario inicializado.")

    def clean(self):
        cleaned_data = super().clean()
        if not self.errors:
            login = cleaned_data.get("login")
            password = cleaned_data.get("password")
            print(f"Login: {login}, Password: {password}")
        else:
            print(f"Errores en el formulario: {self.errors}")
        return cleaned_data



class Proveedorform (forms.ModelForm):
    class Meta:
        model =Proveedor
        fields= '__all__'
        
class CargamentoForm(forms.ModelForm):
    class Meta:
        model = Cargamento
        fields = '__all__'
        
class MoliendaForm (forms.ModelForm):
    class Meta:
        model= Molienda
        fields = '__all__'
        
class ContenidoForm(forms.ModelForm):
    fecha_ingreso = forms.DateTimeField(
        input_formats=["%d/%m/%Y %H:%M:%S"],
        
    )
    class Meta:
        model = Contenido
        fields = ['tanque', 'molienda', 'fecha_ingreso', 'fecha_salida', 'cantidad']
        
class MoverContenidoForm(forms.Form):
    
    tanque = forms.CharField(max_length=100)
    contenido = forms.CharField(max_length=50, required=False)
    fecha_ingreso = forms.CharField(max_length=50)
    fecha_salida = forms.EmailField()
    cantidad = forms.CharField(max_length=50)
    
        
class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super(TareaForm, self).__init__(*args, **kwargs)
        self.fields['creado_por'].widget.attrs['disabled'] = True
        # Si deseas también agregar la clase form-control puedes hacerlo aquí
        self.fields['creado_por'].widget.attrs['class'] = 'form-control'
        
        
class EmbotellamientoForm(forms.ModelForm):
    
    class Meta:
        model = Embotellamiento
        fields = '__all__'
        
class EtiquetadoForm(forms.ModelForm):
    
    class Meta:
        model = StockBodegaEtiquetado
        fields = ['stock', 'cantidad_botellas', 'observaciones', 'fecha_etiquetado','deposito']
        
class EmpaquetadoForm(forms.ModelForm):
    
    class Meta:
        model = StockBodegaEmpaquetado
        fields =['stock', 'cantidad_cajas','fecha_empaquetado','deposito']
        

class DepositoForm(forms.ModelForm):
    class Meta:
        model = Deposito
        fields = ['nombre', 'ubicacion']
        

        

        
#--------------formularios de asignacion de stock a bodegas--------------

class StockBodegaEtiquetadoForm(forms.ModelForm):

    class Meta:
        model = StockBodegaEtiquetado
        fields = '__all__'
        


class StockBodegaEmpaquetadoForm(forms.ModelForm):
    class Meta:
        model = StockBodegaEmpaquetado
        fields = ['stock', 'cantidad_cajas', 'deposito']
        
class MoverStockEtiquetadoForm(forms.ModelForm):
    stock= forms.ModelChoiceField(queryset=StockBodegaEtiquetado.objects.all())
    
    class Meta:
        model=MoverStockEtiquetado
        fields = ['stock', 'cantidad', 'deposito']
    
    def clean(self):
        cleaned_data = super().clean()
        cantidad = cleaned_data.get("cantidad")
        stock_id = cleaned_data.get("stock")
        
        if stock_id:
            stock = StockBodegaEtiquetado.objects.get(pk=stock_id.id)
            
            if cantidad > stock.cantidad_botellas:
                raise ValidationError("La cantidad a mover no puede ser mayor a la cantidad disponible.")

        return cleaned_data
    
    

class MoverStockEmpaquetadoForm(forms.ModelForm):
    stock=forms.ModelChoiceField(queryset=StockBodegaEmpaquetado.objects.all())
    
    class Meta:
        model=MoverStockEmpaquetado
        fields = ['stock', 'cantidad', 'deposito']
        
    def clean(self):
        cleaned_data = super().clean()
        cantidad = cleaned_data.get('cantidad')
        stock_id = cleaned_data.get('stock')
        
        if cantidad <= 0:
            raise ValidationError('La cantidad debe ser mayor que cero.')

        if stock_id:
            try:
                stock = StockBodegaEmpaquetado.objects.get(pk=stock_id.id)
                
                if cantidad > stock.cantidad_cajas:
                    raise ValidationError('No se puede mover una cantidad mayor a la existente.')
            except ObjectDoesNotExist:
                raise ValidationError('El stock especificado no existe.')

        return cleaned_data
                
ConsumoInsumoFormset = modelformset_factory(
    ConsumoInsumo,
    fields=( 'insumo', 'cantidad_consumida'),
    extra=6,
)

class InsumoForm(forms.ModelForm):
    class Meta:
        model = Insumo
        fields = '__all__'
        

class NotasDeCataForm(forms.ModelForm):
    class Meta:
        model = NotasDeCata
        fields = '__all__'