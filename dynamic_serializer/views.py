from rest_framework import viewsets


class FlexFieldsMixin(object):
	""" 
	    Apply this mixin to any view or viewset to dynamically generate the serializer_class
	    which has the expand query parameter applied to the serializer
	"""
	permit_list_expands = []
	_expandable = True
	_force_expand = []
	    
	def list(self, request, *args, **kwargs):
		self._expandable = False
		expand = request.query_params.get('expand')

		if len(self.permit_list_expands) > 0 and expand:
			if expand == '~all':
				self._force_expand = self.permit_list_expands
			else:
				self._force_expand = list( 
					set(expand.split(',')) & set(self.permit_list_expands) 
				)

		return super(DynamicFieldsModelMixin, self).list(request, *args, **kwargs)
	
	
	def get_serializer_class(self):
		expand = None
		exclude = None
		fields = None
		is_valid_request = hasattr(self, 'request') and self.request.method == 'GET'

		if not is_valid_request:
			return self.serializer_class

		exclude = self.request.query_params.get('exclude')
		fields = self.request.query_params.get('fields')

		if self._expandable:
			expand = self.request.query_params.get('expand')
		elif len(self._force_expand) > 0:
			expand = self._force_expand
		
		options = {
			'expand_fields': expand.split(',') if expand else None, 
			'include_fields': fields.split(',') if fields else None, 
			'exclude_fields': exclude.split(',') if exclude else None,
		}

		return type('DynamicFieldsModelSerializer', (self.serializer_class,), options)


class FlexFieldsModelViewSet(FlexFieldsMixin, viewsets.ModelViewSet):
    pass