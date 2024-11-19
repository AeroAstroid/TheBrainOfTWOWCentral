import random, statistics, re, itertools, time, math
from typing import Any, NamedTuple, NoReturn

try:
	from Config._const import ALPHABET
	from Config._functions import is_float, is_whole, is_number, strip_alpha, match_count
except ModuleNotFoundError:
	from _const import ALPHABET
	from _functions import is_float, is_whole, is_number, strip_alpha, match_count

class ProgramDefinedException(Exception): # used in THROW
	pass

class ParsingOperation(NamedTuple):
    id: str
    args: Any | None = None

def express_array(array: list) -> str:
	str_form = " ".join(["\"" + str(element) + "\"" for element in array])
	return f'[ARRAY {str_form}]'

def safe_cut(obj: object, cut: int = 15) -> str:
	return str(obj)[:cut] + ("..." if len(str(obj)) > cut else "")

def weak_index(iter: str | list, to_find: object, from_idx: int | None = None, to_idx: int | None = None) -> str | int:
	index: int = 0
	for element in iter[from_idx:to_idx]:
		if element == to_find or str(element) == str(to_find):
			return index
		index += 1
	return ""

def COMMENT(*_: Any) -> str: return ""

def INDEXOF(iter: str | list, to_find: object, from_idx: int | None = None, to_idx: int | None = None):
	if not is_number(from_idx) and from_idx is not None and not isinstance(from_idx, str):
		raise TypeError(f"Optional third parameter of INDEXOF function (from index) must be a number: {safe_cut(from_idx)}")
	if not is_number(to_idx) and to_idx is not None and not isinstance(to_idx, str):
		raise TypeError(f"Optional fourth parameter of INDEXOF function (to index) must be a number: {safe_cut(to_idx)}")
	if isinstance(from_idx, str):
		try:
			from_idx = int(from_idx)
		except:
			raise TypeError(f"Optional third parameter of INDEXOF function (from index) must be a number: {safe_cut(from_idx)}")

	if isinstance(to_idx, str):
		try:
			to_idx = int(to_idx)
		except:
			raise TypeError(f"Optional fourth parameter of INDEXOF function (to index) must be a number: {safe_cut(to_idx)}")
	if type(iter) != str and not isinstance(iter,list):
		raise TypeError(f"First parameter of INDEXOF function (object to index) must be an array or string: {safe_cut(iter)}")
	if from_idx is not None:
		if to_idx is not None:
			return weak_index(iter, to_find, from_idx, to_idx)
		return weak_index(iter, to_find, from_idx)
	return weak_index(iter, to_find)

def TIMEFUNC() -> float: return time.time()

def USERNAME() -> ParsingOperation: return ParsingOperation("n")

def USERID() -> ParsingOperation: return ParsingOperation("id")

def ABS(value: float | int) -> float | int:
	if not is_number(value):
		raise TypeError(f"Parameter of ABS function must be a number: {safe_cut(value)}")

	return abs(int(value) if is_whole(value) else float(value))

def SPLIT(to_split: object, seperator: object) -> list:
	if type(to_split) == list:
		raise TypeError(f"First parameter of SPLIT function (string to split) cannot be an array: {safe_cut(to_split)}")
	if type(seperator) == list:
		raise TypeError(f"Second parameter of SPLIT function (seperator string) cannot be an array: {safe_cut(seperator)}")
	return str(to_split).split(str(seperator))

def REPLACE(to_replace: object, old: object, new: object) -> str:
	if type(to_replace) == list:
		raise TypeError(f"First parameter of REPLACE function (string to replace) cannot be an array: {safe_cut(to_replace)}")
	return str(to_replace).replace(str(old),str(new))

def INDEX(iter: list | str, idx: int) -> object:
	if type(iter) not in [list, str]:
		raise TypeError(f"First parameter of INDEX function (values to index) must be a string or an array: {safe_cut(iter)}")
	if not is_whole(idx):
		raise TypeError(f"Second parameter of INDEX function (the index) must be an integer: {safe_cut(idx)}")
	return iter[int(idx)]

