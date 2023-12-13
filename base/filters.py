import django_filters
from .models import *


class ProductFilter(django_filters.FilterSet):
    product_name = django_filters.CharFilter(
        field_name='product_name', lookup_expr='icontains')
    description = django_filters.CharFilter(
        field_name='description', lookup_expr='icontains')

    class Meta:
        model = Product
        fields = ('category', 'price')
