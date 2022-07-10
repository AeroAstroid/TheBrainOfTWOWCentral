def type_func(a): # i unno what to name the var
	if a.is_integer(): return "int"
	if is_number(a): return "float"
	return type(a).__name__