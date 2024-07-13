from django.shortcuts import render

# Create your views here.

from . models import ShippingAddress, Order, OrderItem

from cart.cart import Cart


from django.http import JsonResponse

from django.core.mail import send_mail

from django.conf import settings


def checkout(request):

    # Users with accounts -- Pre-fill the form

    if request.user.is_authenticated:

        try:

            # Authenticated users WITH shipping information 

            shipping_address = ShippingAddress.objects.get(user=request.user.id)

            context = {'shipping': shipping_address}

            


            return render(request, 'payment/checkout.html', context=context)


        except:

            # Authenticated users with NO shipping information

            return render(request, 'payment/checkout.html')

    else:
            
        # Guest users

        return render(request, 'payment/checkout.html')



def complete_order(request):

    if request.method == 'POST' and request.POST.get('action') == 'post':
        name = request.POST.get('name')
        email = request.POST.get('email')
        address1 = request.POST.get('address1')
        address2 = request.POST.get('address2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zipcode = request.POST.get('zipcode')

        shipping_address = ShippingAddress.objects.create(
            full_name=name,
            email=email,
            address1=address1,
            address2=address2,
            city=city,
            state=state,
            zipcode=zipcode
        )

        # Shopping cart information
        cart = Cart(request)
        total_cost = cart.get_total()

        if request.user.is_authenticated:
            order = Order.objects.create(
                full_name=name,
                email=email,
                shipping_address=shipping_address,  # Assign the ShippingAddress instance
                amount_paid=total_cost,
                user=request.user
            )
        else:
            order = Order.objects.create(
                full_name=name,
                email=email,
                shipping_address=shipping_address,  # Assign the ShippingAddress instance
                amount_paid=total_cost
            )

        # Create OrderItems
        order_id = order.pk
        for item in cart:
            OrderItem.objects.create(
                order_id=order_id,
                product=item['product'],
                quantity=item['qty'],
                price=item['price'],
                user=request.user if request.user.is_authenticated else None
            )


       

        order_success = True
        response = JsonResponse({'success': order_success})
        return response









def payment_success(request):


    # Clear shopping cart


    for key in list(request.session.keys()):

        if key == 'session_key':

            del request.session[key]



    return render(request, 'payment/payment-success.html')




def payment_failed(request):

    return render(request, 'payment/payment-failed.html')









