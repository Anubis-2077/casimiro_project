from rest_framework import serializers
from administracion.models import StockBodegaEmpaquetado, StockBodegaEtiquetado, Varietal



class StockBodegaEtiquetadoSerializer(serializers.ModelSerializer):
    varietal = serializers.PrimaryKeyRelatedField(queryset=Varietal.objects.all())
    
    class Meta:
        model = StockBodegaEtiquetado
        fields = ['varietal', 'cantidad_botellas', 'precio']
        
        
class StockBodegaEmpaquetadoSerializer(serializers.ModelSerializer):
    varietal = serializers.PrimaryKeyRelatedField(queryset=Varietal.objects.all())
    
    
    class Meta:
        model = StockBodegaEmpaquetado
        fields = ['varietal', 'cantidad_cajas', 'precio']