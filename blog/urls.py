from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import path

from blog.views.views import (
    ProductDetailTemplateView,
    ProductListTemplateView, ProductAddTemplateView, ProductUpdateView, CustomersListView, CustomersAddListView,
    CustomerDetailView, CustomerDeleteView, CustomerUpdateView, ExportDataView
)

from blog.views.auth import (
    logout_page,
    MyLoginView, RegisterView, SendingEmailView, VerifyEmailDoneView, VerifyEmailConfirmView, VerifyEmailCompleteView)

urlpatterns = [
    # Products
    path('', ProductListTemplateView.as_view(), name='index'),
    path('detail/<slug:slug>/', ProductDetailTemplateView.as_view(), name='product_detail'),
    path('add-product/', ProductAddTemplateView.as_view(), name='add_product'),
    path('update-product/<slug:slug>/', ProductUpdateView.as_view(), name='update_product'),
    # Customers
    path('customers/', CustomersListView.as_view(), name='customers'),
    path('customers_detail/<int:pk>/', CustomerDetailView.as_view(), name='customers_detail'),
    path('delete/<int:pk>', CustomerDeleteView.as_view(), name='delete'),
    path('add-customer/', CustomersAddListView.as_view(), name='add_customers'),
    path('customer_update/<int:pk>/', CustomerUpdateView.as_view(), name='update_customer'),
    # authentication's url
    path('login-page/', MyLoginView.as_view(), name='login'),
    path('logout-page/', logout_page, name='logout'),
    path('register-page/', RegisterView.as_view(), name='register'),
    # sending email url
    path('sending-email-url/', SendingEmailView.as_view(), name='sending_email'),

    # verify email

    path('verify-email-done/', VerifyEmailDoneView.as_view(), name='verify_email_done'),
    path('verify-email/complete/', VerifyEmailCompleteView.as_view(), name='verify_email_complete'),
    path('verify-email-confirm/<uidb64>/<token>/', VerifyEmailConfirmView.as_view(), name='verify_email_confirm'),
    # exporting data

    path('customers-export-data-downloads/', ExportDataView.as_view(), name='export_data')

]
