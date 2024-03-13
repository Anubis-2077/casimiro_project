from django.db import models
from django.utils import timezone
from datetime import datetime
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.contrib.auth.models import User

class Proveedor(models.Model):
    razon_social = models.CharField(max_length=200)
    cuit_cuil = models.CharField(max_length=11)
    telefono = models.CharField(max_length=18)
    
    def __str__(self) -> str:
        return self.razon_social
    
class Varietal(models.Model):
    nombre = models.CharField(max_length=50)
    imagen = models.ImageField()
    uva = models.CharField(max_length=50)
    
    def __str__(self):
        return self.nombre, self.id


class Cargamento(models.Model):
    fecha = models.DateField(auto_now_add=True, null=True)
    lote = models.CharField(max_length=10, unique=True)
    peso_bruto = models.IntegerField()
    peso_neto = models.IntegerField()
    tara = models.IntegerField()
    camion = models.CharField(max_length=100)
    dominio = models.CharField(max_length=100, default= 'AAA000')  # Corregido aquí
    camionero = models.CharField(max_length=200, blank=True)
    camionero_razon_social = models.CharField(max_length=100, blank=True)
    camionero_cuit = models.CharField(default=0)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE,)
    varietal = models.ForeignKey(Varietal, on_delete=models.CASCADE, null= True)
    origen = models.CharField(max_length=200)
    parral = models.CharField(max_length=200)
    cuartel = models.CharField(max_length=200)
    declarado = models.BooleanField(default=False, blank=True)
    azucar = models.DecimalField(max_digits=5, decimal_places=2)
    
    def __str__(self):
        return f"Cargamento lote N° {self.lote}, varietal: {self.varietal}, fecha {self.fecha}"

class Molienda(models.Model):
    cargamento = models.OneToOneField(Cargamento, on_delete=models.CASCADE, null=False)
    fecha_molienda = models.DateField(null=True)
    agregados = models.TextField(blank=True)
    observaciones = models.TextField(blank=True)
    responsables = models.CharField(max_length=200)
    cantidad_operarios = models.IntegerField()
    rendimiento = models.IntegerField()
    
    
    def embotellado(self):
        return self.contenido_set.filter(embotellado=True).exists()
    
    def __str__(self):
        return f"Molienda lote N° {self.cargamento.lote}, id:{self.id} varietal: {self.cargamento.varietal}, fecha: {self.fecha_molienda}, rendimiento: {self.rendimiento}"

class Tanque(models.Model):
    numero = models.IntegerField(unique=True)
    volumen = models.IntegerField()
    material = models.CharField(max_length=200)
    qr = models.ImageField(upload_to='qr_tanques/', null=True)
    
    
    def __str__(self):
        return F"Tanque N° {self.numero} de {self.volumen} litros"

class Contenido(models.Model):
    tanque = models.ForeignKey(Tanque, on_delete=models.CASCADE)
    molienda = models.ForeignKey(Molienda, on_delete=models.CASCADE, blank=True, null=True)
    fecha_ingreso = models.DateTimeField(default=datetime.today, null=True)
    fecha_salida = models.DateTimeField(null=True, blank=True,)
    cantidad = models.IntegerField(null=True)
    mover_contenido = models.BooleanField(default=False)
    contenido_trasladado = models.CharField(blank=True, null=True)
    embotellado = models.BooleanField(default=False)
  
  
    
    def save(self, *args, **kwargs):
        if not self.molienda:
            super().save(*args, **kwargs)
        else:
            if self.pk and self.tanque.id != Contenido.objects.get(pk=self.pk).tanque_id:
                self.fecha_salida = timezone.now()
                
            if self.cantidad > self.molienda.rendimiento:
                raise ValidationError ("La cantidad asignada no puede ser mayor al rendimiento de la molienda")
            
            if self.cantidad > self.tanque.volumen:
                raise ValidationError("La cantidad no puede exceder la capacidad del tanque.")
        
            super().save(*args, **kwargs)
        
    def __str__(self):
        return f"lote N° { self.molienda.cargamento.lote } varietal: { self.molienda.cargamento.varietal } cantidad: { self.cantidad }"
    
    
    
class HistorialContenido(models.Model):
    contenido = models.ForeignKey(Contenido, on_delete=models.CASCADE)
    fecha = models.DateField(auto_now_add=True)
    notas_cata = models.TextField(blank=True, null=True)
    correcciones = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    analisis = models.FileField(upload_to='analisis/', blank=True, null=True)
    insumos = models.TextField(blank=True, null=True)

class NotaTarea(models.Model):
    tanque = models.ForeignKey(Tanque, on_delete=models.CASCADE, null= True, blank=True)
    titulo = models.CharField(max_length=100, null=True, blank=True)
    nota = models.TextField(null= True, blank=True)
    notas_operario = models.TextField(null= True, blank=True)
    fecha = models.DateTimeField(null= True, blank=True)
    realizada = models.BooleanField(default=False)
    fecha_realizada = models.DateTimeField( null=True, blank=True)
    
    def __str__(self) :
        return f" { self.titulo} de fecha {self.fecha}"



