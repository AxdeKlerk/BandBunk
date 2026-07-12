from django.shortcuts import render
from apps.listings.models import Listing
from apps.accounts.models import User


def home_view(request):
    featured = Listing.objects.filter(is_active=True).select_related('host').prefetch_related('photos')[:6]
    host_count   = User.objects.filter(user_type__in=('host', 'both')).count()
    artist_count = User.objects.filter(user_type__in=('artist', 'both')).count()
    listing_count = Listing.objects.filter(is_active=True).count()
    return render(request, 'core/home.html', {
        'featured': featured,
        'host_count': host_count,
        'artist_count': artist_count,
        'listing_count': listing_count,
    })


def about_view(request):
    return render(request, 'core/about.html')


def how_it_works_view(request):
    return render(request, 'core/how_it_works.html')


def safety_view(request):
    return render(request, 'core/safety.html')


def contact_view(request):
    return render(request, 'core/contact.html')


def privacy_view(request):
    return render(request, 'core/privacy.html')


def terms_view(request):
    return render(request, 'core/terms.html')
