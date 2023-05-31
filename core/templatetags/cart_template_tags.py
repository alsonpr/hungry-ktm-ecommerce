from django import template
from core.models import Order, Category, ContactInfo

register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = Order.objects.filter(user=user, ordered=False)
        if qs.exists():
            return qs[0].items.count()
    return 0

@register.filter
def categories(user):
    return Category.objects.filter(is_active=True,)
    
@register.filter
def contacts(user):
    return ContactInfo.objects.all()