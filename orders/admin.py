from django.contrib import admin
from .models import *

# Register your models here.


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'payment_id', 'amount_paid', 'created_at', ]

admin.site.register(Payment, PaymentAdmin)

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price', 'ordered')
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'first_name', 'phone', 'email', 'order_total',
                    'address_line_1', 'city', 'is_ordered', 'payment', 'created_at' ]
    list_filter = ['status', 'is_ordered',]
    search_fields = ['order_number', 'first_name', 'last_name', 'phone', 'email']
    list_per_page = 20
    inlines = [OrderProductInline]







class OrderProductAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'user', 'order', 'payment',]




# class CartAdmin(admin.ModelAdmin):
#     list_display = ['date_added']

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct, OrderProductAdmin)
