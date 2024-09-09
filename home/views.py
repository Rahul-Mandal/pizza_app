from django.shortcuts import render, redirect
from .models import *
# Create your views here.
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.decorators import login_required
from instamojo_wrapper import Instamojo

api = Instamojo(api_key=settings.API_KEY,
auth_token=settings.AUTH_TOKEN, endpoint='https://test.instamojo.com/api/1.1/')

def home(request):
    print(request.user)
    pizza_obj = Pizza.objects.all()
    context = {'pizzas': pizza_obj}
    print(context)
    return render(request, 'home.html', context)

def register_page(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')

            user_obj = User.objects.filter(username=username)

            if user_obj.exists():
                messages.error(request, 'Username already exists')
                return redirect('/register')
            user_obj = User.objects.create(username=username)
            user_obj.set_password(password)
            user_obj.save()

            messages.success(request, 'Account created')
            return redirect('/login')
        except Exception as e:
            messages.error(request, 'Something went wrong')
            return redirect('/register')
    return render(request, 'register.html')

def login_page(request):
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')

            user_obj = User.objects.filter(username=username)
            print(user_obj)
            if not user_obj:
                messages.warning(request, 'User not found')
                return redirect('/login')
            
            user_obj = authenticate(username = username, password=password)

            if user_obj:
                login(request, user_obj)
                return redirect('/')
            messages.warning(request, 'wrong password')
            return redirect('/login')
        except Exception as e:
            messages.warning(request, 'Something went wrong')
            return redirect('/login')
        
    return render(request, 'login.html')

@login_required(login_url='/login')
def add_cart(request, pizza_uid):
    user = request.user
    pizza_obj = Pizza.objects.get(uid = pizza_uid)
    cart, _ = Cart.objects.get_or_create(user=user, is_paid = False)
    cart_items = CartItems.objects.create(
        cart = cart,
        pizza = pizza_obj
    )
    if cart_items:
        messages.success(request, 'successfully added to cart')
        return redirect('/')


def cart(request):
    cart = Cart.objects.get(is_paid = False, user = request.user)
    # for i in cart.cart_item.all():
    #     print(i)
    #     print(i.pizza)
    response = api.payment_request_create(
        amount = cart.get_cart_total(),
        purpose = "Order",
        buyer_name = request.user.username,
        email = 'rahulmandal@gmail.com',
        redirect_url = "http://127.0.0.1:8000/success/"
    )
    cart.instamojo_id = response['payment_request']['id']
    cart.save()
    context = {'carts':cart, 'payment_url':response['payment_request']['longurl']}
    print(response)
    # print(context)
    return render(request, 'cart.html', context)


def remove_cart_item(request, cart_item_uid):
    try:
        CartItems.objects.get(uid = cart_item_uid).delete()
        return redirect('/cart')
    except Exception as e:
        print(e)

def orders(request):
    try:
        cart_obj = Cart.objects.filter(is_paid = True, user = request.user)
        context = {'orders':cart_obj}
    except Exception as e:
        print(e)
    return render(request, 'order.html', context)

def success(request):
    payment_request = request.GET.get('payment_request_id')
    cart = Cart.objects.get(instamojo_id = payment_request)
    cart.is_paid = True
    cart.save()
    return redirect('/orders/')