from django.http import HttpResponse, JsonResponse
from django import forms
import archimage
from test_inspect import describe_class_methods
import json

mount = archimage.archimage(live=False)

def index(request):
	js = describe_class_methods(mount)
	return HttpResponse(json.dumps(js))

def execute(request):
	arguments = None
	command = None
	command_list = [ x['name'] for x in describe_class_methods(mount) ]

	# get method and arguments from get or post request:
	if request.method == "POST":
		command = request.POST.get('command')
		if request.POST.get('args'):
					arguments = json.loads(request.GET.get('args'))
	
	elif request.method == "GET":

		command = request.GET.get('command')
		if request.GET.get('args'):
					arguments = json.loads(request.GET.get('args'))

	# execute:
	try:
		if command in command_list:

			call = getattr(mount,command)

			if arguments:
				result = call(**arguments)
			else:
				result = call()
			
			resp = {"command": command,"arguments": arguments, "response": result}

		else:
			resp = {"command": command,"arguments": arguments, "response": "command not in command list", "command": command_list}

	except:
		resp = {"command": command,"arguments": arguments, "response": "error"}

	
	return JsonResponse(resp)
