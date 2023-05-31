from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.shortcuts import reverse
from django_countries.fields import CountryField
from ckeditor_uploader.fields import RichTextUploadingField


CATEGORY_CHOICES = (
    ('Meat', 'Meat'),
    ('Dairy', 'Dairy'),
    ('Bakery', 'Bakery')
)

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)
PAYMENT_CHOICES_ = (
    ('COD', 'Cash On Delivery'),
    ('KHALTI', 'Khalti'),
)
PAYMENT_CHOICES = (
    ('Pending', 'Pending'),
    ('Paid', 'Paid'),
    ('Void', 'Void'),
)
DELIVERY_CHOICES = (
    ('Pending', 'Pending'),
    ('Delivered', 'Delivered'),
    ('Cancelled', 'Cancelled'),
)


class Category(models.Model):
    name = models.CharField(max_length=20)
    slug = models.SlugField(unique=True,)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("core:item-list", kwargs={'slug': self.slug})

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class Item(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True,)
    price = models.IntegerField()
    discount_price = models.IntegerField(blank=True, null=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag',blank = True, null=True)
    # label = models.CharField(choices=LABEL_CHOICES, max_length=1,blank=True,null=True)
    description = RichTextUploadingField('Description',blank=True,null=True)
    is_featured = models.BooleanField(default = True)
    is_active = models.BooleanField(default = True)
    image = models.ImageField()
    sub_image1 = models.ImageField(blank = True)
    sub_image2 = models.ImageField(blank = True)
    sub_image3 = models.ImageField(blank = True)
    sub_image4 = models.ImageField(blank = True)
    
    
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug': self.slug
        })
    
    def get_buy_now_url(self):
        return reverse("core:buy-now", kwargs={
            'slug': self.slug
        })

class Tag(models.Model):
    tag = models.CharField(max_length = 50)

    def __str__(self):
        return self.tag

class ContactInfo(models.Model):
    location = models.CharField(max_length = 200)
    phone = models.CharField(max_length = 50)
    email = models.CharField(max_length = 50)

    def __str__(self):
        return self.location


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.IntegerField(default = 0)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()
    

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class ShippingCharge(models.Model):
    shipping_amount = models.IntegerField(default=0)

    @property
    def get_delivery_charge(self):
        if self.shipping_amount:
            return str(self.shipping_amount)
        else:
            return str(0)
        

    def __str__(self):
        return str(self.shipping_amount)

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    total_amount = models.CharField(max_length=50, blank=True, null=True)
    
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    payment_status = models.CharField(choices=PAYMENT_CHOICES, max_length=20)
    delivery_status = models.CharField(choices=DELIVERY_CHOICES, max_length=20)
    # being_delivered = models.BooleanField(default=False)
    # received = models.BooleanField(default=False)
    # refund_requested = models.BooleanField(default=False)
    # refund_granted = models.BooleanField(default=False)

    '''
    1. Item added to cart
    2. Adding a billing address
    (Failed checkout)
    3. Payment
    (Preprocessing, processing, packaging etc.)
    4. Being delivered
    5. Received
    6. Refunds
    '''

    def __str__(self):
        return self.user.username

    def get_product_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total

    def get_total(self):
        total = 0
        shipping_charge = ShippingCharge.objects.all()
        if shipping_charge:
            shipping_amount = shipping_charge[0].shipping_amount
        else:
            shipping_amount = 0

        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total + shipping_amount


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    receiver_name = models.CharField(max_length=100)
    receiver_phone = models.CharField(max_length=100)
    address1 = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100,blank=True,null=True)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return '{0}-{1}'.format(self.address1,self.address2)

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    payment_type = models.CharField(choices=PAYMENT_CHOICES_, max_length=40)
    

    def __str__(self):
        return self.payment_type


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.IntegerField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)