def SLICE(to_cut: object, start: int, end: int, step: int | None = None) -> str | list:
	if not is_whole(start):
		raise TypeError(f"Second parameter of SLICE function (start of slice) must be an integer: {safe_cut(start)}")
	if not is_whole(end):
		raise TypeError(f"Third parameter of SLICE function (end of slice) must be an integer: {safe_cut(end)}")
	if not is_whole(step) and step is not None:
		raise TypeError(f"Optional fourth parameter of SLICE function (slice step) must be an integer: {safe_cut(step)}")
	if step == 0 and step is not None:
		raise TypeError(f"Optional fourth parameter of SLICE function (slice step) cannot be 0: {safe_cut(step)}")
	if type(to_cut) == list:
		to_cut = to_cut
	else:
		to_cut = str(to_cut)
		
	return to_cut[int(start):int(end):(int(step) if step else 1)]

def ARRAY(*elements: object) -> list:
	return list(elements)

def CONCAT(*to_concatenate: object) -> str | list:
	all_type = None
	
	for element in to_concatenate:
		if type(element) in [int, float]: element = str(element)
		if all_type is None: all_type = type(element)
		elif type(element) != all_type:
			raise TypeError("CONCAT function parameters must either be all arrays or all strings")
	
	if all_type == str:
		to_concatenate = [str(element) for element in to_concatenate]
		return ''.join(to_concatenate)
	if all_type == list:
		to_concatenate = list(itertools.chain(*to_concatenate))
		return to_concatenate
	else:
		raise IndexError("Cannot call CONCAT function with no arguments")

def LENGTH(obj: object) -> int:
	if type(obj) in [int, float]: obj = str(obj)
	return len(obj)

def ARGS(idx: int | None = None) -> ParsingOperation:
	if not is_whole(idx) and idx is not None:
		raise ValueError(f"Optional parameter of ARGS function (the argument to get) must be an integer: {safe_cut(idx)}")
	
	if idx is None:
		return ParsingOperation("aa")
	
	return ParsingOperation("a", int(idx))

def GLOBALDEFINE(gvar: str, value: object) -> ParsingOperation:
	if type(gvar) != str:
		raise NameError(f"Global variable name must be a string: {safe_cut(gvar)}")

	if re.search(r"[^A-Za-z_0-9]", gvar) or re.search(r"[0-9]", gvar[0]):
		raise NameError(
		f"Global variable name must be only letters, underscores and numbers, and cannot start with a number: {safe_cut(gvar)}")
	
	return ParsingOperation("gd", (gvar, value))

def GLOBALVAR(gvar: str) -> ParsingOperation:
	if type(gvar) != str:
		raise NameError(f"Global variable name must be a string: {safe_cut(gvar)}")

	if re.search(r"[^A-Za-z_0-9]", gvar) or re.search(r"[0-9]", gvar[0]):
		raise NameError(
		f"Global variable name must be only letters, underscores and numbers, and cannot start with a number: {safe_cut(gvar)}")
	
	return ParsingOperation("gv", gvar)

def DEFINE(var_name: str, value: object) -> ParsingOperation:
	if type(var_name) != str:
		raise NameError(f"Variable name must be a string: {safe_cut(var_name)}")
	
	return ParsingOperation("d", (var_name, value))

def VAR(var_name: str) -> ParsingOperation:
	if type(var_name) != str:
		raise NameError(f"Variable name must be a string: {safe_cut(var_name)}")
	
	return ParsingOperation("v", var_name)

def REPEAT(to_repeat: object, times: int) -> str:
	if not is_whole(times):
		raise ValueError(f"Second parameter of REPEAT function (times to repeat) is not an integer: {safe_cut(times)}")

	if type(to_repeat) != list:
		to_repeat = str(to_repeat)
	times = int(times)

	if times > 1024:
		raise ValueError(f"Second parameter of REPEAT function (times to repeat) is above 1,024: {safe_cut(times)}")

	return to_repeat * times

