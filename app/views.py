from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View
from .models import Customer, Product, Cart, OrderPlaced
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from instamojo_wrapper import Instamojo
from os import getenv
from dotenv import load_dotenv
load_dotenv()
API_KEY = getenv('API_KEY')
AUTH_TOKEN = getenv('AUTH_TOKEN')



class ProductView(View):
    def get(self, request):
 
        topwears = Product.objects.filter(category='TW')
        bottomwears = Product.objects.filter(category='BW')
        mobiles = Product.objects.filter(category='M')
        

        return render(request, 'app/home.html', {'topwears':topwears,
                                                'bottomwears':bottomwears,
                                                'mobiles':mobiles, 
                                                })


class ProductDetailView(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        item_already_in_cart = False
        if request.user.is_authenticated:
            item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()
        return render(request, 'app/productdetail.html', {'product':product, 
                                                        'item_already_in_cart':item_already_in_cart })


@method_decorator(login_required, name='dispatch')
class AddtoCartView(View):
    def get(self, request):
        user=request.user
        prod_id = request.GET.get("prod_id")
        product = Product.objects.get(id=prod_id)
        Cart.objects.get_or_create(user=user, product=product)  # saving products to cart
        return redirect('/cart')

@method_decorator(login_required, name='dispatch')
class ShowCartView(View):
    def get(self, request):
        if request.user.is_authenticated:
            usr=request.user
            cart = Cart.objects.filter(user=usr)
            amount = 0.0
            shipping_amount = 70.0
            cart_product = [p for p in Cart.objects.all() if p.user==usr]
            if cart_product:
                for p in cart_product:
                    net_amount = (p.quantity * p.product.discounted_price)
                    amount+= net_amount
                    total_amount = amount + shipping_amount
                return render(request, 'app/addtocart.html', {'carts':cart, 'total_amount':total_amount, 'amount':amount})
            return render(request, 'app/emptycart.html')

@login_required
def adding_quantity(request):
    if request.method =="GET":
        #Adding product quantity
        if request.GET.get('prod_plus_id'):
            prod_id = request.GET['prod_plus_id']
            c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
            c.quantity+=1
        #lessen product quantity
        elif request.GET.get('prod_minus_id'):
            prod_id = request.GET['prod_minus_id']
            c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
            c.quantity-=1
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user==request.user]
      
        for p in cart_product:
            net_amount = (p.quantity * p.product.discounted_price)
            amount+= net_amount
          
        cart_data={
                'quantity':c.quantity,
                'amount' : amount,
                'totalamount':amount + shipping_amount
            }
        return JsonResponse(cart_data)

        
@login_required
def remove_cart(request):
    if request.method =="GET":
        prod_id = request.GET['prod_remove_id']
        try:
            c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
            c.delete()
        except Cart.DoesNotExist:
            c = None
            
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user==request.user]
      
        for p in cart_product:
            net_amount = (p.quantity * p.product.discounted_price)
            amount+= net_amount
            
        cart_data={
                'amount' : amount,
                'totalamount':amount + shipping_amount
            }
        return JsonResponse(cart_data)



@method_decorator(login_required, name='dispatch')
class OrdersView(View):
    def get(self, request):
        order_id = request.GET.get('order_id')
        if order_id:
            orders = OrderPlaced.objects.filter(user=request.user, order_id=order_id, is_paid=False)
            for _ in orders:
                _.delete()
            return JsonResponse({'status':'deleted'})
        orders = OrderPlaced.objects.filter(user=request.user)
        return render(request, 'app/orders.html',{'orders':orders})



def search_products(request):
    searched_prods = request.GET.get('search_query')
    all_products = Product.objects.filter(Q(brand__icontains=searched_prods) | Q(title__icontains=searched_prods) | Q(category__icontains=searched_prods))
    if all_products:
        return render(request, 'app/all_products.html', {'all_products':all_products})
    else:
        return render(request, 'app/all_products.html', {'no_product_exists':'No such product available!'})



