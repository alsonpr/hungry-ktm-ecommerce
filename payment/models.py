from django.db import models

# Create your models here.
class KhaltiCredentials(models.Model):
    public_key= models.CharField(max_length=250,null=True,blank=True)
    secret_key=models.CharField(max_length=250,null=True,blank=True)
    verification_url = models.CharField(max_length=250,null=True,blank=True)
    def __str__(self):
        return '{0}-{1}'.format(self.public_key,self.secret_key)
    class Meta:
        verbose_name_plural = 'Khalti Credentials'

class PaymentResponseKhalti(models.Model):
    fee_amount = models.CharField(max_length= 200, null=True,blank=True)
    created_on = models.CharField(max_length= 200, null=True,blank=True)
    state_idx = models.CharField(max_length= 200, null=True, blank=True)
    state_name = models.CharField(max_length= 200, null=True, blank=True)
    state_template = models.CharField(max_length= 200, null=True, blank=True)
    merchant_idx = models.CharField(max_length= 200, null=True, blank=True)
    merchant_name = models.CharField(max_length= 200, null=True, blank=True)
    merchant_mobile = models.CharField(max_length= 200, null=True, blank=True)
    idx = models.CharField(max_length= 200, null=True, blank=True)
    refunded = models.CharField(max_length= 200, null=True, blank=True)
    amount = models.CharField(max_length= 200, null=True, blank=True)
    type_idx = models.CharField(max_length= 200, null=True, blank=True)
    type_name = models.CharField(max_length= 200, null=True, blank=True)
    user_idx = models.CharField(max_length= 200, null=True, blank=True)
    user_name = models.CharField(max_length= 200, null=True, blank=True)
    user_mobile = models.CharField(max_length= 200, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Payment Response'
        ordering = ('-id',)