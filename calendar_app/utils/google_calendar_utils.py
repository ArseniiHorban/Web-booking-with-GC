from datetime import datetime, timedelta
from calendar_app.models import Booking
from calendar_auth import authenticate_google

# Connect to Google Calendar API
service = authenticate_google()

TIME_ZONE = "Europe/Kyiv"


def build_event_from_booking(booking: Booking):
    """
    Creates a Google Calendar event structure from a Booking object.
    """
    start_datetime = datetime.combine(booking.date, booking.time)
    end_datetime = start_datetime + timedelta(minutes=60)

    description = (
        f"Masterclass\n"
        f"Phone: {booking.phone}\n"
    )

    return {
        'summary': f'Booking from {booking.name}',
        'description': description,
        'start': {
            'dateTime': start_datetime.isoformat(),
            'timeZone': TIME_ZONE,
        },
        'end': {
            'dateTime': end_datetime.isoformat(),
            'timeZone': TIME_ZONE,
        },
        'colorId': '5',
    }

def build_booking_from_event(event) -> dict:
    """
    Converts a Google Calendar event object into a dictionary suitable for creating/updating a Booking.
    """
    try:
        start = event['start']['dateTime']
        summary = event.get('summary', '')
        description = event.get('description', '')

        start_dt = datetime.fromisoformat(start)
        date = start_dt.date()
        time = start_dt.time()

        # Extract phone number from description
        phone = ''
        lines = description.split('\n')
        for line in lines:
            if line.startswith("Phone: "):
                phone = line.replace("Phone:", "").strip()

        name = summary.replace("Booking from ", "").strip()

        return {
            'name': name,
            'date': date,
            'time': time,
            'phone': phone,
            'google_event_id': event['id'],
        }
    except Exception as e:
        print(f"[build_booking_from_event] Error: {e}")
        return {}

def create_or_update_event(booking: Booking):
    """
    Creates or updates an event in Google Calendar.
    """
    event_data = build_event_from_booking(booking)

    if booking.google_event_id:
        try:
            updated_event = service.events().update(
                calendarId='primary',
                eventId=booking.google_event_id,
                body=event_data
            ).execute()
            return updated_event['id']
        except Exception as e:
            print("Failed to update event:", e)
    else:
        try:
            created_event = service.events().insert(
                calendarId='primary',
                body=event_data
            ).execute()
            return created_event['id']
        except Exception as e:
            print("Failed to create event:", e)


def delete_event(google_event_id):
    """
    Deletes an event in Google Calendar by its ID.
    """
    try:
        service.events().delete(calendarId='primary', eventId=google_event_id).execute()
        print(f"Deleted event from Google Calendar: {google_event_id}")
    except Exception as e:
        print("Error while deleting event:", e)
