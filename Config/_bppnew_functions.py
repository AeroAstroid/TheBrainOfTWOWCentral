import random, statistics, re, itertools
import numpy as np

try:
	from Config._const import ALPHABET
	from Config._functions import is_float, is_whole, is_number, strip_alpha, match_count
except ModuleNotFoundError:
	from _const import ALPHABET
	from _functions import is_float, is_whole, is_number, strip_alpha, match_count

def express_array(l):
	str_form = " ".join(["\"" + str(a) + "\"" for a in l])
	return f'[ARRAY {str_form}]'

def safe_cut(s):
	return str(s)[:15] + ("..." if len(s) > 15 else "")

def COMMENT(*a): return ""

def USERNAME(): return ("n", )

def USERID(): return ("id", )

def ABS(a):
	if not is_number(a):
		raise TypeError(f"Parameter of ABS function must be a number: {safe_cut(a)}")

	return abs(int(a) if is_whole(a) else float(a))

def INDEX(a, b):
	if type(a) not in [list, str]:
		raise TypeError(f"First parameter of INDEX function must be a string or an array: {safe_cut(a)}")
	if not is_whole(b):
		raise TypeError(f"Second parameter of INDEX function must be an integer: {safe_cut(b)}")
	return a[int(b)]

def SLICE(a, b, c):
	if type(a) not in [list, str]:
		raise TypeError(f"First parameter of SLICE function must be a string or an array: {safe_cut(a)}")
	if not is_whole(b):
		raise TypeError(f"Second parameter of SLICE function must be an integer: {safe_cut(b)}")
	if not is_whole(c):
		raise TypeError(f"Third parameter of SLICE function must be an integer: {safe_cut(c)}")
	return a[int(b):int(c)]

def ARRAY(*a):
	return list(a)

def CONCAT(*a):
	all_type = None
	
	for a1 in a:
		if type(a1) in [int, float]: a1 = str(a1)
		if all_type is None: all_type = type(a1)
		elif type(a1) != all_type:
			raise TypeError("CONCAT parameters must either be all arrays or all strings")
	
	if all_type == str:
		a = [str(a1) for a1 in a]
		return ''.join(a)
	if all_type == list:
		a = list(itertools.chain(*a))
		return a
	else:
		raise IndexError("Cannot call CONCAT function with no arguments")

def LENGTH(a):
	if type(a) in [int, float]: a = str(a)
	return len(a)

def ARGS(a):
	if not is_whole(a):
		raise ValueError(f"ARGS function index must be an integer: {safe_cut(a)}")
	
	return ("a", int(a))

def GLOBALDEFINE(a, b):
	if type(a) != str:
		raise NameError(f"Global variable name must be a string: {safe_cut(a)}")

	if re.search(r"[^A-Za-z_0-9]", a) or re.search(r"[0-9]", a[0]):
		raise NameError(
		f"Global variable name must be only letters, underscores and numbers, and cannot start with a number: {safe_cut(a)}")
	
	return ("gd", b)

def GLOBALVAR(a):
	if type(a) != str:
		raise NameError(f"Global variable name must be a string: {safe_cut(a)}")

	if re.search(r"[^A-Za-z_0-9]", a) or re.search(r"[0-9]", a[0]):
		raise NameError(
		f"Global variable name must be only letters, underscores and numbers, and cannot start with a number: {safe_cut(a)}")
	
	return ("gv", a)

def DEFINE(a, b):
	if type(a) != str:
		raise NameError(f"Variable name must be a string: {safe_cut(a)}")

	if re.search(r"[^A-Za-z_0-9]", a) or re.search(r"[0-9]", a[0]):
		raise NameError(
		f"Variable name must be only letters, underscores and numbers, and cannot start with a number: {safe_cut(a)}")
	
	return ("d", b)

def VAR(a):
	if type(a) != str:
		raise NameError(f"Variable name must be a string: {safe_cut(a)}")

	if re.search(r"[^A-Za-z_0-9]", a) or re.search(r"[0-9]", a[0]):
		raise NameError(
		f"Variable name must be only letters, underscores and numbers, and cannot start with a number: {safe_cut(a)}")
	
	return ("v", a)

def REPEAT(a, b):
	if not is_whole(b):
		raise ValueError(f"Second parameter of REPEAT function is not an integer: {safe_cut(b)}")

	if type(a) != list:
		a = str(a)
	b = int(b)

	if b > 1024:
		raise ValueError(f"Second parameter of REPEAT function is too large: {safe_cut(b)} (limit 1024)")

	return a * b

def CHOOSE(*a):
	if len(a) == 1:
		a = a[0]
	return random.choice(a)

