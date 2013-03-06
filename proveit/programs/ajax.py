from django.utils import simplejson
from dajaxice.decorators import dajaxice_register

@dajaxice_register(method='GET')
def sayhello1(request, text):
	return simplejson.dumps(
{'values': [{'alias': 'x', 'values': ['1', '2', '3', '4', '5', '6', '7', '8', '9','10','11','12'], 'name': 'x'},{'alias': 'y', 'values': ['1', '2', '3', '4', '5', '6', '7', '8', '9','8','8','9'], 'name': 'y->y'},], 'length':12, 'lines':[8,9,10,11,12,13,8,9,10,11,12,13], 'firstLine':8}
	)
