from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Booking
from .forms import BookingRequestForm, HostResponseForm
from apps.listings.models import Listing
import decimal
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def request_booking_view(request, listing_pk):
    listing = get_object_or_404(Listing, pk=listing_pk, is_active=True)
    if listing.host == request.user:
        messages.error(request, "You cannot book your own listing.")
        return redirect('listings:detail', pk=listing_pk)
    if not request.user.is_artist():
        messages.error(request, "Only artists can make booking requests. Update your profile.")
        return redirect('accounts:profile_edit')

    if request.method == 'POST':
        form = BookingRequestForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.listing = listing
            booking.artist  = request.user
            nights = (booking.check_out - booking.check_in).days
            booking.total_price = decimal.Decimal(nights) * listing.price_per_night
            booking.save()

            # Notify host by email
            try:
                send_mail(
                    subject=f"[BandBunk] New booking request from {booking.band_name}",
                    message=(
                        f"Hi {listing.host.first_name or listing.host.username},\n\n"
                        f"{booking.band_name} has requested to stay at your listing '{listing.title}'.\n"
                        f"Dates: {booking.check_in} → {booking.check_out} ({nights} night{'s' if nights > 1 else ''})\n"
                        f"Venue: {booking.venue_name}, {booking.venue_address}\n"
                        f"Gig date: {booking.gig_date}\n\n"
                        f"Log in to approve or decline: {request.build_absolute_uri('/bookings/host/')}\n\n"
                        f"Keep it loud,\nBandBunk 🤘"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[listing.host.email],
                    fail_silently=True,
                )
            except Exception:
                pass

            messages.success(request, f"Booking request sent to {listing.host.username}! They'll be in touch. 🎸")
            return redirect('bookings:my_bookings')
    else:
        form = BookingRequestForm()

    return render(request, 'bookings/request.html', {
        'listing': listing,
        'form': form,
    })


@login_required
def my_bookings_view(request):
    as_artist = Booking.objects.filter(artist=request.user).select_related('listing', 'listing__host').order_by('-created_at')
    as_host   = Booking.objects.filter(listing__host=request.user).select_related('listing', 'artist').order_by('-created_at') if request.user.is_host() else []
    return render(request, 'bookings/my_bookings.html', {
        'bookings_as_artist': as_artist,
        'bookings_as_host': as_host,
    })


@login_required
def booking_detail_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if booking.artist != request.user and booking.listing.host != request.user:
        messages.error(request, "You don't have access to this booking.")
        return redirect('bookings:my_bookings')
    return render(request, 'bookings/detail.html', {'booking': booking})


@login_required
def host_respond_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk, listing__host=request.user, status='pending')

    action = request.POST.get('action')
    if action == 'confirm':
        booking.confirm()
        booking.host_response = request.POST.get('host_response', '')
        booking.host_responded_at = timezone.now()
        booking.save()
        # Email artist
        send_mail(
            subject=f"[BandBunk] Your booking at '{booking.listing.title}' is CONFIRMED 🤘",
            message=(
                f"Hi {booking.artist.first_name or booking.artist.username},\n\n"
                f"Great news — {booking.listing.host.username} has confirmed your stay!\n"
                f"Address: {booking.listing.address_line1}, {booking.listing.town_city}, {booking.listing.postcode}\n"
                f"Dates: {booking.check_in} → {booking.check_out}\n"
                f"Total: £{booking.total_price}\n\n"
                f"{booking.host_response}\n\n"
                f"Have a killer gig,\nBandBunk 🎸"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.artist.email],
            fail_silently=True,
        )
        messages.success(request, f"Booking confirmed for {booking.band_name}!")
    elif action == 'decline':
        booking.decline()
        booking.host_response = request.POST.get('host_response', '')
        booking.save()
        messages.info(request, f"Booking declined.")

    return redirect('bookings:my_bookings')


@login_required
def cancel_booking_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk, artist=request.user, status__in=('pending', 'confirmed'))
    booking.status = 'cancelled'
    booking.save()
    messages.info(request, "Booking cancelled.")
    return redirect('bookings:my_bookings')


@login_required
def mark_complete_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk, listing__host=request.user, status='confirmed')
    booking.complete()
    messages.success(request, "Stay marked as complete. Don't forget to leave a review!")
    return redirect('bookings:my_bookings')


# ---------------------------------------------------------------------------
# Stripe payment
# ---------------------------------------------------------------------------

@login_required
def create_checkout_session_view(request, pk):
    """Artist pays for a confirmed booking via Stripe Checkout."""
    booking = get_object_or_404(
        Booking, pk=pk, artist=request.user, status='confirmed', payment_status__in=('unpaid', 'failed')
    )

    session = stripe.checkout.Session.create(
        mode='payment',
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'gbp',
                'unit_amount': int(booking.total_price * 100),  # pence
                'product_data': {
                    'name': f"BandBunk stay — {booking.listing.title}",
                    'description': f"{booking.check_in} → {booking.check_out} ({booking.num_nights} night{'s' if booking.num_nights != 1 else ''})",
                },
            },
            'quantity': 1,
        }],
        customer_email=request.user.email or None,
        client_reference_id=str(booking.pk),
        metadata={'booking_id': str(booking.pk)},
        success_url=request.build_absolute_uri(reverse('bookings:payment_success')) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri(reverse('bookings:payment_cancelled', args=[booking.pk])),
    )

    booking.stripe_payment_intent_id = session.id
    booking.payment_status = 'processing'
    booking.save()

    return redirect(session.url, permanent=False)


@login_required
def payment_success_view(request):
    session_id = request.GET.get('session_id')
    booking = None

    if session_id:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            booking_id = session.metadata.get('booking_id') if session.metadata else None
            if booking_id:
                booking = get_object_or_404(Booking, pk=booking_id, artist=request.user)
                if session.payment_status == 'paid' and booking.payment_status != 'paid':
                    booking.payment_status = 'paid'
                    booking.stripe_charge_id = session.payment_intent or ''
                    booking.save()
                    messages.success(request, f"Payment received — you're all set for {booking.band_name}! 🎸")
        except stripe.error.StripeError:
            messages.warning(request, "We couldn't confirm your payment automatically — check My Bookings shortly.")

    return render(request, 'bookings/payment_success.html', {'booking': booking})


@login_required
def payment_cancelled_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk, artist=request.user)
    if booking.payment_status == 'processing':
        booking.payment_status = 'unpaid'
        booking.save()
    messages.info(request, "Payment cancelled — no charge was made. You can try again any time.")
    return redirect('bookings:detail', pk=booking.pk)


@csrf_exempt
@require_POST
def stripe_webhook_view(request):
    """Stripe calls this to confirm payment server-side, independent of the browser redirect."""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponseBadRequest("Invalid Stripe webhook payload/signature")

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        booking_id = (session.get('metadata') or {}).get('booking_id')
        if booking_id:
            try:
                booking = Booking.objects.get(pk=booking_id)
                if session.get('payment_status') == 'paid' and booking.payment_status != 'paid':
                    booking.payment_status = 'paid'
                    booking.stripe_charge_id = session.get('payment_intent') or ''
                    booking.save()
            except Booking.DoesNotExist:
                pass

    return HttpResponse(status=200)
