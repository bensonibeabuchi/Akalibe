from base.models import Category
from .views import *
from .views import _cart_id


def menu_links(request):
    links = Category.objects.all()
    return dict(links=links)

# def cart_counter(request):
 
#     cart_items_count = 0  # initialize this first before referencing it below

#     cart = Cart.objects.get(cart_id=_cart_id(request))
#     cart_items = CartItem.objects.filter(cart=cart)
#     for cart_item in cart_items:
#         cart_items_count += cart_item.quantity

#     # print(cart_items.count())
#     # print(cart_items_count)
#     # cart_items_count = cart_items.count()

#     return dict(cart_items_count=cart_items_count)

def counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return{}
    else:
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))
            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().filter(user=request.user)
            else:
                # If the user is not authenticated, you need to use .first() to get a single cart
                cart_items = CartItem.objects.all().filter(cart=cart[:1])
            for cart_item in cart_items:
                    cart_count += cart_item.quantity

        except Cart.DoesNotExist:
            cart_count = 0

    return {'cart_count':cart_count}