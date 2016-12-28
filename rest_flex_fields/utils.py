

def check_expand(request, key):
	""" Examines request object to return boolean of whether passed field is expanded. """
	
	expand = query_params.get('expand', '')
	expand_fields = expand.split(',')
	return '~all' in expand_fields or key in expand_fields
