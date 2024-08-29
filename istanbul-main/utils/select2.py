def make_select2_attr(field_name = 'name', input_length = 2):
	attr= {
		'attrs':{
			'data-placeholder':'Select by '+field_name+' ...',
			'style':'width:100%',
			'class':'searching',
			'data-minimum-input-length':str(input_length)
		}
	}
	return attr
