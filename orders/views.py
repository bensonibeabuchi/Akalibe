import datetime
from django.http import HttpResponse
from django.shortcuts import render, redirect
from base.models import *
from users.forms import OrderForm
from .models import Order
import json

import paypalrestsdk
from django.conf import settings
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

paypalrestsdk.configure({
    "mode": "sandbox",  # Change to "live" for production
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_SECRET,
})

def create_payment(request):
    total = 0
    quantity = 0
    cart_items = None
    tax = 0
    grand_total = 0

    try:
        if request.user.is_authenticated:
            # If the user is authenticated, filter the cart items by the user
            cart_items = CartItem.objects.filter(user=request.user, is_active=True).order_by('product__product_name')
        else:
            # If the user is not authenticated, return an empty queryset or handle as needed 
            cart_items = CartItem.objects.none()

        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax

    except ObjectDoesNotExist:
        pass

    # Convert grand_total to string before passing it to PayPal
    grand_total_str = str(grand_total)

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal",
        },
        "redirect_urls": {
            "return_url": request.build_absolute_uri(reverse('execute_payment')),
            "cancel_url": request.build_absolute_uri(reverse('payment_failed')),
        },
        "transactions": [
            {
                "amount": {
                    "total": grand_total_str,  # Convert to string
                    "currency": "USD",
                },
                "description": "Payment for Product",
            }
        ],
    })

    if payment.create():
        return redirect(payment.links[1].href)  # Redirect to PayPal for payment
    else:
        return render(request, 'base/payment_failed.html')
    



def execute_payment(request):
    
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
      
        return render(request, 'base/payment_success.html')
    else:
        return render(request, 'base/payment_failed.html')
    
    cart_items = CartItem.objects.filtere(user=request.user)

    for item in case_items:
        orderproduct = OrderProduct()



def payment_checkout(request):
    return render(request, 'base/checkout.html')



def payment_failed(request):
    return render(request, 'base/payment_failed.html')


def place_order(request):
    current_user = request.user

    # if the cart count is 0 then redirect back to store

    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    
    grand_total = 0
    tax = 0
    total = 0
    quantity = 0

    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            #store all the billing information inside the Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.email = form.cleaned_data['email']
            data.phone = form.cleaned_data['phone']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # Generate Order Number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'base/payments.html', context)
        else:
            return OrderForm()
    else:
        return redirect('checkout')



def payments(request):
    body = json.loads(request.body)
    print(body)
    return render(request, 'base/payments.html')