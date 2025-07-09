from celery import shared_task
from calendar_auth import authenticate_google
from calendar_app.models import Booking
from django.utils import timezone
from datetime import datetime
import googleapiclient.errors
import logging
from .utils.google_calendar_utils import build_booking_from_event

logger = logging.getLogger(__name__)

@shared_task

def sync_calendar_to_db():
    """
    Synchronize events from Google Calendar into the Django database.
    Google Calendar is considered the source of truth.
    """
    logger.info("Starting synchronization with Google Calendar")

    #Authenticate with Google API
    try:
        service = authenticate_google()
    except Exception as e:
        logger.error(f"Google API authentication failed: {e}")
        return

    now = timezone.now().isoformat()

    #Fetch upcoming events from Google Calendar
    try:
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=100,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
    except googleapiclient.errors.HttpError as e:
        logger.error(f"Google Calendar API error while fetching events: {e}")
        return
    except Exception as e:
        logger.error(f"Unexpected error while fetching events: {e}")
        return

    all_events = events_result.get('items', [])

    #Filter events: only those with start dateTime and matching color ID
    valid_events = [
        e for e in all_events
        if e.get('start', {}).get('dateTime') and e.get('colorId') == '5'
    ]

    #Get existing bookings in the DB that match these Google event IDs
    existing_bookings = {
        b.google_event_id: b
        for b in Booking.objects.filter(google_event_id__in=[e['id'] for e in valid_events])
    }

    #Process each valid event from the calendar
    event_ids_from_calendar = set()

    for event in valid_events:
        event_id = event['id']
        event_ids_from_calendar.add(event_id)

        # Parse the calendar event into booking data dict
        booking_data = build_booking_from_event(event)

        if not booking_data:
            logger.warning(f"Skipped event {event_id} due to parsing error")
            continue

        try:
            existing_booking = existing_bookings.get(event_id)

            if existing_booking:
                # Compare fields and update if changes are detected
                has_changes = (
                        existing_booking.date != booking_data['date'] or
                        existing_booking.time != booking_data['time'] or
                        existing_booking.phone != booking_data['phone'] or
                        existing_booking.name != booking_data['name']
                )
                if has_changes:
                    for field, value in booking_data.items():
                        setattr(existing_booking, field, value)
                    existing_booking.save()
                    logger.info(f"Updated booking for event {event_id}")
            else:
                # Create a new booking if it doesn't exist in the DB
                Booking.objects.create(**booking_data)
                logger.info(f"Created new booking for event {event_id}")
        except Exception as e:
            logger.error(f"Error while processing event {event_id}: {e}")

    #Remove bookings from the DB that are no longer present in Google Calendar
    try:
        deleted_count, _ = Booking.objects.exclude(
            google_event_id__in=event_ids_from_calendar
        ).exclude(
            google_event_id__isnull=True
        ).delete()

        if deleted_count:
            logger.info(f"Deleted {deleted_count} outdated bookings from the database")
    except Exception as e:
        logger.error(f"Error while deleting outdated bookings: {e}")

    logger.info("Calendar synchronization completed successfully")