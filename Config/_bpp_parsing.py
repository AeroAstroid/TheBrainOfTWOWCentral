import traceback

try:
	from Config._functions import is_whole
	from Config._bpp_functions import express_array, safe_cut, FUNCTIONS, ProgramDefinedException
	from Config._db import Database
except ModuleNotFoundError:
	from _functions import is_whole
	from _bpp_functions import express_array, safe_cut, FUNCTIONS, ProgramDefinedException
	from _db import Database

import re, copy


def str_array(s):
	out = "["
	for x in s:
		if type(x) == list:
			out += str_array(x) + ', '
		else:
			out += "'" + str(x).replace('\\', '\\\\').replace("'", "\\'") + "', "
	return out[:-2] + "]"


def undo_str_array(s):
	if s[:1] == "[": s = s[1:]
	if s[-1:] == "]": s = s[:-1]

	is_quote = False
	bracket_count = 0
	is_escaped = False
	outlist = []
	current_append = ""
	for char in s:

		if char == "'" and not is_escaped and bracket_count == 0:
			is_quote = not is_quote
			if not is_quote:
				outlist.append(current_append)
				current_append = ""
			continue

		if char == "\\" and is_quote and not is_escaped and bracket_count == 0:
			is_escaped = True
			continue

		if char == "[" and not is_quote:
			bracket_count += 1
			continue
		if char == "]" and not is_quote:
			bracket_count -= 1
			if bracket_count == 0:
				outlist.append(undo_str_array(current_append))
				current_append = ""
			continue

		if is_quote or char not in " ,":
			current_append += char
			is_escaped = False
	return outlist


