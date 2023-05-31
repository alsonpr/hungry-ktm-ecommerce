from django.urls import path
from django.views.generic import TemplateView
from .views import *
app_name = 'payment'

urlpatterns = [
    path('khalti', pay_by_khalti, name='payment'),
]
