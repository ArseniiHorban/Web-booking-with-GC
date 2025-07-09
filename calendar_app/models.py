from django.db import models

# Create your models here.

class Booking(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    date = models.DateField()
    time = models.TimeField()

    google_event_id = models.CharField(max_length=255, unique=True, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.date} {self.time}"