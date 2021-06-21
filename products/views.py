from builtins import int, open
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from json.decoder import JSONDecodeError

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import json

from django.utils import timezone
from django.contrib import messages
import random
import string
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, DetailView, ListView
from .models import Item, Order, OrderItem, BillingAddress, Payment, Refund
from .forms import ProductForm, CheckoutForm, RefundForm


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


@login_required
def home_view(request, *args, **kwargs):
    return render(request, "home.html")


# Create your views here.
@login_required
def product_create_view(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        form = ProductForm()
    context = {
        'form': form,
    }
    return render(request, 'products/product_create.html', context)


def product_update_view(request, id):
    obj = get_object_or_404(Item, id=id)
    form = ProductForm(instance=obj)
    if request.method == 'POST':
        form = ProductForm(request.POST or None, request.FILES or None, instance=obj)
        if form.is_valid():
            form.save()
            form = ProductForm()
    context = {
        'form': form,
        'obj': obj,
    }
    return render(request, 'products/product_create.html', context)


@login_required
def product_delete_view(request, id):
    obj = get_object_or_404(Item, id=id)
    if request.method == 'POST':
        obj.delete()
        return redirect('products:admin-dashboard')
    context = {
        'object': obj
    }
    return render(request, "products/product_delete.html", context)


# def product_list_view(request ):


class product_list_view(LoginRequiredMixin, ListView):
    def get(self, *args, **kwargs):
        item = Item.objects.all()
        paginator = Paginator(item, 4)  # Show 4 contacts per page.
        page_number = self.request.GET.get('page')
        item = paginator.get_page(page_number)
        context = {

            'item': item,
            'page_obj': item
        }
        return render(self.request, 'products/product_list.html', context)

    # def get


# model = Item
# template_name = 'products/product_list.html'


class order_summary_view(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'products/order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, 'you do not have an active order')
            return redirect("products:product-list")


class CheckoutView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            form = CheckoutForm()
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'form': form,
                'order': order
            }
            return render(self.request, "products/checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, 'you do not have an active order')
            return redirect("products:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                first_name = form.cleaned_data.get('first_name')
                last_name = form.cleaned_data.get('last_name')
                street_or_office_address = form.cleaned_data.get('street_or_office_address')
                apartment_or_suite = form.cleaned_data.get('apartment_or_suite')
                zip = form.cleaned_data.get('zip')
                phone_number = form.cleaned_data.get('phone_number')
                # TODO: add functionality to this field
                # same_shipping_address = form.cleaned_data.get('same_shipping_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_options = form.cleaned_data.get('payment_options')
                billing_address = BillingAddress(
                    user=self.request.user,
                    first_name=first_name,
                    last_name=last_name,
                    street_or_office_address=street_or_office_address,
                    apartment_or_suite=apartment_or_suite,
                    zip=zip,
                    phone_number=phone_number
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                if payment_options == 'PS':
                    return redirect("products:payment", payment_options='PayStack')
                elif payment_options == 'BTC':
                    return redirect("products:bitcoin-payment", payment_options='Bitcoin')
                else:
                    messages.info(self.request, 'invalid payment option')
                    return redirect("products:checkout")
        except ObjectDoesNotExist:
            messages.info(self.request, 'you do not have an active order')
            return redirect("products:product-list")


class RefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, 'products/refund.html', context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            refund = Refund.objects.filter(ref_code=ref_code)
            try:
                order = Order.objects.get(ref_code=ref_code)
                if refund.exists():
                    messages.info(self.request, "you have submitted your request before")
                    return redirect("products:request-refund")
                else:
                    order.refund_requested = True
                    order.save()

                    refund = Refund()
                    refund.order = order
                    refund.email = email
                    refund.reason = message
                    refund.ref_code = ref_code
                    refund.save()
                    messages.info(self.request, "your request was submitted successfully")
                    return redirect("products:request-refund")
            except ObjectDoesNotExist:
                messages.info(self.request, "wrong reference code, failed")
                return redirect("products:request-refund")


class BitcoinPaymentView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        print(self.request.POST.get('ref'));
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order
            }
            return render(self.request, 'products/bitcoin_payment.html', context)
        else:
            messages.warning(self.request, "fill you billing address")
            return redirect("products:checkout")


@login_required
def product_detail_view(request, id):
    obj = get_object_or_404(Item, id=id)
    context = {
        'object': obj
    }
    return render(request, "products/products_detail.html", context)


@login_required
def add_to_cart(request, id):
    item = get_object_or_404(Item, id=id)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # checking if the order item is in the order
        if order.items.filter(item__id=item.id).exists():
            order_item.quantity += 1
            order_item.save()
            messages.success(request, "this item quantity was updated.")
            return redirect("products:order-summary")
        else:
            order.items.add(order_item)
            messages.success(request, "this item was added to your cart.")
        return redirect("products:product-list")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.success(request, "this item was added to your cart.")
    return redirect("products:product-list")


class PaymentView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order
            }
            return render(self.request, 'products/payment.html', context)
        else:
            messages.warning(self.request, "fill you billing address")
            return redirect("products:checkout")


@csrf_exempt
def PaymentHookView(request, *args, **kwargs):
    if request.is_ajax and request.method == "POST":
        data = request.POST
        amount_paid = data['amount']
        # cus_email = request.POST.get(data['email'])
        # print(cus_email)
        trans_ref = data['flw_ref']
        # trans_status = data['status']
        print(data)
        # if trans_status == ['successful']:
        order = Order.objects.get(user=request.user, ordered=False)
        payment = Payment()
        payment.payment_charge_id = trans_ref
        payment.user = request.user
        payment.amount = amount_paid
        payment.save()
        print(payment)
        order_items = order.items.all()
        order_items.update(ordered=True)
        for item in order_items:
            item.save()
        order.ordered = True
        order.payment = payment
        order.ref_code = create_ref_code()
        order.save()
        messages.success(request, "your payment was received successful .")
        return HttpResponse()


def remove_from_cart(request, id):
    item = get_object_or_404(Item, id=id)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__id=item.id).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]

            order.items.remove(order_item)
            messages.success(request, "this item was removed from your cart.")
            return redirect("products:order-summary")
        else:
            messages.success(request, "this item was not in your cart.")
            # add a message saying the order does not contain the item
            return redirect("products:product-list")
    else:
        # add a message saying the user doesnt have an order
        messages.success(request, "you do not have an active order.")
        return redirect("products:product-list")


def remove_single_item_from_cart(request, id):
    item = get_object_or_404(Item, id=id)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__id=item.id).exists():
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
            messages.success(request, "this item was removed from your cart.")
            return redirect("products:order-summary")
        else:
            messages.success(request, "this item was not in your cart.")
            # add a message saying the order does not contain the item
            return redirect("products:product-list")
    else:
        # add a message saying the user doesnt have an order
        messages.success(request, "you do not have an active order.")
        return redirect("products:product-list")


def admin_dashboard_view(request):
    item = Item.objects.all()
    context = {
        'object': item,
    }
    return render(request, 'products/admin-dashboard.html', context)
