

def is_expanded(request, key):
    """ Examines request object to return boolean of whether 
        passed field is expanded. 
    """
    expand = request.query_params.get('expand', '')
    expand_fields = []

    for e in expand.split(','):
        expand_fields.extend([e for e in e.split('.')]) 
        
    return '*' in expand_fields or key in expand_fields


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

	for e in fields:
		if '.' in e:
			first_level, next_level = e.split('.', 1)
			first_level_fields.append(first_level)
			next_level_fields.setdefault(first_level, []).append(next_level)
		else:
			first_level_fields.append(e)

	first_level_fields = list(set(first_level_fields))
	return first_level_fields, next_level_fields


def get_list_query_param(query_params, param):
    """
    >>> get_list_query_param({'foo': 'a,b,c'}, 'foo')
    ['a', 'b', 'c']
	>>> get_list_query_param({'foo': 'a, b'}, 'foo')
    ['a', 'b']
    >>> get_list_query_param({'foo': ''}, 'foo')
    []
    >>> get_list_query_param({}, 'foo')
    []
    """
    return query_params.get(param, '').replace(',', ' ').split()  # split(',') doesn't handle empty gracefully


def get_requested_fields(all_fields, query_params, required_fields=None):
    """
    Determine the requested fields through a combination of the fields and omit query params
    """
    fields = get_list_query_param(query_params, 'fields')
    omit = get_list_query_param(query_params, 'omit')
    permitted_omit = set(omit) - set(required_fields) if required_fields else set(omit)

    if fields:
        requested_fields = [field for field in fields if field in all_fields]
    else:
        requested_fields = [field for field in all_fields if field not in permitted_omit]

    return requested_fields