def CHOOSECHAR(a):
	if type(a) != str:
		raise ValueError(f"CHOOSECHAR function parameter is not a string: {safe_cut(a)}")

	return random.choice(list(a))

def IF(a, b, c):
	a = a not in [0, "0"]

	if a:
		return b
	else:
		return c

def COMPARE(a, b, c):
	operations = [">", "<", ">=", "<=", "!=", "="]
	if b not in operations:
		raise ValueError(f"Operation parameter of COMPARE function is not a comparison operator: {safe_cut(b)}")

	if is_number(a): a = float(a)
	if is_number(c): c = float(c)

	if operations.index(b) <= 3 and type(a) != type(c):
		raise TypeError(f"Entries to compare in COMPARE function are not the same type")

	if b == ">": return int(a > c)
	if b == "<": return int(a < c)
	if b == ">=": return int(a >= c)
	if b == "<=": return int(a <= c)
	if b == "!=": return int(a != c)
	if b == "=": return int(a == c)

def MOD(a, b):
	if not is_number(a):
		raise ValueError(f"First parameter of MOD function is not a number: {safe_cut(a)}")
	if not is_number(b):
		raise ValueError(f"First parameter of MOD function is not a number: {safe_cut(a)}")

	a = int(a) if is_whole(a) else float(a)
	b = int(b) if is_whole(b) else float(b)

	if b == 0: raise ZeroDivisionError(f"Second parameter of MOD function cannot be zero")

	return a % b

def MATH(a, b, c):
	operations = "+-*/^"
	if not is_number(a):
		raise ValueError(f"First parameter of MATH function is not a number: {safe_cut(a)}")
	if b not in operations:
		raise ValueError(f"Operation parameter of MATH function not an operation: {safe_cut(b)}")
	if not is_number(c):
		raise ValueError(f"Second parameter of MATH function is not a number: {safe_cut(c)}")

	a = int(a) if is_whole(a) else float(a)
	c = int(c) if is_whole(c) else float(c)

	if b == "+": return a+c
	if b == "-": return a-c

	if b == "*":
		if abs(a) > 1e50:
			raise ValueError(f"First parameter of MATH function too large to safely multiply: {safe_cut(a)} (limit 10^50)")
		if abs(c) > 1e50:
			raise ValueError(f"Second parameter of MATH function too large to safely multiply: {safe_cut(a)} (limit 10^50)")
		return a*c

	if b == "/":
		if c == 0: raise ZeroDivisionError(f"Second parameter of MATH function in division cannot be zero")
		return a/c
	
	if b == "^":
		if abs(a) > 1024:
			raise ValueError(f"First parameter of MATH function too large to safely exponentiate: {safe_cut(a)} (limit 1024)")
		if abs(c) > 128:
			raise ValueError(f"Second parameter of MATH function too large to safely exponentiate: {safe_cut(c)} (limit 128)")
		return a**c

def RANDINT(a, b):
	if not is_whole(a):
		raise ValueError(f"First parameter of RANDINT function is not an integer: {safe_cut(a)}")
	if not is_whole(b):
		raise ValueError(f"Second parameter of RANDINT function is not an integer: {safe_cut(b)}")

	ints = [int(a), int(b)]
	a, b = [min(ints), max(ints)]

	if a == b: b += 1

	return random.randrange(a, b)

def RANDOM(a, b):
	if not is_number(a):
		raise ValueError(f"First parameter of RANDOM function is not a number: {safe_cut(a)}")
	if not is_number(b):
		raise ValueError(f"Second parameter of RANDOM function is not a number: {safe_cut(b)}")

	a = float(a)
	b = float(b)

	return random.uniform(a, b)

def ROUND(a):
	if not is_number(a):
		raise ValueError(f"ROUND function parameter is not a number: {safe_cut(a)}")
	
	return int(round(float(a)))

def FLOOR(a):
	if not is_number(a):
		raise ValueError(f"FLOOR function parameter is not a number: {safe_cut(a)}")
	
	return int(float(a))

def CEIL(a):
	if not is_number(a):
		raise ValueError(f"CEIL function parameter is not a number: {safe_cut(a)}")
	
	return np.ceil(float(a))

FUNCTIONS = {
	"MATH": MATH,
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
	"ARGS": ARGS,
	"ABS": ABS,
	"#": COMMENT,
	"GLOBAL DEFINE": GLOBALDEFINE,
	"GLOBAL VAR": GLOBALVAR,
	"MOD": MOD,
	"LENGTH": LENGTH,
	"USERNAME": USERNAME,
	"USERID": USERID,
	"SLICE": SLICE
}
