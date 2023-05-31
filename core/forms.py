from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from .models import *



class CheckoutForm(forms.ModelForm):
    # receiver_name = forms.CharField(required=True,widget=forms.TextInput(attrs={'placeholder': "Receiver's Full name"}))
    # receiver_phone = forms.IntegerField(widget=forms.TextInput(attrs={'placeholder': "Receiver's Phone Number",'type':'number'}))
    # address1 = forms.CharField(required=True,widget=forms.TextInput(attrs={'placeholder': "Receiver's Full Address"}))
    # address2 = forms.CharField(label="Address2 (Optional)" ,required=False,widget=forms.TextInput(attrs={'placeholder': "Receiver's Address2 (Optional)"}))
    
    class Meta:
        model = Address
        fields = ('receiver_name','receiver_phone','address1','address2',)
        widgets={
            'receiver_name':forms.TextInput(attrs={'placeholder': "Receiver's Full name"}),
            'receiver_phone':forms.TextInput(attrs={'placeholder': "Receiver's Phone Number",'type':'number'}),
            'address1':forms.TextInput(attrs={'placeholder': "Receiver's Full Address"}),
            'address2':forms.TextInput(attrs={'placeholder': "Receiver's Address2 (Optional)"}),
            }

    


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()


class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)
