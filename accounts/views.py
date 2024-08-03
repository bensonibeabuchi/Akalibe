from email.message import EmailMessage
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from users.forms import CustomUserCreationForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from users.models import CustomUser
from django.http import HttpResponseBadRequest
from base.models import Cart, CartItem
from base.views import _cart_id
import requests



def login_page(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password')

            user = authenticate(request, email=email, password=password)

            if user is not None:
                try:
                    cart = Cart.objects.get(cart_id=_cart_id(request))
                    is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()  # noqa
                   
                    if is_cart_item_exists:
                        cart_item = CartItem.objects.filter(cart=cart)


                        # Getting the product variations by cart id
                        product_variation = []
                        for item in cart_item:
                            varitation = item.variations.all()
                            product_variation.append(list(varitation))

                        # Get the cart items from the user to access his or her product variations
                        cart_item = CartItem.objects.filter(user=user)
                        ex_var_list = []
                        id = []
                        for item in cart_item:
                            exisiting_variation = item.variations.all()
                            ex_var_list.append(list(exisiting_variation))
                            id.append(item.id)

                        for pr in product_variation:
                            if pr in ex_var_list:
                                index = ex_var_list.index(pr)
                                item_id = id[index]
                                item = CartItem.objects.get(id=item_id)
                                item.quantity += 1
                                item.user = user
                                item.save()
                            else:
                                cart_item = CartItem.objects.filter(cart=cart)
                                for item in cart_item:
                                    item.user = user
                                    item.save()
                except:
                    pass

                login(request, user)
                url = request.META.get('HTTP_REFERER')
                try:
                    query = requests.utils.urlparse(url).query
              
                    params = dict(x.split('=') for x in query.split('&'))
                    if 'next' in params:
                        nextPage = params['next']
                        return redirect(nextPage)
                except:
                    return redirect('dashboard')
            else:
                messages.error(request, 'Username or Password is incorrect')

        context = {}
        return render(request, 'accounts/login.html', context)
    




@login_required(login_url='login')
def logout_user(request):
    logout(request)
    messages.success(request, 'You are logged out')
    return redirect('login')


def register_page(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        if request.method == 'POST':
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.is_active = False  # Deactivate the user until email confirmation

                # Check password complexity
                password = form.cleaned_data['password1']
                if (
                    not any(char.isupper() for char in password) or
                    not any(char.isdigit() for char in password) or
                    not any(char in '!@#$%^&*()_+{}:;<>,.?~' for char in password)
                ):
                    messages.error(
                        request, "Password must contain a capital letter, a number, and a special character."
                    )
                    return render(request, 'accounts/register.html', {'form': form})

                email = form.cleaned_data['email']

                user.save()
                

               # Send email confirmation
                current_site = get_current_site(request)
                subject = 'Please Activate your account'
                message = render_to_string('accounts/account_activation_email.html', {
                    'user': user,
                    'domain': current_site,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                })
                to_email = email
                send_email = EmailMessage(subject, message, to=[to_email])
                send_email.send()

                # messages.success(request, 'Thank you for registering with us. Kindly check your email to activate your Account')  # noqa
                return redirect('account_activation_sent')

                # messages.success(
                # request, f'Account was created for {user.username}')
                # return redirect('login')
        else:
            form = CustomUserCreationForm()

        context = {'form': form}
        return render(request, 'accounts/register.html', context)


# @login_required
def account_activation_sent(request):
    return render(request, 'accounts/account_activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # messages.success(request, 'Congratulations! your account has been activated.') #noqa
        return redirect('account_activation_complete')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('account_invalid_link')


def account_activation_complete(request):
    return render(request, 'accounts/account_activation_complete.html')


def account_invalid_link(request):
    return render(request, 'accounts/account_invalid_link.html')


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if CustomUser.objects.filter(email=email).exists():
            user = CustomUser.objects.get(email__iexact=email) #iexact is case insensitive

            # Reset password email
            current_site = get_current_site(request)
            subject = 'Reset your password'
            message = render_to_string('accounts/forgotPasswordEmail.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(subject, message, to=[to_email])
            send_email.send()

            # messages.success(
            #     request, 'Password reset email has been sent to your email address.')
            return redirect('forgotPassword_sent')
        else:
            messages.error(request, 'Account does not exist!')
            return redirect('forgotPassword')

    return render(request, 'accounts/forgotPassword.html')


def forgotPassword_sent(request):
    return render(request, 'accounts/forgotPassword_sent.html')


def forgotPassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        # messages.success(request, 'Please reset your password')
        return redirect('forgotPassword_reset_page')
    else:
        # messages.error(request, 'Invalid password reset link')
        return redirect('forgotPassword_invalid_link')

def forgotPassword_reset_page(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # Check password complexity
       
        if (
            not any(char.isupper() for char in password) or
            not any(char.isdigit() for char in password) or
            not any(char in '!@#$%^&*()_+{}:;<>,.?~' for char in password)
        ):
            messages.error(
                request, "Password must contain a capital letter, a number, and a special character."
            )
            return render (request, 'accounts/forgotPassword_reset_page.html')
        
        # Confirm password

        if password == confirm_password:
            uid = request.session.get('uid')
            user = CustomUser.objects.get(pk=uid)
            user.set_password(password) #you have to use the set_password function to save the new password to the database
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        
        else:
            messages.error(request, 'Password do not match!')
            return redirect('forgotPassword_reset_page')
    
    else:
        return render (request, 'accounts/forgotPassword_reset_page.html')


def forgotPassword_invalid_link(request):
    return render(request, 'accounts/forgotPassword_invalid_link.html')


