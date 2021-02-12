from Config._bpp_functions import *
from Config._functions import grammar_list

# Breaks code up into the operations/variables in parentheses for them to be interpreted by other functions
def parenthesis_parser(raw, VARIABLES, OUTPUT, var=False):
	expression = [[0, ""]] # List of all expressions and their parenthesis level
	current_level = 0 # List of the current level in parsing
	backslash = False # Is the next character backslashed?

	for char in list(raw): # Analyze character by character

		# Which expression is the one being analyzed currently? It's always gonna be the last one on the current level
		current_var_index = [x for x in range(len(expression)) if expression[x][0] == current_level][-1]

		if char == "\\": # If it's a backslash character...
			if backslash: # If it's backslashed itself, include it normally
				expression[current_var_index][1] += char
				backslash = False
			else: # If it's not, the next character will be backslashed
				backslash = True
			continue
		
		if char == "(":
			if backslash: # If the parenthesis is backslashed, append it as a normal character
				expression[current_var_index][1] += "\\"
				expression[current_var_index][1] += char
				backslash = False # End the backslash
			else: # If it's not backslashed, it's a level rise
				current_level += 1 # Increase the current level
				expression[current_var_index][1] += "{res}" # There's an operation to solve for this expression now
				expression.append([current_level, "("]) # Add a new expression with the new level
			continue
		
		if char == ")":
			if backslash: # Again, if the parenthesis is backslashed, append it as a normal character
				expression[current_var_index][1] += "\\"
				expression[current_var_index][1] += char
				backslash = False # End the backslash

			elif current_level == 0: # Throw an error if there's an imbalance in the parenthesis level
				raise SyntaxError("Unbackslashed closing parentheses without any opening parentheses.")
				# If it's not backslashed and it's valid...
				expression[current_var_index][1] += ")" # Append it to the end of the current expression
				current_level -= 1 # Go a level down
			continue
		
		if char == ";":
			expression[current_var_index][1] += char
			backslash = False
			continue
		
		if backslash: # If this character is backslashed but it's not a character that needs special escaping
			# with backslashes (like parentheses), just add the backslash before adding the character
			expression[current_var_index][1] += "\\"
			backslash = False # End the backslash

		expression[current_var_index][1] += char # Add the character
	
	# We're going to move top down for this, so start with the highest index in the whole expression array
	starting_index = max([x[0] for x in expression])

	for counting_up in range(starting_index + 1):
		# Across iterations, will range from starting_index to 0
		parsing_level = starting_index - counting_up

		for r in range(len(expression)): # Search through each expression
			if expression[r][0] == parsing_level: # If it's on the same level as the current parsing level...

				expression_to_solve = expression[r][1] # The expression is the one specified...
				if parsing_level != 0: # But if the level is above zero, there are parentheses, so get rid of them
					expression_to_solve = expression_to_solve[1:-1]

				operation_info = operation_check(expression_to_solve) # operation() defined above

				if operation_info[0]: # There is an operation
					if operation_info[0] == "out": # If that operation is out{}...
						if var:
							raise TypeError("Cannot call variable as an out{} operation")
						
						new_op_info = operation_check(operation_info[1][1:-1]) # Run the operation checker in the
						# contents of out{} to solve an operation inside (this is not meant to be done for variables)
						
						if new_op_info[0]: # If the operation went fine

							if type(new_op_info[1]) == list:
								new_op_info[1] = list_to_array(new_op_info[1])

							try:
								if "\t" in new_op_info[1]:
									new_op_info[1] = new_op_info[1].replace("\t", ";")
							except TypeError:
								pass
							
							OUTPUT += str(new_op_info[1]) # Add the result of above to the output
							return [new_op_info[1], OUTPUT] # End the line here - out{} operations are final

						elif not new_op_info[0]: # If there's no operation, just add the old result to OUTPUT

							if type(new_op_info[1]) == list:
								new_op_info[1] = list_to_array(new_op_info[1])

							try:
								if "\t" in operation_info[1]:
									operation_info[1] = operation_info[1].replace("\t", ";")
							except TypeError:
								pass
							
							OUTPUT += str(operation_info[1][1:-1]) # When there's no operation, parentheses are removed
							return [operation_info[1][1:-1], OUTPUT]

						# If it gets here, that means there was an operation but there was an error
						operation_info = new_op_info # Replace new_op_info with operation_info
						# It'll go through the if operation_info[2] checker below and the error will be reported
					
					'''if operation_info[2]: # If there was an error with the operation...
						operation = operation_info[1][0]
						operation_f = operation.replace("_", " ").strip().replace("\\", "")
						param_name = operation_info[1][1]
						expected_types = grammar_list(FUNCTIONS[operation]["TYPES"][param_name], c_or=True)
						param = operation_info[1][2]

						raise TypeError( # Raise the error
						f"Operation `{operation_f}` expected type {expected_types}, but `{param}` can't fit said type")
						'''
					
					# If it got here, that means the operation was successful and is not out{}
					result = operation_info[1] # Define the result
					if type(result) == list: 
						result = list_to_array(result) # Converts result to b++ array format if operation result is a list
				elif r != 0: # If there was no matching operation, try to interpret it as a variable
					# Do this if and only if r != 0, because if r == 0 the expression is outside parentheses, and
					# variables are not meant to be called outside parentheses even when there's only a variable call
					variable_info = variables(expression_to_solve, VARIABLES) # variables() defined above

					if variable_info[0]: # If the variable was found in the dict
						result = variable_info[1] # Define the results
					else: # If it wasn't found, return a KeyError
						raise KeyError(f"Variable {expression_to_solve} called but not defined")

				else: # If r == 0 and it's not an operation, pass the expression unchanged
					result = expression_to_solve
				
				if r == 0: # If r == 0, last operation; whatever the result, it's the result of the entire line
					final_result = result

				# If r != 0 change the expression that originated this operation/variable
				for back in range(r): # For every element before the current one in expression array
					# r-back-1 means to go backwards from r to the start
					if expression[r-back-1][0] == expression[r][0] - 1: # If it's the first one that has the level
						# 1 under the level of the current expression, it means that's the expression that called
						# for the current expression
						# Replace {res} placeholder with the result from the operation/variable
						expression[r-back-1][1] = expression[r-back-1][1].replace("{res}", str(result), 1)
						break

	return [final_result, OUTPUT]
