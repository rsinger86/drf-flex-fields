""" 
	This class dynamically generates the serializer_class with dynamic parameters set from incoming GET params.
	It also examines the request and allows certain fields to be expanded within the list view.
"""

from rest_framework import viewsets


class FlexFieldsMixin(object):
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

		return super(FlexFieldsMixin, self).list(request, *args, **kwargs)
	

	def get_serializer_context(self):
		default_context = super(FlexFieldsMixin, self).get_serializer_context()
		default_context['expandable'] = self._expandable
		default_context['force_expand'] = self._force_expand
		return default_context
		


class FlexFieldsModelViewSet(FlexFieldsMixin, viewsets.ModelViewSet):
    pass