def run_bpp_program(code, p_args, author, runner, channel):
	# Pointers for tag and function organization
	tag_level = 0
	tag_code = []
	tag_globals = {}
	user_functions = {}
	call_stack = []
	tag_str = lambda: ' '.join([str(s) for s in tag_code])
	buttons_to_add = []

	debug_values = ""

	backslashed = False	# Flag for whether to unconditionally escape the next character

	functions = {}	# Dict flattening a tree of all functions to be evaluated

	current = ["", False] # Raw text of what's being parsed right now + whether it's a string

	output = "" # Stores the final output of the program

	goto = 0 # Skip characters in evaluating the code

	stored_error = None

	try:
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

					space_idx = code.find(" ", ind + 1)
					bracket_idx = code.find("]", ind + 1)
					end_of_f = -1
					if space_idx != -1 and bracket_idx != -1:
						end_of_f = min(space_idx, bracket_idx)
					elif space_idx != -1:
						end_of_f = space_idx
					elif bracket_idx != -1:
						end_of_f = bracket_idx
					else:
						raise NameError("Invalid function call syntax")

					found_f = code[ind + 1:end_of_f].upper()
					if not found_f:
						raise NameError("Function name cannot be empty")

					if code[end_of_f] == ' ':
						goto = end_of_f + 1
					else:
						goto = end_of_f

					functions[tag_str()] = [found_f]

				else:
					old_tag_code = tag_str()

					k = 1
					while old_tag_code + f" {k}" in functions.keys():
						k += 1

					new_tag_code = old_tag_code + f" {k}"

					space_idx = code.find(" ", ind + 1)
					bracket_idx = code.find("]", ind + 1)
					end_of_f = -1
					if space_idx != -1 and bracket_idx != -1:
						end_of_f = min(space_idx, bracket_idx)
					elif space_idx != -1:
						end_of_f = space_idx
					elif bracket_idx != -1:
						end_of_f = bracket_idx
					else:
						raise NameError("Invalid function call syntax")

					found_f = code[ind + 1:end_of_f].upper()
					if not found_f:
						raise NameError("Function name cannot be empty")

					if code[end_of_f] == ' ':
						goto = end_of_f + 1
					else:
						goto = end_of_f

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

			if char in " \n":
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

		type_list = [int, float, str, list]

		db = Database()
		match = re.finditer("(?i)\[global var \w*?\]", code)
		found_vars = []
		for var in match:
			var = var[0].replace("]", "").replace("\n", " ").strip().split(" ")[-1]
			found_vars.append(var)

		v_list = db.get_entries("b++2variables", columns=["name", "value", "type", "owner"])
		v_list = [v for v in v_list if v[0] in found_vars]

		for v in v_list:
			if type_list[v[2]] == list:
				v_value = undo_str_array(v[1])
			else:
				v_value = type_list[v[2]](v[1])
			tag_globals[v[0]] = [v_value, str(v[3]), False]

		def var_type(v):
			try:
				return type_list.index(type(v))
			except IndexError:
				raise TypeError(f"Value {safe_cut(v)} could not be attributed to any valid data type")

		def evaluate_result(k, func_params=None, custom_func_name=None, no_memoize=False):
			# if k is not a key, it's a literal value
			if k not in functions:
				return k

			v = functions[k]

			# if v is not a list, it has been evaluated and memoized
			if type(v) is not list:
				return v

			func_name = v[0]
			args = v[1:]

			# Lazy eval for ifs
			if func_name == "IF":
				if len(args) < 2: raise TypeError("IF requires at least 2 arguments")
				cond_arg = args[0]
				cond_val = evaluate_result(cond_arg[0], func_params, custom_func_name, no_memoize) if type(cond_arg) == tuple else cond_arg

				if cond_val:
					branch_arg = args[1]
					result = evaluate_result(branch_arg[0], func_params, custom_func_name, no_memoize) if type(branch_arg) == tuple else branch_arg
				elif len(args) > 2:
					branch_arg = args[2]
					result = evaluate_result(branch_arg[0], func_params, custom_func_name, no_memoize) if type(branch_arg) == tuple else branch_arg
				else:
					result = ""

				if not no_memoize:
					functions[k] = result
				return result

			# Trying...
			if func_name == "TRY":
				if len(args) != 2: raise TypeError("TRY requires 2 arguments")

				try_stmt = args[0]
				exc_stmt = args[1]
				try:
					result = evaluate_result(try_stmt[0], func_params, custom_func_name, no_memoize) if type(try_stmt) == tuple else try_stmt
				except Exception as e:
					if isinstance(e, ProgramDefinedException):
						VARIABLES["__bpp_exc_class"] = e.pseudo_class_name if e.pseudo_class_name else "ProgramDefinedException"
						VARIABLES["__bpp_exc_desc"] = str(e)
					else:
						VARIABLES["__bpp_exc_class"] = type(e).__name__
						VARIABLES["__bpp_exc_desc"] = str(e)
					result = evaluate_result(exc_stmt[0], func_params, custom_func_name, no_memoize) if type(exc_stmt) == tuple else exc_stmt

				if not no_memoize:
					functions[k] = result
				return result

			# Evaluate arguments for other functions, except FUNC's code block
			evaluated_args = []
			for i, arg in enumerate(args):
				if func_name == "FUNC" and i == 1:
					evaluated_args.append(arg)
					continue

				eval_arg = evaluate_result(arg[0], func_params, custom_func_name, no_memoize) if type(arg) == tuple else arg
				evaluated_args.append(eval_arg)

			# Functions! :D
			result = None
			if func_name in user_functions:
				if func_name in call_stack:
					raise RecursionError(f"Recursion is not allowed in function definitions, at '{func_name}'.")

				func_def = user_functions[func_name]

				call_stack.append(func_name)
				code_tag = func_def['code']
				result = evaluate_result(code_tag[0], func_params=evaluated_args, custom_func_name=func_name, no_memoize=True)
				call_stack.pop()

			elif func_name in FUNCTIONS:
				result = FUNCTIONS[func_name](*evaluated_args)
			else:
				raise NameError(f"Function {func_name} is not defined.")

			# Tuples indicate special behavior necessary
			if type(result) == tuple:
				if result[0] == "d":
					if len(str(result[1])) > 100000:
						raise MemoryError(
						f"The variable {safe_cut(evaluated_args[0])} is too large: {safe_cut(result[1])} (limit 100kb)")
						
					VARIABLES[evaluated_args[0]] = result[1]
					result = ""
	
				elif result[0] == "v":
					try:
						result = VARIABLES[evaluated_args[0]]
					except KeyError:
						raise NameError(f"No variable by the name {safe_cut(evaluated_args[0])} defined")
	
				elif result[0] == "a":
					if result[1] >= len(p_args) or -result[1] >= len(p_args) + 1:
						result = ""
					else:
						result = p_args[result[1]]
	
				elif result[0] == "gd":
					v_name = result[1]
					if len(str(result[2])) > 100000:
						raise MemoryError(
							f"The global variable {safe_cut(v_name)} is too large: {safe_cut(result[2])} (limit 100kb)")
					
					if v_name in tag_globals.keys():
						if tag_globals[v_name][1] == str(author):
							tag_globals[v_name][2] = True
							tag_globals[v_name][0] = copy.deepcopy(result[1]) if type(result[1]) == list else result[1]
						else:
							raise PermissionError(
						 		f"Only the author of the {v_name} variable can edit its value ({tag_globals[v_name][1]})")

						result = ""

					else:
						tag_globals[v_name] = [result[2], str(author), True]
						result = ""

				elif result[0] == "gv":
					v_name = result[1]
					if v_name in tag_globals.keys():
						result = tag_globals[v_name][0]
					else:
						if (v_name,) not in db.get_entries("b++2variables", columns=["name"]):
							raise NameError(f"No global variable by the name {safe_cut(v_name)} defined")

						v_list = db.get_entries("b++2variables", columns=["name", "value", "type", "owner"])
						v_value, v_type, v_owner = [v[1:4] for v in v_list if v[0] == v_name][0]

						if type_list[v_type] == list:
							v_value = undo_str_array(v_value)
						else:
							v_value = type_list[v_type](v_value)

						tag_globals[v_name] = [v_value, str(v_owner), False]

						result = v_value

				elif result[0] == 'func_def':
					_, name, code_tuple = result
					user_functions[name] = {"code": code_tuple}
					result = ""
				elif result[0] == 'p':
					if func_params is None: raise NameError(
						"PARAM function cannot be used outside of a custom function.")
					if result[1] >= len(func_params) or result[1] < -len(func_params):
						if result[2]:
							raise KeyError(f"PARAM {result[1]} was not specified in the call to function {custom_func_name}.")
						result = ""
					else:
						result = func_params[result[1]]
				elif result[0] == 'pa':
					if func_params is None: raise NameError(
						"PARAM function cannot be used outside of a custom function.")
					if len(func_params) == 0 and result[1]:
						raise KeyError(f"Function {custom_func_name} requires parameters.")
					result = list(func_params)

				elif result[0] == "n":
					result = runner.name

				elif result[0] == "id":
					result = runner.id

				elif result[0] == "aa":
					result = p_args

				elif result[0] == "c_id":
					result = channel.id

				elif result[0] == "b":
					buttons_to_add.append(evaluated_args)
					result = ""

			if not no_memoize:
				functions[k] = result
			return result

		for k in base_keys:
			evaluate_result(k)

		results = []
		for k, v in functions.items():
			if is_whole(k):
				if type(v) == list: v = express_array(v)
				results.append(v)

	except Exception as e:
		stored_error = e

	for v_name, value in tag_globals.items():
		if not value[2]: continue
		v_value = value[0]
		v_string = str_array(v_value) if type(v_value) == list else str(v_value)

		if (v_name,) not in db.get_entries("b++2variables", columns=["name"]):
			curr_v_type = var_type(v_value)
			db.add_entry("b++2variables", [v_name, v_string, curr_v_type, str(author)])

		else:
			v_list = db.get_entries("b++2variables", columns=["name", "owner"])
			v_owner = [v for v in v_list if v_name == v[0]][0][1]

			if v_owner != str(author):
				raise PermissionError(
				f"Only the author of the {v_name} variable can edit its value ({v_owner})")

			db.edit_entry(
				"b++2variables",
				entry={"value": v_string, "type": var_type(v_value)},
				conditions={"name": v_name})

	output = output.replace("{}", "\t").replace("{", "{{").replace("}", "}}").replace("\t", "{}")

	return [stored_error if stored_error is not None else output.format(*results).replace("\v", "{}") + debug_values,
			buttons_to_add]

if __name__ == "__main__":
	while True:
		_program = input("Program:\n\t")
		print("\n")
		_program = _program.replace("{}", "\v")
		_res = run_bpp_program(_program, [], 184768535107469314, 0, 0)
		if isinstance(_res[0], Exception):
			traceback.print_exception(_res[0])
		else:
			print(_res)
# [TRY [THROW "aeugh" "CustomExceptionName"] [CONCAT "Woa, error! (" [VAR __bpp_exc_class] "). Details: " [VAR __bpp_exc_type]]]