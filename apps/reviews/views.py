from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from .forms import ReviewForm
from apps.bookings.models import Booking


@login_required
def leave_review_view(request, booking_pk, review_type):
    booking = get_object_or_404(Booking, pk=booking_pk)

    if not booking.can_be_reviewed_by(request.user):
        messages.error(request, "You can't leave a review for this booking.")
        return redirect('bookings:my_bookings')

    if review_type == 'host' and request.user != booking.artist:
        messages.error(request, "Only the artist can review the host.")
        return redirect('bookings:my_bookings')
    if review_type == 'artist' and request.user != booking.listing.host:
        messages.error(request, "Only the host can review the artist.")
        return redirect('bookings:my_bookings')

    reviewed_user = booking.listing.host if review_type == 'host' else booking.artist

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking       = booking
            review.reviewer      = request.user
            review.reviewed_user = reviewed_user
            review.review_type   = review_type
            review.save()
            messages.success(request, "Review submitted. Thanks for keeping the community honest! 🤘")
            return redirect('bookings:my_bookings')
    else:
        form = ReviewForm()

    return render(request, 'reviews/leave_review.html', {
        'form': form,
        'booking': booking,
        'review_type': review_type,
        'reviewed_user': reviewed_user,
    })
