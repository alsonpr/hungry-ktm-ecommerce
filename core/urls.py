from django.urls import path
from django.views.generic import TemplateView
# from .views import (
#     ItemDetailView,
#     CheckoutView,
#     HomeView,
#     OrderSummaryView,
#     add_to_cart,
#     remove_from_cart,
#     remove_single_item_from_cart,
#     PaymentView,
#     AddCouponView,
#     RequestRefundView,
#     PlaceOrder,
#     buy_now,
    
# )
from .views import *
app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    # path('request-refund/', RequestRefundView.as_view(), name='request-refund'),
    path('place-order/', PlaceOrder.as_view(), name='place-order'),
    path('buy-now/<slug>/', buy_now, name='buy-now'),
    path('checkout/login/',MyLoginView.as_view(),name='checkout-login'),
    path('checkout/signup/',MySignupView.as_view(),name='checkout-signup'),
    path('cod/', place_order, name='place-order'),
    path('item-list/<slug>/', ItemList.as_view(), name='item-list'),
    path('orders/', UserOrder.as_view(), name='user-order'),
    path('search/', SearchView.as_view(), name='search'),
    path('order/<order>', ThankYouView.as_view() , name='thank-view'),
]
