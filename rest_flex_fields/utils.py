

def is_expanded(request, key):
    """ Examines request object to return boolean of whether 
        passed field is expanded. 
    """
    expand = request.query_params.get('expand', '')
    expand_fields = []

    for e in expand.split(','):
        expand_fields.extend([e for e in e.split('.')]) 
        
    return '~all' in expand_fields or key in expand_fields
	

def split_levels(fields):
	"""
		Convert dot-notation such as ['a', 'a.b', 'a.d', 'c'] into 
		current-level fields ['a', 'c'] and next-level fields 
		{'a': ['b', 'd']}.
	"""
	first_level_fields = []
	next_level_fields = {}

	if not fields:
		return first_level_fields, next_level_fields

	if not isinstance(fields, list):
		fields = [a.strip() for a in fields.split(',') if a.strip()]
	for e in fields:
		if '.' in e:
			first_level, next_level = e.split('.', 1)
			first_level_fields.append(first_level)
			next_level_fields.setdefault(first_level, []).append(next_level)
		else:
			first_level_fields.append(e)
			
	first_level_fields = list(set(first_level_fields))
	return first_level_fields, next_level_fields