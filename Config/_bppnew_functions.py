import random, statistics, re, itertools, time, math
import numpy as np

try:
	from Config._const import ALPHABET
	from Config._functions import is_float, is_whole, is_number, strip_alpha, match_count
except ModuleNotFoundError:
	from _const import ALPHABET
	from _functions import is_float, is_whole, is_number, strip_alpha, match_count

class ProgramDefinedException(Exception): # used in THROW
	pass

def express_array(l):
	str_form = " ".join(["\"" + str(a) + "\"" for a in l])
	return f'[ARRAY {str_form}]'

def safe_cut(s):
	return str(s)[:15] + ("..." if len(str(s)) > 15 else "")

def COMMENT(*a): return ""

def INDEXOF(a,b,c=None,d=None):
	if not is_number(c) and c is not None and not isinstance(c,str):
		raise TypeError(f"Optional third parameter of INDEXOF function must be a number: {safe_cut(c)}")
	if not is_number(d) and d is not None and not isinstance(d,str):
		raise TypeError(f"Optional fourth parameter of INDEXOF function must be a number: {safe_cut(d)}")
	if isinstance(c,str):
		try:
			c = int(c)
		except:
			raise TypeError(f"Optional third parameter of INDEXOF function must be a number: {safe_cut(c)}")

	if isinstance(d,str):
		try:
			d = int(d)
		except:
			raise TypeError(f"Optional third parameter of INDEXOF function must be a number: {safe_cut(d)}")
	if type(a) != str and not isinstance(a,list):
		raise TypeError(f"First parameter of INDEXOF function must be an array or string: {safe_cut(a)}")
	if c is not None:
		if d is not None:
			return a.index(b,c,d)
		return a.index(b,c)
	return a.index(b)

def TIMEFUNC(): return time.time()

def USERNAME(): return ("n", )

def USERID(): return ("id", )

def ABS(a):
	if not is_number(a):
		raise TypeError(f"Parameter of ABS function must be a number: {safe_cut(a)}")

	return abs(int(a) if is_whole(a) else float(a))

def SPLIT(a,b):
	if type(a) == list:
		raise TypeError(f"Parameter of SPLIT function cannot be an array: {safe_cut(a)}")
	if type(b) == list:
		raise TypeError(f"Parameter of SPLIT function cannot be an array: {safe_cut(b)}")
	return str(a).split(str(b))

def REPLACE(a,b,c):
	if type(a) == list:
		raise TypeError(f"Parameter of REPLACE function cannot be an array: {safe_cut(a)}")
	return str(a).replace(str(b),str(c))

def INDEX(a, b):
	if type(a) not in [list, str]:
		raise TypeError(f"First parameter of INDEX function must be a string or an array: {safe_cut(a)}")
	if not is_whole(b):
		raise TypeError(f"Second parameter of INDEX function must be an integer: {safe_cut(b)}")
	return a[int(b)]

def SLICE(a, b, c):
	if not is_whole(b):
		raise TypeError(f"Second parameter of SLICE function must be an integer: {safe_cut(b)}")
	if not is_whole(c):
		raise TypeError(f"Third parameter of SLICE function must be an integer: {safe_cut(c)}")
	if type(a) == list:
		to_cut = a
	else:
		to_cut = str(a)
		
	return to_cut[int(b):int(c)]

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

def ARGS(a=None):
	if not is_whole(a) and a is not None:
		raise ValueError(f"ARGS function index must be an integer: {safe_cut(a)}")
	
	if a is None:
		return ("aa", )
	
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

def IF(a, b, c=""):
	a = a not in [0, "0"]

	if a:
		return b
	else:
		return c

def COMPARE(a, b, c):
	operations = [">", "<", ">=", "<=", "!=", "=", "=="]
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
	if b == "=" or b == "==": return int(a == c)

def MOD(a, b):
	if not is_number(a):
		raise ValueError(f"First parameter of MOD function is not a number: {safe_cut(a)}")
	if not is_number(b):
		raise ValueError(f"Second parameter of MOD function is not a number: {safe_cut(b)}")

	a = int(a) if is_whole(a) else float(a)
	b = int(b) if is_whole(b) else float(b)

	if b == 0: raise ZeroDivisionError(f"Second parameter of MOD function cannot be zero")

	return a % b

def MATHFUNC(a, b, c):
	operations = "+-*/^%"
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
	
	if b == "%":
		if c == 0: raise ZeroDivisionError(f"Second parameter of MATH function in modulo cannot be zero")
		return a%c
	
	
	if b == "^":
		try:
			return math.pow(a, c)
		except OverflowError:
			raise ValueError(f"Parameters of MATH function too large to safely exponentiate: {safe_cut(a)}, {safe_cut(c)}")

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

