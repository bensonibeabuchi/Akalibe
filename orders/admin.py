from django.contrib import admin
from .models import *

# Register your models here.


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'status', 'payment_id', 'amount_paid' ]

admin.site.register(Payment, PaymentAdmin)


class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'first_name', 'phone', 'email',
                    'address_line_1', 'city', 'is_ordered', 'created_at' ]
    list_filter = ['status', 'is_ordered',]
    search_fields = ['order_number', 'first_name', 'last_name', 'phone', 'email']
    list_per_page = 20



class OrderProductAdmin(admin.ModelAdmin):
    list_display = ['user', 'order', 'payment', 'product', 'quantity']

# class CartAdmin(admin.ModelAdmin):
#     list_display = ['date_added']

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct, OrderProductAdmin)
