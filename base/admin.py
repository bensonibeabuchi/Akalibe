from django.contrib import admin
from .models import *

# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name',]
    prepopulated_fields = {"slug": ("category_name",)}


admin.site.register(Category, CategoryAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'price', 'category',
                    'stock', 'date_modified', 'is_available', ]
    list_filter = ['category', 'is_available']
    list_editable = ['category', 'price', 'stock',]
    prepopulated_fields = {"slug": ("product_name",)}


class VariationAdmin(admin.ModelAdmin):
    list_display = ['product', 'variation_category', 'variation_value']
    list_filter = ['product', 'variation_category', 'variation_value']

# class CartAdmin(admin.ModelAdmin):
#     list_display = ['date_added']

admin.site.register(Variation, VariationAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart)
admin.site.register(CartItem)