def CHOOSE(*options: list) -> object:
	if len(options) == 1:
		options = options[0]
	return random.choice(options)

def CHOOSECHAR(string: str) -> str:
	if type(string) != str:
		raise ValueError(f"CHOOSECHAR function parameter is not a string: {safe_cut(string)}")

	return random.choice(list(string))

def IF(condition: object, if_true: object, if_false: object = "") -> object:
	condition = condition not in [0, "0"]

	if condition:
		return if_true
	else:
		return if_false

def COMPARE(first: object, op: str, second: object) -> object:
	operations = [">", "<", ">=", "<=", "!=", "=", "==", "and", "or"]
	if op not in operations:
		raise ValueError(f"Second parameter of COMPARE function (the operation) is not a comparison operator: {safe_cut(op)}")

	if is_number(first): first = float(first)
	if is_number(second): second = float(second)

	if operations.index(op) <= 3 and type(first) != type(second):
		raise TypeError(f"Entries to compare in COMPARE function are not the same type")

	if op == ">": return int(first > second)
	if op == "<": return int(first < second)
	if op == ">=": return int(first >= second)
	if op == "<=": return int(first <= second)
	if op == "!=": return int(first != second)
	if op == "=" or op == "==": return int(first == second)
	if op == "and": return int(first and second) if type(first and second) is bool else first and second
	if op == "or": return int(first or second) if type(first or second) is bool else first or second

def MOD(value: int | float, divisor: int | float) -> int | float:
	if not is_number(value):
		raise ValueError(f"First parameter of MOD function (the value) is not a number: {safe_cut(value)}")
	if not is_number(divisor):
		raise ValueError(f"Second parameter of MOD function (the divisor) is not a number: {safe_cut(divisor)}")

	value = int(value) if is_whole(value) else float(value)
	divisor = int(divisor) if is_whole(divisor) else float(divisor)

	if divisor == 0: raise ZeroDivisionError(f"Second parameter of MOD function (the divisor) cannot be zero")

	return value % divisor

def MATHFUNC(first: int | float, op: str, second: int | float) -> int | float:
	operations = "+-*/^%"
	if not is_number(first):
		raise ValueError(f"First parameter of MATH function is not a number: {safe_cut(first)}")
	if op not in operations:
		raise ValueError(f"Operation parameter of MATH function not an operation: {safe_cut(op)}")
	if not is_number(second):
		raise ValueError(f"Second parameter of MATH function is not a number: {safe_cut(second)}")

	first = int(first) if is_whole(first) else float(first)
	second = int(second) if is_whole(second) else float(second)

	if op == "+": return first+second
	if op == "-": return first-second

	if op == "*":
		if abs(first) > 1e150:
			raise ValueError(f"First parameter of MATH function too large to safely multiply: {safe_cut(first)} (limit 10^150)")
		if abs(second) > 1e150:
			raise ValueError(f"Second parameter of MATH function too large to safely multiply: {safe_cut(first)} (limit 10^150)")
		return first*second

	if op == "/":
		if second == 0: raise ZeroDivisionError(f"Second parameter of MATH function in division cannot be zero")
		return first/second
	
	if op == "%":
		if second == 0: raise ZeroDivisionError(f"Second parameter of MATH function in modulo cannot be zero")
		return first%second
	
	
	if op == "^":
		try:
			return math.pow(first, second)
		except OverflowError:
			raise ValueError(f"Parameters of MATH function too large to safely exponentiate: {safe_cut(first)}, {safe_cut(second)}")

