from django.contrib import admin
from .models import Order, OrderLineItem, UserOrderProfile


class OrderLineItemAdminInline(admin.TabularInline):
    model = OrderLineItem
    readonly_fields = ('line_item_total',)


class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderLineItemAdminInline,)
    readonly_fields = ('order_number', 'date', 'delivery_cost', 'order_total',
                       'grand_total', 'payment_confirmed')
    fields = ('order_number', 'date', 'payment_confirmed', 'fulfilled',
              'full_name', 'email', 'phone_number', 'country', 'postcode',
              'town_or_city', 'street_address1', 'street_address2', 'county',
              'delivery_cost', 'order_total', 'grand_total',)
    list_display = ('order_number', 'date', 'pid', 'payment_confirmed',
                    'fulfilled', 'full_name', 'delivery_cost', 'order_total',
                    'grand_total')
    ordering = ('-date',)


class UserOrderProfileAdmin(admin.ModelAdmin):
    model = UserOrderProfile
    list_display = ('full_name', 'email', 'phone_number', 'country',
                    'postcode', 'town_or_city', 'street_address1',
                    'street_address2', 'county',)


admin.site.register(Order, OrderAdmin)
admin.site.register(UserOrderProfile, UserOrderProfileAdmin)
