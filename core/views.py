from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.shortcuts import redirect
from django.utils import timezone
from .forms import CheckoutForm, CouponForm, RefundForm, PaymentForm
from .models import Item, OrderItem, Order, Address, Payment, Coupon, Refund, UserProfile, Tag, ShippingCharge
from allauth.account.views import SignupView,ConfirmEmailView,LoginView,PasswordResetView,PasswordChangeView,PasswordSetView
import random
import string
import stripe
from allauth.account.forms import SignupForm
from allauth.account.forms import LoginForm
stripe.api_key = settings.STRIPE_SECRET_KEY
from django.http import JsonResponse
import uuid
from django.http.response import Http404
from django.contrib import messages
from django.http import HttpResponseRedirect,JsonResponse
from django.urls import reverse
from django.views.generic import TemplateView
from payment.models import *



class MyLoginView(LoginView):
    template_name = 'login.html'
   

    # form_class = CustomLoginForm
    # signup_form  = CustomSignupForm
    def __init__(self, **kwargs):
        super(MyLoginView, self).__init__(*kwargs)        
 
    def get_context_data(self, **kwargs):
        ret = super(MyLoginView, self).get_context_data(**kwargs)
        ret['form'] = self.get_form()
        ret['signupform'] = SignupForm
        
        return ret
 

class MySignupView(SignupView):
    template_name = 'login.html'
    # success_url = reverse_lazy('sales:checkout')
 

    # form_class = CustomSignupForm
    # signup_form  = CustomSignupForm
    def __init__(self, **kwargs):
        super(MySignupView, self).__init__(*kwargs)        
 
    def get_context_data(self, **kwargs):
        ret = super(MySignupView, self).get_context_data(**kwargs)
        ret['form'] = LoginForm
        ret['signupform'] = self.get_form()
        print(self.get_form())
        
        return ret
 

def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def products(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "products.html", context)


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid

from django.contrib.sites.shortcuts import get_current_site
class CheckoutView(LoginRequiredMixin,View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            product_names_list = [item.item.title for item in order.items.all()]
            products_names = ';'.join(product_names_list)
            products_slug_list = [item.item.slug for item in order.items.all()]
            products_slug = ';'.join(products_slug_list)
            total_amount = order.get_total()
            product_url = "https://hungrykathmandu.com"
            khalti_payment = KhaltiCredentials.objects.all().get()
            public_key = khalti_payment.public_key
            delivery_charge_obj = ShippingCharge.objects.all()[0]
            delivery_charge = delivery_charge_obj.get_delivery_charge

            if not order.items.all().exists():
                raise Http404
            
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True,
                'product_name':products_names,
                'product_slug':products_slug,
                'product_url':product_url,
                'total_amount': total_amount,
                'public_key': public_key,
                'delivery_charge':delivery_charge
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            ).order_by('-id')
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})

            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
            )
            if billing_address_qs.exists():
                context.update(
                    {'default_billing_address': billing_address_qs[0]})

            return render(self.request, "payment.html", context)
        except ObjectDoesNotExist:
            # messages.info(self.request, "You do not have an active order")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        
        order = Order.objects.get(user=self.request.user, ordered=False)
        if form.is_valid():
            shipping_address = form.save(commit = False)
            shipping_address.address_type = "S"
            shipping_address.user = self.request.user
            shipping_address.default = True
            shipping_address.save()
            order.shipping_address = shipping_address
            order.save()
            # messages.success(self.request, "Your order was successful!")
            return JsonResponse({'message':'success'})
        else:
            # messages.info(self.request, "Please fill in the required shipping address fields")
            return redirect("core:order-summary")


def place_order(request):
    if request.method == "POST":
        order = Order.objects.get(user=request.user, ordered=False)
        order.ordered = True
        order.total_amount = order.get_total()
        payment_type = Payment.objects.get(payment_type="COD")
        order.payment = payment_type
        order.delivery_status = "Pending"
        order.payment_status = "Pending"
        ref_code = uuid.uuid4().hex[:10]
        order.ref_code = ref_code
        order.save()

        order_items = order.items.all()
        order_items.update(ordered=True)
        for item in order_items:
            item.price = item.get_final_price()
            item.save()
        
        # list(messages.get_messages(request))
        # messages.success(request,"Thank you for your purchase. Your order has been placed successfully")
        return HttpResponseRedirect(reverse('core:thank-view',kwargs={'order': ref_code}))



class HomeView(ListView):
    model = Item
    paginate_by = 10
    context_object_name = "products"
    template_name = "index.html"

    def get_queryset(self):
        return Item.objects.filter(is_active = True, is_featured = True)
        

