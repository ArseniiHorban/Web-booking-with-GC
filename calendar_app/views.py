from django.shortcuts import render
from .forms import BookingForm
from datetime import datetime
from .utils.google_calendar_utils import create_or_update_event
from .utils.slots import get_available_intervals

def create_booking(request):
    # Get available time intervals for the current and upcoming days
    slots = get_available_intervals()

    if request.method == 'POST':
        print("POST request received", request.POST)

        # Bind the form with POST data
        form = BookingForm(request.POST)

        if form.is_valid():
            # Save form without committing to DB yet
            booking = form.save(commit=False)

            # Prepend phone number with +380 (Ukraine format)
            booking.phone = '+380' + str(booking.phone)

            # Parse submitted date and time strings into Python objects
            booking.date = datetime.strptime(form.cleaned_data['date'], "%Y-%m-%d").date()
            booking.time = datetime.strptime(form.cleaned_data['time'], "%H:%M").time()

            # Save the booking to the database
            booking.save()
            
            # Create or update corresponding event in Google Calendar
            event_id = create_or_update_event(booking)

            # Save the event ID returned from Google into the booking
            if event_id:
                booking.google_event_id = event_id
                booking.save(update_fields=["google_event_id"])

            # Render success page after successful booking
            return render(request, 'calendar_app/booking_success.html')
        else:
            # If form is invalid, print errors to console for debugging
            print("Form is invalid", form.errors)
    else:
        # If GET request, render an empty form
        form = BookingForm()

    # Render the booking form template with the form and available slots
    return render(request, 'calendar_app/booking_form.html', {'form': form, 'slots': slots})
