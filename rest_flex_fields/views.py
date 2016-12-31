from rest_framework import viewsets


class FlexFieldsMixin(object):
	""" 
	    Dynamically generates the serializer_class with dynamic parameters set from incoming GET params.
	"""

	permit_list_expands = []
	_expandable = True
	_force_expand = []
	    
	def list(self, request, *args, **kwargs):
		""" Examines request and allows certain fields to be expanded within the list view. """

		self._expandable = False
		expand = request.query_params.get('expand')

		if len(self.permit_list_expands) > 0 and expand:
			if expand == '~all':
				self._force_expand = self.permit_list_expands
			else:
				self._force_expand = list( 
					set(expand.split(',')) & set(self.permit_list_expands) 
				)

		return super(FlexFieldsMixin, self).list(request, *args, **kwargs)
	
	
	def get_serializer_class(self):
		""" Dynamically adds properties to serializer_class from request's GET params. """

		expand = None
		fields = None
		is_valid_request = hasattr(self, 'request') and self.request.method == 'GET'

		if not is_valid_request:
			return self.serializer_class

		fields = self.request.query_params.get('fields')
		fields = fields.split(',') if fields else None
		
		if self._expandable:
			expand = self.request.query_params.get('expand')
			expand = expand.split(',') if expand else None
		elif len(self._force_expand) > 0:
			expand = self._force_expand
		
		return type('DynamicFieldsModelSerializer', (self.serializer_class,), {
			'expand': expand, 
			'include_fields': fields,
		})


class FlexFieldsModelViewSet(FlexFieldsMixin, viewsets.ModelViewSet):
    pass