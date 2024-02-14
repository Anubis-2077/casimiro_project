from django import forms
from administracion.models import *
from allauth.account.forms import LoginForm
from django.forms import formset_factory
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
        
class Moliendaform (forms.ModelForm):
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
        
class HistorialContenidoForm(forms.ModelForm):
    class Meta:
        model = HistorialContenido
        fields = '__all__'
        
class NotaTareasForm(forms.ModelForm):
    class Meta:
        model = NotaTarea
        fields = '__all__'
        
        
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
                
