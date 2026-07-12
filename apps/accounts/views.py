from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm, ProfileForm
from .models import User


def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to BandBunk, {user.username}! 🤘")
            return redirect('accounts:profile_edit')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', '/')
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect(next_url)
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out. See you after the next gig. 🎸")
    return redirect('core:home')


@login_required
def dashboard_view(request):
    from apps.bookings.models import Booking
    from apps.listings.models import Listing

    context = {
        'listings': Listing.objects.filter(host=request.user)[:5] if request.user.is_host() else [],
        'bookings_as_artist': Booking.objects.filter(artist=request.user).select_related('listing')[:5],
        'bookings_as_host': Booking.objects.filter(listing__host=request.user).select_related('listing', 'artist')[:5] if request.user.is_host() else [],
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect('accounts:dashboard')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/profile_edit.html', {'form': form})


def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    from apps.reviews.models import Review
    host_reviews   = Review.objects.filter(reviewed_user=profile_user, review_type='host', is_public=True).select_related('reviewer')[:10]
    artist_reviews = Review.objects.filter(reviewed_user=profile_user, review_type='artist', is_public=True).select_related('reviewer')[:10]
    return render(request, 'accounts/profile.html', {
        'profile_user': profile_user,
        'host_reviews': host_reviews,
        'artist_reviews': artist_reviews,
    })
