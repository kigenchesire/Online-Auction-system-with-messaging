import pytz
from datetime import datetime, timedelta, date
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Review,  BidItems, Bidders
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from .forms import ReviewForm, FeedbackForm, BiddersForm
from django.contrib import messages
from cart.forms import CartAddProductForm
from django.contrib.auth.decorators import login_required
from django.db.models import Max
import requests
from account.models import Profile
from django.utils import timezone


def product_list(request, category_slug=None):
    category = None
    bidders = Bidders.objects.all()
    checker = False
    today = date.today().strftime("%A")
    utc = pytz.UTC

    now_time = timezone.now()

    print(now_time)
    bidItems = BidItems.objects.all()

    men = Category.objects.get(name='Men')
    women = Category.objects.get(name='Women')
    shoes = Category.objects.get(name='Shoes')
    jewelry = Category.objects.get(name='Jewelry')
    phones = Category.objects.get(name='Phones')
    laptops = Category.objects.get(name='Laptops')
    home_appliances = Category.objects.get(name='Home Appliances')
    play_station = Category.objects.get(name='Play Station')
    others = Category.objects.get(name='Others')
    furniture = Category.objects.get(name='Furniture')
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    paginator = Paginator(products, 12)

    page = None

    try:
        page = request.GET.get('page')
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    except:
        pass

    return render(request, 'catalog/list.html', {
        # # 'category': category,
                                                 'categories': categories,
                                                 'page': page,
                                                 'checker': checker,
                                                 'bidItems': bidItems,
                                                 'products': products,
                                                 'men': men,
                                                 'women': women,
                                                 'shoes': shoes,
                                                 'jewelry': jewelry,
                                                 'phones': phones,
                                                 'laptops': laptops,
                                                 'home_appliances': home_appliances,
                                                 'play_station': play_station,
                                                 'furniture': furniture,
                                                 'others': others,
                                                 'today': today,
                                                 'now': now_time
                                                 })


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug)
    reviews = product.reviews.filter(active=True)

    review_count = product.reviews.count()

    paginator = Paginator(reviews, 3)
    page = request.GET.get('page')
    try:
        reviews = paginator.page(page)
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)

    cart_product_form = CartAddProductForm()
    return render(request,
                  'catalog/detail.html',
                  {'product': product,
                   'reviews': reviews,
                   'review_count': review_count,
                   'cart_product_form': cart_product_form})

@login_required
def bid_detail(request, id):
    bidItem = get_object_or_404(BidItems, id=id)

    now = timezone.now()
    bid_end = bidItem.end_date

    bidder = Bidders.objects.filter(bidItem=bidItem, active=True).aggregate(Max('amount'))

        


    bids = bidItem.biditems.filter(active=True)
    if request.method == 'POST':
        bid_form = BiddersForm(data=request.POST)

        if bid_form.is_valid():
            if bid_form.cleaned_data['amount'] <= bidItem.minimum_price:
                messages.error(request, 'Your amount is less than the minimum bid amount required')
                return redirect('catalog:bid_detail', bidItem.id)
            new_bid_form = bid_form.save(commit=False)
            new_bid_form.bidItem = bidItem
            new_bid_form.user = request.user
            new_bid_form.save()

            if bid_form.cleaned_data['amount'] > bidItem.minimum_price:
                bidItem.minimum_price = bid_form.cleaned_data['amount']
                
                # send text to the auctioneer
                auctioneer_phonenumber = bidItem.actioneer_phonenumber
                auctioneer_name = bidItem.auctioneer

                message = f"Dear {auctioneer_name}, {request.user.username} has placed a bid of {bid_form.cleaned_data['amount']}."

                api_url = 'https://api.mobitechtechnologies.com/sms/sendsms'

                headers = {"Content-Type": "application/json", "h_api_key":"6bb06b8724fcbd880285addf6d22b9b41139f7fd4f5f5ea0318404035afcc44c"}

                request = {
                        "mobile": auctioneer_phonenumber,
                        "response_type": "json",
                        "sender_name": "23107",
                        "service_id": 0,
                        "message": message
                        }

                response = requests.post(api_url,json=request,headers=headers)

                print(response.content)

                bidItem.save()
            return redirect('catalog:bid_detail', bidItem.id)
    else:
        bid_form = BiddersForm()
    bid_count = bidItem.biditems.count()
    return render(request,
                  'catalog/bid.html',
                  {'bidItem': bidItem,
                   'bid_count': bid_count,
                   'bids': bids,
                   'bid_form': bid_form})