class Embotellamiento(models.Model):
    contenido = models.ForeignKey(Contenido, on_delete=models.CASCADE)
    fecha_envasado = models.DateTimeField()
    cantidad_botellas = models.PositiveIntegerField(null=True)
    tipo_botella = models.CharField(max_length=255)
    cantidad_corchos = models.PositiveIntegerField()
    tipo_de_corchos= models.CharField(max_length=255)
    insumos = models.TextField(null=True, blank=True)  # Puedes usar TextField para una lista de insumos
    operarios = models.TextField(default=" ")  # Puedes usar TextField para una lista de operarios
    observaciones = models.TextField(default=" ")

    def __str__(self):
        return f"Embotellamiento de {self.contenido.molienda.cargamento.varietal}, lote {self.contenido.molienda.cargamento.lote} ({self.fecha_envasado})"
    
def get_default_deposito():
    return Deposito.objects.get_or_create(id=3)[0].id

class StockBodegaSinEtiquetar(models.Model):
    embotellamiento = models.ForeignKey(Embotellamiento, on_delete=models.CASCADE)
    cantidad_botellas = models.PositiveIntegerField(null=True)
    varietal = models.ForeignKey(Varietal, on_delete=models.CASCADE)
    lote = models.CharField(max_length=255)
    etiquetado = models.BooleanField(default=False)
    deposito = models.ForeignKey('Deposito', on_delete=models.SET_NULL, null=True, blank=True, default=get_default_deposito)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo asigna el valor si la instancia es nueva (no se ha guardado en la base de datos)
        if self.pk is None:
            self.cantidad_botellas = self.embotellamiento.cantidad_botellas

    def save(self, *args, **kwargs):
        self.varietal = self.embotellamiento.contenido.molienda.cargamento.varietal
        self.lote = self.embotellamiento.contenido.molienda.cargamento.lote
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Stock sin etiquetar varietal {self.varietal} cantidad: {self.cantidad_botellas} lote: {self.lote}"



class StockBodegaEtiquetado(models.Model):
    stock = models.ForeignKey(StockBodegaSinEtiquetar, on_delete=models.CASCADE, null=True)
    fecha_etiquetado = models.DateTimeField(default=datetime.today())
    cantidad_botellas = models.PositiveIntegerField(null=True)
    varietal = models.ForeignKey(Varietal, on_delete=models.CASCADE)
    lote = models.CharField(max_length=255)
    empaquetado = models.BooleanField(default=False)
    observaciones = models.TextField(default=" ", null=True)
    deposito = models.ForeignKey('Deposito', on_delete=models.SET_NULL, null=True, blank=True, default=get_default_deposito)
    precio=models.IntegerField(null=True)


    def save(self, *args, **kwargs):
        self.varietal = self.stock.varietal
        self.lote = self.stock.lote
        super().save(*args, **kwargs)

    def __str__(self):
        return f"id: {self.id} Botella etiquetada varietal {self.varietal.nombre} cantidad: {self.cantidad_botellas} lote: {self.lote}, empaquetado: {self.empaquetado}"



class StockBodegaEmpaquetado(models.Model):
    stock = models.ForeignKey(StockBodegaEtiquetado, on_delete=models.CASCADE)
    cantidad_cajas = models.IntegerField(null=True)
    empaquetado = models.BooleanField(default=False)
    varietal = models.ForeignKey(Varietal, on_delete=models.CASCADE)
    lote = models.CharField(max_length=255)
    fecha_empaquetado= models.DateTimeField(null=True)
    deposito = models.ForeignKey('Deposito', on_delete=models.SET_NULL, null=True, blank=True)
    precio=models.IntegerField(null=True)

    
    
    def save(self, *args, **kwargs):
        self.varietal = self.stock.varietal
        self.lote = self.stock.lote
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"id: {self.id}, cantidad: {self.cantidad_cajas}, varietal: {self.varietal.nombre}"
    
    

    
    
class Deposito(models.Model):
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=100)
    # Otros campos que necesites

    def __str__(self):
        return self.nombre

    

class MoverStockEtiquetado(models.Model):
    stock = models.ForeignKey(StockBodegaEtiquetado, on_delete=models.CASCADE, related_name='stock_origen')
    deposito= models.ForeignKey(Deposito,on_delete=models.CASCADE, related_name='deposito_destino')
    cantidad = models.IntegerField()
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        
        return f"Id: {self.id} Lote: {self.stock.lote}, Carietal: {self.stock.varietal}, Cantidad: {self.cantidad}, Fecha: {self.fecha_movimiento}"


class MoverStockEmpaquetado(models.Model):
    stock = models.ForeignKey(StockBodegaEmpaquetado, on_delete=models.CASCADE, related_name='stock_origen_empaquetado')
    deposito= models.ForeignKey(Deposito,on_delete=models.CASCADE, related_name='deposito_destino_empaquetado')
    cantidad = models.IntegerField()
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        
        return f"Id: {self.id} Lote: {self.stock.lote}, Varietal: {self.stock.varietal}, Cantidad: {self.cantidad}, Fecha: {self.fecha_movimiento}"
