from django.db import models
from administracion.models import *
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Create your models here.
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=50, null=True)
    cuit_cuil = models.CharField(max_length=50)
    direccion = models.TextField()
    email = models.EmailField()
    telefono = models.CharField(max_length=50)
    tipo = models.CharField(max_length=50, choices=[('mayorista', 'Mayorista'), ('minorista', 'Minorista'), ('consumidor final', 'Consumidor Final')])
    observaciones= models.TextField(null=True, blank=True)
    cuenta_corriente = models.OneToOneField(
        'CuentaCorrienteDeudores',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cliente_relacionado' 
    )
    

class ProveedorInsumos(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=50, null=True)
    cuit_cuil = models.CharField(max_length=50)
    direccion = models.TextField()
    email = models.EmailField()
    telefono = models.CharField(max_length=50)
    observaciones= models.TextField(null=True, blank=True)
    cuenta_corriente = models.OneToOneField(
        'CuentaCorrienteAcreedores',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='proveedor_insumos_relacionado'
    )
    
    
    def __str__(self):
        return f"el id es: {self.id}, proveedor: {self.nombre}, apellido: {self.apellido}"

class CuentaCorrienteDeudores(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='cuenta_corriente_clientes'  
    )
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ventas = models.ManyToManyField('VentaCuentaCorriente', related_name='cuenta_corriente_deudores')

class VentaCuentaCorriente(models.Model):
    fecha = models.DateField(auto_now_add=True)
    descripcion = models.TextField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    confirmada = models.BooleanField(default=False)

    class Meta:
        ordering = ['-fecha']

class CuentaCorrienteAcreedores(models.Model):
    proveedor_insumos = models.ForeignKey(ProveedorInsumos, on_delete=models.CASCADE,  related_name='cuenta_corriente_proveedores_insumos' )
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    compras = models.ManyToManyField('CompraCuentaCorriente', related_name='cuenta_corriente_acreedores')

class CompraCuentaCorriente(models.Model):
    fecha = models.DateField(auto_now_add=True)
    descripcion = models.TextField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    confirmada = models.BooleanField(default=False)

    class Meta:
        ordering = ['-fecha']

class Deudor(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_inicio_deuda = models.DateField(auto_now_add=True)
    fecha_fin_deuda = models.DateField(null=True, blank=True)
    descripcion = models.CharField(max_length=200)

class Acreedor(models.Model):
    proveedor_insumos = models.ForeignKey(ProveedorInsumos, on_delete=models.CASCADE)
    fecha_inicio_acreedor = models.DateField(auto_now_add=True)
    fecha_fin_acreedor = models.DateField(null=True, blank=True)
    descripcion = models.CharField(max_length=200)
    
#---------------------------producto-----------------------------

    
class Venta(models.Model):
    comprador = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    precio_total = models.DecimalField(max_digits=10, decimal_places=2)
    condicion = models.CharField(max_length=50, choices=[
    ('Contado', 'Contado'), 
    ('Cuenta corriente', 'Cuenta corriente'), 
    ('Tarjeta de credito', 'Tarjeta de credito'), 
    ('Debito automatico', 'Debito automatico'), 
    ('Donacion', 'Donacion'), 
    ('Ventas en linea', 'Ventas en linea'), 
    ('Transferencia', 'Transferencia')
])
    fecha_venta = models.DateTimeField(auto_now_add=True)
    deposito = models.ForeignKey(Deposito, on_delete = models.CASCADE, null=True, blank=True)

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, related_name='detalles', on_delete=models.CASCADE)
    prod_empaquetado = models.ForeignKey(StockBodegaEmpaquetado, on_delete=models.CASCADE, null=True, blank=True)
    prod_etiquetado = models.ForeignKey(StockBodegaEtiquetado, on_delete=models.CASCADE, null=True, blank=True)
    precio_unitario = models.IntegerField()
    cantidad = models.IntegerField()
    
    def clean(self):
        if self.prod_empaquetado and self.prod_etiquetado:
            raise ValidationError("Una venta no puede tener simultáneamente un producto empaquetado y etiquetado.")
        if not self.prod_empaquetado and not self.prod_etiquetado:
            raise ValidationError("Debe especificar un producto empaquetado o etiquetado.")
        
        
class DetalleVentaSucursal(models.Model):
    venta = models.ForeignKey(Venta, related_name='detalles_sucursal', on_delete=models.CASCADE)
    prod_empaquetado = models.ForeignKey(MoverStockEmpaquetado, on_delete=models.CASCADE, null=True, blank=True, related_name='detalles_venta_empaquetado')
    prod_etiquetado = models.ForeignKey(MoverStockEtiquetado, on_delete=models.CASCADE, null=True, blank=True, related_name='detalles_venta_etiquetado')
    precio_unitario = models.IntegerField()
    cantidad = models.IntegerField()
    
    def clean(self):
        # Lógica de validación
        if self.prod_empaquetado and self.prod_etiquetado:
            raise ValidationError("Una venta no puede tener simultáneamente un producto empaquetado y etiquetado.")
        if not self.prod_empaquetado and not self.prod_etiquetado:
            raise ValidationError("Debe especificar un producto empaquetado o etiquetado.")
    

#Carrito 
class Carrito(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    producto = GenericForeignKey('content_type', 'object_id')
    cantidad = models.IntegerField(default=1)
    
class Envio(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    numero_de_envio = models.CharField(max_length=100, unique=True, blank=True, null=True)  
    fecha_envio = models.DateField(null=True, blank=True)
    medio = models.CharField(max_length=100, null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    enviado = models.BooleanField(default=False)

    def __str__(self):
        return f"Envío {self.numero_de_envio} para {self.cliente}"