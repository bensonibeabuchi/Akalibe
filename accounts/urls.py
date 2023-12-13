from django.urls import path
from .views import *
from base.views import dashboard
from django.contrib.auth import views as auth_views

urlpatterns = [
       path('', dashboard, name='dashboard'),
       path('login/', login_page, name='login'),  # noqa
       path('logout/', logout_user, name='logout'),  # noqa
       path('register/', register_page, name='register'),  # noqa 

       path('account_activation_sent/', account_activation_sent, name='account_activation_sent'),  # noqa
       path('account_invalid_link/', account_invalid_link, name='account_invalid_link'),  # noqa
       path('account_activation_complete/', account_activation_complete, name='account_activation_complete'),  # noqa
       path('activate/<uidb64>/<token>/', activate, name='activate'),  # noqa
       
       path('forgotPassword/', forgotPassword, name='forgotPassword'),
       path('forgotPassword_sent/', forgotPassword_sent, name='forgotPassword_sent'),  # noqa
       path('forgotPassword_validate/<uidb64>/<token>/', forgotPassword_validate, name='forgotPassword_validate'),  # noqa
       path('forgotPassword_reset_page/', forgotPassword_reset_page, name='forgotPassword_reset_page'),  # noqa
       path('forgotPassword_invalid_link/', forgotPassword_invalid_link, name='forgotPassword_invalid_link'),  # noqa


]