def mobile(request, data=None):
    if data == None:
        mobiles = Product.objects.filter(category='M')
    elif data == 'Oppo' or data =='Vivo' or data =='Samsung' or data == 'MI':
        mobiles = Product.objects.filter(category='M').filter(brand__icontains=data)
    elif data == 'below':
        mobiles = Product.objects.filter(category='M').filter(discounted_price__lt=20000)
    elif data == 'above':
        mobiles = Product.objects.filter(category='M').filter(discounted_price__gt=20000)
    
    return render(request, 'app/mobile.html', {'mobiles':mobiles})

def bottomwear(request, data=None):
    if data == None:
        bottomwears = Product.objects.filter(category='BW')
    elif data =='Lee' or data =='Spykar' or data == 'Gucci' :
        bottomwears = Product.objects.filter(category='BW').filter(brand__icontains=data)
    elif data == 'below':
        bottomwears = Product.objects.filter(category='BW').filter(discounted_price__lt=300)
    elif data == 'above':
        bottomwears = Product.objects.filter(category='BW').filter(discounted_price__gt=300)
    
    return render(request, 'app/bottomwear.html', {'bottomwears':bottomwears})




class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm
        return render(request, 'app/customerregistration.html', {'form':form})
    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, 'You have successfully registered!')
            form.save()
            
        return render(request, 'app/customerregistration.html', {'form':form})

@method_decorator(login_required, name='dispatch')
class CheckoutView(View):
    def get(self,request):
        customer_details = Customer.objects.filter(user=request.user)
        cart_product = Cart.objects.filter(user=request.user)
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user==request.user]
        if cart_product:
            for p in cart_product:
                net_amount = (p.quantity * p.product.discounted_price)
                amount+= net_amount
            total_amount = amount + shipping_amount
            
        return render(request, 'app/checkout.html', {'customer_details':customer_details,
                                                     'totalamount':total_amount,
                                                     'amount':amount,
                                                     'cart_product':cart_product
                                                      })





api = Instamojo(api_key=API_KEY, auth_token=AUTH_TOKEN, endpoint='https://test.instamojo.com/api/1.1/')

@method_decorator(login_required, name='dispatch')
class PaymentDoneView(View):
    def get(self, request):
        usr = request.user
        #Calculating total amount
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user==usr]
        if cart_product:
            for p in cart_product:
                net_amount = (p.quantity * p.product.discounted_price)
                amount+= net_amount
            total_amount = amount + shipping_amount
            
        # Create a new Payment Request
        response = api.payment_request_create(
        amount=total_amount,
        purpose='Order_purpose',
        send_email=True,
        # buyer_name=usr,
        email="foo@example.com",
        redirect_url="http://127.0.0.1:8000/payment-success/"
        )
   
        order_id = response['payment_request']['id']
        prod_status = response['payment_request']['status']
        payment_url = response['payment_request']['longurl']
        
        custid = request.GET.get('custid')
        customer = Customer.objects.get(id=custid)
        cart = Cart.objects.filter(user=usr)
        for c in cart:
            orders, _ = OrderPlaced.objects.get_or_create(user=usr, customer=customer, product=c.product, 
                                    quantity=c.quantity, order_id=order_id,
                                     is_paid=False, status=prod_status)
            orders.save()
            # after order placing deleting the current cart
            c.delete()
        return JsonResponse({'payment_url':payment_url})
   


@login_required
def paymentSuccess(request):
    payment_req_id = request.GET.get('payment_request_id')
    order_obj = OrderPlaced.objects.filter(order_id=payment_req_id)
    for _ in order_obj:
        _.is_paid=True
        _.save()
    return render(request, 'app/payment_success.html')



@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(request, 'app/profile.html',{'form':form, 'active':'btn-warning'})
    
    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data.get('name')
            locality = form.cleaned_data.get('locality')
            city = form.cleaned_data.get('city')
            state = form.cleaned_data.get('state')
            zipcode = form.cleaned_data.get('zipcode')
            reg = Customer(user=usr, name=name, locality=locality, city=city, state=state, zipcode=zipcode)
            reg.save()
            messages.success(request, 'Profile has been updated!')
        return render(request, 'app/profile.html',{ 'form':form, 'active':'btn-warning'})


@method_decorator(login_required, name='dispatch')
class AddressView(View):
    def get(self,request):
        customer_details = Customer.objects.filter(user=request.user)
        return render(request, 'app/address.html', {'customer_details':customer_details, 'active':'btn-warning'})
