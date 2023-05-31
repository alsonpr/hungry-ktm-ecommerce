from django.shortcuts import render,redirect
from django.http.response import Http404
from django.http import JsonResponse
import requests
from .models import *
from core.models import Order, Payment
import uuid
# Create your views here.



def pay_by_khalti(request):
    if request.method == "GET":
        raise Http404

    if request.method == "POST":
        khalti_payment = KhaltiCredentials.objects.all().get()
        url = khalti_payment.verification_url
        token = request.POST.get('token', None)
        print(token)
        total_amount_in_paisa, order = get_total_amount(request.user)
        
        # order = Order.objects.get(user=request.user, ordered=False)
        
        payload = {
            "token": token,
            "amount": total_amount_in_paisa
        }


        headers = {
            "Authorization": "Key {}".format(khalti_payment.secret_key)
        }

        response = requests.post(url, payload, headers=headers)
        # Save response to table 
        put_khalti_json_response(response.json())

        if response.status_code == 200:
            place_khalti_order(order)
            print(order.ref_code)
            return JsonResponse({'status':response.status_code, 'order':order.ref_code})
        else:
            print("Payment Failed")
            return redirect(request.META['HTTP_REFERER'])


def put_khalti_json_response(data):
    try:
        json_data = data
        fee_amount = json_data['fee_amount']
        created_on = json_data['created_on']
        state_idx = (json_data['state'])['idx']
        state_name = (json_data['state'])['name']
        state_template = (json_data['state'])['template']
        merchant_idx = (json_data['merchant'])['idx']
        merchant_name = (json_data['merchant'])['name']
        merchant_mobile = (json_data['merchant'])['mobile']
        idx = json_data['idx']
        refunded = json_data['refunded']
        amount = json_data['amount']
        type_idx = (json_data['type'])['idx']
        type_name = (json_data['type'])['name']
        user_idx = (json_data['user'])['idx']
        user_name = (json_data['user'])['name']
        user_mobile = (json_data['user'])['mobile']

        PaymentResponseKhalti.objects.create(fee_amount=fee_amount, created_on=created_on, state_idx=state_idx,
                                        state_name=state_name, state_template=state_template,
                                        merchant_idx=merchant_idx, merchant_name=merchant_name,
                                        merchant_mobile=merchant_mobile, idx=idx,
                                        refunded=refunded, amount=amount, type_idx=type_idx, type_name=type_name,
                                        user_idx=user_idx, user_name=user_name,
                                        user_mobile=user_mobile)
    except:
        pass


def place_khalti_order(order):
    order.ordered = True
    order.total_amount = order.get_total()
    payment_type = Payment.objects.get(payment_type="KHALTI")
    order.payment = payment_type
    order.delivery_status = "Pending"
    order.payment_status = "Paid"
    ref_code = uuid.uuid4().hex[:10]
    order.ref_code = ref_code
    order.save()

    order_items = order.items.all()
    order_items.update(ordered=True)
    for item in order_items:
        item.price = item.get_final_price()
        item.save()


def get_total_amount(user):
    order = Order.objects.get(user= user, ordered=False)
    total_amount = order.get_total() * 100
    return total_amount , order

