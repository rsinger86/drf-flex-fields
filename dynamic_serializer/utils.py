

def check_expand(request, key):
	expand = query_params.get('expand', '')
	expand_fields = expand.split(',')
	return '~all' in expand_fields or key in expand_fields
