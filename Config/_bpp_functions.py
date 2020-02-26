import random, statistics, re
from Config._const import ALPHABET
from Config._functions import is_float, is_whole, strip_alpha, match_count
import numpy as np

def safe_multiply(a, b):
	if isinstance(a, int) and isinstance(b, int) and \
	    (abs(a) > 1<<512 or abs(b) > 1<<512):
		raise ValueError('Numbers are too large to multiply')
	return a*b
		
def safe_exponent(a, b):
	if abs(a) > 1024 or b > 1024:
		raise ValueError('Numbers are too large to exponentiate')
	return a**b

FUNCTIONS = {

	# Basic operations
	"out{?}": {
		"TYPES": {
			"a": []
		}
	},


	# Mathematical
	"?\+?": {
		"MAIN": (lambda a, b: a + b),
		"TYPES": {
			"a": ["NUMBER"],
			"b": ["NUMBER"]
		},
		"PRIORITY": 1
	},

	"?-?": {
		"MAIN": (lambda a, b: a - b),
		"TYPES": {
			"a": ["NUMBER"],
			"b": ["NUMBER"]
		},
		"PRIORITY": 1
	},

	"?\*?": {
		"MAIN": safe_multiply,
		"TYPES": {
			"a": ["NUMBER"],
			"b": ["NUMBER"]
		},
		"PRIORITY": 2
	},

	"?/?": {
		"MAIN": (lambda a, b: a / b),
		"TYPES": {
			"a": ["NUMBER"],
			"b": ["NUMBER"]
		},
		"PRIORITY": 2
	},

	"?\^?": {
		"MAIN": safe_exponent,
		"TYPES": {
			"a": ["NUMBER"],
			"b": ["NUMBER"]
		},
		"PRIORITY": 3
	},

	"avg?": {
		"MAIN": (lambda a: np.mean(a)),
		"TYPES": {
			"a": ["ARRAY NUMBER"]
		}
	},

	"stdev?": {
		"MAIN": (lambda a: statistics.stdev(a)),
		"TYPES": {
			"a": ["ARRAY NUMBER"]
		}
	},

	"stdevp?": {
		"MAIN": (lambda a: np.std(a)),
		"TYPES": {
			"a": ["ARRAY NUMBER"]
		}
	},

	"randint?to?": {
		"MAIN": (lambda a, b: random.randrange(a, b+1)),
		"TYPES": {
			"a": ["INTEGER"],
			"b": ["INTEGER"]
		}
	},

	"rand?to?": {
		"MAIN": (lambda a, b: random.uniform(a, b)),
		"TYPES": {
			"a": ["NUMBER"],
			"b": ["NUMBER"]
		}
	},


	# STRING and ARRAY manipulation
	"?index?": {
		"MAIN": (lambda a, b: a[b-1] if b >= 0 else a[b]),
		"TYPES": {
			"a": ["ARRAY", "STRING"],
			"b": ["INTEGER"]
		},
		"PRIORITY": 4
	},

	"?&?": {
		"MAIN": (lambda a, b: a + b),
		"TYPES": {
			"a": ["ARRAY", "STRING"],
			"b": ["ARRAY", "STRING"]
		},
		"PRIORITY": 4
	},

	"?rept?": {
		"MAIN": (lambda a, b: a * b),
		"TYPES": {
			"a": ["ARRAY", "STRING"],
			"b": ["INTEGER"]
		}
	},

	"?choose?": {
		"MAIN": (lambda a, b: (random.sample(a, b) if b != 1 else random.sample(a, b)[0])),
		"TYPES": {
			"a": ["ARRAY"],
			"b": ["INTEGER"]
		}
	},

	"sort?": {
		"MAIN": (lambda a: sorted(a)),
		"TYPES": {
			"a": ["ARRAY NUMBER", "ARRAY STRING", "ARRAY BOOLEAN"]
		}
	},

	"desort?": {
		"MAIN": (lambda a: sorted(a, reverse=True)),
		"TYPES": {
			"a": ["ARRAY NUMBER", "ARRAY STRING", "ARRAY BOOLEAN"]
		}
	},


	# Conditional
	"?==?": {
		"MAIN": (lambda a, b: a == b),
		"TYPES": {
			"a": [],
			"b": []
		},
		"PRIORITY": 0
	},

	"?>?": {
		"MAIN": (lambda a, b: a > b),
		"TYPES": {
			"a": [],
			"b": []
		},
		"PRIORITY": 0
	},

	"?<?": {
		"MAIN": (lambda a, b: a < b),
		"TYPES": {
			"a": [],
			"b": []
		},
		"PRIORITY": 0
	},

	"?>=?": {
		"MAIN": (lambda a, b: a >= b),
		"TYPES": {
			"a": [],
			"b": []
		},
		"PRIORITY": 0
	},

	"?<=?": {
		"MAIN": (lambda a, b: a <= b),
		"TYPES": {
			"a": [],
			"b": []
		},
		"PRIORITY": 0
	},

	"?!=?": {
		"MAIN": (lambda a, b: a != b),
		"TYPES": {
			"a": [],
			"b": []
		},
		"PRIORITY": 0
	},

	"!?": {
		"MAIN": (lambda a: not a),
		"TYPES": {
			"a": ["BOOLEAN"]
		},
		"PRIORITY": 1
	},
}

