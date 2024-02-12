from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from .filters import *
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.contrib import messages
from users.forms import *
from orders.models import *

# Create your views here.

# @login_required(login_url='login')


def index(request):
    products = Product.objects.filter(is_available=True)

    context = {
        "products": products,
    }
    return render(request, "base/index.html", context)


def store(request, category_slug=None):
    categories = None
    products = None

    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(
            category=categories, is_available=True)
        paginator = Paginator(products, 6)  # Show 6 contacts per page.
        page_number = request.GET.get("page")
        page_product = paginator.get_page(page_number)
        product_count = products.count()
    else:
        products = Product.objects.filter(is_available=True)
        paginator = Paginator(products, 6)  # Show 6 contacts per page.
        page_number = request.GET.get("page")
        page_product = paginator.get_page(page_number)
        product_count = products.count()

    context = {
        "products": products,
        "product_count": product_count,
        "page_product": page_product,
    }
    return render(request, "base/store.html", context)


def search(request):
    keyword = request.GET.get("keyword", "")

    # Start with an empty queryset
    products = Product.objects.none()

    if keyword:
        products = Product.objects.filter(
            Q(product_name__icontains=keyword) | Q(
                description__icontains=keyword)
        )

    # Get a list of product IDs in the cart for the user's session
    # in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=products).exists()

    context = {
        "products": products,
        # 'in_cart': in_cart,
        "keyword": keyword,
    }
    return render(request, "base/search-result.html", context)


def product_detail(request, category_slug, product_slug,):
    orderproduct = None
    category = get_object_or_404(
        Category, slug=category_slug)  # Get the Category
    try:
        single_product = get_object_or_404(Product, category=category, slug=product_slug)  # noqa
        is_out_of_stock = single_product.stock == 0
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()  # noqa
        variation = Variation.objects.filter(product=single_product).first()

    except Exception as e:
        raise e
    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.uuid).exists() # noqa
        except OrderProduct.DoesNotExist:
            orderproduct = None

    reviews = ReviewRating.objects.filter(product_id=single_product.uuid, status=True).order_by('-updated_date')
  

    context = {
        "single_product": single_product,
        "category": category,
        "is_out_of_stock": is_out_of_stock,
        "in_cart": in_cart,
        "variation": variation,
        "orderproduct": orderproduct,
        "reviews": reviews
    }

    return render(request, "base/product-detail.html", context)


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
        return cart


# This view function is used to add products to a user's shopping cart. It takes the request and the product_id as parameters.
def add_cart(request, product_uuid):
    current_user = request.user
    product = Product.objects.get(uuid=product_uuid)

    # if the user is authenticated
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value) #noqa
                    product_variation.append(variation)
                except Variation.DoesNotExist:
                    pass

        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists() #noqa
        if is_cart_item_exists:
            # If the product is already in the cart (determined by checking if a CartItem with the same product and cart exists), it increments the quantity of that item in the cart.
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            ex_var_list = []
            id = []

            for item in cart_item:
                exisiting_variation = item.variations.all()
                ex_var_list.append(list(exisiting_variation))
                id.append(item.id)

            if product_variation in ex_var_list:
                # increase the cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()

            else:
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                user=current_user,
                )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()

        return redirect('cart')

    # if current user is NOT authenticated 
    else:

        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]

                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        try:
            # get the cart using the cart_id present in the session
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:  # If the cart does not exist, it creates a new cart.
            cart = Cart.objects.create(
                cart_id=_cart_id(request)
            )
        cart.save()

        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            # If the product is already in the cart (determined by checking if a CartItem with the same product and cart exists), it increases the quantity of that item in the cart.
            cart_item = CartItem.objects.filter(product=product, cart=cart)

            # existing_variation coming from database
            # current variation coming from product_variation
            # item id coming from database

            ex_var_list = []
            id = []
            for item in cart_item:
                exisiting_variation = item.variations.all()
                ex_var_list.append(list(exisiting_variation))
                id.append(item.id)

            if product_variation in ex_var_list:
                # increase the cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()

            else:
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                cart=cart,
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()

        return redirect('cart')





def remove_cart(request, product_uuid, cart_item_id):
    product = get_object_or_404(Product, uuid=product_uuid)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect("cart")



def remove_cart_item(request, product_uuid, cart_item_id):    
    product = get_object_or_404(Product, uuid=product_uuid)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)  # noqa
    cart_item.delete()
    
    return redirect("cart")


def cart(request):
    total = 0
    quantity = 0
    cart_items = None
    tax = 0
    grand_total = 0

    try:
        if request.user.is_authenticated:
            # If the user is authenticated, filter the cart items by the user
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart= Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter( cart=cart, is_active=True)

        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax

    except ObjectDoesNotExist:
        pass

    context = {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_items,
        "tax": tax,
        "grand_total": grand_total,
    }
    return render(request, "base/cart.html", context)


@login_required(login_url='login')
def dashboard(request):
    messages.success(request, 'You are now logged in!')
    return render(request, 'base/dashboard.html')


@login_required(login_url='login')
def checkout(request):
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

    context = {
        "total": total,
        "quantity": quantity,
        "cart_items": cart_items,
        "tax": tax,
        "grand_total": grand_total,
    }
    return render(request, 'base/checkout.html', context)



def submit_review(request, product_uuid):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            # Check if the user has already submitted a review for this product
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__uuid=product_uuid)
            form = ReviewForm(request.POST, instance=reviews)
            if form.is_valid():
                form.save()
                messages.success(request, 'Thank you! Your review has been updated successfully')
            else:
                messages.error(request, 'Error updating review.')
            return redirect(url)

        except ReviewRating.DoesNotExist:
            # If the user has not submitted a review for this product, create a new one
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = form.save(commit=False)
                data.user = request.user  # Set the user field
               
                try:
                    product = Product.objects.get(uuid=product_uuid)
                    data.product = product #set the product field
                    data.ip = request.META.get('REMOTE_ADDR')
                    data.save()
                    messages.success(request, 'Thank you! Your review has been submitted successfully')
                except Product.DoesNotExist:
                    messages.error(request, 'Error submitting review. Product not found.')
            else:
                messages.error(request, 'Error submitting review. Please check the form.')
            return redirect(url)

                # data = ReviewRating()
                # data.subject = form.cleaned_data['subject']
                # data.rating = form.cleaned_data['rating']
                # data.review = form.cleaned_data['review']
                # data.ip = request.META.get('REMOTE_ADDR')
                # data.product_uuid = product_uuid
                # data.user_id = request.user.id
                # data.save()
                # messages.success(request, 'Thank you! Your review has been submitted successfully')
                # return redirect(url)