def RANDINT(minval: int, maxval: int) -> int: # Yes, technically they can be flipped. I'm still using min/max though.
	if not is_whole(minval):
		raise ValueError(f"First parameter of RANDINT function is not an integer: {safe_cut(minval)}")
	if not is_whole(maxval):
		raise ValueError(f"Second parameter of RANDINT function is not an integer: {safe_cut(maxval)}")

	ints = [int(minval), int(maxval)]
	minval, maxval = [min(ints), max(ints)]

	if minval == maxval: maxval += 1

	return random.randrange(minval, maxval)

def RANDOM(minval: int | float, maxval: int | float) -> float:
	if not is_number(minval):
		raise ValueError(f"First parameter of RANDOM function is not a number: {safe_cut(minval)}")
	if not is_number(maxval):
		raise ValueError(f"Second parameter of RANDOM function is not a number: {safe_cut(maxval)}")

	minval = float(minval)
	maxval = float(maxval)

	return random.uniform(minval, maxval)

def THROW(details: any) -> NoReturn:
	raise ProgramDefinedException(str(details))
	
def TYPEFUNC(obj: object) -> str:
	if is_whole(obj): return "int"
	if is_number(obj): return "float"
	return type(obj).__name__
	
def ROUND(to_round: int | float, places: int = 0) -> int | float:
	if not is_number(to_round):
		raise ValueError(f"First parameter of ROUND function (value to round) is not a number: {safe_cut(to_round)}")
	if not is_whole(places):
		raise ValueError(f"Optional second parameter of ROUND function (decimal places) is not an integer: {safe_cut(places)}")
	
	rounded = round(float(to_round), int(places))
	if rounded.is_integer(): return int(rounded)
	return rounded

def FLOOR(val: float) -> int:
	if not is_number(val):
		raise ValueError(f"FLOOR function parameter is not a number: {safe_cut(val)}")
	
	return math.floor(float(val))

def CEIL(val: float) -> int:
	if not is_number(val):
		raise ValueError(f"CEIL function parameter is not a number: {safe_cut(val)}")
	
	return math.ceil(float(val))

def LOG(val: int | float, base: int | float) -> float:
	if not is_number(val):
		raise ValueError(f"First parameter of LOG function (the value) is not a number: {safe_cut(val)}")
	if not is_number(base):
		raise ValueError(f"Second parameter of LOG function (the base) is not a number: {safe_cut(base)}")
		
	if base == 0: raise ValueError("Second parameter of LOG function (the base) must not be zero")
		
	return math.log(float(val),float(base))

def FACTORIAL(val: int | float) -> float:
	if not is_number(val):
		raise ValueError(f"FACTORIAL function parameter is not a number: {safe_cut(val)}")
	
	try:
		return math.gamma(float(val)+1) # extension of the factorial function, allows floats too
	except OverflowError:
		raise ValueError(f"First parameter of FACTORIAL function too large to safely factorial: {safe_cut(val)}")

def SIN(val: int | float) -> float:
	if not is_number(val):
		raise ValueError(f"SIN function parameter is not a number: {safe_cut(val)}")
	
	return math.sin(float(val))

def TAN(val: int | float) -> float:
	if not is_number(val):
		raise ValueError(f"TAN function parameter is not a number: {safe_cut(val)}")
	
	return math.tan(float(val))

def COS(val: int | float) -> float:
	if not is_number(val):
		raise ValueError(f"COS function parameter is not a number: {safe_cut(val)}")
	
	return math.cos(float(val))

def MINFUNC(lst: list) -> object:
	if not type(lst) == list:
		raise ValueError(f"MIN function parameter is not a list: {safe_cut(lst)}")
	
	if 0 not in [is_number(elem) for elem in lst]:
		lst = [float(elem) for elem in lst]
	
	return min(lst)

def MAXFUNC(lst: list) -> object:
	if not type(lst) == list:
		raise ValueError(f"MAX function parameter is not a list: {safe_cut(lst)}")
	
	if 0 not in [is_number(elem) for elem in lst]:
		lst = [float(elem) for elem in lst]
	
	return max(lst)

