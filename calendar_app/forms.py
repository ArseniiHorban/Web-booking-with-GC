from django import forms
from calendar_app.models import Booking

class BookingForm(forms.ModelForm):
    date = forms.CharField(widget=forms.HiddenInput())
    time = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = Booking
        fields = ['name', 'phone', 'date', 'time']

