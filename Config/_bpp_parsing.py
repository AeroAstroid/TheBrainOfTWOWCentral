try:
	from Config._functions import is_whole
	from Config._bpp_functions import express_array, safe_cut, FUNCTIONS
	from Config._db import Database
except ModuleNotFoundError:
	from _functions import is_whole
	from _bpp_functions import express_array, safe_cut, FUNCTIONS
	from _db import Database

def run_bpp_program(code, p_args, author, runner):
	# Pointers for tag and function organization
	tag_level = 0
	tag_code = []
	tag_str = lambda: ' '.join([str(s) for s in tag_code])

	backslashed = False	# Flag for whether to unconditionally escape the next character
	
	functions = {}	# Dict flattening a tree of all functions to be evaluated

	current = ["", False] # Raw text of what's being parsed right now + whether it's a string

	output = "" # Stores the final output of the program

	goto = 0 # Skip characters in evaluating the code

	for ind, char in enumerate(list(code)):
		normal_case = True

		if ind < goto:
			continue

		if backslashed:
			if tag_code == []:
				output += char
			else:
				current[0] += char
			
			backslashed = False
			continue

		if char == "\\":
			backslashed = True
			continue

		if char == "[" and not current[1]:
			tag_level += 1

			if tag_level == 1:
				try:
					tag_code = [max([int(k) for k in functions if is_whole(k)]) + 1]
				except ValueError:
					tag_code = [0]
				
				output += "{}"

				found_f = ""

				for f_name in FUNCTIONS.keys():
					try:
						attempted_f = ''.join(code[ind+1:ind+len(f_name)+2]).upper()
						if attempted_f == f_name + " ":
							found_f = f_name
							goto = ind + len(f_name) + 2
						elif attempted_f == f_name + "]":
							found_f = f_name
							goto = ind + len(f_name) + 1
					except IndexError: pass
				
				if found_f == "":
					end_of_f = min(code.find(" ", ind+1), code.find("]", ind+1))
					called_f = ''.join(code[ind+1:end_of_f])
					raise NameError(f"Function {called_f} does not exist")
				
				functions[tag_str()] = [found_f]
			
			else:
				old_tag_code = tag_str()
				
				k = 1
				while old_tag_code + f" {k}" in functions.keys():
					k += 1

				new_tag_code = old_tag_code + f" {k}"

				found_f = ""

				for f_name in FUNCTIONS.keys():
					try:
						attempted_f = ''.join(code[ind+1:ind+len(f_name)+2]).upper()
						if attempted_f == f_name + " ":
							found_f = f_name
							goto = ind + len(f_name) + 2
						elif attempted_f == f_name + "]":
							found_f = f_name
							goto = ind + len(f_name) + 1
					except IndexError: pass
				
				if found_f == "":
					end_of_f = min(code.find(" ", ind+1), code.find("]", ind+1))
					called_f = ''.join(code[ind+1:end_of_f])
					raise NameError(f"Function {called_f} does not exist")

				functions[new_tag_code] = [found_f]
				functions[tag_str()].append((new_tag_code,))

				tag_code.append(k)
			
			normal_case = False
		
		if char == "]" and not current[1]:
			if current[0] != "":
				functions[tag_str()].append(current[0])
				current = ["", False]
			tag_level -= 1
			normal_case = False
		
		if char == " ":
			if not current[1] and tag_level != 0:
				if current[0] != "":
					functions[tag_str()].append(current[0])
					current = ["", False]
				normal_case = False
		
		if char in '"“”':
			if current[0] == "" and not current[1]:
				current[1] = True
			elif current[1]:
				functions[tag_str()].append(current[0])
				current = ["", False]
			normal_case = False
		
		if normal_case:
			if tag_level == 0: output += char
			else: current[0] += char
		
		tag_code = tag_code[:tag_level]
		tag_code += [1] * (tag_level - len(tag_code))

	VARIABLES = {}

	base_keys = [k for k in functions if is_whole(k)]

	db = Database()

	type_list = [int, float, str, list]
	def var_type(v):
		try:
			return type_list.index(type(v))
		except IndexError:
			raise TypeError(f"Value {safe_cut(v)} could not be attributed to any valid data type")
	
	def evaluate_result(k):
		v = functions[k]

		if type(v) == tuple:
			k1 = v[0]
			functions[k] = evaluate_result(k1)
			return functions[k]
		
		args = v[1:]

		for i, a in enumerate(args):
			if v[0] == "IF" and is_whole(v[1]) and int(v[1]) != 2-i:
				continue
			if type(a) == tuple:
				k1 = a[0]
				functions[k][i+1] = evaluate_result(k1)
		
		args = v[1:]

		result = FUNCTIONS[v[0]](*args)

		# Tuples indicate special behavior necessary
		if type(result) == tuple:
			if result[0] == "d":
				if len(str(result[1])) > 100000:
					raise MemoryError(
					f"The variable {safe_cut(args[0])} is too large: {safe_cut(result[1])} (limit 100kb)")
					
				VARIABLES[args[0]] = result[1]
				result = ""

			elif result[0] == "v":
				try:
					result = VARIABLES[args[0]]
				except KeyError:
					raise NameError(f"No variable by the name {safe_cut(args[0])} defined")

			elif result[0] == "a":
				if result[1] >= len(p_args) or -result[1] >= len(p_args) + 1:
					result = ""
				else:
					result = p_args[result[1]]

			elif result[0] == "gd":
				v_name = args[0]
				if len(str(result[1])) > 100000:
					raise MemoryError(
					f"The global variable {safe_cut(v_name)} is too large: {safe_cut(result[1])} (limit 100kb)")
				
				if (v_name,) not in db.get_entries("b++2variables", columns=["name"]):
					v_value = express_array(result[1]) if type(result[1]) == list else result[1]

					db.add_entry("b++2variables", [v_name, str(v_value), var_type(v_value), str(author)])
					result = ""

				else:
					v_list = db.get_entries("b++2variables", columns=["name", "owner"])
					v_owner = [v for v in v_list if v_name == v[0]][0][1]

					if v_owner != str(author):
						raise PermissionError(
						f"Only the author of the {v_name} variable can edit its value ({v_owner})")
					
					db.edit_entry(
						"b++2variables",
						entry={"value": str(result[1]), "type": var_type(result[1])},
						conditions={"name": v_name})
					result = ""
				
			elif result[0] == "gv":
				v_name = args[0]

				if (v_name,) not in db.get_entries("b++2variables", columns=["name"]):
					raise NameError(f"No global variable by the name {safe_cut(v_name)} defined")

				v_list = db.get_entries("b++2variables", columns=["name", "value", "type"])
				v_value, v_type = [v[1:3] for v in v_list if v[0] == v_name][0]
				v_value = type_list[v_type](v_value)

				result = v_value

			elif result[0] == "n":
				result = runner.name

			elif result[0] == "id":
				result = runner.id
			
			elif result[0] == "aa":
				result = p_args
		
		functions[k] = result
		return result

	for k in base_keys:
		evaluate_result(k)
	
	for k in base_keys:
		if type(functions[k]) == tuple:
			evaluate_result(k)

	results = []
	for k, v in functions.items():
		if is_whole(k):
			if type(v) == list: v = express_array(v)
			results.append(v)

	output = output.replace("{}", "\t").replace("{", "{{").replace("}", "}}").replace("\t", "{}")

	return output.format(*results).replace("\v", "{}")

if __name__ == "__main__":
	program = input("Program:\n\t")
	print("\n")
	program = program.replace("{}", "\v")
	print(run_bpp_program(program, [], 184768535107469314))
