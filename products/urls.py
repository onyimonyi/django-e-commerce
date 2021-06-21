from django.urls import path
from .views import (
    product_list_view,
    product_delete_view,
    product_detail_view,
    product_create_view,
    add_to_cart,
    remove_single_item_from_cart,
    remove_from_cart,
    order_summary_view,
    CheckoutView,
    PaymentView,
    home_view,
    admin_dashboard_view,
    product_update_view,
    BitcoinPaymentView,
    PaymentHookView,
    RefundView
)

app_name = 'products'
urlpatterns = [
    path('delete/<int:id>/', product_delete_view, name='delete-item'),
    path('product-list', product_list_view.as_view(), name='product-list'),
    path('<int:id>/', product_detail_view, name='product-detail'),
    path('create/', product_create_view, name='product-create'),
    path('<int:id>/add-to-cart/', add_to_cart, name='add-to-cart'),
    path('<int:id>/remove-from-cart/', remove_from_cart, name='remove-from-cart'),
    path('<int:id>/remove-single-item-from-cart/', remove_single_item_from_cart, name='remove-single-item-from-cart'),
    path('order-summary/', order_summary_view.as_view(), name='order-summary'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('payment/<payment_options>/', PaymentView.as_view(), name='payment'),
    path('admin-dashboard/', admin_dashboard_view, name='admin-dashboard'),
    path('', home_view, name='home'),
    path('update/<int:id>/', product_update_view, name='update-item'),
    path('bitcoin-payment/<payment_options>/', BitcoinPaymentView.as_view(), name='bitcoin-payment'),
    path('webhook/', PaymentHookView, name='webhook'),
    path('request-refund/', RefundView.as_view(), name='request-refund'),

]
