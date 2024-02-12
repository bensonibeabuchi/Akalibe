from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django import forms
from .models import *
from orders.models import Order
from base.models import *


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("email", "username", "first_name", "last_name",)
    
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        
        #Check for password validation if password1 is true and password2 is true and password1 and password2 are NOT the same, raise validation error

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        return password2
    
    def clean_email(self):
        email = self.cleaned_data['email']
        # Check for uniqueness
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Account with this email already exists.")
        return email



class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ("email", "username", "first_name", "last_name",)


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('first_name', 'last_name', 'email', 'phone', 'address_line_1', 'address_line_2', 'country', 'state', 'city', 'order_note')


class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject', 'review', 'rating']