def confirm_bid_winner(request, id):
    bidItem = get_object_or_404(BidItems, id=id)

    now = timezone.now()
    bid_end = bidItem.end_date

    bidder = Bidders.objects.filter(bidItem=bidItem, active=True).aggregate(Max('amount'))
    if now > bid_end:
        # send sms to the winner
            if bidder.get('amount__max') is not None:
                bidder_obj = Bidders.objects.get(amount=bidder.get('amount__max'))
                winner_phone_number = Profile.objects.get(user=bidder_obj.user).phone_number

                winner_name = bidder_obj.user.username
                bid_item = bidder_obj.bidItem
                bid_amount = bidder_obj.amount

                message = f"Dear {winner_name}, Congratulations! You have won the bid {bid_item}. You are required to pay {bid_amount} to collect your item."

                api_url = 'https://api.mobitechtechnologies.com/sms/sendsms'

                headers = {"Content-Type": "application/json", "h_api_key":"6bb06b8724fcbd880285addf6d22b9b41139f7fd4f5f5ea0318404035afcc44c"}

                request_body = {
                        "mobile": winner_phone_number,
                        "response_type": "json",
                        "sender_name": "23107",
                        "service_id": 0,
                        "message": message
                        }

                response = requests.post(api_url,json=request_body,headers=headers) 
                print(response.content) 
                bidder_obj.won = True
                bidder_obj.active = False
                bidder_obj.save()

                bidItem.available = False
                bidItem.save()
                messages.success(request, f"The winner of the bid is {bidder_obj.user.username}")
                return redirect('catalog:product_list')
            else:
                messages.error(request, "No Winner! This bid ended without a single placed bid")
                return redirect('catalog:product_list')


    else:
        messages.error(request, "Error confirming winner")
        return redirect('catalog:product_list')





@login_required
def product_review(request, id):
    product = get_object_or_404(Product, id=id, available=True)
    reviews = product.reviews.filter(active=True)

    if request.method == 'POST':
        review_form = ReviewForm(data=request.POST)

        if review_form.is_valid():
            new_review_form = review_form.save(commit=False)
            new_review_form.product = product
            new_review_form.user = request.user
            new_review_form.save()
            messages.success(request, 'Your review has successfully been submitted')
    else:
        review_form = ReviewForm()

    review_count = product.reviews.count()

    cart_product_form = CartAddProductForm()

    return render(request,
                  'catalog/review.html',
                  {'product': product,
                   'reviews': reviews,
                   'review_form': review_form,
                   'review_count': review_count,
                   'cart_product_form': cart_product_form})


def help_center(request):
    return render(request, 'catalog/help.html')


def returns_policy(request):
    return render(request, 'catalog/returns.html')


def secure_payment(request):
    return render(request, 'catalog/payment.html')


def responsibility(request):
    return render(request, 'catalog/responsibility.html')


def privacy(request):
    return render(request, 'catalog/privacy.html')


def delivery(request):
    return render(request, 'catalog/delivery.html')


def careers(request):
    return render(request, 'catalog/career.html')


def conditions(request):
    return render(request, 'catalog/conditions.html')


def contact(request):
    return render(request, 'catalog/contact.html')


def feedback(request):
    if request.method == 'POST':
        feedback_form = FeedbackForm(request.POST, instance=request.user.feedback)
        if feedback_form.is_valid():
            feedback_form.save()
            messages.success(request, 'Thank you! Your feedback has successfully been received')
    else:
        feedback_form = FeedbackForm(instance=request.user.feedback)
    return render(request, 'catalog/feedback.html', {'feedback_form': feedback_form})





