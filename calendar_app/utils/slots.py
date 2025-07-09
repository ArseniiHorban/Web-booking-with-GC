from datetime import datetime, timedelta, time
from calendar_app.models import Booking

def get_available_intervals(days_ahead=30, start_hour=10, end_hour=18):
    """
    Returns a dictionary with dates as keys and lists of available intervals (start, end)
    within which the user can choose a time to start a masterclass.
    """
    today = datetime.now().date()
    available = {}

    for i in range(days_ahead):
        date = today + timedelta(days=i)
        day_start = datetime.combine(date, time(start_hour, 0))
        day_end = datetime.combine(date, time(end_hour, 0))

        # Load all bookings for the day
        bookings = Booking.objects.filter(date=date).order_by('time')
        occupied = []

        for b in bookings:
            start = datetime.combine(b.date, b.time)
            end = start + timedelta(minutes=90)  # 1 hour + 30 min break
            occupied.append((start, end))

        # Build intervals between occupied slots
        free_intervals = []
        current = day_start

        for start, end in occupied:
            if current < start:
                if start - current >= timedelta(minutes=90):
                    free_intervals.append((current, start))
            current = max(current, end)

        # Add interval at the end of the day if there's enough room
        if current + timedelta(minutes=90) <= day_end:
            free_intervals.append((current, day_end))

        # Format intervals for template rendering
        formatted = [
            {
                'start': interval[0].strftime('%H:%M'),
                'end': interval[1].strftime('%H:%M')
            }
            for interval in free_intervals
        ]

        if formatted:
            available[date.strftime('%Y-%m-%d')] = formatted

    return available