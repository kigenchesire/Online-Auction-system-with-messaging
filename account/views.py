from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserEditForm, ProfileEditForm, TermsForm
from .models import Profile
from orders.models import Order, OrderNotification, OrderDetails
from payment.models import Balance
from catalog.models import Feedback, Bidders




def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        terms_form = TermsForm(request.POST)
        if user_form.is_valid() and terms_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(user_form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            terms_form.save()
            # Create the user profile
            profile = Profile.objects.create(user=new_user)
            feedback = Feedback.objects.create(user=new_user)
            return render(request,
                          'account/register_done.html',
                          {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
        terms_form = TermsForm()
    return render(request, 'account/register.html', {'user_form': user_form, 'terms_form': terms_form})


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                                     data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile,
                                       data=request.POST,
                                       files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request, 'account/edit.html', {'user_form': user_form,
                                                 'profile_form': profile_form})


@login_required
def dashboard(request):
    orders = Order.objects.filter(user=request.user).order_by('order')
    recent_order = OrderDetails.objects.filter(details__user=request.user, active=True).distinct()
    order_notifications = OrderNotification.objects.filter(user=request.user, active=True, read=False)
    read_notifications = OrderNotification.objects.filter(user=request.user, active=True)
    notification_count = order_notifications.count()
    balances = Balance.objects.filter(user=request.user)
    bidder = Bidders.objects.filter(user=request.user, won=True)
    return render(request, 'account/dashboard.html', {'orders': orders,
                                                      'order_notifications': order_notifications,
                                                      'notification_count': notification_count,
                                                      'read_notifications': read_notifications,
                                                      'recent_order': recent_order,
                                                      'balances': balances,
                                                      'bidder': bidder})


@login_required
def cancel_order(request, order_id):
    current_order = get_object_or_404(OrderDetails, id=order_id)
    current_order.active = False
    current_order.save()
    return render(request, 'account/cancel_done.html')


@login_required
def clear_order(request, order_id):
    current_order = get_object_or_404(OrderDetails, id=order_id)
    current_order.active = False
    current_order.save()
    return redirect('account:dashboard')




