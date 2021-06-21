from django.test import TestCase

# Create your tests here.
@login_required
def add_to_cart(request, id):
    item = get_object_or_404(Images, id=id)
    order_item = OrderItem.objects.create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # checking if the order item is in the order
        if order.items.filter(item__id=item.id).exists():
            print('mee')
            messages.success(request, "you have already placed your supply.")
            return redirect("products:order-summary")
        else:
            ordered_date = timezone.now()
            order = Order.objects.create(user=request.user, ordered_date=ordered_date)
            order.items.add(order_item)
            messages.success(request, "your supply was successfully placed.")
        return redirect("products:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.success(request, "your supply was successfully placed.")
    return redirect("products:order-summary")


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


def remove_from_cart(request, id):
    item = get_object_or_404(Images, id=id)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__id=item.id).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            print('mee')
            order.items.remove(order_item)
            messages.success(request, "this item was removed from your supply.")
            return redirect("products:product-list")
        else:
            messages.success(request, "this item was not in your supply.")
            # add a message saying the order does not contain the item
            return redirect("products:product-list")
    else:
        # add a message saying the user doesnt have an order
        messages.success(request, "you do not have an active supply.")
        return redirect("products:product-list")



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
