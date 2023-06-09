# Generated by Django 2.2 on 2020-04-08 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='KhaltiCredentials',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('public_key', models.CharField(blank=True, max_length=250, null=True)),
                ('secret_key', models.CharField(blank=True, max_length=250, null=True)),
                ('verification_url', models.CharField(blank=True, max_length=250, null=True)),
            ],
            options={
                'verbose_name_plural': 'Khalti Credentials',
            },
        ),
        migrations.CreateModel(
            name='PaymentResponseKhalti',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fee_amount', models.CharField(blank=True, max_length=200, null=True)),
                ('created_on', models.CharField(blank=True, max_length=200, null=True)),
                ('state_idx', models.CharField(blank=True, max_length=200, null=True)),
                ('state_name', models.CharField(blank=True, max_length=200, null=True)),
                ('state_template', models.CharField(blank=True, max_length=200, null=True)),
                ('merchant_idx', models.CharField(blank=True, max_length=200, null=True)),
                ('merchant_name', models.CharField(blank=True, max_length=200, null=True)),
                ('merchant_mobile', models.CharField(blank=True, max_length=200, null=True)),
                ('idx', models.CharField(blank=True, max_length=200, null=True)),
                ('refunded', models.CharField(blank=True, max_length=200, null=True)),
                ('amount', models.CharField(blank=True, max_length=200, null=True)),
                ('type_idx', models.CharField(blank=True, max_length=200, null=True)),
                ('type_name', models.CharField(blank=True, max_length=200, null=True)),
                ('user_idx', models.CharField(blank=True, max_length=200, null=True)),
                ('user_name', models.CharField(blank=True, max_length=200, null=True)),
                ('user_mobile', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'verbose_name_plural': 'Payment Response',
                'ordering': ('-id',),
            },
        ),
    ]
