from django.contrib import admin

from .models import Item, OrderItem, Order, Payment, Coupon, Refund, Address, UserProfile, Tag, Category, ContactInfo, ShippingCharge

from easy_select2 import select2_modelform


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'shipping_address',
                    'billing_address',
                    'payment',
                    'delivery_status',
                    'payment_status',
                    'coupon'
                    ]
    list_display_links = [
        'user',
        'shipping_address',
        'billing_address',
        'payment',
        'coupon'
    ]
    list_filter = ['ordered',
                   'payment_status',
                   'delivery_status',
                   ]
    search_fields = [
        'user__username',
        'ref_code'
    ]
    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'address1',
        'address2',
        'address_type',
        'default'
    ]
    list_filter = ['default', 'address_type',]
    search_fields = ['user', 'address1', 'address2',]

ItemForm = select2_modelform(Item, attrs={'width': '250px'})
class ItemAdmin(admin.ModelAdmin):
    form = ItemForm
    prepopulated_fields = {'slug': ('title',)}

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Item,ItemAdmin)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(Address, AddressAdmin)
admin.site.register(UserProfile)
admin.site.register(Tag)
admin.site.register(Category,CategoryAdmin)
admin.site.register(ContactInfo,)
admin.site.register(ShippingCharge,)
