from django.contrib import admin

# Register your models here.

from .models import Item, OrderItem, Order, Payment, BillingAddress, Refund


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'ordered',
        'being_delivered',
        'received',
        'refund_requested',
        'refund_granted',
        'payment',
        'billing_address',

    ]
    list_display_links = [
        'user',
        'billing_address',
        'payment'
    ]

    list_filter = [
        'ordered',
        'being_delivered',
        'received',
        'refund_requested',
        'refund_granted',

    ]

    search_fields = [
        'user__email',
        'ref_code'
    ]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'first_name',
        'last_name',
        'street_or_office_address',
        'apartment_or_suite',
        'phone_number'

    ]

    list_filter = [
        'user',
        'phone_number',
        'first_name'
    ]

    search_fields = [
        'user__email',
        'phone_number',
        'first_name'
    ]


admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(BillingAddress, AddressAdmin)
admin.site.register(Refund)
