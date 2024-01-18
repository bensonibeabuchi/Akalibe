from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('search/', search, name='search-result'),
    path('store/', store, name='store'),
    path('cart/', cart, name='cart'),
    path('dashboard/', dashboard, name='dashboard'),
    path('add_cart/<uuid:product_uuid>/', add_cart, name='add_cart'),
    path('remove_cart/<uuid:product_uuid>/<int:cart_item_id>/', remove_cart, name='remove_cart'),
    path('remove_cart_item/<uuid:product_uuid>/<int:cart_item_id>/', remove_cart_item, name='remove_cart_item'),

    # path('cart/checkout/', checkout, name='checkout'),
    path('cart/place_order/', place_order, name='place_order'),


    path('category/<slug:category_slug>/', store, name='products_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>/', product_detail, name='product-detail'),  # Include both slugs

]
