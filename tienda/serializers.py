from rest_framework import serializers
from .models import Categoria, Producto, Orden, OrdenItem
from django.contrib.auth.models import User
from decimal import Decimal

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class ProductoSerializer(serializers.ModelSerializer):
    precio_final = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = '__all__'

    def get_precio_final(self, obj):
        return float(obj.precio * (Decimal(1) - Decimal(obj.descuento) / Decimal(100)))

class OrdenItemSerializer(serializers.ModelSerializer):
    producto = ProductoSerializer()

    class Meta:
        model = OrdenItem
        fields = ['producto', 'cantidad', 'precio_unitario']

class OrdenItemCreateSerializer(serializers.ModelSerializer):
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all())  # 👈 clave

    class Meta:
        model = OrdenItem
        fields = ['producto', 'cantidad']

class OrdenSerializer(serializers.ModelSerializer):
    items = OrdenItemSerializer(many=True)

    class Meta:
        model = Orden
        fields = ['id', 'nombre', 'email', 'direccion', 'telefono', 'fecha_creacion', 'total', 'items']

class OrdenCreateSerializer(serializers.ModelSerializer):
    items = OrdenItemCreateSerializer(many=True)

    class Meta:
        model = Orden
        fields = ['nombre', 'email', 'direccion', 'telefono', 'total', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        orden = Orden.objects.create(**validated_data)

        total = 0
        for item in items_data:
            producto = item['producto']  # ya es una instancia gracias al PrimaryKeyRelatedField
            cantidad = item['cantidad']

            if producto.stock < cantidad:
                raise serializers.ValidationError(f"Stock insuficiente para {producto.nombre}")

            producto.stock -= cantidad
            producto.save()

            precio_unitario = producto.precio * (Decimal(1) - Decimal(producto.descuento) / Decimal(100))
            OrdenItem.objects.create(
                orden=orden,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio_unitario
            )
            total += precio_unitario * cantidad

        orden.total = total
        orden.save()
        return orden

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
