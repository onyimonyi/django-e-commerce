from django.conf import settings
from django.db import models
from django.urls import reverse

CATEGORY_CHOICES = (
    ('MT', 'Meat'),
    ('SW', 'Swallow'),
    ('R', 'Rice'),
    ('BN', 'Beans'),
    ('SH', 'Shawarma'),
    ('DR', 'Drink'),
    ('BG', 'Burger'),
    ('FH', 'Fish'),
    ('SP', 'Soup'),
    ('S', 'Salad'),
    ('T', 'Tea'),
    ('SH', 'Shoe')
)
LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger'),
)


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10000, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    description = models.TextField(null=True, blank=True)
    picture = models.ImageField(upload_to='picture', max_length=255, null=True, blank=True)
    label = models.CharField(choices=LABEL_CHOICES, max_length=2, default='P')

    def get_absolute_url(self):
        return reverse("products:product-detail", kwargs={"id": self.id})

    def get_add_to_cart_url(self):
        return reverse("products:add-to-cart", kwargs={"id": self.id})

    def get_remove_from_cart_url(self):
        return reverse("products:remove-from-cart", kwargs={"id": self.id})

    def get_remove_single_item_from_cart_url(self):
        return reverse("products:remove-single-item-from-cart", kwargs={"id": self.id})

    def __str__(self):
        return self.title


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return F"{self.quantity} of {self.item.title}"

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


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    ref_code = models.CharField(max_length=20)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'BillingAddress', on_delete=models.SET_NULL, blank=True, null=True
    )
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total


class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    street_or_office_address = models.CharField(max_length=255)
    apartment_or_suite = models.CharField(max_length=255)
    zip = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)

    def __str__(self):
        return self.user.email


class Payment(models.Model):
    payment_charge_id = models.CharField(max_length=1000)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()
    ref_code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.pk}"
