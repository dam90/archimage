from django import forms
from .models import Location
    
class LocationForm(forms.ModelForm):

	class Meta:
	
		model = Location
		fields = ('latitude','longitude','altitude','name')
    # latitude = forms.FloatField(help_text="Enter a Latitude (decimal degrees)")
    # longitude = forms.FloatField(help_text="Enter a Longitude (decimal degrees, East)")
    # altitude = forms.FloatField(help_text="Enter an Altitude (meters)")
    # name = forms.CharField(help_text="Enter a Location Name")