def SHUFFLE(lst: list) -> list:
	if not type(lst) == list:
		raise ValueError(f"SHUFFLE function parameter is not a list: {safe_cut(lst)}")
		
	return random.sample(lst, k=len(lst))

def SORTFUNC(lst: list) -> list:
	if not type(lst) == list:
		raise ValueError(f"SORT function parameter is not a list: {safe_cut(lst)}")
	
	if 0 not in [is_number(elem) for elem in lst]:
		lst = [float(elem) for elem in lst]
	
	return sorted(lst)

def JOIN(to_join: list, seperator: str = "") -> str:
	if not type(to_join) == list:
		raise ValueError(f"First JOIN function parameter (list of values) is not a list: {safe_cut(to_join)}")
	if not type(seperator) == str:
		raise ValueError(f"Optional second JOIN function parameter (seperator) is not a string: {safe_cut(seperator)}")
	
	to_join = [str(elem) for elem in to_join]
	
	return seperator.join(to_join)
	
def SETINDEX(lst: list | str, idx: int, value: object) -> list | str:
	if not is_whole(idx):
		raise ValueError(f"SETINDEX function parameter is not an integer: {safe_cut(idx)}")
	if type(lst) == list:
		mylist = lst.copy()
		mylist[int(idx)] = value
		return mylist
	lst = str(lst)
	if len(str(value)) > 1:
		raise ValueError(f"SETINDEX function paramater is not a character: {safe_cut(value)}")
	return lst[0:int(idx)] + value + lst[int(idx)+1:]

def UNICODE(char: str) -> int:
	if len(str(char)) != 1:
		ValueError(f"UNICODE function paramater is not a character: {safe_cut(char)}")
	return ord(str(char))

def CHARFUNC(val: int) -> str:
	if not is_whole(val):
		raise ValueError(f"CHAR function parameter is not an integer: {safe_cut(val)}")
	try:
		out = chr(val)
	except:
		raise ValueError(f"CHAR function parameter is not a valid character: {safe_cut(val)}")
	return out

def CHANNEL() -> ParsingOperation:
	return ParsingOperation("c_id")

FUNCTIONS = {
	"MATH": MATHFUNC,
	"RANDINT": RANDINT,
	"RANDOM": RANDOM,
	"FLOOR": FLOOR,
	"CEIL": CEIL,
	"ROUND": ROUND,
	"COMPARE": COMPARE,
	"IF": IF,
	"CHOOSE": CHOOSE,
	"CHOOSECHAR": CHOOSECHAR,
	"REPEAT": REPEAT,
	"DEFINE": DEFINE,
	"VAR": VAR,
	"CONCAT": CONCAT,
	"ARRAY": ARRAY,
	"INDEX": INDEX,
	"INDEXOF": INDEXOF,
	"ARGS": ARGS,
	"ABS": ABS,
	"#": COMMENT,
	"GLOBAL DEFINE": GLOBALDEFINE,
	"GLOBAL VAR": GLOBALVAR,
	"MOD": MOD,
	"LENGTH": LENGTH,
	"USERNAME": USERNAME,
	"USERID": USERID,
	"SLICE": SLICE,
	"REPLACE": REPLACE,
	"SPLIT": SPLIT,
	"TIME": TIMEFUNC,
	"LOG": LOG,
	"FACTORIAL": FACTORIAL,
	"SIN": SIN,
	"COS": COS,
	"TAN": TAN,
	"TYPE": TYPEFUNC,
	"THROW": THROW,
	"MIN": MINFUNC,
	"MAX": MAXFUNC,
	"SHUFFLE": SHUFFLE,
	"SORT": SORTFUNC,
	"JOIN": JOIN,
	"SETINDEX": SETINDEX,
	"CHAR" : CHARFUNC,
	"UNICODE" : UNICODE,
	"CHANNEL" : CHANNEL
}