# Tries to interpret the code passed as an operation
# Return format: [is_it_an_operation, result_of_operation, was_there_an_error]
def operation_check(block):
	matching_ops = [] # List of operations that match

	for possible_op in FUNCTIONS.keys(): # Check through each operation
		letter_expect = False
		op_regex = possible_op # Prepare a variable to serve as the regex for whether or not the code matches 
		# this operation

		for param in range(possible_op.count("?")): # Each ? is a parameter of the function
			alph = ALPHABET.lower()[param]
			types = FUNCTIONS[possible_op]["TYPES"][alph] # Find out what type is expected for that parameter

			if "STRING" in types or "BOOLEAN" in types or "ARRAY STRING" in types or "ARRAY BOOLEAN" in types:
				letter_expect = True
			
			dot_exp = r"([^\^!-&\*-\/<-@_]{1,})"
			if possible_op == "out{?}":
				dot_exp = r"([^\^]{1,})"
			elif types == ["NUMBER"] or types == ["INTEGER"] or types == ["ARRAY NUMBER"]:
				dot_exp = r"([^\\A-z]{1,})"
			'''if len(strip_alpha(possible_op)) == 0:
				dot_exp = r"([^\^\\!-\/<-@]{1,})"
			elif len(types) == 0:
				dot_exp = r"([^\\]{1,})"
			elif types == ["NUMBER"] or types == ["INTEGER"] or types == ["ARRAY NUMBER"]:
				# If it's expecting a number of some kind, the parameter shouldn't have any letters in it, and so we 
				# can use a regex that does not count letter characters to detect this parameter
				dot_exp = r"([^A-z]{1,})"'''
			
			# If any type is allowed (len(types) == 0) or the type is BOOLEAN or STRING (which contain letters)
			# Use the regex that matches all characters except for backslashes

			op_regex = op_regex.replace("?", dot_exp, 1) # Replace the _ placeholder with the matching group for that
			# parameter
		
		match = re.search(op_regex, block) # Try to match this operation (the previously generated regex) with the code
		
		if match: # If it's a match, append it to the matching operations array
			if possible_op.count("?") == 2 and "\\" == match.group(1)[-1]:
				continue
			
			if not possible_op.startswith("?") and match.span()[0] != 0 and block[match.span()[0]-1] == "\\":
				continue
			
			matching_ops.append([possible_op, match, letter_expect])


	if "out{?}" in matching_ops or "out{" in block: # If the operation is out{}, leave a flag for it. It'll be handled
		substring = block[block.find("out{")+4:block.find("}")]
		return ["out", f"({substring})", False] # in parenthesis_parser

	if len(matching_ops) == 0: # If no operations match the code, return it unchanged
		return [False, block, False]
	
	letter_operations = [x for x in matching_ops if strip_alpha(x[0]) != ""] # Operations that don't use letters are

	if len(letter_operations) == 0 and strip_alpha(block) != "":
		if True not in [x[2] for x in matching_ops]:
			return [False, block, False]
		
	if len(letter_operations) == 0 and len(matching_ops) != 0: # all either math operations or other operations that
	# can be used with eachother. If this statement is composed entirely of them, then we can treat it differently

		operators = [
			[x[0].replace("?", "").replace("\\", ""), 
			FUNCTIONS[x[0]]["PRIORITY"],
			x[0]]
			for x in matching_ops
		]

		full_token_list = []
		current_index = 0
		omit_bracket = False

		while True:
			operator_indices = []
			for op in operators:
				found = block.find(op[0], current_index)
				if found != -1:
					operator_indices.append(found)
				else:
					operator_indices.append(len(block))

			min_op = min(operator_indices)
			now_op = operators[operator_indices.index(min_op)][0]

			if min_op == len(block):
				full_token_list.append(block[current_index:])
				break

			to_add = block[current_index:min_op]

			full_token_list.append(to_add)
			full_token_list.append(now_op)
			current_index = min_op + len(now_op)
		
		#full_token_list.append(block[current_index:])
		
		#operator_order = sorted(operator_order, key=lambda o: (5 - o[1]))


		priority_limit = max([x[1] for x in operators])
		op_list = [x[0] for x in operators]

		for p in range(priority_limit + 1):
			current_priority = priority_limit - p

			for token in full_token_list:
				if token in op_list:
					ind = op_list.index(token)
					if operators[ind][1] != current_priority:
						continue
					
					token_ind = full_token_list.index(token)
					operation_name = operators[ind][2]
					param_info = FUNCTIONS[operation_name]["TYPES"]
					
					params = []
					params_ind = []
					if len(param_info.keys()) != 1:
						for r in range(token_ind):
							search_ind = token_ind - r - 1
							if full_token_list[search_ind] != []:
								c_param = full_token_list[search_ind]

								param_name = "a"
								expected_types = param_info[param_name] # The allowed types for param
								fit_type = "" # The type this parameter will fit under

								for expect in expected_types:
									if expect == "NUMBER":
										if is_whole(c_param):
											c_param = int(c_param)
											fit_type = expect
											break
										if is_float(c_param):
											c_param = float(c_param)
											fit_type = expect
											break
									if expect == "INTEGER":
										if is_whole(c_param):
											c_param = int(c_param)
											fit_type = expect
											break
									if expect == "BOOLEAN":
										if c_param in ["True", "False"]:
											c_param = bool(c_param)
											fit_type = expect
											break
									if expect.startswith("ARRAY"):
										if c_param.startswith("[") and c_param.endswith("]"):
											c_param = array_to_list(c_param)
											fit_type = expect
											break
									if expect == "STRING":
										if (not is_float(c_param) and not is_whole(c_param)
										and c_param not in ["True", "False"]):
											fit_type = expect
											break
								
								if fit_type == "" and len(expected_types) > 0:
									#return [True, [operation_name, param_name, c_param], True]
									return [True, block, True]
								
								params_ind.append(search_ind)
								params.append(c_param)
								break

					for search_ind in range(token_ind + 1, len(full_token_list)):
						if full_token_list[search_ind] != []:
							c_param = full_token_list[search_ind]

							param_name = "a" if len(param_info.keys()) == 1 else "b"
							expected_types = param_info[param_name]
							fit_type = "" # The type this parameter will fit under

							for expect in expected_types:
								if expect == "NUMBER":
									if is_whole(c_param):
										c_param = int(c_param)
										fit_type = expect
										break
									if is_float(c_param):
										c_param = float(c_param)
										fit_type = expect
										break
								if expect == "INTEGER":
									if is_whole(c_param):
										c_param = int(c_param)
										fit_type = expect
										break
								if expect == "BOOLEAN":
									if c_param in ["True", "False"]:
										c_param = bool(c_param)
										fit_type = expect
										break
								if expect.startswith("ARRAY"):
									if c_param.startswith("[") and c_param.endswith("]"):
										c_param = array_to_list(c_param)
										fit_type = expect
										break
								if expect == "STRING":
									if (not is_float(c_param) and not is_whole(c_param)
									and c_param not in ["True", "False"]):
										fit_type = expect
										break
							
							if fit_type == "" and len(expected_types) > 0:
								#return [True, [operation_name, param_name, c_param], True]
								return [True, block, True]
							
							params_ind.append(search_ind)
							params.append(c_param)
							break
					
					result = FUNCTIONS[operation_name]["MAIN"](*params)

					if type(result) is list:
						result = list_to_array(result)
					
					full_token_list[token_ind] = str(result)
					for x in params_ind:
						full_token_list[x] = []
			
			full_token_list = [x for x in full_token_list if x != []]
		
		full_token_list = [x for x in full_token_list if x.strip() != ""]

		return [True, full_token_list[0], False] # There was an operation and no error. Pass the result

	# Just in case there's more than 1 matching operation, run this sorted command. It takes the span of the operation
	# match (the start and end indices for when the operation applies), and subtracts the start index from end index 
	# to determine how long the span is. Put the one with the longest span first
	matching_ops = sorted(matching_ops, reverse=True, key=(lambda m: len(m[0])))
	matching_ops = sorted(matching_ops, reverse=True, key=(lambda m: m[1].span()[1] - m[1].span()[0]))

	# Assume it's the one with the longest span. This prevents subsets of operations being counted instead of the
	operation, match, lt = matching_ops[0] # actual operation specified. Define the operation and the match object
	
	parameters = [] # List of parameters that will be used in the operation function

	for g in range(operation.count("?")): # For each parameter necessary...
		param = match.group(g + 1).strip() # Match the group of the parameter (group 0 is the entire block; start at 1)
		param_name = ALPHABET.lower()[g] # Get the parameter name (which is just the corresponding letter in alphabet)
		
		expected_types = FUNCTIONS[operation]["TYPES"][param_name] # The allowed types for this parameter
		fit_type = "" # The type this parameter will fit under

		for expect in expected_types:
			if expect == "NUMBER": # NUMBER can be both int and float
				if is_whole(param): # Detect if it can be interpreted as an int
					param = int(param) # If so, make it an int
					fit_type = expect
					break
				if is_float(param): # Detect if it can be interpreted as a float
					param = float(param) # If so, make it a float
					fit_type = expect
					break
			if expect == "INTEGER": # INTEGER is exclusively int
				if is_whole(param): # Detect if it can be an int
					param = int(param) # If so, make it an int
					fit_type = expect
					break
			if expect == "BOOLEAN": # BOOLEAN can only be True or False
				if param in ["True", "False"]: # Detect if it's one of those
					param = bool(param) # If so, turn it into a bool
					fit_type = expect
					break
			if expect.startswith("ARRAY"): # ARRAYs are defined with brackets
				if param.startswith("[") and param.endswith("]"):
					param = array_to_list(param)
					fit_type = expect
					break
			if expect == "STRING": # STRING can be anything that isn't instantly defined as one of the others
				if not is_float(param) and not is_whole(param) and param not in ["True", "False"]: # Detect that it's
					# not any of the other types. param is already a str, so it doesn't need to be made into one
					fit_type = expect
					break

		if fit_type == "" and len(expected_types) > 0: # If there ARE expected types but the parameter can't fit them
			#return [True, [operation_name, param_name, c_param], True]
			return [True, block, True] # There IS an operation but there is an error.
			# Return the operation and param name for error specification
			
		parameters.append(param) # If everything went alright, add param to the parameter list

	result = FUNCTIONS[operation]["MAIN"](*parameters) # Extract a result from the operation function

	return [True, result, False] # There was an operation and no error. Pass the result


# Tries to interpret the code passed as a variable call
# Return format: [is_it_a_variable, result]
def variables(block, VARIABLES):
	try: # Try to get the variable from the VARIABLES dict
		result = VARIABLES[block]
		return [True, result]
	except KeyError: # If you can't, it's not a valid variable
		return [False, block]


# Returns a python list with the input as a B++ array
def array_to_list(raw):
	if "\t" not in raw:
		list_eq = raw[1:-1].split("; ")
	else:
		list_eq = raw[1:-1].split("\t ")

	for entry in range(len(list_eq)):
		if is_whole(list_eq[entry]):
			list_eq[entry] = int(list_eq[entry])
		if is_float(list_eq[entry]):
			list_eq[entry] = float(list_eq[entry])
		if list_eq[entry] in ["True", "False"]:
			list_eq[entry] = bool(list_eq[entry])

	return list_eq


# Returns a B++ array with input as a python list
def list_to_array(formatted):
	array_eq = f"[{'; '.join([str(x) for x in formatted])}]"
	return array_eq
