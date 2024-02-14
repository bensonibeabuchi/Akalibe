from django.urls import path
from .views import *

urlpatterns = [
    path('place_order/', place_order, name='place_order'),
    path('payments/', payments, name='payments'),
    
    path('checkout/', payment_checkout, name='checkout_payment'),
    path('create_payment/', create_payment, name='create_payment'),
    path('execute_payment/', execute_payment, name='execute_payment'),
    path('payment_failed/', payment_failed, name='payment_failed'),
    # path('payment_success/', payment_success, name='payment_success'),
]