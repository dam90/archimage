from django.http import HttpResponse, JsonResponse
from django import forms
import archimage
from test_inspect import describe_class_methods
import json, traceback
from django.views.decorators.csrf import csrf_exempt, csrf_protect

mount = archimage.archimage(live=True)

def index(request):
	js = describe_class_methods(mount)
	return HttpResponse(json.dumps(js))


@csrf_exempt
def execute(request):
	arguments = None
	command = None
	command_list = [ x['name'] for x in describe_class_methods(mount) ]

	print 'REQUEST METHOD: ' + request.method

	# get method and arguments from get or post request:
	if request.method == "POST":
		command = request.POST.get('command')

		print "\n\n-----------------------"
		print "POST PARAMS:"

		for key in request.POST:
				print key+": "+request.POST[key]
		print "-----------------------\n\n"

		if request.POST.get('args'):

			arguments = json.loads(request.POST.get('args'))
			print arguments
	
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

	except Exception, exc:
		print "[API_EXECUTE_EXCEPTION]: ", exc
		traceback.print_exc()
		resp = {"command": command,"arguments": arguments, "response": "error"}

	
	return JsonResponse(resp)
