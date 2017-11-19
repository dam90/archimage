from django.http import HttpResponse
from django.shortcuts import render
from .forms import LocationForm
from .models import Location

def index(request):
    #return HttpResponse("Hello, world. You're at the scope index.")

	for location in Location.objects.all():
	    	print "current location:"
	    	print location.name

	return render(request,'scope/index.html')

def setup(request):
    #return HttpResponse("Hello, world. You're at the scope index.")
    return render(request,'scope/setup.html')

def align(request):
    #return HttpResponse("Hello, world. You're at the scope index.")
    return render(request,'scope/align.html')

def track(request):
    #return HttpResponse("Hello, world. You're at the scope index.")
    return render(request,'scope/track.html')

def locations(request):
    #return HttpResponse("Hello, world. You're at the scope index.")
    form =  LocationForm()
    
    return render(request,'scope/location_form.html',{'form': form})

def monitor(request):
    #return HttpResponse("Hello, world. You're at the scope index.")
    return render(request,'scope/monitor.html')