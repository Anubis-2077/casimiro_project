from django import forms
from contabilidad.models import *
from allauth.account.forms import LoginForm
from django.forms import modelformset_factory
from django.core.exceptions import ValidationError, ObjectDoesNotExist






class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'cuit_cuil', 'direccion', 'telefono', 'email', 'observaciones', 'tipo']

class ProveedorInsumosForm(forms.ModelForm):
    class Meta:
        model = ProveedorInsumos
        fields = ['nombre','apellido', 'cuit_cuil', 'direccion', 'email', 'telefono','observaciones']
        
class VentaForm(forms.ModelForm):
    class Meta:
        model= Venta
        fields = '__all__'
        
class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model=DetalleVenta
        fields=['venta', 'prod_empaquetado', 'prod_etiquetado', 'precio_unitario', 'cantidad' ]

class DetalleVentaSucursalForm(forms.ModelForm):
    class Meta:
        model=DetalleVentaSucursal
        fields=['venta', 'prod_empaquetado', 'prod_etiquetado', 'precio_unitario', 'cantidad' ]
        
    def __init__(self, *args, **kwargs):
        deposito_id = kwargs.pop('deposito_id', None)  # Asegúrate de que esto coincida con lo que pasas en la vista
        super().__init__(*args, **kwargs)
        
        if deposito_id is not None:
            empaquetado_qs = MoverStockEmpaquetado.objects.filter(deposito__id=deposito_id)
            etiquetado_qs = MoverStockEtiquetado.objects.filter(deposito__id=deposito_id)

            

            self.fields['prod_empaquetado'].queryset = empaquetado_qs
            self.fields['prod_etiquetado'].queryset = etiquetado_qs
        
        
class StockBodegaEmpaquetadoPrecioForm(forms.ModelForm):
    class Meta:
        model = StockBodegaEmpaquetado
        fields = ['precio',]

# Formulario para StockBodegaEtiquetado
class StockBodegaEtiquetadoPrecioForm(forms.ModelForm):
    class Meta:
        model = StockBodegaEtiquetado
        fields = ['precio',]

StockBodegaEmpaquetadoPrecioFormSet = modelformset_factory(StockBodegaEmpaquetado, form=StockBodegaEmpaquetadoPrecioForm, extra=0)
StockBodegaEtiquetadoPrecioFormSet = modelformset_factory(StockBodegaEtiquetado, form=StockBodegaEtiquetadoPrecioForm, extra=0)


class EnvioForm(forms.Form):
    
    nombre = forms.CharField(max_length=100)
    apellido = forms.CharField(max_length=50, required=False)
    telefono = forms.CharField(max_length=50)
    email = forms.EmailField()
    cuit_cuil = forms.CharField(max_length=50)
    calle= forms.CharField(max_length=50)
    numero = forms.CharField(max_length=5)
    departamento = forms.CharField(max_length=5)
    localidad = forms.CharField(max_length=50)
    provincia = forms.CharField(max_length=50)
    codigo_postal = forms.CharField(max_length=10)
    
class EnvioForm_Vista(forms.ModelForm):
    class Meta:
        model = Envio
        fields = '__all__'
    
    