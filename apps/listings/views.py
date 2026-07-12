from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Listing, ListingPhoto
from .forms import ListingForm, ListingPhotoForm, ListingSearchForm
import json


def browse_view(request):
    form = ListingSearchForm(request.GET)
    listings = Listing.objects.filter(is_active=True).select_related('host').prefetch_related('photos')

    if form.is_valid():
        q = form.cleaned_data.get('q')
        ltype = form.cleaned_data.get('type')
        max_price = form.cleaned_data.get('max_price')
        if q:
            listings = listings.filter(Q(town_city__icontains=q) | Q(postcode__icontains=q))
        if ltype:
            listings = listings.filter(listing_type=ltype)
        if max_price:
            listings = listings.filter(price_per_night__lte=max_price)

    return render(request, 'listings/browse.html', {
        'listings': listings,
        'form': form,
        'count': listings.count(),
    })


def listing_detail_view(request, pk):
    listing = get_object_or_404(Listing, pk=pk, is_active=True)
    from apps.reviews.models import Review
    reviews = Review.objects.filter(
        booking__listing=listing, review_type='host', is_public=True
    ).select_related('reviewer')[:10]
    return render(request, 'listings/detail.html', {
        'listing': listing,
        'reviews': reviews,
    })


def map_view(request):
    listings = Listing.objects.filter(is_active=True, latitude__isnull=False).select_related('host')
    listings_json = json.dumps([{
        'id': l.pk,
        'title': l.title,
        'lat': float(l.latitude),
        'lng': float(l.longitude),
        'price': str(l.price_per_night),
        'type_display': l.get_listing_type_display(),
        'town_city': l.town_city,
    } for l in listings])
    return render(request, 'listings/map.html', {'listings_json': listings_json})


@login_required
def create_listing_view(request):
    if not request.user.is_host():
        messages.error(request, "You need a host account to post a listing.")
        return redirect('accounts:profile_edit')
    if request.method == 'POST':
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.host = request.user
            listing.save()
            # Handle photos
            for img in request.FILES.getlist('photos'):
                ListingPhoto.objects.create(listing=listing, image=img)
            messages.success(request, "Listing created! Bands can now find your bunk. 🛋️")
            return redirect('listings:detail', pk=listing.pk)
    else:
        form = ListingForm()
    return render(request, 'listings/create.html', {'form': form})


@login_required
def edit_listing_view(request, pk):
    listing = get_object_or_404(Listing, pk=pk, host=request.user)
    if request.method == 'POST':
        form = ListingForm(request.POST, instance=listing)
        if form.is_valid():
            form.save()
            for img in request.FILES.getlist('photos'):
                ListingPhoto.objects.create(listing=listing, image=img)
            messages.success(request, "Listing updated.")
            return redirect('listings:detail', pk=listing.pk)
    else:
        form = ListingForm(instance=listing)
    return render(request, 'listings/edit.html', {'form': form, 'listing': listing})


@login_required
def my_listings_view(request):
    listings = Listing.objects.filter(host=request.user).prefetch_related('photos')
    return render(request, 'listings/my_listings.html', {'listings': listings})


@login_required
def toggle_listing_view(request, pk):
    listing = get_object_or_404(Listing, pk=pk, host=request.user)
    listing.is_active = not listing.is_active
    listing.save()
    state = "activated" if listing.is_active else "deactivated"
    messages.success(request, f"Listing {state}.")
    return redirect('listings:my_listings')
