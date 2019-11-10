# grammar_list : Simple function to properly list many strings
def grammar_list(listed):
	if len(listed) > 2:
		first_list = ", ".join(listed[:-1])
		listed = first_list + ", and " + str(listed[-1])
	elif len(listed) == 2:
		listed = " and ".join(listed)
	elif len(listed) == 1:
		listed = "".join(listed)
	else:
		listed = "none"
	return listed