def make_select2_attr(field_name = 'name', input_length = 2, width="100"):
	attr= {
		'attrs':{
			'data-placeholder':'Select by '+field_name+' ...',
			'style':'width:{}%'.format(width),
			'class':'searching',
			'data-minimum-input-length':str(input_length)
		}
	}
	return attr
