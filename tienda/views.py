from rest_framework import viewsets, permissions, filters
from .models import Producto, Categoria, Orden
from .serializers import ProductoSerializer, CategoriaSerializer, OrdenSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny
from .serializers import OrdenSerializer, OrdenCreateSerializer


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categoria', 'descuento']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['precio', 'nombre']
    permission_classes = [AllowAny] 


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [AllowAny]

class OrdenViewSet(viewsets.ModelViewSet):
    queryset = Orden.objects.all()
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Orden.objects.all().order_by('-fecha_creacion')

    def get_serializer_class(self):
        if self.action == 'create':
            return OrdenCreateSerializer  # ✅ Para POST (crear orden)
        return OrdenSerializer  # ✅ Para GET, PUT, etc.

    def perform_create(self, serializer):
        serializer.save()  # Si no hay usuario asociado, está perfecto así