class ItemList(ListView):

    def get(self, *args, **kwargs):
        slug = kwargs['slug']
        tag_name = self.request.GET.get('tag-name',None)
        price_name = self.request.GET.get('price-filter',None)
        
        if tag_name:
            products = Item.objects.filter(category__slug=slug,is_active=True,tags__tag = tag_name)
            product_count = products.count()
            tag_name = tag_name
        
        elif price_name and price_name=="l2h":
            products = Item.objects.filter(category__slug=slug,is_active=True).order_by('discount_price')
            product_count = products.count()
            price_filter = "l2h"
        
        elif price_name and price_name=="h2l":
            products = Item.objects.filter(category__slug=slug,is_active=True).order_by('-discount_price')
            product_count = products.count()
            price_filter = "h2l"
        
        else:
            products = Item.objects.filter(category__slug=slug,is_active=True)
            product_count = products.count()
        
        
        tags = Tag.objects.filter(item__category__slug=slug,item__is_active=True).distinct()
        context = {
            'products': products,
            'count':product_count,
            'tags':tags,
            'slug':slug,
            'tag_name':tag_name,
            'price_filter':price_name
        }
        return render(self.request, 'item-list.html', context)
        
        


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            delivery_charge = ShippingCharge.objects.all()
            if delivery_charge:
                delivery_amount = delivery_charge[0].shipping_amount
            else:
                delivery_amount = 0
            product_total = order.get_product_total()
            context = {
                'object': order,
                'delivery_amount': delivery_amount,
                'product_total':product_total
            }
            return render(self.request, 'cart.html', context)
        except ObjectDoesNotExist:
            # messages.warning(self.request, "You do not have an active order")
            return render(self.request, 'cart.html')


class ItemDetailView(DetailView):
    model = Item
    context_object_name = "product"
    template_name = "item-detail.html"


@login_required(login_url='/checkout/login/')
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False,
        price = item.discount_price,
    )
    
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            # messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            order.items.add(order_item)
            # messages.info(request, "This item was added to your cart.")
            return redirect("core:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        # messages.info(request, "This item was added to your cart.")
        return redirect("core:order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            # messages.info(request, "This item was removed from your cart.")
            return redirect("core:order-summary")
        else:
            # messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        # messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            # messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            # messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        # messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        # messages.info(request, "This coupon does not exist")
        return redirect("core:checkout")


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                # messages.success(self.request, "Successfully added coupon")
                return redirect("core:checkout")
            except:
                # messages.info(self.request, "You do not have an active order")
                return redirect("core:checkout")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                # messages.info(self.request, "Your request was received.")
                return redirect("core:request-refund")

            except ObjectDoesNotExist:
                # messages.info(self.request, "This order does not exist.")
                return redirect("core:request-refund")


class UserOrder(LoginRequiredMixin,View):
    def get(self, *args, **kwargs):
        orders = Order.objects.filter(user=self.request.user,ordered=True).order_by('-id')
        context = {
            'orders':orders,
            'count':orders.count(),
        } 
        return render(self.request, "profile.html",context)

class SearchView(View):
    def get(self, *args, **kwargs):
        keyword = self.request.GET.get('keyword',None)
        tags = Tag.objects.filter(item__title__icontains=keyword,item__is_active=True).distinct()
        tag_name = self.request.GET.get('tag-name',None)
        price_name = self.request.GET.get('price-filter',None)
        
        if tag_name:
            products = Item.objects.filter(title__icontains=keyword,is_active=True,tags__tag = tag_name)
            product_count = products.count()
            tag_name = tag_name
        
        elif price_name and price_name=="l2h":
            products = Item.objects.filter(title__icontains=keyword,is_active=True).order_by('discount_price')
            product_count = products.count()
            price_filter = "l2h"
        
        elif price_name and price_name=="h2l":
            products = Item.objects.filter(title__icontains=keyword,is_active=True).order_by('-discount_price')
            product_count = products.count()
            price_filter = "h2l"

        else:
            
            products = Item.objects.filter(title__icontains=keyword,is_active=True)
        context = {
            'products':products,
            'count':products.count(),
            'tags':tags,
            'keyword':keyword,
            'tag_name':tag_name,
            'price_filter':price_name
        } 

        return render(self.request, "item-list-search.html",context)

class PlaceOrder(LoginRequiredMixin,ListView):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        order_items = order.items.all()
        order_items.update(ordered=True)
        for item in order_items:
            item.save()

        order.ordered = True
        order.payment = payment
        order.ref_code = create_ref_code()
        order.save()

        # messages.success(self.request, "Your order was successful!")
        return redirect("/")

@login_required(login_url='/checkout/login/')
def buy_now(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            # messages.info(request, "This item quantity was updated.")
            return redirect("core:checkout")
        else:
            order.items.add(order_item)
            # messages.info(request, "This item was added to your cart.")
            return redirect("core:checkout")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        # messages.info(request, "This item was added to your cart.")
        return redirect("core:checkout")

class ThankYouView(TemplateView):
    template_name = 'thankyou.html'

    def get(self, request, order):
        order_present = Order.objects.filter(ref_code = order,user=request.user).exists()
        if order_present:
            return super(ThankYouView, self).get(request,order_number = order)
        else:
            raise Http404