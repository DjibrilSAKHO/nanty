from django.db import models

class User(models.Model):
    category = models.CharField(
        max_length=10,
        choices=[
            ('chatbot', 'Chatbot'),
            ('client', 'Client'),
            ('operator', 'Operator'),
            ('system', 'System'),
            ('founder', 'Founder')
        ],
        default='client',
        null=False
    )
    firstname = models.CharField(max_length=100, null=True)
    lastname = models.CharField(max_length=100, null=True)
    email = models.CharField(max_length=255, null=True, unique=True)
    password = models.CharField(max_length=255, null=True)
    contry_phone_code = models.CharField(max_length=10, null=False)
    phone_number = models.CharField(max_length=20, null=False, unique=True)
    display_phone_number = models.CharField(max_length=255, null=False)
    business_account_id = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=[
            ('active', 'Active'),
            ('suspended', 'Suspended'),
            ('disabled', 'Disabled')
        ],
        default='active',
        null=False
    )

    class Meta:
        db_table = 'users'

class Platform(models.Model):
    platform_name = models.CharField(max_length=50, unique=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)

    class Meta:
        db_table = 'platforms'

class Country(models.Model):
    country_code = models.CharField(max_length=10, unique=True, null=False)
    country_phone_code = models.CharField(max_length=10, null=False)
    country_name = models.CharField(max_length=100, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)

    class Meta:
        db_table = 'countries'

class SubscriptionType(models.Model):
    subscription_name = models.CharField(max_length=50, unique=True, null=False)
    monthly_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    annual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    features = models.TextField(null=True)
    description = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    class Meta:
        db_table = 'subscription_types'

class Company(models.Model):
    company_name = models.CharField(max_length=100, null=False)
    address = models.CharField(max_length=255, null=True)
    email = models.CharField(max_length=100, null=True)
    phone_number = models.CharField(max_length=20, null=True)
    contact_person = models.CharField(max_length=100, null=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=False)
    subscription_type = models.ForeignKey(SubscriptionType, on_delete=models.CASCADE, null=False)
    subscription_start_date = models.DateField(null=False)
    subscription_end_date = models.DateField(null=False)
    status = models.CharField(
        max_length=8,
        choices=[
            ('Enabled', 'Enabled'),
            ('Disabled', 'Disabled')
        ],
        default='Disabled',
        null=False
    )
    created_at = models.DateTimeField(auto_now_add=True, null=False)

    class Meta:
        db_table = 'companies'
