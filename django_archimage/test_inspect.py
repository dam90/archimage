import inspect

def describe_class_methods(base_class):
	function_list = []
	for a in inspect.getmembers(base_class,predicate=inspect.ismethod):
		if a[0] == "__init__":
			continue
		function = getattr(base_class,a[0])
		function_args = inspect.getargspec(function)
		d = {'name': a[0],
			 'args': function_args[0][1:],
			 'doc': function.__doc__
			}
		function_list.append(d)
	return function_list