def THROW(a): # don't need to check, because either way it'll error
	raise ProgramDefinedException(a)
	
def TYPEFUNC(a):
	if is_whole(a): return "int"
	if is_number(a): return "float"
	return type(a).__name__
	
def ROUND(a, b=0):
	if not is_number(a):
		raise ValueError(f"ROUND function parameter is not a number: {safe_cut(a)}")
	if not is_whole(b):
		raise ValueError(f"ROUND function parameter is not an integer: {safe_cut(b)}")
	
	rounded = round(float(a), int(b))
	if rounded.is_integer(): return int(rounded)
	return rounded

def FLOOR(a):
	if not is_number(a):
		raise ValueError(f"FLOOR function parameter is not a number: {safe_cut(a)}")
	
	return math.floor(float(a))

def CEIL(a):
	if not is_number(a):
		raise ValueError(f"CEIL function parameter is not a number: {safe_cut(a)}")
	
	return math.ceil(float(a))

def LOG(a, b):
	if not is_number(a):
		raise ValueError(f"LOG function parameter is not a number: {safe_cut(a)}")
	if not is_number(b):
		raise ValueError(f"LOG function parameter is not a number: {safe_cut(b)}")
		
	if b == 0: raise ValueError("Second parameter of LOG function must not be zero")
		
	return math.log(float(a),float(b))

def FACTORIAL(a):
	if not is_number(a):
		raise ValueError(f"FACTORIAL function parameter is not a number: {safe_cut(a)}")
	
	try:
		return math.gamma(float(a)+1) # extension of the factorial function, allows floats too
	except OverflowError:
		raise ValueError(f"First parameter of FACTORIAL function too large to safely factorial: {safe_cut(a)}")

def SIN(a):
	if not is_number(a):
		raise ValueError(f"SIN function parameter is not a number: {safe_cut(a)}")
	
	return math.sin(float(a))

def TAN(a):
	if not is_number(a):
		raise ValueError(f"TAN function parameter is not a number: {safe_cut(a)}")
	
	return math.tan(float(a))

def COS(a):
	if not is_number(a):
		raise ValueError(f"COS function parameter is not a number: {safe_cut(a)}")
	
	return math.cos(float(a))

def MINFUNC(a):
	if not type(a) == list:
		raise ValueError(f"MIN function parameter is not a list: {safe_cut(a)}")
	
	if 0 not in [is_number(elem) for elem in a]:
		a = [float(elem) for elem in a]
	
	return min(a)

def MAXFUNC(a):
	if not type(a) == list:
		raise ValueError(f"MAX function parameter is not a list: {safe_cut(a)}")
	
	if 0 not in [is_number(elem) for elem in a]:
		a = [float(elem) for elem in a]
	
	return max(a)

def SHUFFLE(a):
	if not type(a) == list:
		raise ValueError(f"SHUFFLE function parameter is not a list: {safe_cut(a)}")
		
	return random.sample(a, k=len(a))

def SORTFUNC(a):
	if not type(a) == list:
		raise ValueError(f"SORT function parameter is not a list: {safe_cut(a)}")
	
	if 0 not in [is_number(elem) for elem in a]:
		a = [float(elem) for elem in a]
	
	return sorted(a)

def JOIN(a, b=""):
	if not type(a) == list:
		raise ValueError(f"First JOIN function parameter is not a list: {safe_cut(a)}")
	if not type(b) == str:
		raise ValueError(f"Second JOIN function parameter is not a string: {safe_cut(b)}")
	
	a = [str(elem) for elem in a]
	
	return b.join(a)
	
def SETINDEX(a, b, c):
	if not is_whole(b):
		raise ValueError(f"SETINDEX function parameter is not an integer: {safe_cut(b)}")
	if type(a) == list:
		mylist = a.copy()
		mylist[int(b)] = c
		return mylist
	a = str(a)
	if len(str(c)) > 1:
		raise ValueError(f"SETINDEX function paramater is not a character: {safe_cut(c)}")
	return a[0:int(b)] + c + a[int(b)+1:]

def UNICODE(a):
	if len(str(a)) != 1:
		ValueError(f"CHAR function paramater is not a character: {safe_cut(a)}")
	return ord(str(a))

def CHARFUNC(a):
	if not is_whole(a):
		raise ValueError(f"CHAR function parameter is not an integer: {safe_cut(a)}")
	try:
		out = chr(a)
	except:
		raise ValueError(f"CHAR function parameter is not a valid character: {safe_cut(a)}")
	return out

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
	"UNICODE" : UNICODE
}
