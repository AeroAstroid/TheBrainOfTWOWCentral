from lark import Lark

bstargrammar = r"""
start: bstar*
    
?bstar:
    | function
    | ALLBUTBRACKETS
?arg:
    | ("true" | "True") -> true
    | ("false" | "False") -> false
    | unescaped_string
    | string
    | float
    | integer
    | function
    | array
string: ESCAPED_STRING
integer.0: INT
float.2: FLOAT
FLOAT: INT "." INT | "." INT
block: ALPHANUMERIC
array: "{" [arg ("," arg)*] "}"
function: ("[") (block | function) arg* ("]")
COMMENT: ("[# ") ALLBUTBRACKETS ("]")
unescaped_string.-1: ALPHANUMERIC
ALLBUTBRACKETS: ALLEXCEPTBRACKETS+
DIGIT: "0".."9"
INT: DIGIT+
ALPHANUMERIC: (ALLNONCONFLICTING)+
ALLNONCONFLICTING: /([^\[\]\{\}\"\s\,\-]|\- )/
ALLEXCEPTBRACKETS: /[^\[\]]/
// imports from common library my beloved
%import common.ESCAPED_STRING
%import common.SIGNED_INT
%import common.DECIMAL
%import common.C_COMMENT
%import common.WS
%ignore WS
%ignore C_COMMENT
%ignore COMMENT"""
parser = Lark(bstargrammar)


def parseCode(code):
    return parser.parse(code)
